-- Botonera: la base entera en una migración. Se puede correr más de una vez.
--
-- Nadie lee ni escribe las tablas directo: RLS prendido y sin políticas. Todo pasa por funciones
-- SECURITY DEFINER que piden una de dos llaves:
--   · BM_SECRET (p_secret): la usan los scripts del skill desde tu máquina. En la base vive solo su sha256.
--   · el token de sesión (p_token): lo da bm_entrar a la web después del PIN. Dura 30 días por dispositivo.
-- La anon/publishable key sola no alcanza para nada.
--
-- Después de esta migración se corre una vez bm_instalar(...) con el hash de tu BM_SECRET
-- (install.sh lo deja listo en ~/.config/botonera/instalar.sql).

create extension if not exists pgcrypto with schema extensions;
create extension if not exists pg_net with schema extensions;
create extension if not exists pg_cron;

-- ───────────────────────── tablas ─────────────────────────

create table if not exists public.botoneras (
  clave            text primary key,
  session_id       text,
  sesion_titulo    text,
  skill            text,
  proyecto         text,
  titulo           text not null,
  n_items          integer not null default 0,
  datos            jsonb not null,
  html             text not null,
  estado           text not null default 'abierta'
                   check (estado in ('abierta', 'decidida', 'recibida', 'esperando', 'aplicada',
                                     'respondida_en_chat', 'archivada')),
  respuesta_texto  text,
  resumen_aplicado text,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now(),
  decided_at       timestamptz,
  received_at      timestamptz,
  applied_at       timestamptz,
  espera_motivo    text,
  esperando_at     timestamptz,
  avisada_at       timestamptz
);

-- k/v: hashes del secreto y del PIN, contadores del PIN, y la config de los avisos.
create table if not exists public.bm_config (
  k text primary key,
  v text not null
);

create table if not exists public.bm_sesiones (
  token_sha256 text primary key,
  created_at   timestamptz not null default now(),
  expires_at   timestamptz not null default (now() + interval '30 days'),
  last_used_at timestamptz
);

-- Un dispositivo suscripto a los avisos (Web Push).
create table if not exists public.bm_push (
  endpoint     text primary key,
  p256dh       text not null,
  auth         text not null,
  token_sha256 text,
  created_at   timestamptz not null default now(),
  last_ok_at   timestamptz,
  fallos       integer not null default 0
);

alter table public.botoneras   enable row level security;
alter table public.bm_config   enable row level security;
alter table public.bm_sesiones enable row level security;
alter table public.bm_push     enable row level security;
revoke all on public.botoneras, public.bm_config, public.bm_sesiones, public.bm_push from anon, authenticated;

insert into public.bm_config (k, v) values
  ('pin_fallos', '0'), ('pin_bloqueado', 'false'), ('zona', 'UTC')
on conflict (k) do nothing;

-- ───────────────────────── llaves ─────────────────────────

create or replace function public.bm_check(p_secret text)
returns void language plpgsql security definer set search_path = public, extensions as $$
begin
  if p_secret is null or not exists (
    select 1 from public.bm_config
     where k = 'secret_sha256' and v = encode(digest(p_secret, 'sha256'), 'hex')
  ) then
    raise exception 'secret invalido';
  end if;
end $$;

create or replace function public.bm_check_token(p_token text)
returns void language plpgsql security definer set search_path = public, extensions as $$
begin
  update public.bm_sesiones set last_used_at = now()
   where token_sha256 = encode(digest(coalesce(p_token, ''), 'sha256'), 'hex')
     and expires_at > now();
  if not found then
    raise exception 'token invalido';
  end if;
end $$;

-- ───────────────────────── instalación ─────────────────────────

-- Una vez, desde el editor SQL (como postgres). Se puede repetir: pisa la config y conserva el secreto de avisos.
--   p_secret_sha256: sha256 hex de tu BM_SECRET
--   p_avisar_url:    https://<ref>.supabase.co/functions/v1/bm-avisar (la función de los avisos)
--   p_zona:          zona horaria IANA para el silencio nocturno y el aviso de vencimientos
--   p_contacto:      URL https o mailto: que va en la firma VAPID de los avisos
create or replace function public.bm_instalar(p_secret_sha256 text, p_avisar_url text, p_zona text, p_contacto text)
returns text language plpgsql security definer set search_path = public, extensions as $$
begin
  if coalesce(p_secret_sha256, '') !~ '^[0-9a-f]{64}$' then raise exception 'p_secret_sha256 tiene que ser sha256 hex'; end if;
  if not exists (select 1 from pg_timezone_names where name = p_zona) then raise exception 'zona desconocida: %', p_zona; end if;
  insert into public.bm_config (k, v) values
    ('secret_sha256', p_secret_sha256), ('avisar_url', p_avisar_url), ('zona', p_zona), ('contacto', p_contacto)
  on conflict (k) do update set v = excluded.v;
  if not exists (select 1 from vault.secrets where name = 'bm_avisar_secret') then
    perform vault.create_secret(encode(gen_random_bytes(32), 'hex'), 'bm_avisar_secret');
  end if;
  return 'ok';
end $$;

-- ───────────────────────── PIN y sesiones de la web ─────────────────────────

create or replace function public.bm_poner_pin(p_secret text, p_pin text)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare v_sal text := encode(gen_random_bytes(16), 'hex');
begin
  perform public.bm_check(p_secret);
  if p_pin !~ '^[0-9]{4}$' then raise exception 'el PIN son 4 digitos'; end if;
  insert into public.bm_config (k, v) values ('pin_sal', v_sal)
    on conflict (k) do update set v = excluded.v;
  insert into public.bm_config (k, v) values ('pin_sha256', encode(digest(v_sal || p_pin, 'sha256'), 'hex'))
    on conflict (k) do update set v = excluded.v;
  update public.bm_config set v = '0' where k = 'pin_fallos';
  update public.bm_config set v = 'false' where k = 'pin_bloqueado';
  delete from public.bm_sesiones where true;   -- PIN nuevo: se cierran todas las sesiones (safeupdate pide WHERE)
  return 'ok';
end $$;

-- Devuelve el error en vez de hacer raise: un raise desharía el contador de fallos.
create or replace function public.bm_entrar(p_pin text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_sal text; v_hash text; v_fallos int; v_token text;
begin
  if (select v from public.bm_config where k = 'pin_bloqueado') = 'true' then
    return jsonb_build_object('ok', false, 'motivo', 'bloqueado');
  end if;
  select v into v_sal from public.bm_config where k = 'pin_sal';
  select v into v_hash from public.bm_config where k = 'pin_sha256';
  if v_hash is null then
    return jsonb_build_object('ok', false, 'motivo', 'sin_pin');
  end if;

  if coalesce(p_pin, '') ~ '^[0-9]{4}$' and encode(digest(v_sal || p_pin, 'sha256'), 'hex') = v_hash then
    update public.bm_config set v = '0' where k = 'pin_fallos';
    v_token := encode(gen_random_bytes(32), 'hex');
    insert into public.bm_sesiones (token_sha256) values (encode(digest(v_token, 'sha256'), 'hex'));
    delete from public.bm_sesiones where expires_at < now();
    return jsonb_build_object('ok', true, 'token', v_token);
  end if;

  update public.bm_config set v = (v::int + 1)::text where k = 'pin_fallos' returning v::int into v_fallos;
  if v_fallos >= 10 then
    update public.bm_config set v = 'true' where k = 'pin_bloqueado';
  end if;
  perform pg_sleep(0.5);
  return jsonb_build_object('ok', false, 'motivo', case when v_fallos >= 10 then 'bloqueado' else 'pin_incorrecto' end,
                            'fallos', v_fallos);
end $$;

create or replace function public.bm_salir(p_token text)
returns void language sql security definer set search_path = public, extensions as $$
  delete from public.bm_push where token_sha256 = encode(digest(coalesce(p_token, ''), 'sha256'), 'hex');
  delete from public.bm_sesiones where token_sha256 = encode(digest(coalesce(p_token, ''), 'sha256'), 'hex');
$$;

create or replace function public.bm_desbloquear(p_secret text)
returns text language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check(p_secret);
  update public.bm_config set v = '0' where k = 'pin_fallos';
  update public.bm_config set v = 'false' where k = 'pin_bloqueado';
  return 'ok';
end $$;

create or replace function public.bm_estado_pin(p_secret text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check(p_secret);
  return jsonb_build_object(
    'puesto', exists (select 1 from public.bm_config where k = 'pin_sha256'),
    'fallos', (select v::int from public.bm_config where k = 'pin_fallos'),
    'bloqueado', (select v::boolean from public.bm_config where k = 'pin_bloqueado'),
    'sesiones', (select count(*) from public.bm_sesiones where expires_at > now()));
end $$;

-- ───────────────────────── el loop: publicar → decidir → recibir → marcar ─────────────────────────

create or replace function public.bm_publicar(p_secret text, p_clave text, p_session_id text, p_sesion_titulo text,
  p_skill text, p_proyecto text, p_titulo text, p_n_items integer, p_datos jsonb, p_html text)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare
  v_rows int;
  v_estado text;
begin
  perform public.bm_check(p_secret);
  if length(p_html) > 3000000 then
    raise exception 'html demasiado grande';
  end if;

  insert into public.botoneras (clave, session_id, sesion_titulo, skill, proyecto, titulo, n_items, datos, html)
  values (p_clave, p_session_id, p_sesion_titulo, p_skill, p_proyecto, p_titulo, coalesce(p_n_items, 0), p_datos, p_html)
  on conflict (clave) do nothing;
  get diagnostics v_rows = row_count;
  if v_rows = 1 then
    return 'creada';
  end if;

  -- Republicar pisa la tanda solo mientras sigue abierta.
  update public.botoneras
     set session_id = p_session_id, sesion_titulo = p_sesion_titulo, skill = p_skill, proyecto = p_proyecto,
         titulo = p_titulo, n_items = coalesce(p_n_items, 0), datos = p_datos, html = p_html, updated_at = now()
   where clave = p_clave and estado = 'abierta';
  get diagnostics v_rows = row_count;
  if v_rows = 1 then
    return 'actualizada';
  end if;

  select estado into v_estado from public.botoneras where clave = p_clave;
  return 'ya_decidida:' || coalesce(v_estado, 'desconocido');
end $$;

-- bm_lista cambia de columnas en una migración posterior: se suelta antes para poder repetir esta.
drop function if exists public.bm_lista(text);
create or replace function public.bm_lista(p_token text)
returns table(clave text, session_id text, sesion_titulo text, skill text, proyecto text, titulo text,
  n_items integer, estado text, resumen_aplicado text, created_at timestamptz, updated_at timestamptz,
  decided_at timestamptz, received_at timestamptz, applied_at timestamptz, espera_motivo text, esperando_at timestamptz)
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check_token(p_token);
  return query select b.clave, b.session_id, b.sesion_titulo, b.skill, b.proyecto, b.titulo, b.n_items,
    b.estado, b.resumen_aplicado, b.created_at, b.updated_at, b.decided_at, b.received_at, b.applied_at,
    b.espera_motivo, b.esperando_at
    from public.botoneras b order by b.created_at desc;
end $$;

create or replace function public.bm_fila(p_token text, p_clave text)
returns table(clave text, html text, estado text, updated_at timestamptz, respuesta_texto text,
  resumen_aplicado text, datos jsonb)
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check_token(p_token);
  return query select b.clave, b.html, b.estado, b.updated_at, b.respuesta_texto, b.resumen_aplicado, b.datos
    from public.botoneras b where b.clave = p_clave;
end $$;

create or replace function public.bm_decidir_pin(p_token text, p_clave text, p_respuesta text,
  p_version timestamptz default null)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare v_estado text;
begin
  perform public.bm_check_token(p_token);
  if p_respuesta is null
     or left(p_respuesta, length('/botonera respuesta · ' || p_clave)) <> ('/botonera respuesta · ' || p_clave) then
    raise exception 'respuesta invalida';
  end if;
  -- La tanda se republicó mientras decidías: no se pisa con una respuesta a la versión vieja.
  if p_version is not null and exists (
       select 1 from public.botoneras
        where clave = p_clave
          and date_trunc('milliseconds', updated_at) <> date_trunc('milliseconds', p_version)) then
    return 'cambio';
  end if;
  update public.botoneras
     set estado = 'decidida', respuesta_texto = p_respuesta, decided_at = now()
   where clave = p_clave and estado = 'abierta';
  if found then return 'decidida'; end if;
  select estado into v_estado from public.botoneras where clave = p_clave;
  return v_estado;
end $$;

-- Si un esperar.py murió después de recibir y se relanza, vuelve a entregar la respuesta (marcada como reentrega).
create or replace function public.bm_recibir(p_secret text, p_clave text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_resp text;
  v_estado text;
begin
  perform public.bm_check(p_secret);
  update public.botoneras
     set estado = 'recibida', received_at = now()
   where clave = p_clave and estado = 'decidida'
   returning respuesta_texto into v_resp;
  if found then
    return jsonb_build_object('estado', 'recibida', 'respuesta_texto', v_resp, 'reentrega', false);
  end if;

  select estado, respuesta_texto into v_estado, v_resp from public.botoneras where clave = p_clave;
  if not found then
    return jsonb_build_object('estado', 'no_existe');
  end if;
  if v_estado = 'recibida' then
    return jsonb_build_object('estado', 'recibida', 'respuesta_texto', v_resp, 'reentrega', true);
  end if;
  return jsonb_build_object('estado', v_estado);
end $$;

-- Transiciones válidas; si no vale, no se toca nada:
--   aplicada desde recibida o esperando · respondida_en_chat desde abierta
--   esperando desde recibida o esperando (actualiza el motivo) · trabajando (vuelve a recibida) desde esperando
--   archivada (la sesión que preguntó ya no está) desde cualquier estado no cerrado
create or replace function public.bm_marcar(p_secret text, p_clave text, p_estado text, p_resumen text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_anterior text;
begin
  perform public.bm_check(p_secret);
  if p_estado is null or p_estado not in ('aplicada', 'respondida_en_chat', 'esperando', 'trabajando', 'archivada') then
    raise exception 'estado invalido: %', p_estado;
  end if;

  select estado into v_anterior from public.botoneras where clave = p_clave for update;
  if not found then
    raise exception 'clave inexistente';
  end if;

  if not ((p_estado = 'aplicada' and v_anterior in ('recibida', 'esperando'))
       or (p_estado = 'respondida_en_chat' and v_anterior = 'abierta')
       or (p_estado = 'esperando' and v_anterior in ('recibida', 'esperando'))
       or (p_estado = 'trabajando' and v_anterior = 'esperando')
       or (p_estado = 'archivada' and v_anterior in ('abierta', 'decidida', 'recibida', 'esperando'))) then
    return jsonb_build_object('anterior', v_anterior, 'cambiado', false);
  end if;

  if p_estado = 'esperando' then
    update public.botoneras set estado = 'esperando', espera_motivo = p_resumen, esperando_at = now()
     where clave = p_clave;
  elsif p_estado = 'trabajando' then
    update public.botoneras set estado = 'recibida', espera_motivo = null, esperando_at = null
     where clave = p_clave;
  elsif p_estado = 'archivada' then
    update public.botoneras set estado = 'archivada', resumen_aplicado = p_resumen, espera_motivo = null
     where clave = p_clave;
  else
    update public.botoneras
       set estado = p_estado, resumen_aplicado = p_resumen, applied_at = now(), espera_motivo = null
     where clave = p_clave;
  end if;
  return jsonb_build_object('anterior', v_anterior, 'cambiado', true);
end $$;

create or replace function public.bm_pendientes(p_secret text, p_horas integer)
returns setof public.botoneras language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check(p_secret);
  return query
    select * from public.botoneras b
     where b.estado in ('decidida', 'recibida')
       and b.decided_at < now() - make_interval(hours => p_horas)
       and b.applied_at is null;
end $$;

create or replace function public.bm_sin_cerrar(p_secret text)
returns table(clave text, estado text, session_id text, sesion_titulo text, titulo text,
  created_at timestamptz, decided_at timestamptz)
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check(p_secret);
  return query
    select b.clave, b.estado, b.session_id, b.sesion_titulo, b.titulo, b.created_at, b.decided_at
      from public.botoneras b
     where b.estado in ('abierta', 'decidida', 'recibida', 'esperando')
     order by b.created_at;
end $$;

-- ───────────────────────── avisos (Web Push) ─────────────────────────
-- Dos cron de la base llaman a la función bm-avisar con un secreto de Vault. Viajan solo conteos y nombres
-- de categoría; nunca el texto de una card. Las claves VAPID las genera la función la primera vez y la
-- privada queda en Vault.

create or replace function public.bm_push_clave(p_token text)
returns text language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check_token(p_token);
  return (select v from public.bm_config where k = 'vapid_publica');
end $$;

create or replace function public.bm_push_suscribir(p_token text, p_endpoint text, p_p256dh text, p_auth text)
returns text language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check_token(p_token);
  if p_endpoint is null
     or p_endpoint !~ '^https://(fcm\.googleapis\.com|[a-z0-9.-]+\.push\.apple\.com|[a-z0-9.-]+\.push\.services\.mozilla\.com|[a-z0-9.-]+\.notify\.windows\.com)/'
     or coalesce(p_p256dh, '') = '' or coalesce(p_auth, '') = '' then
    raise exception 'suscripcion invalida';
  end if;
  insert into public.bm_push (endpoint, p256dh, auth, token_sha256)
  values (p_endpoint, p_p256dh, p_auth, encode(digest(p_token, 'sha256'), 'hex'))
  on conflict (endpoint) do update
    set p256dh = excluded.p256dh, auth = excluded.auth, token_sha256 = excluded.token_sha256, fallos = 0;
  return 'ok';
end $$;

create or replace function public.bm_estado_avisos(p_secret text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check(p_secret);
  return jsonb_build_object(
    'dispositivos', (select count(*) from public.bm_push),
    'ultimo', (select v from public.bm_config where k = 'aviso_ultimo'),
    'error', (select v from public.bm_config where k = 'aviso_error'));
end $$;

-- Lo que necesita la función bm-avisar (solo service_role).
create or replace function public.bm_avisos_datos()
returns jsonb language sql security definer set search_path = public, extensions as $$
  select jsonb_build_object(
    'secreto', (select decrypted_secret from vault.decrypted_secrets where name = 'bm_avisar_secret'),
    'contacto', (select v from public.bm_config where k = 'contacto'),
    'vapid_publica', (select v from public.bm_config where k = 'vapid_publica'),
    'vapid_privada', (select decrypted_secret from vault.decrypted_secrets where name = 'bm_vapid_privada'),
    'dispositivos', coalesce((select jsonb_agg(jsonb_build_object('endpoint', endpoint, 'p256dh', p256dh, 'auth', auth))
                                from public.bm_push), '[]'::jsonb));
$$;

create or replace function public.bm_avisos_guardar_vapid(p_publica text, p_privada text)
returns text language plpgsql security definer set search_path = public, extensions as $$
begin
  if exists (select 1 from vault.secrets where name = 'bm_vapid_privada') then return 'ya'; end if;
  perform vault.create_secret(p_privada, 'bm_vapid_privada');
  insert into public.bm_config (k, v) values ('vapid_publica', p_publica)
    on conflict (k) do update set v = excluded.v;
  return 'ok';
end $$;

create or replace function public.bm_avisos_llamar(p_cuerpo jsonb)
returns bigint language plpgsql security definer set search_path = public, extensions as $$
declare v_url text := (select v from public.bm_config where k = 'avisar_url');
begin
  if v_url is null then return null; end if;
  return net.http_post(
    url := v_url,
    headers := jsonb_build_object('Content-Type', 'application/json',
      'x-bm-avisar', (select decrypted_secret from vault.decrypted_secrets where name = 'bm_avisar_secret')),
    body := p_cuerpo,
    timeout_milliseconds := 20000);
end $$;

-- Hasta 3 nombres de categoría para el cuerpo del aviso. Las categorías `privada` no se nombran.
create or replace function public.bm_avisos_nombres(p_claves text[])
returns text language sql stable security definer set search_path = public, extensions as $$
  with c as (
    select b.datos->'categoria'->>'nombre' nombre, count(*) n
      from public.botoneras b
     where b.clave = any(p_claves)
       and b.datos->'categoria'->>'nombre' is not null
       and coalesce(b.datos->'categoria'->>'privada', 'false') <> 'true'
       and coalesce(b.datos->'categoria'->>'id', '') <> 'otras'
     group by 1
  ), o as (select nombre, row_number() over (order by n desc, nombre) r, count(*) over () t from c)
  select case when max(t) > 3 then string_agg(nombre, ', ' order by r) filter (where r <= 3) || ' +' || (max(t) - 3)
              else string_agg(nombre, ', ' order by r) end
    from o;
$$;

create or replace function public.bm_avisos_resultado(p_ok text[], p_muertos text[], p_fallidos text[],
  p_claves text[], p_error text)
returns void language plpgsql security definer set search_path = public, extensions as $$
begin
  update public.bm_push set last_ok_at = now(), fallos = 0 where endpoint = any(p_ok);
  delete from public.bm_push where endpoint = any(p_muertos);
  update public.bm_push set fallos = fallos + 1 where endpoint = any(p_fallidos);
  delete from public.bm_push where fallos >= 5;
  if coalesce(array_length(p_ok, 1), 0) > 0 then
    update public.botoneras set avisada_at = now() where clave = any(p_claves);
    insert into public.bm_config (k, v) values ('aviso_ultimo', now()::text)
      on conflict (k) do update set v = excluded.v;
  end if;
  if p_error is not null then
    insert into public.bm_config (k, v) values ('aviso_error', now()::text || ' · ' || left(p_error, 200))
      on conflict (k) do update set v = excluded.v;
  end if;
end $$;

create or replace function public.bm_zona()
returns text language sql stable security definer set search_path = public, extensions as $$
  select coalesce((select v from public.bm_config where k = 'zona'), 'UTC');
$$;

-- Cada 5 minutos: avisa las tandas nuevas que nadie avisó. Calla de 22 a 8 (hora local de `zona`).
create or replace function public.bm_avisos_tick(p_ahora timestamptz default now(), p_solo_prueba boolean default false)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare
  v_hora int := extract(hour from p_ahora at time zone public.bm_zona());
  v_claves text[];
  v_n int;
  v_cards int;
  v_cards_txt text;
begin
  -- Recién instalada: sin claves VAPID la web no puede suscribirse. La función las genera con un llamado vacío.
  if not exists (select 1 from public.bm_config where k = 'vapid_publica') then
    perform public.bm_avisos_llamar('{}'::jsonb);
    return 'iniciando';
  end if;
  if v_hora >= 22 or v_hora < 8 then return 'silencio'; end if;
  if not exists (select 1 from public.bm_push) then return 'sin_dispositivos'; end if;
  select array_agg(clave) into v_claves from public.botoneras
   where estado = 'abierta' and avisada_at is null
     and (not p_solo_prueba or clave like 'prueba-avisos-%');
  v_n := coalesce(array_length(v_claves, 1), 0);
  if v_n = 0 then return 'nada'; end if;
  select coalesce(sum(n_items), 0) into v_cards from public.botoneras where estado = 'abierta';
  v_cards_txt := case when v_cards = 1 then '1 card por decidir' else v_cards || ' cards por decidir' end;
  perform public.bm_avisos_llamar(jsonb_build_object(
    'tag', 'nuevas',
    'titulo', case when v_n = 1 then '1 botonera nueva' else v_n || ' botoneras nuevas' end,
    'cuerpo', concat_ws(' · ', public.bm_avisos_nombres(v_claves), v_cards_txt),
    'claves', to_jsonb(v_claves)));
  return 'avisado ' || v_n;
end $$;

-- Cada hora; avisa solo a las 9 locales: cards con `vence` hoy o mañana.
create or replace function public.bm_avisos_vence(p_ahora timestamptz default now(), p_forzar boolean default false)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare
  v_local timestamp := p_ahora at time zone public.bm_zona();
  v_dia date := v_local::date;
  v_hoy int; v_man int; v_txt text; v_claves text[];
begin
  if not p_forzar and extract(hour from v_local) <> 9 then return 'no_es_la_hora'; end if;
  if not exists (select 1 from public.bm_push) then return 'sin_dispositivos'; end if;
  select count(*) filter (where i->>'vence' = v_dia::text),
         count(*) filter (where i->>'vence' = (v_dia + 1)::text),
         array_agg(distinct b.clave) filter (where i->>'vence' in (v_dia::text, (v_dia + 1)::text))
    into v_hoy, v_man, v_claves
    from public.botoneras b, jsonb_array_elements(coalesce(b.datos->'items', '[]'::jsonb)) i
   where b.estado = 'abierta';
  if v_hoy + v_man = 0 then return 'nada'; end if;
  v_txt := concat_ws(' · ',
    case when v_hoy = 1 then '1 card vence hoy' when v_hoy > 1 then v_hoy || ' cards vencen hoy' end,
    case when v_man = 0 then null
         when v_hoy > 0 then v_man || ' mañana'
         when v_man = 1 then '1 card vence mañana'
         else v_man || ' cards vencen mañana' end);
  perform public.bm_avisos_llamar(jsonb_build_object('tag', 'vence', 'titulo', v_txt,
    'cuerpo', coalesce(public.bm_avisos_nombres(v_claves), 'Tocá para decidir'), 'claves', '[]'::jsonb));
  return v_txt;
end $$;

select cron.schedule('bm-avisos-nuevas', '*/5 * * * *', 'select public.bm_avisos_tick()');
select cron.schedule('bm-avisos-vence', '0 * * * *', 'select public.bm_avisos_vence()');

-- ───────────────────────── permisos ─────────────────────────
-- Por default Postgres deja ejecutar cualquier función a PUBLIC: se cierra todo y se abre lo justo.

revoke execute on all functions in schema public from public, anon, authenticated;

-- La web (anon + token de sesión) y los scripts (anon + BM_SECRET).
grant execute on function
  public.bm_entrar(text), public.bm_salir(text), public.bm_lista(text), public.bm_fila(text, text),
  public.bm_decidir_pin(text, text, text, timestamptz), public.bm_push_clave(text),
  public.bm_push_suscribir(text, text, text, text),
  public.bm_publicar(text, text, text, text, text, text, text, integer, jsonb, text),
  public.bm_recibir(text, text), public.bm_marcar(text, text, text, text), public.bm_pendientes(text, integer),
  public.bm_sin_cerrar(text), public.bm_poner_pin(text, text), public.bm_desbloquear(text),
  public.bm_estado_pin(text), public.bm_estado_avisos(text)
to anon;

-- La función bm-avisar.
grant execute on function
  public.bm_avisos_datos(), public.bm_avisos_guardar_vapid(text, text),
  public.bm_avisos_resultado(text[], text[], text[], text[], text)
to service_role;

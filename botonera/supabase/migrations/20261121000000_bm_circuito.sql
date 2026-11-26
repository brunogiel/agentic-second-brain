-- Botonera 1.3.0 · el circuito: lo que mandaste vuelve y lo que está en vuelo se ve. Se puede correr más de una vez.
--
-- Solo agrega: una tabla y seis funciones. No cambia ni borra filas ni redefine funciones existentes.
--   1. bm_vuelo: lo que está en vuelo. Una fila por sesión del agente (session_id): qué hace y su próximo paso.
--      La sesión la escribe `vuelo.py` (bm_vuelo_anotar / bm_vuelo_cerrar, con secret).
--   2. bm_seguimiento(p_token): lo que el home de Sesiones no saca de bm_lista: las sesiones en vuelo.
--      Devuelve también `pedidos`, `escucha_at` y `activos` con valores vacíos (null / 0 / []): son campos que lee la
--      web y que esta versión no usa («Nueva tarea» y «Que la retome otra» no están en el kit). Un campo omitido deja
--      la pantalla en blanco, por eso la forma no cambia.
--   3. bm_archivar_pin(p_token, p_clave): «Archivar» desde la web (bm_marcar solo entra con secret).
--   4. bm_trabadas(p_secret, p_horas): tandas decidida/recibida con más de N horas. Solo lectura.
--   5. bm_vuelo_anotar / bm_vuelo_cerrar (secret): lo que escribe vuelo.py.
--
-- Roles. Todas las funciones con secret usan bm_check: solo entra el secret total. El secret de bot NO anota ni cierra
-- vuelos, no ve las tandas trabadas y no archiva; los vuelos son de las sesiones del dueño, un bot no tiene sesión.
-- Las dos funciones de la web usan bm_check_token (el token que da bm_entrar con el PIN).
--
-- La tabla con RLS prendida y sin policies: solo se llega por las funciones SECURITY DEFINER. Grants explícitos:
-- REVOKE de PUBLIC y authenticated, EXECUTE a anon y service_role.

begin;

create table if not exists public.bm_vuelo (
  session_id text primary key,
  titulo     text not null default '',
  que_hace   text not null default '',
  proximo    text not null default '',
  estado     text not null default 'trabajando'
             check (estado in ('trabajando', 'esperando', 'cerrada')),
  desde      timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.bm_vuelo enable row level security;
revoke all on public.bm_vuelo from anon, authenticated;

-- ───────────────────────── web (token del PIN) ─────────────────────────

-- Sesiones en vuelo (las que se movieron en las últimas 48 horas, hasta 30). Solo lee.
create or replace function public.bm_seguimiento(p_token text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check_token(p_token);
  return jsonb_build_object(
    'vuelo', coalesce((
      select jsonb_agg(jsonb_build_object('session_id', v.session_id, 'titulo', v.titulo, 'que_hace', v.que_hace,
                                          'proximo', v.proximo, 'estado', v.estado, 'updated_at', v.updated_at,
                                          'desde', v.desde)
                       order by v.updated_at desc, v.session_id)
        from (select * from public.bm_vuelo
               where estado <> 'cerrada' and updated_at > now() - interval '48 hours'
               order by updated_at desc, session_id
               limit 30) v), '[]'::jsonb),
    'pedidos', '[]'::jsonb,
    'escucha_at', null,
    'activos', 0);
end $$;

-- Archivar desde Sesiones: decidida | recibida | esperando -> archivada. Otro estado: cambiado=false, sin error.
create or replace function public.bm_archivar_pin(p_token text, p_clave text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_anterior text;
begin
  perform public.bm_check_token(p_token);

  -- for update: si la sesión marca `aplicada` a la vez, una de las dos espera y la otra ve el estado ya cambiado.
  select estado into v_anterior from public.botoneras where clave = p_clave for update;
  if not found then
    raise exception 'clave inexistente';
  end if;

  if v_anterior not in ('decidida', 'recibida', 'esperando') then
    return jsonb_build_object('anterior', v_anterior, 'cambiado', false);
  end if;

  update public.botoneras
     set estado = 'archivada',
         resumen_aplicado = 'Archivada desde Sesiones',
         espera_motivo = null,
         updated_at = now()
   where clave = p_clave;
  return jsonb_build_object('anterior', v_anterior, 'cambiado', true);
end $$;

-- ───────────────────────── scripts (secret total) ─────────────────────────

-- Tandas trabadas: decidida desde decided_at; recibida desde coalesce(received_at, decided_at). Solo lectura.
-- `en_pausa` marca las claves de bot (no tienen una sesión que las retome); `pedido` queda siempre null (no hay cola de retomar).
create or replace function public.bm_trabadas(p_secret text, p_horas integer default 24)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check(p_secret);
  return coalesce((
    select jsonb_agg(jsonb_build_object(
             'clave', t.clave, 'estado', t.estado, 'session_id', t.session_id, 'sesion_titulo', t.sesion_titulo,
             'titulo', t.titulo, 'desde', t.desde,
             'horas', round((extract(epoch from (now() - t.desde)) / 3600)::numeric, 1),
             'en_pausa', public.bm_es_bot(t.clave),
             'pedido', null)
           order by t.desde asc, t.clave)
      from (select b.clave, b.estado, b.session_id, b.sesion_titulo, b.titulo,
                   case when b.estado = 'decidida'
                        then coalesce(b.decided_at, b.updated_at)
                        else coalesce(b.received_at, b.decided_at, b.updated_at) end as desde
              from public.botoneras b
             where b.estado in ('decidida', 'recibida')) t
     where t.desde < now() - make_interval(hours => coalesce(p_horas, 24))), '[]'::jsonb);
end $$;

-- vuelo.py anota (upsert por session_id). `desde` se queda con el primer anotado; si la fila estaba cerrada, arranca un vuelo nuevo.
create or replace function public.bm_vuelo_anotar(
    p_secret text, p_session_id text, p_titulo text, p_que_hace text, p_proximo text,
    p_estado text default 'trabajando')
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_fila public.bm_vuelo;
begin
  perform public.bm_check(p_secret);

  if p_session_id is null or btrim(p_session_id) = '' then
    raise exception 'session_id vacio';
  end if;
  if p_estado is null or p_estado not in ('trabajando', 'esperando', 'cerrada') then
    raise exception 'estado invalido';
  end if;

  insert into public.bm_vuelo as v (session_id, titulo, que_hace, proximo, estado, desde, updated_at)
  values (p_session_id, left(coalesce(p_titulo, ''), 140), left(coalesce(p_que_hace, ''), 140),
          left(coalesce(p_proximo, ''), 140), p_estado, now(), now())
  on conflict (session_id) do update
     set titulo     = left(coalesce(p_titulo, ''), 140),
         que_hace   = left(coalesce(p_que_hace, ''), 140),
         proximo    = left(coalesce(p_proximo, ''), 140),
         estado     = excluded.estado,
         desde      = case when v.estado = 'cerrada' then now() else v.desde end,
         updated_at = now()
  returning * into v_fila;

  return jsonb_build_object('session_id', v_fila.session_id, 'estado', v_fila.estado,
                            'desde', v_fila.desde, 'updated_at', v_fila.updated_at);
end $$;

-- vuelo.py cerrar. Una sesión que no anotó nunca no es un error: cerrada=false.
create or replace function public.bm_vuelo_cerrar(p_secret text, p_session_id text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_n integer;
begin
  perform public.bm_check(p_secret);
  update public.bm_vuelo set estado = 'cerrada', updated_at = now() where session_id = p_session_id;
  get diagnostics v_n = row_count;
  return jsonb_build_object('session_id', p_session_id, 'cerrada', v_n > 0);
end $$;

-- ───────────────────────── permisos ─────────────────────────

revoke all on function public.bm_seguimiento(text) from public, authenticated;
grant execute on function public.bm_seguimiento(text) to anon, service_role;
revoke all on function public.bm_archivar_pin(text, text) from public, authenticated;
grant execute on function public.bm_archivar_pin(text, text) to anon, service_role;
revoke all on function public.bm_trabadas(text, integer) from public, authenticated;
grant execute on function public.bm_trabadas(text, integer) to anon, service_role;
revoke all on function public.bm_vuelo_anotar(text, text, text, text, text, text) from public, authenticated;
grant execute on function public.bm_vuelo_anotar(text, text, text, text, text, text) to anon, service_role;
revoke all on function public.bm_vuelo_cerrar(text, text) from public, authenticated;
grant execute on function public.bm_vuelo_cerrar(text, text) to anon, service_role;

commit;

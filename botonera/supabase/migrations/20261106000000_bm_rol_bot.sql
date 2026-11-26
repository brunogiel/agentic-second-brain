-- Botonera 1.1.0 · rol de bot: un segundo secret que solo sirve para lo suyo. Se puede correr más de una vez.
--
-- Un bot (un agente que no es tu sesión de Claude Code) puede publicar tandas y recibir tus respuestas sin tener
-- tu secret completo. El secret de bot solo trabaja con claves que empiezan con `bot-` (y con un session_id que
-- también empieza con `bot-`): no ve ni toca el resto de las tandas.
--
--   · bm_rol(p_secret) -> 'total' (el BM_SECRET de siempre, fila `secret_sha256`) | 'bot' (fila `bot_secret_sha256`)
--     | error 'secret invalido'.
--   · bm_publicar, bm_recibir, bm_marcar y bm_pendientes pasan de bm_check a bm_rol. Con rol 'bot':
--       - solo claves `bot-`; bm_publicar además exige session_id `bot-…` y fuerza skill = 'bot';
--       - bm_pendientes devuelve solo filas `bot-`.
--     Con rol 'total' todo queda igual que en 1.0.0.
--   · NO se tocan bm_check, bm_poner_pin, bm_desbloquear, bm_estado_pin, bm_sin_cerrar ni bm_estado_avisos: siguen
--     aceptando solo el secret total. El secret de bot no puede ver ni resetear el PIN, ni listar lo sin cerrar.
--
-- El secret de bot NO se genera ni se inserta acá: lo crea `secret-bot.py`, que muestra el INSERT con su hash.
-- Mientras la fila `bot_secret_sha256` no exista, bm_rol nunca devuelve 'bot'.
--   Rotar:  correr secret-bot.py --rotar y cargar el hash nuevo.
--   Baja:   delete from public.bm_config where k = 'bot_secret_sha256';

-- ───────────────────────── rol ─────────────────────────

create or replace function public.bm_rol(p_secret text)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare v_hash text;
begin
  if p_secret is null then
    raise exception 'secret invalido';
  end if;
  v_hash := encode(digest(p_secret, 'sha256'), 'hex');
  if exists (select 1 from public.bm_config where k = 'secret_sha256' and v = v_hash) then
    return 'total';
  end if;
  if exists (select 1 from public.bm_config where k = 'bot_secret_sha256' and v = v_hash) then
    return 'bot';
  end if;
  raise exception 'secret invalido';
end $$;

-- ¿La clave es de un bot? El prefijo `bot-` es fijo.
create or replace function public.bm_es_bot(p_texto text)
returns boolean language sql immutable set search_path = public as $$
  select coalesce(left(p_texto, 4) = 'bot-', false);
$$;

-- ───────────────────────── funciones con rol ─────────────────────────

create or replace function public.bm_publicar(p_secret text, p_clave text, p_session_id text, p_sesion_titulo text,
  p_skill text, p_proyecto text, p_titulo text, p_n_items integer, p_datos jsonb, p_html text)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare
  v_rows int;
  v_estado text;
  v_rol text := public.bm_rol(p_secret);
  v_skill text := p_skill;
begin
  if v_rol = 'bot' then
    if not public.bm_es_bot(p_clave) then
      raise exception 'rol bot: solo claves bot-';
    end if;
    -- Un bot no puede atar su tanda a una sesión de Claude Code: el hook entregar.py inyectaría la respuesta ahí.
    if not public.bm_es_bot(p_session_id) then
      raise exception 'rol bot: session_id tiene que empezar con bot-';
    end if;
    v_skill := 'bot';
  end if;
  if length(p_html) > 3000000 then
    raise exception 'html demasiado grande';
  end if;

  insert into public.botoneras (clave, session_id, sesion_titulo, skill, proyecto, titulo, n_items, datos, html)
  values (p_clave, p_session_id, p_sesion_titulo, v_skill, p_proyecto, p_titulo, coalesce(p_n_items, 0), p_datos, p_html)
  on conflict (clave) do nothing;
  get diagnostics v_rows = row_count;
  if v_rows = 1 then
    return 'creada';
  end if;

  -- Republicar pisa la tanda solo mientras sigue abierta.
  update public.botoneras
     set session_id = p_session_id, sesion_titulo = p_sesion_titulo, skill = v_skill, proyecto = p_proyecto,
         titulo = p_titulo, n_items = coalesce(p_n_items, 0), datos = p_datos, html = p_html, updated_at = now()
   where clave = p_clave and estado = 'abierta';
  get diagnostics v_rows = row_count;
  if v_rows = 1 then
    return 'actualizada';
  end if;

  select estado into v_estado from public.botoneras where clave = p_clave;
  return 'ya_decidida:' || coalesce(v_estado, 'desconocido');
end $$;

create or replace function public.bm_recibir(p_secret text, p_clave text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_resp text;
  v_estado text;
  v_rol text := public.bm_rol(p_secret);
begin
  if v_rol = 'bot' and not public.bm_es_bot(p_clave) then
    raise exception 'rol bot: solo claves bot-';
  end if;
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
  -- Si un esperar.py murió después de recibir y se relanza, vuelve a entregar la respuesta (marcada como reentrega).
  if v_estado = 'recibida' then
    return jsonb_build_object('estado', 'recibida', 'respuesta_texto', v_resp, 'reentrega', true);
  end if;
  return jsonb_build_object('estado', v_estado);
end $$;

create or replace function public.bm_marcar(p_secret text, p_clave text, p_estado text, p_resumen text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_anterior text;
  v_rol text := public.bm_rol(p_secret);
begin
  if v_rol = 'bot' and not public.bm_es_bot(p_clave) then
    raise exception 'rol bot: solo claves bot-';
  end if;
  if p_estado is null or p_estado not in ('aplicada', 'respondida_en_chat', 'esperando', 'trabajando', 'archivada') then
    raise exception 'estado invalido: %', p_estado;
  end if;

  select estado into v_anterior from public.botoneras where clave = p_clave for update;
  if not found then
    raise exception 'clave inexistente';
  end if;

  -- Transiciones válidas; si no vale, no se toca nada:
  --   aplicada desde recibida o esperando · respondida_en_chat desde abierta
  --   esperando desde recibida o esperando (actualiza el motivo) · trabajando (vuelve a recibida) desde esperando
  --   archivada (la sesión que preguntó ya no está) desde cualquier estado no cerrado
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
declare v_rol text := public.bm_rol(p_secret);
begin
  return query
    select * from public.botoneras b
     where b.estado in ('decidida', 'recibida')
       and b.decided_at < now() - make_interval(hours => p_horas)
       and b.applied_at is null
       and (v_rol = 'total' or public.bm_es_bot(b.clave));   -- el bot ve solo lo suyo
end $$;

-- ───────────────────────── permisos ─────────────────────────
-- Las funciones nuevas son internas (las llaman las otras bm_* como SECURITY DEFINER): ni anon ni authenticated.
-- CREATE OR REPLACE conserva los grants de las cuatro funciones que ya existían.

revoke all on function public.bm_rol(text) from public, anon, authenticated;
revoke all on function public.bm_es_bot(text) from public, anon, authenticated;

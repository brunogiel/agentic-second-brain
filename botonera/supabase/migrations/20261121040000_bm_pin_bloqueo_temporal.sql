-- Botonera 1.3.0 · el bloqueo del PIN pasa a ser temporal y creciente. Se puede correr más de una vez.
--
-- Antes: tras 10 fallos seguidos la entrada quedaba bloqueada hasta que alguien corría `pin.py desbloquear`.
-- Ahora:
--   · A los 10 fallos seguidos, bm_entrar bloquea 15 minutos.
--   · Cada tanda nueva de 10 fallos duplica la espera: 15, 30, 60, 120… con tope de 24 horas.
--   · Un ingreso correcto pone el contador y el escalón en cero.
--   · `pin.py desbloquear` (bm_desbloquear, con secret) sigue levantando el bloqueo en el acto y pone el escalón en cero.
--   · Poner un PIN nuevo (bm_poner_pin) también lo pone todo en cero.
--
-- Carrera cerrada: bm_entrar toma con `for update` la fila `pin_fallos` al empezar. Dos intentos a la vez ya no leen
-- el mismo contador: el segundo espera al primero. Efecto buscado: probar PIN en paralelo no acelera nada.
--
-- Forma de la respuesta (la web lee `motivo`; los campos nuevos solo se suman):
--   bm_entrar bloqueado  -> {ok:false, motivo:'bloqueado', hasta:<timestamptz>, espera_seg:<int>}
--                           (un bloqueo viejo, de antes de esta versión, no trae hora: sin `hasta`, dura hasta desbloquear)
--   bm_estado_pin        -> los campos de siempre (puesto, fallos, bloqueado, sesiones) más
--                           bloqueado_hasta (null si no hay) y escalon.
--
-- Estado en bm_config (texto): pin_bloqueado ('true'/'false'), pin_fallos, y dos filas nuevas:
--   pin_bloqueo_hasta  hasta cuándo dura el bloqueo vigente ('' si no hay)
--   pin_escalon        cuántos bloqueos seguidos van (define la próxima espera)

insert into public.bm_config (k, v) values ('pin_bloqueo_hasta', ''), ('pin_escalon', '0')
on conflict (k) do nothing;

-- Devuelve el error en vez de hacer raise: un raise desharía el contador de fallos.
create or replace function public.bm_entrar(p_pin text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_sal text; v_hash text; v_fallos int; v_token text;
  v_hasta timestamptz; v_esc int; v_min int;
begin
  -- Serializa los intentos: la fila del contador queda tomada hasta el final de esta llamada.
  perform 1 from public.bm_config where k = 'pin_fallos' for update;

  select nullif(v, '')::timestamptz into v_hasta from public.bm_config where k = 'pin_bloqueo_hasta';
  if (select v from public.bm_config where k = 'pin_bloqueado') = 'true' then
    if v_hasta is null then
      -- bloqueo sin hora (versión anterior): solo lo levanta pin.py desbloquear
      return jsonb_build_object('ok', false, 'motivo', 'bloqueado');
    end if;
    if v_hasta > now() then
      return jsonb_build_object('ok', false, 'motivo', 'bloqueado', 'hasta', v_hasta,
                                'espera_seg', ceil(extract(epoch from (v_hasta - now())))::int);
    end if;
    -- el bloqueo venció: nueva tanda de 10 intentos (el escalón se queda, así la próxima espera es el doble)
    update public.bm_config set v = 'false' where k = 'pin_bloqueado';
    update public.bm_config set v = '0' where k = 'pin_fallos';
    update public.bm_config set v = '' where k = 'pin_bloqueo_hasta';
  end if;

  select v into v_sal from public.bm_config where k = 'pin_sal';
  select v into v_hash from public.bm_config where k = 'pin_sha256';
  if v_hash is null then
    return jsonb_build_object('ok', false, 'motivo', 'sin_pin');
  end if;

  if coalesce(p_pin, '') ~ '^[0-9]{4}$' and encode(digest(v_sal || p_pin, 'sha256'), 'hex') = v_hash then
    update public.bm_config set v = '0' where k = 'pin_fallos';
    update public.bm_config set v = '0' where k = 'pin_escalon';
    update public.bm_config set v = '' where k = 'pin_bloqueo_hasta';
    update public.bm_config set v = 'false' where k = 'pin_bloqueado';
    v_token := encode(gen_random_bytes(32), 'hex');
    insert into public.bm_sesiones (token_sha256) values (encode(digest(v_token, 'sha256'), 'hex'));
    delete from public.bm_sesiones where expires_at < now();
    return jsonb_build_object('ok', true, 'token', v_token);
  end if;

  update public.bm_config set v = (v::int + 1)::text where k = 'pin_fallos' returning v::int into v_fallos;
  if v_fallos >= 10 then
    select coalesce(nullif(v, ''), '0')::int into v_esc from public.bm_config where k = 'pin_escalon';
    v_min := least(15 * (2 ^ least(v_esc, 7))::int, 1440);      -- 15, 30, 60, 120… tope 24 h
    v_hasta := now() + make_interval(mins => v_min);
    update public.bm_config set v = 'true' where k = 'pin_bloqueado';
    update public.bm_config set v = v_hasta::text where k = 'pin_bloqueo_hasta';
    update public.bm_config set v = (v_esc + 1)::text where k = 'pin_escalon';
  end if;
  perform pg_sleep(0.5);
  if v_fallos >= 10 then
    return jsonb_build_object('ok', false, 'motivo', 'bloqueado', 'fallos', v_fallos,
                              'hasta', v_hasta, 'espera_seg', v_min * 60);
  end if;
  return jsonb_build_object('ok', false, 'motivo', 'pin_incorrecto', 'fallos', v_fallos);
end $$;

-- Levanta el bloqueo en el acto (lo llama pin.py desbloquear) y pone el escalón en cero.
create or replace function public.bm_desbloquear(p_secret text)
returns text language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check(p_secret);
  update public.bm_config set v = '0' where k = 'pin_fallos';
  update public.bm_config set v = 'false' where k = 'pin_bloqueado';
  update public.bm_config set v = '' where k = 'pin_bloqueo_hasta';
  update public.bm_config set v = '0' where k = 'pin_escalon';
  return 'ok';
end $$;

-- Un PIN nuevo cierra todas las sesiones y lo pone todo en cero.
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
  update public.bm_config set v = '0' where k = 'pin_escalon';
  update public.bm_config set v = '' where k = 'pin_bloqueo_hasta';
  update public.bm_config set v = 'false' where k = 'pin_bloqueado';
  delete from public.bm_sesiones where true;   -- PIN nuevo: se cierran todas las sesiones (safeupdate pide WHERE)
  return 'ok';
end $$;

-- `bloqueado` es verdadero solo mientras el bloqueo está vigente; un bloqueo vencido ya no cuenta.
create or replace function public.bm_estado_pin(p_secret text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_hasta timestamptz;
  v_flag boolean;
  v_vigente boolean;
begin
  perform public.bm_check(p_secret);
  select nullif(v, '')::timestamptz into v_hasta from public.bm_config where k = 'pin_bloqueo_hasta';
  select v::boolean into v_flag from public.bm_config where k = 'pin_bloqueado';
  v_vigente := coalesce(v_flag, false) and (v_hasta is null or v_hasta > now());
  return jsonb_build_object(
    'puesto', exists (select 1 from public.bm_config where k = 'pin_sha256'),
    'fallos', case when coalesce(v_flag, false) and not v_vigente then 0
                   else (select v::int from public.bm_config where k = 'pin_fallos') end,
    'bloqueado', v_vigente,
    'bloqueado_hasta', case when v_vigente then v_hasta end,
    'escalon', (select coalesce(nullif(v, ''), '0')::int from public.bm_config where k = 'pin_escalon'),
    'sesiones', (select count(*) from public.bm_sesiones where expires_at > now()));
end $$;

-- create or replace conserva los grants de las cuatro funciones (anon y service_role las ejecutan, como antes);
-- se repiten para que la migración sea explícita.
revoke all on function public.bm_entrar(text) from public, authenticated;
grant execute on function public.bm_entrar(text) to anon, service_role;
revoke all on function public.bm_desbloquear(text) from public, authenticated;
grant execute on function public.bm_desbloquear(text) to anon, service_role;
revoke all on function public.bm_poner_pin(text, text) from public, authenticated;
grant execute on function public.bm_poner_pin(text, text) to anon, service_role;
revoke all on function public.bm_estado_pin(text) from public, authenticated;
grant execute on function public.bm_estado_pin(text) to anon, service_role;

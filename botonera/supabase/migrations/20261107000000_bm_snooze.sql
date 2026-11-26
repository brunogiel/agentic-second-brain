-- Botonera 1.2.0 · snooze: dormir una botonera entera hasta una hora. Se puede correr más de una vez.
--
--   · botoneras.snooze_hasta (null = nunca snoozeada). Una botonera está DORMIDA si snooze_hasta > now(): sigue
--     `abierta` en la base con sus marcas, pero no se muestra en «Por decidir» (la web la pasa a «Snoozeadas»),
--     no se avisa por push, no cuenta en los vencimientos ni como colgada. No hay cron de despertar: al pasar la
--     hora deja de cumplirse sola, y la botonera vuelve arriba (su `llegada` pasa a ser snooze_hasta).
--   · bm_snoozear(p_token, p_clave, p_hasta) -> text: solo sobre una `abierta`. p_hasta tiene que ser futuro y a
--     menos de 8 días (si no: error 'hora invalida'). Pone avisada_at = null para que el push la cuente recién al
--     despertar. Devuelve 'abierta' si snoozeó; si no, el estado actual de la fila ('no_existe' si no hay).
--   · bm_despertar(p_token, p_clave) -> text: si está dormida, snooze_hasta = now() y avisada_at = now() (vuelve
--     arriba, sin push). Si no está dormida no toca nada. Devuelve el estado actual.
--   · Cambian: bm_lista (suma snooze_hasta y llegada), bm_recibir (una `abierta` dormida devuelve también
--     snooze_hasta, para esperar.py), bm_sin_cerrar, bm_avisos_tick y bm_avisos_vence (saltean las dormidas) y
--     bm_decidir_pin (decidir una dormida la despierta).
--   · No se toca updated_at al snoozear ni al despertar: bm_decidir_pin compara p_version contra updated_at, y la
--     página que tiene la botonera abierta no tiene que recibir «cambio» por un snooze.
--   · Ninguna fila existente cambia de valor: la columna nueva queda en null para todas.
--
-- Cada función redefinida es la de 1.1.0 más lo marcado con «-- snooze».

-- ───────────────────────── columna ─────────────────────────

alter table public.botoneras add column if not exists snooze_hasta timestamptz;

-- ───────────────────────── snoozear / despertar ─────────────────────────

create or replace function public.bm_snoozear(p_token text, p_clave text, p_hasta timestamptz)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare v_estado text;
begin
  perform public.bm_check_token(p_token);
  if p_hasta is null or p_hasta <= now() or p_hasta >= now() + interval '8 days' then
    raise exception 'hora invalida';
  end if;
  -- Sin updated_at a propósito: no invalida la p_version de bm_decidir_pin.
  update public.botoneras
     set snooze_hasta = p_hasta, avisada_at = null
   where clave = p_clave and estado = 'abierta';
  if found then return 'abierta'; end if;
  select estado into v_estado from public.botoneras where clave = p_clave;
  return coalesce(v_estado, 'no_existe');
end $$;

create or replace function public.bm_despertar(p_token text, p_clave text)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare v_estado text;
begin
  perform public.bm_check_token(p_token);
  -- avisada_at = now(): vuelve arriba sin push. Solo si de verdad está dormida; si ya despertó sola y el tick
  -- todavía no la avisó, no se le apaga el aviso. Sin updated_at, igual que bm_snoozear.
  update public.botoneras
     set snooze_hasta = now(), avisada_at = now()
   where clave = p_clave and estado = 'abierta' and snooze_hasta > now();
  if found then return 'abierta'; end if;
  select estado into v_estado from public.botoneras where clave = p_clave;
  return coalesce(v_estado, 'no_existe');
end $$;

-- ───────────────────────── bm_lista ─────────────────────────
-- Devuelve columnas nuevas: Postgres no deja cambiar el tipo de retorno con create or replace.

drop function if exists public.bm_lista(text);
create function public.bm_lista(p_token text)
returns table(clave text, session_id text, sesion_titulo text, skill text, proyecto text, titulo text,
  n_items integer, estado text, resumen_aplicado text, created_at timestamptz, updated_at timestamptz,
  decided_at timestamptz, received_at timestamptz, applied_at timestamptz, espera_motivo text, esperando_at timestamptz,
  snooze_hasta timestamptz, llegada timestamptz)   -- snooze: las dos últimas
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check_token(p_token);
  return query select b.clave, b.session_id, b.sesion_titulo, b.skill, b.proyecto, b.titulo, b.n_items,
    b.estado, b.resumen_aplicado, b.created_at, b.updated_at, b.decided_at, b.received_at, b.applied_at,
    b.espera_motivo, b.esperando_at,
    b.snooze_hasta,   -- snooze
    case when b.snooze_hasta is not null and b.snooze_hasta <= now()
         then greatest(b.created_at, b.snooze_hasta)
         else b.created_at end   -- snooze: llegada
    from public.botoneras b order by b.created_at desc;
end $$;

-- ───────────────────────── bm_decidir_pin ─────────────────────────

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
     set estado = 'decidida', respuesta_texto = p_respuesta, decided_at = now(),
         snooze_hasta = case when snooze_hasta > now() then null else snooze_hasta end   -- snooze: decidir una dormida la despierta; una que ya despertó conserva su snooze_hasta (su llegada no cambia)
   where clave = p_clave and estado = 'abierta';
  if found then return 'decidida'; end if;
  select estado into v_estado from public.botoneras where clave = p_clave;
  return v_estado;
end $$;

-- ───────────────────────── bm_recibir ─────────────────────────

create or replace function public.bm_recibir(p_secret text, p_clave text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_resp text;
  v_estado text;
  v_rol text := public.bm_rol(p_secret);
  v_snooze timestamptz;   -- snooze
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

  select estado, respuesta_texto, snooze_hasta into v_estado, v_resp, v_snooze   -- snooze: + snooze_hasta
    from public.botoneras where clave = p_clave;
  if not found then
    return jsonb_build_object('estado', 'no_existe');
  end if;
  -- Si un esperar.py murió después de recibir y se relanza, vuelve a entregar la respuesta (marcada como reentrega).
  if v_estado = 'recibida' then
    return jsonb_build_object('estado', 'recibida', 'respuesta_texto', v_resp, 'reentrega', true);
  end if;
  -- snooze: una abierta dormida avisa hasta cuándo (UTC ISO 8601 con milis, estable para comparar strings).
  if v_estado = 'abierta' and v_snooze is not null and v_snooze > now() then
    return jsonb_build_object('estado', v_estado,
      'snooze_hasta', to_char(v_snooze at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'));
  end if;
  return jsonb_build_object('estado', v_estado);
end $$;

-- ───────────────────────── bm_sin_cerrar ─────────────────────────

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
       and (b.estado <> 'abierta' or b.snooze_hasta is null or b.snooze_hasta <= now())   -- snooze: las dormidas no están colgadas (con null explícito: NOT (… > now()) daría null y sacaría las filas sin snooze)
     order by b.created_at;
end $$;

-- ───────────────────────── avisos ─────────────────────────

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
     and (snooze_hasta is null or snooze_hasta <= now())   -- snooze: las dormidas no se avisan
     and (not p_solo_prueba or clave like 'prueba-avisos-%');
  v_n := coalesce(array_length(v_claves, 1), 0);
  if v_n = 0 then return 'nada'; end if;
  select coalesce(sum(n_items), 0) into v_cards from public.botoneras
   where estado = 'abierta'
     and (snooze_hasta is null or snooze_hasta <= now());   -- snooze: ni cuentan en «N cards por decidir»
  v_cards_txt := case when v_cards = 1 then '1 card por decidir' else v_cards || ' cards por decidir' end;
  perform public.bm_avisos_llamar(jsonb_build_object(
    'tag', 'nuevas',
    'titulo', case when v_n = 1 then '1 botonera nueva' else v_n || ' botoneras nuevas' end,
    'cuerpo', concat_ws(' · ', public.bm_avisos_nombres(v_claves), v_cards_txt),
    'claves', to_jsonb(v_claves)));
  return 'avisado ' || v_n;
end $$;

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
   where b.estado = 'abierta'
     and (b.snooze_hasta is null or b.snooze_hasta <= now());   -- snooze: las dormidas no cuentan
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

-- ───────────────────────── permisos ─────────────────────────
-- bm_snoozear, bm_despertar y bm_lista (recreada) los llama la web con la clave pública (anon) + token, como
-- bm_decidir_pin. Las demás son create or replace: conservan los grants que ya tenían.

revoke all on function public.bm_snoozear(text, text, timestamptz) from public, anon, authenticated;
revoke all on function public.bm_despertar(text, text) from public, anon, authenticated;
revoke all on function public.bm_lista(text) from public, anon, authenticated;
grant execute on function
  public.bm_snoozear(text, text, timestamptz),
  public.bm_despertar(text, text),
  public.bm_lista(text)
to anon;

-- Botonera 1.3.0 · un aviso push por ráfaga. Se puede correr más de una vez.
--
--   Antes: el cron corría cada 5 minutos y avisaba todo lo pendiente. Una ráfaga que cruzaba el borde de los
--   5 minutos sonaba dos veces, y una tanda sola esperaba hasta 5 minutos.
--   Ahora: el cron corre cada minuto y bm_avisos_tick espera a que la ráfaga termine: avisa cuando la última tanda
--   que entró tiene 2 minutos o más (las que entran dentro de 2 minutos de la anterior suenan juntas).
--   Tope: si la primera sin avisar ya espera 10 minutos o más, avisa igual, para que un goteo continuo no te deje
--   sin aviso. La franja de silencio (22 a 8) no cambia: usa la zona horaria de bm_zona().
--   Reintento: si un envío falla, las mismas tandas no se vuelven a mandar antes de 5 minutos. Con el cron cada
--   minuto, cada fallo sumaba 1 a bm_push.fallos y a los 5 seguidos se borraba el dispositivo: en 5 minutos de
--   caída del servicio de push se perdía la suscripción. La marca vive en bm_config('aviso_intento').
--
-- bm_avisos_tick parte de la versión 1.2.1 (20261107010000) y conserva todo lo suyo: bm_zona, la rama `iniciando`,
-- el snooze y los títulos. Solo suma el chequeo de la ráfaga y el reintento. Misma firma, mismos grants.
--
-- Prueba sin avisar a nadie: select bm_avisos_tick(<ahora>, true) mira solo las claves `prueba-avisos-*`.
--   Devuelve 'silencio' | 'iniciando' | 'sin_dispositivos' | 'nada' | 'esperando N' | 'reintento_espera N' | 'avisado N'.

create or replace function public.bm_avisos_tick(p_ahora timestamptz default now(), p_solo_prueba boolean default false)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare
  v_hora int := extract(hour from p_ahora at time zone public.bm_zona());
  v_claves text[];
  v_n int;
  v_volvieron int;
  v_ultima timestamptz;
  v_primera timestamptz;
  v_cards int;
  v_cards_txt text;
  v_titulos text;
  v_titulo text;
  v_cuerpo text;
  v_firma text;
  v_intento text;
begin
  -- Recién instalada: sin claves VAPID la web no puede suscribirse. La función las genera con un llamado vacío.
  if not exists (select 1 from public.bm_config where k = 'vapid_publica') then
    perform public.bm_avisos_llamar('{}'::jsonb);
    return 'iniciando';
  end if;
  if v_hora >= 22 or v_hora < 8 then return 'silencio'; end if;
  if not exists (select 1 from public.bm_push) then return 'sin_dispositivos'; end if;
  -- cuándo entró cada tanda (la hora en que volvió, si venía de un snooze)
  select array_agg(clave), count(*) filter (where snooze_hasta is not null),
         max(greatest(created_at, coalesce(snooze_hasta, created_at))),
         min(greatest(created_at, coalesce(snooze_hasta, created_at)))
    into v_claves, v_volvieron, v_ultima, v_primera
    from public.botoneras
   where estado = 'abierta' and avisada_at is null
     and (snooze_hasta is null or snooze_hasta <= now())   -- snooze: las dormidas no se avisan
     and (not p_solo_prueba or clave like 'prueba-avisos-%');
  v_n := coalesce(array_length(v_claves, 1), 0);
  if v_n = 0 then return 'nada'; end if;
  -- la ráfaga sigue (entró algo hace menos de 2 minutos) y la más vieja espera menos de 10: se espera
  if p_ahora - v_ultima < interval '2 minutes' and p_ahora - v_primera < interval '10 minutes' then
    return 'esperando ' || v_n;
  end if;
  -- las mismas tandas, ya intentadas hace menos de 5 minutos (el envío falló o su resultado no llegó): se espera
  select string_agg(c, ',' order by c) into v_firma from unnest(v_claves) c;
  v_firma := md5(coalesce(v_firma, ''));
  select v into v_intento from public.bm_config where k = 'aviso_intento';
  if v_intento is not null and split_part(v_intento, '|', 2) = v_firma
     and p_ahora - split_part(v_intento, '|', 1)::timestamptz < interval '5 minutes' then
    return 'reintento_espera ' || v_n;
  end if;
  insert into public.bm_config (k, v) values ('aviso_intento', p_ahora::text || '|' || v_firma)
    on conflict (k) do update set v = excluded.v;
  select coalesce(sum(n_items), 0) into v_cards from public.botoneras
   where estado = 'abierta'
     and (snooze_hasta is null or snooze_hasta <= now());   -- snooze: ni cuentan en «N cards por decidir»
  v_cards_txt := case when v_cards = 1 then '1 card por decidir' else v_cards || ' cards por decidir' end;
  -- El título de la botonera cuando hay una sola; con varias, sus títulos abajo.
  v_titulos := public.bm_avisos_titulos(v_claves, 2);
  if v_n = 1 then
    v_titulo := case when v_titulos is null then '1 botonera nueva'
                     when v_volvieron = 1 then 'Volvió: ' || v_titulos
                     else v_titulos end;
    v_cuerpo := concat_ws(' · ', public.bm_avisos_nombres(v_claves), v_cards_txt);
  else
    v_titulo := v_n || case when v_volvieron = v_n then ' botoneras volvieron' else ' botoneras nuevas' end;
    v_cuerpo := concat_ws(' · ', coalesce(v_titulos, public.bm_avisos_nombres(v_claves)), v_cards_txt);
  end if;
  perform public.bm_avisos_llamar(jsonb_build_object(
    'tag', 'nuevas',
    'titulo', v_titulo,
    'cuerpo', v_cuerpo,
    'claves', to_jsonb(v_claves)));
  return 'avisado ' || v_n;
end $$;

-- El cron de «nuevas» pasa de cada 5 minutos a cada minuto (el chequeo de la ráfaga vive en la función).
do $$ begin
  if exists (select 1 from cron.job where jobname = 'bm-avisos-nuevas') then
    perform cron.alter_job(job_id := (select jobid from cron.job where jobname = 'bm-avisos-nuevas'), schedule := '* * * * *');
  end if;
end $$;

revoke all on function public.bm_avisos_tick(timestamptz, boolean) from public, anon, authenticated;

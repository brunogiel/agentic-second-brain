-- Botonera 1.2.1 · el aviso de una botonera nueva lleva su título. Se puede correr más de una vez.
--
--   · Una sola botonera nueva: el título del aviso es el título de la botonera. Si despertó de un snooze,
--     «Volvió: <título>». Abajo van la categoría y «N cards por decidir».
--   · Varias: «N botoneras nuevas» (o «N botoneras volvieron» si todas despertaron de un snooze). Abajo van
--     hasta 2 títulos separados por «, », con «+N» por los que no entran, y después las cards.
--   · Las categorías marcadas `privada` en categorias.json (y la categoría `otras`) no muestran título: el mismo
--     filtro que usa bm_avisos_nombres para los nombres de categoría. Cuentan en el número y el aviso cae al
--     texto genérico («1 botonera nueva»).
--   · Los títulos se recortan a 40 letras y salen los más nuevos primero.
--
-- bm_avisos_titulos es nueva y solo la llama bm_avisos_tick (como bm_avisos_nombres: sin grants para la clave
-- pública). bm_avisos_tick conserva todo lo de la 1.2.0 (bm_zona, la rama `iniciando`, el snooze) y cambia solo
-- cómo arma el título y el cuerpo.

-- Hasta p_max títulos de botonera para el aviso. Las categorías `privada` no se muestran (igual que en bm_avisos_nombres).
create or replace function public.bm_avisos_titulos(p_claves text[], p_max integer default 2)
returns text language sql stable security definer set search_path = public, extensions as $$
  with t as (
    select case when length(b.titulo) > 40 then left(b.titulo, 39) || '…' else b.titulo end titulo,
           row_number() over (order by greatest(b.created_at, coalesce(b.snooze_hasta, b.created_at)) desc, b.clave) r,
           count(*) over () n
      from public.botoneras b
     where b.clave = any(p_claves)
       and coalesce(b.titulo, '') <> ''
       and coalesce(b.datos->'categoria'->>'privada', 'false') <> 'true'
       and coalesce(b.datos->'categoria'->>'id', '') <> 'otras'
  )
  select case when max(n) > p_max then string_agg(titulo, ', ' order by r) filter (where r <= p_max) || ' +' || (max(n) - p_max)
              else string_agg(titulo, ', ' order by r) end
    from t;
$$;

create or replace function public.bm_avisos_tick(p_ahora timestamptz default now(), p_solo_prueba boolean default false)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare
  v_hora int := extract(hour from p_ahora at time zone public.bm_zona());
  v_claves text[];
  v_n int;
  v_volvieron int;
  v_cards int;
  v_cards_txt text;
  v_titulos text;
  v_titulo text;
  v_cuerpo text;
begin
  -- Recién instalada: sin claves VAPID la web no puede suscribirse. La función las genera con un llamado vacío.
  if not exists (select 1 from public.bm_config where k = 'vapid_publica') then
    perform public.bm_avisos_llamar('{}'::jsonb);
    return 'iniciando';
  end if;
  if v_hora >= 22 or v_hora < 8 then return 'silencio'; end if;
  if not exists (select 1 from public.bm_push) then return 'sin_dispositivos'; end if;
  select array_agg(clave), count(*) filter (where snooze_hasta is not null)   -- cuántas vuelven de un snooze
    into v_claves, v_volvieron
    from public.botoneras
   where estado = 'abierta' and avisada_at is null
     and (snooze_hasta is null or snooze_hasta <= now())   -- snooze: las dormidas no se avisan
     and (not p_solo_prueba or clave like 'prueba-avisos-%');
  v_n := coalesce(array_length(v_claves, 1), 0);
  if v_n = 0 then return 'nada'; end if;
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

-- ───────────────────────── permisos ─────────────────────────
-- bm_avisos_titulos solo la llama bm_avisos_tick (security definer, la corre el cron): sin grants, como
-- bm_avisos_nombres. Una función nueva nace ejecutable por PUBLIC, así que se cierra acá. bm_avisos_tick
-- es create or replace: conserva los grants que ya tenía.

revoke all on function public.bm_avisos_titulos(text[], integer) from public, anon, authenticated;

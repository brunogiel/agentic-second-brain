-- Botonera 1.3.0 · «Ya no aplica»: una card que el agente reemplazó por otra. Se puede correr más de una vez.
--
-- `armar.py --reemplaza <clave>#<n>` marca la card vieja de una tanda abierta. Solo agrega una función: no toca tablas
-- ni redefine nada. La card queda marcada con `reemplazada_por` ("<clave nueva>#<n>") dentro de botoneras.datos->items[i].
-- La página la saca del mazo y la muestra gris con el link a la nueva.
--
--   bm_reemplazar(p_secret, p_clave, p_n, p_por)
--     -> 'reemplazada:<cuántas cards activas le quedan a la tanda>' | 'no_existe' | 'sin_card' | 'ya_decidida:<estado>'
--   n_items baja a las cards activas (el home y los avisos no cuentan la gris). Repetir la misma marca no toca nada.
--   Una tanda ya decidida no se toca: la respuesta ya salió. updated_at sube (igual que al republicar): una decisión en
--   vuelo sobre la versión vieja contesta «cambio» y la página pide volver a entrar.
--
-- Roles. Entra el secret total y el de bot; el de bot solo sobre claves `bot-` (como bm_marcar y bm_recibir).
--
-- Rollback: drop function public.bm_reemplazar(text, text, integer, text);

create or replace function public.bm_reemplazar(p_secret text, p_clave text, p_n integer, p_por text)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare
  v_rol text;
  v_estado text;
  v_items jsonb;
  v_idx int;
  v_activas int;
begin
  v_rol := public.bm_rol(p_secret);
  if v_rol = 'bot' and not public.bm_es_bot(p_clave) then
    raise exception 'rol bot: solo claves bot-';
  end if;
  if p_por is null or p_por !~ '^[A-Za-z0-9._-]{1,120}#[0-9]{1,4}$' then
    raise exception 'p_por tiene que ser <clave>#<n>';
  end if;
  if split_part(p_por, '#', 1) = p_clave then
    raise exception 'una tanda no se reemplaza a sí misma';
  end if;

  select b.estado, b.datos->'items' into v_estado, v_items
    from public.botoneras b where b.clave = p_clave for update;
  if not found then
    return 'no_existe';
  end if;
  if v_estado <> 'abierta' then
    return 'ya_decidida:' || v_estado;
  end if;

  -- la card se busca por su `n`; sin `n` numérico vale su posición (la página hace lo mismo)
  select (t.ord - 1)::int into v_idx
    from jsonb_array_elements(coalesce(v_items, '[]'::jsonb)) with ordinality as t(i, ord)
   where jsonb_typeof(t.i) = 'object'
     and (case when jsonb_typeof(t.i->'n') = 'number' and (t.i->>'n')::numeric between 0 and 9999 and (t.i->>'n')::numeric = trunc((t.i->>'n')::numeric)
               then (t.i->>'n')::numeric::int else t.ord::int end) = p_n
   order by t.ord
   limit 1;
  if v_idx is null then
    return 'sin_card';
  end if;

  -- cuántas cards activas le quedan (contando ésta como ya reemplazada); n_items acompaña, así el home y los avisos no cuentan la gris
  select count(*) into v_activas
    from jsonb_array_elements(v_items) with ordinality as t(i, ord)
   where (t.ord - 1)::int <> v_idx and jsonb_typeof(t.i) = 'object' and coalesce(t.i->>'reemplazada_por', '') = '';

  -- idempotente: la misma marca otra vez no toca nada (updated_at invalidaría las decisiones en vuelo sin motivo)
  if v_items->v_idx->>'reemplazada_por' = p_por then
    return 'reemplazada:' || v_activas;
  end if;

  update public.botoneras
     set datos = jsonb_set(datos, array['items', v_idx::text, 'reemplazada_por'], to_jsonb(p_por)),
         n_items = v_activas,
         updated_at = now()
   where clave = p_clave;
  return 'reemplazada:' || v_activas;
end $$;

revoke all on function public.bm_reemplazar(text, text, integer, text) from public, authenticated;
grant execute on function public.bm_reemplazar(text, text, integer, text) to anon, service_role;

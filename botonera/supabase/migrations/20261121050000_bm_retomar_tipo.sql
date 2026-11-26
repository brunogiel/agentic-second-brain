-- Botonera 1.3.0 · bm_retomar también devuelve el `tipo` de cada card. Se puede correr más de una vez.
--
-- retomar.py y colgadas.py necesitan saber cuáles son cards de revisión (`tipo: "revision"`): una revisión no es una
-- decisión, no lleva plan `aplicar` obligatorio y no cuenta como «sin plan». Antes bm_retomar no traía el tipo y
-- una revisión se contaba como una decisión sin plan.
--
-- Solo suma una clave por ítem ('tipo', null en las cards de siempre). Mismos roles, mismos grants que 1.1.0.

create or replace function public.bm_retomar(p_secret text, p_clave text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_rol text := public.bm_rol(p_secret);
  b public.botoneras%rowtype;
  v_items jsonb;
begin
  -- Igual que bm_recibir / bm_marcar: el secret de bot solo ve claves bot-.
  if v_rol = 'bot' and not public.bm_es_bot(p_clave) then
    raise exception 'rol bot: solo claves bot-';
  end if;

  select * into b from public.botoneras where clave = p_clave;
  if not found then
    return jsonb_build_object('estado', 'no_existe');
  end if;

  select coalesce(jsonb_agg(jsonb_build_object(
           'n', i->'n',
           'titulo', i->'titulo',
           'contexto', i->'contexto',
           'opciones', i->'opciones',
           'varias', i->'varias',
           'accion_va', i->'accion_va',
           'accion_no_va', i->'accion_no_va',
           'tipo', i->'tipo',
           'aplicar', i->'aplicar'
         ) order by ord), '[]'::jsonb)
    into v_items
    from jsonb_array_elements(coalesce(b.datos->'items', '[]'::jsonb)) with ordinality as t(i, ord);

  return jsonb_build_object(
    'clave', b.clave,
    'estado', b.estado,
    'titulo', b.titulo,
    'contexto', b.datos->'contexto',
    'sesion_titulo', b.sesion_titulo,
    'session_id', b.session_id,
    'proyecto', b.proyecto,
    'decided_at', b.decided_at,
    'applied_at', b.applied_at,
    'respuesta_texto', b.respuesta_texto,
    'resumen_aplicado', b.resumen_aplicado,
    'items', v_items
  );
end $$;

revoke all on function public.bm_retomar(text, text) from public, anon, authenticated;
grant execute on function public.bm_retomar(text, text) to anon;

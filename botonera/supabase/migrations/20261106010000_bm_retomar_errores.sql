-- Botonera 1.1.0 · retomar una tanda sin la sesión viva y la fila «Con error». Se puede correr más de una vez.
-- Depende de bm_rol (migración 20261106000000_bm_rol_bot.sql).
--
--   A. bm_retomar(p_secret, p_clave): lectura pura de una tanda (estado, respuesta y el plan `aplicar` de cada ítem)
--      para que cualquier sesión nueva la retome. No cambia el estado: bm_recibir sí lo cambia y no trae el plan.
--      Lo usan retomar.py (y colgadas.py para contar cuántas cards tienen plan).
--   B. Tabla bm_errores y 3 RPC: publicar (con secret), listar y marcar visto (con el token de la web).
--      Lo que murió sin avisar (una tarea programada que pegó el límite de uso, una tanda archivada con una
--      respuesta sin aplicar) aparece en la fila «Con error» del home hasta que tocás «Visto».
--
-- Todo es aditivo. Para deshacerlo:
--   drop function public.bm_retomar(text, text);
--   drop function public.bm_error_visto(text, bigint);
--   drop function public.bm_errores_lista(text);
--   drop function public.bm_error_publicar(text, text, text, text, text, timestamptz);
--   drop table public.bm_errores;

-- ───────────────────────── A. bm_retomar ─────────────────────────
-- No trae `datos` entero: las cards llevan imágenes como data: URI (hasta 900 KB cada una). Devuelve solo lo que
-- hace falta para aplicar: por ítem n, título, tipo de card, etiquetas de los botones y el plan `aplicar`.

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

-- ───────────────────────── B. bm_errores ─────────────────────────

create table if not exists public.bm_errores (
  id          bigint generated always as identity primary key,
  tipo        text        not null check (tipo in ('tarea', 'sesion')),
  origen_id   text        not null,           -- tarea: el taskId · sesion: la clave de la tanda
  titulo      text        not null,
  motivo      text,
  ocurrio_at  timestamptz not null,
  visto_at    timestamptz,
  created_at  timestamptz not null default now(),
  -- publicar dos veces el mismo fallo no lo duplica (una rutina que repite la lectura cada noche)
  constraint bm_errores_unico unique (tipo, origen_id, ocurrio_at)
);

-- RLS prendida y sin policies: ni anon ni authenticated tocan la tabla. Solo las RPC (SECURITY DEFINER).
alter table public.bm_errores enable row level security;
revoke all on public.bm_errores from anon, authenticated;

-- Con secret. El rol bot no publica errores.
create or replace function public.bm_error_publicar(p_secret text, p_tipo text, p_origen_id text, p_titulo text,
  p_motivo text, p_ocurrio_at timestamptz)
returns text language plpgsql security definer set search_path = public, extensions as $$
declare
  v_rol text := public.bm_rol(p_secret);
  v_rows int;
begin
  if v_rol <> 'total' then
    raise exception 'rol bot: no publica errores';
  end if;
  if p_tipo is null or p_tipo not in ('tarea', 'sesion') then
    raise exception 'tipo invalido: %', p_tipo;
  end if;
  if coalesce(trim(p_origen_id), '') = '' or coalesce(trim(p_titulo), '') = '' or p_ocurrio_at is null then
    raise exception 'faltan origen_id, titulo u ocurrio_at';
  end if;

  insert into public.bm_errores (tipo, origen_id, titulo, motivo, ocurrio_at)
  values (p_tipo, left(p_origen_id, 200), left(p_titulo, 200), left(p_motivo, 600), p_ocurrio_at)
  on conflict (tipo, origen_id, ocurrio_at) do nothing;
  get diagnostics v_rows = row_count;
  return case when v_rows = 1 then 'creado' else 'repetido' end;
end $$;

-- Con el token de la web (mismo patrón que bm_lista). Solo los no vistos.
create or replace function public.bm_errores_lista(p_token text)
returns table(id bigint, tipo text, origen_id text, titulo text, motivo text, ocurrio_at timestamptz)
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check_token(p_token);
  return query select e.id, e.tipo, e.origen_id, e.titulo, e.motivo, e.ocurrio_at
    from public.bm_errores e
   where e.visto_at is null
   order by e.ocurrio_at desc
   limit 50;
end $$;

-- Con el token de la web. Marca uno como visto y avisa si lo marcó.
create or replace function public.bm_error_visto(p_token text, p_id bigint)
returns boolean language plpgsql security definer set search_path = public, extensions as $$
declare v_rows int;
begin
  perform public.bm_check_token(p_token);
  update public.bm_errores set visto_at = now() where id = p_id and visto_at is null;
  get diagnostics v_rows = row_count;
  return v_rows = 1;
end $$;

-- ───────────────────────── permisos ─────────────────────────
-- Como bm_recibir y bm_lista: la web y los scripts las llaman con la clave pública (anon) + secret o token.

revoke all on function public.bm_retomar(text, text) from public, anon, authenticated;
revoke all on function public.bm_error_publicar(text, text, text, text, text, timestamptz) from public, anon, authenticated;
revoke all on function public.bm_errores_lista(text) from public, anon, authenticated;
revoke all on function public.bm_error_visto(text, bigint) from public, anon, authenticated;
grant execute on function
  public.bm_retomar(text, text),
  public.bm_error_publicar(text, text, text, text, text, timestamptz),
  public.bm_errores_lista(text),
  public.bm_error_visto(text, bigint)
to anon;

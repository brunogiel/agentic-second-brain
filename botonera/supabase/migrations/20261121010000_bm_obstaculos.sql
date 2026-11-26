-- Botonera 1.3.0 · Bloqueos: lo que el agente no puede hacer solo y te espera a vos. Se puede correr más de una vez.
--
-- Un obstáculo es algo que frena al agente y solo vos podés destrabar: abrir un permiso, pegar una clave, aprobar algo
-- en una página. El agente lo publica con `obstaculo.py`; vos lo ves en la pestaña Bloqueos como «Te esperan a vos».
--
--   Tabla  bm_obstaculos(id, titulo, por_que, de, frena, link, comando, estado, comentario, creado_at, cambio_at,
--                        atendido_at, llevado_at)
--   Estados: abierta (nada tocado) · comentada (dejaste un comentario, sigue abierta) · no_puedo (no podés hoy, sigue en la
--            lista con su marca) · hecho (lo resolviste: sale de la lista y espera que el agente lo recoja).
--
--   Web (token del PIN)
--     bm_acciones_lista(p_token)                              -> {items:[{origen, ref, titulo, por_que, de, fecha, frena, link,
--                                                                          comando, estado, comentario}]}
--     bm_accion_hecha(p_token, 'item', ref, comentario)       -> {resultado: 'en_cola' | 'ya no esta trabado'}
--     bm_accion_marcar(p_token, 'item', ref, estado, coment.) -> {origen, ref, estado, comentario, cambio_at}   (no_puedo | comentada)
--   Agente (secret)
--     bm_obstaculo_publicar(p_secret, titulo, por_que, de, frena, link, comando, retoma) -> {id, nuevo}
--     bm_obstaculos_resueltos(p_secret)                       -> [{id, ref, titulo, estado, comentario, de, frena, retoma, atendido_at}]
--     bm_obstaculo_llevado(p_secret, p_id)                    -> {id, llevado}
--
-- El JSON de la web es el mismo de siempre: `origen` vale siempre 'item' y `ref` es el id del obstáculo como texto.
-- «en_cola» en bm_accion_hecha quiere decir «quedó anotado»; la web lo muestra como «Listo».
--
-- Roles. Las funciones con secret usan bm_check: solo entra el secret total. El secret de bot NO publica, ni lee, ni cierra
-- obstáculos. Los obstáculos son del dueño de la botonera; un bot no tiene a quién pedirle que destrabe nada.
--
-- La tabla con RLS prendida y sin policies: solo se llega por las funciones SECURITY DEFINER.

begin;

create table if not exists public.bm_obstaculos (
  id          bigserial primary key,
  titulo      text not null,
  por_que     text not null default '',
  de          text not null default '',     -- de qué proyecto o sesión viene
  frena      text not null default '',      -- qué trabajo frena (vacío = no frena nada hoy)
  link        text not null default '',     -- solo https
  comando     text not null default '',
  retoma      text not null default '',     -- qué sigue cuando lo hagas (una pista para el agente que lo recoge)
  estado      text not null default 'abierta' check (estado in ('abierta', 'comentada', 'no_puedo', 'hecho')),
  comentario  text not null default '',
  creado_at   timestamptz not null default now(),
  cambio_at   timestamptz not null default now(),
  atendido_at timestamptz,                  -- cuándo lo marcaste hecho
  llevado_at  timestamptz                   -- cuándo el agente lo recogió
);
alter table public.bm_obstaculos enable row level security;
revoke all on public.bm_obstaculos from anon, authenticated;

-- Dos obstáculos abiertos con el mismo título no conviven (lo mira bm_obstaculo_publicar).
alter table public.bm_obstaculos add column if not exists retoma text not null default '';

create index if not exists bm_obstaculos_estado_idx on public.bm_obstaculos (estado, creado_at);

-- ───────────────────────── agente (secret total) ─────────────────────────

-- Una versión anterior de esta migración tenía siete parámetros: se saca para no dejar dos funciones con el mismo nombre.
drop function if exists public.bm_obstaculo_publicar(text, text, text, text, text, text, text);

create or replace function public.bm_obstaculo_publicar(
    p_secret text, p_titulo text, p_por_que text, p_de text, p_frena text, p_link text, p_comando text,
    p_retoma text default '')
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_titulo  text := left(btrim(coalesce(p_titulo, '')), 300);
  v_link    text := btrim(coalesce(p_link, ''));
  v_comando text := left(btrim(coalesce(p_comando, '')), 300);
  v_fila    public.bm_obstaculos;
begin
  perform public.bm_check(p_secret);
  if v_titulo = '' then
    raise exception 'falta titulo';
  end if;
  -- el link vale solo si es https, sin espacios y de hasta 500 letras; cualquier otra cosa se rechaza
  if v_link <> '' and not (length(v_link) <= 500 and v_link ~ '^https://[^[:space:]]+$') then
    raise exception 'link invalido: tiene que ser https y sin espacios';
  end if;
  if v_link = '' and v_comando = '' then
    raise exception 'falta link o comando: sin uno de los dos no hay nada que hacer';
  end if;

  -- dos publicaciones a la vez no duplican
  perform pg_advisory_xact_lock(hashtext('bm_obstaculo_publicar'));
  select * into v_fila from public.bm_obstaculos
   where lower(titulo) = lower(v_titulo) and estado <> 'hecho'
   order by id desc limit 1;
  if found then
    return jsonb_build_object('id', v_fila.id, 'nuevo', false);
  end if;

  insert into public.bm_obstaculos (titulo, por_que, de, frena, link, comando, retoma)
  values (v_titulo, left(btrim(coalesce(p_por_que, '')), 600), left(btrim(coalesce(p_de, '')), 80),
          left(btrim(coalesce(p_frena, '')), 200), v_link, v_comando, left(btrim(coalesce(p_retoma, '')), 300))
  returning * into v_fila;
  return jsonb_build_object('id', v_fila.id, 'nuevo', true);
end $$;

-- Lo que resolviste (hecho) o marcaste «no puedo» y el agente todavía no recogió.
create or replace function public.bm_obstaculos_resueltos(p_secret text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check(p_secret);
  return coalesce((
    select jsonb_agg(jsonb_build_object('id', o.id, 'ref', o.id::text, 'titulo', o.titulo, 'estado', o.estado,
                                        'comentario', o.comentario, 'de', o.de, 'frena', o.frena, 'retoma', o.retoma,
                                        'atendido_at', coalesce(o.atendido_at, o.cambio_at))
                     order by coalesce(o.atendido_at, o.cambio_at), o.id)
      from public.bm_obstaculos o
     where o.estado in ('hecho', 'no_puedo') and o.llevado_at is null), '[]'::jsonb);
end $$;

-- El agente ya recogió el obstáculo. Un `hecho` queda cerrado; un `no_puedo` sigue en la lista pero ya no se avisa de nuevo.
create or replace function public.bm_obstaculo_llevado(p_secret text, p_id bigint)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_n integer;
begin
  perform public.bm_check(p_secret);
  update public.bm_obstaculos set llevado_at = now()
   where id = p_id and llevado_at is null and estado in ('hecho', 'no_puedo');
  get diagnostics v_n = row_count;
  return jsonb_build_object('id', p_id, 'llevado', v_n > 0);
end $$;

-- ───────────────────────── web (token del PIN) ─────────────────────────

-- Los que frenan trabajo primero; dentro de cada grupo, el más viejo primero. Un `hecho` ya no sale.
create or replace function public.bm_acciones_lista(p_token text)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
begin
  perform public.bm_check_token(p_token);
  return jsonb_build_object('items', coalesce((
    select jsonb_agg(jsonb_build_object(
             'origen', 'item', 'ref', o.id::text, 'titulo', o.titulo, 'por_que', o.por_que,
             'de', o.de, 'fecha', o.creado_at,
             'frena', o.frena, 'link', o.link, 'comando', o.comando,
             'estado', case when o.estado = 'comentada' then 'comentada' when o.estado = 'no_puedo' then 'no_puedo' else 'abierta' end,
             'comentario', o.comentario)
           order by (o.frena <> '') desc, o.creado_at asc, o.id)
      from public.bm_obstaculos o
     where o.estado <> 'hecho'
  ), '[]'::jsonb));
end $$;

-- «Listo». El comentario de Listo y el comentario suelto previo («Comentar») viajan juntos en `comentario`.
create or replace function public.bm_accion_hecha(p_token text, p_origen text, p_ref text, p_comentario text default '')
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_id   bigint;
  v_fila public.bm_obstaculos;
  v_com  text := left(btrim(coalesce(p_comentario, '')), 500);
  v_prev text;
  v_nota text;
begin
  perform public.bm_check_token(p_token);
  if p_origen is distinct from 'item' then
    raise exception 'origen invalido';
  end if;
  if coalesce(p_ref, '') !~ '^[0-9]{1,18}$' then
    raise exception 'ref invalido';
  end if;
  v_id := p_ref::bigint;

  select * into v_fila from public.bm_obstaculos where id = v_id for update;
  if not found or v_fila.estado = 'hecho' then
    return jsonb_build_object('resultado', 'ya no esta trabado');
  end if;

  v_prev := case when v_fila.estado = 'comentada' then left(v_fila.comentario, 400) end;
  v_nota := concat_ws(' · ', nullif(v_com, ''),
                      case when coalesce(v_prev, '') <> '' and v_prev is distinct from v_com
                           then 'comentario previo: ' || v_prev end);
  update public.bm_obstaculos
     set estado = 'hecho', comentario = left(v_nota, 1000), cambio_at = now(), atendido_at = now(), llevado_at = null
   where id = v_id;
  return jsonb_build_object('resultado', 'en_cola');
end $$;

-- «No puedo» (comentario opcional) y «Comentar» (comentario obligatorio, no cierra la fila).
create or replace function public.bm_accion_marcar(
    p_token text, p_origen text, p_ref text, p_estado text, p_comentario text default '')
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare
  v_com  text := left(btrim(coalesce(p_comentario, '')), 1000);
  v_id   bigint;
  v_fila public.bm_obstaculos;
begin
  perform public.bm_check_token(p_token);
  if p_origen is distinct from 'item' then
    raise exception 'origen invalido';
  end if;
  if coalesce(p_ref, '') !~ '^[0-9]{1,18}$' then
    raise exception 'ref invalido';
  end if;
  if p_estado is null or p_estado not in ('no_puedo', 'comentada') then
    raise exception 'estado invalido';
  end if;
  if v_com = '' and p_estado = 'comentada' then
    raise exception 'falta comentario';
  end if;
  v_id := p_ref::bigint;

  select * into v_fila from public.bm_obstaculos where id = v_id for update;
  if not found then
    raise exception 'ref inexistente';
  end if;
  if v_fila.estado = 'hecho' then
    raise exception 'ya no esta trabado';
  end if;

  update public.bm_obstaculos
     set -- «Comentar» no pisa un no_puedo: solo actualiza el comentario.
         estado     = case when p_estado = 'comentada' and estado = 'no_puedo' then 'no_puedo' else p_estado end,
         comentario = v_com,
         cambio_at  = now(),
         -- marcar de nuevo vuelve a avisarle al agente; un comentario sobre un no_puedo ya recogido no cambia eso
         llevado_at = case when p_estado = 'comentada' and estado = 'no_puedo' then llevado_at else null end
   where id = v_id
   returning * into v_fila;
  return jsonb_build_object('origen', 'item', 'ref', v_fila.id::text, 'estado', v_fila.estado,
                            'comentario', v_fila.comentario, 'cambio_at', v_fila.cambio_at);
end $$;

-- ───────────────────────── permisos ─────────────────────────

revoke all on function public.bm_obstaculo_publicar(text, text, text, text, text, text, text, text) from public, authenticated;
grant execute on function public.bm_obstaculo_publicar(text, text, text, text, text, text, text, text) to anon, service_role;
revoke all on function public.bm_obstaculos_resueltos(text) from public, authenticated;
grant execute on function public.bm_obstaculos_resueltos(text) to anon, service_role;
revoke all on function public.bm_obstaculo_llevado(text, bigint) from public, authenticated;
grant execute on function public.bm_obstaculo_llevado(text, bigint) to anon, service_role;
revoke all on function public.bm_acciones_lista(text) from public, authenticated;
grant execute on function public.bm_acciones_lista(text) to anon, service_role;
revoke all on function public.bm_accion_hecha(text, text, text, text) from public, authenticated;
grant execute on function public.bm_accion_hecha(text, text, text, text) to anon, service_role;
revoke all on function public.bm_accion_marcar(text, text, text, text, text) from public, authenticated;
grant execute on function public.bm_accion_marcar(text, text, text, text, text) to anon, service_role;

commit;

/* ARTIFACT: adaptador de datos.
   La web de la botonera habla con su base por `createClient(...).rpc(nombre, params)` -> Promise<{data, error}>.
   Este adaptador tiene esa misma interfaz, pero contesta cada RPC con la base de la página privada de Claude (`db`).

   Documentos (el contrato con Claude; ver SKILL.md):
     tandas/<clave>     lo escribe Claude: la tanda (lo que arma `armar.py --artifact`) + creada, estado
                        ('abierta'|'decidida'|'aplicada'|'archivada'), resumen?, actualizada?, snooze_hasta?
     respuestas/<clave> lo escribe la página al Enviar: {clave, texto, por, cuando}
     estado/<clave>     lo escribe Claude mientras trabaja: {texto, cuando}
     marcas/<clave>     lo escribe la página: {clave, marcas?, snooze_hasta?, archivada?, por, cuando}
   La página NUNCA escribe en `tandas` ni en `estado`. */
(function(){
'use strict';
var A = window.__art = {enviadas: {}, aviso: {}, canal: {room: false, com: false}, room: null, comments: null, alCambiar: null, soloLectura: false};
var db = null, user = null, uid = null;
var C = {tandas: new Map(), respuestas: new Map(), estado: new Map(), marcas: new Map()};
var ultimoMarcas = {}, pendMarcas = {}, cola = {}, enVuelo = {};
var resolverListo;
A.listo = new Promise(function(r){ resolverListo = r; });

function usar(n){
  try{ return window.claude && typeof window.claude.use === 'function' ? Promise.resolve(window.claude.use(n)).then(function(x){ return x || null; }, function(){ return null; }) : Promise.resolve(null); }
  catch(e){ return Promise.resolve(null); }
}
function ok(d){ return {data: d, error: null}; }
function err(m){ return {data: null, error: {message: m}}; }
function iso(x){ if(!x) return null; var t = new Date(x).getTime(); return isFinite(t) ? new Date(t).toISOString() : null; }
function ms(x){ return x ? (new Date(x).getTime() || 0) : 0; }
function ahoraISO(){ return new Date().toISOString(); }

/* ---------- categoría: si la tanda no la trae embebida, sale de origen.categoria; si falta, «Pendientes» ---------- */
var ICONO_LIBRE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8Z"/><circle cx="7.5" cy="7.5" r="1.3"/></svg>';
var COLORES = ['#8ECAC8', '#F2C6A0', '#BFD8A8', '#D9CBA3', '#C9B8E0', '#E8B4B8', '#B8D4E8'];
function slug(t){ return String(t).toLowerCase().normalize('NFKD').replace(/[^\x00-\x7f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 30).replace(/-+$/, '') || 'cat'; }
function categoriaDe(t){
  var c = t && t.categoria;
  if(c && typeof c === 'object' && /^[a-z0-9_-]{1,30}$/i.test(String(c.id || ''))) return c;
  var o = t && t.origen && typeof t.origen === 'object' ? t.origen : {};
  var nombre = String(o.categoria || o.proyecto || '').trim() || 'Pendientes';
  var id = slug(nombre), h = 0;
  for(var i = 0; i < id.length; i++) h += id.charCodeAt(i);
  return {id: id, nombre: nombre, color: COLORES[h % COLORES.length], icono: ICONO_LIBRE, orden: 1, privada: false};
}

/* ---------- de los documentos a las filas que devuelve bm_lista ---------- */
function filaDe(clave, t){
  var r = C.respuestas.get(clave) || null, e = C.estado.get(clave) || null, m = C.marcas.get(clave) || null;
  var est = t.estado || 'abierta';
  if(est === 'abierta' && r) est = e && e.texto ? 'recibida' : 'decidida';
  else if(est === 'decidida' && e && e.texto) est = 'recibida';
  var archivada = !!(m && m.archivada) && (est === 'decidida' || est === 'recibida' || est === 'esperando');
  if(archivada) est = 'archivada';
  var creada = iso(t.creada) || new Date(0).toISOString();
  var upd = iso(t.actualizada) || creada;
  var snooze = m && m.snooze_hasta !== undefined ? iso(m.snooze_hasta) : iso(t.snooze_hasta);
  var o = t.origen && typeof t.origen === 'object' ? t.origen : {};
  var decidida = iso(r && r.cuando) || iso(t.decidida);
  var trabaja = est === 'recibida' || est === 'aplicada';
  var resumen = est === 'aplicada' ? (t.resumen || null) : (est === 'archivada' && archivada ? 'Archivada desde Sesiones' : (t.resumen || null));
  return {
    clave: clave, session_id: null, sesion_titulo: o.sesion_titulo || null, skill: o.skill || 'tarjetas', proyecto: o.proyecto || null,
    titulo: t.titulo || clave, n_items: Array.isArray(t.items) ? t.items.length : 0, estado: est, resumen_aplicado: resumen,
    created_at: creada, updated_at: upd, decided_at: decidida,
    received_at: trabaja ? (iso(e && e.cuando) || decidida) : null,
    applied_at: est === 'aplicada' ? (iso(t.aplicada) || iso(t.actualizada) || iso(e && e.cuando) || decidida || creada) : null,
    espera_motivo: est === 'esperando' ? (t.espera_motivo || null) : null, esperando_at: est === 'esperando' ? (iso(t.esperando_at) || upd) : null,
    snooze_hasta: snooze,
    llegada: snooze && ms(snooze) <= Date.now() ? new Date(Math.max(ms(creada), ms(snooze))).toISOString() : creada,
    estado_texto: (e && e.texto && (est === 'decidida' || est === 'recibida')) ? String(e.texto) : ''
  };
}
function filas(){
  var out = [];
  C.tandas.forEach(function(t, clave){ if(t && typeof t === 'object') out.push(filaDe(clave, t)); });
  out.sort(function(a, b){ return ms(b.created_at) - ms(a.created_at) || (a.clave < b.clave ? -1 : 1); });
  return out;
}

/* ---------- escritura: de a una por documento ---------- */
function escribir(path, doc){
  var antes = cola[path] || Promise.resolve();
  var p = antes.then(function(){ return db.doc(path).set(doc); });
  cola[path] = p.catch(function(){});
  return p;
}
function errEscritura(e){
  var c = e && e.code;
  if(c === 'invalid_argument' || c === 'revoked' || c === 'not_granted') return 'No tenés permiso para cambiar nada en esta página.';
  return 'No se pudo guardar. Probá de nuevo.';
}
function setMarcas(clave, parche){
  var cur = C.marcas.get(clave) || {clave: clave};
  var nuevo = {}; Object.keys(cur).forEach(function(k){ nuevo[k] = cur[k]; });
  Object.keys(parche).forEach(function(k){ nuevo[k] = parche[k]; });
  nuevo.clave = clave; nuevo.por = uid; nuevo.cuando = ahoraISO();
  C.marcas.set(clave, nuevo);   // se ve ya; el snapshot lo confirma
  return escribir('marcas/' + clave, nuevo);
}

/* ---------- las RPC ---------- */
function categoriaEmbebida(t){ var d = {}; Object.keys(t).forEach(function(k){ d[k] = t[k]; }); d.categoria = categoriaDe(t); return d; }
var RPC = {
  bm_entrar: function(){ return Promise.resolve(ok({ok: true, token: 'claude'})); },
  bm_salir: function(){ return Promise.resolve(ok(null)); },
  bm_lista: function(){ return Promise.resolve(ok(filas())); },
  bm_fila: function(a){
    var t = C.tandas.get(a.p_clave); if(!t) return Promise.resolve(err('no existe'));
    var f = filaDe(a.p_clave, t), r = C.respuestas.get(a.p_clave);
    return Promise.resolve(ok({clave: f.clave, html: '', estado: f.estado, updated_at: f.updated_at, respuesta_texto: r ? r.texto : null,
      resumen_aplicado: f.resumen_aplicado, datos: categoriaEmbebida(t)}));
  },
  bm_decidir_pin: function(a){
    var c = a.p_clave, txt = a.p_respuesta, pref = '/botonera respuesta · ' + c;
    if(typeof txt !== 'string' || txt.slice(0, pref.length) !== pref) return Promise.resolve(err('respuesta invalida'));
    var t = C.tandas.get(c); if(!t) return Promise.resolve(ok('no_existe'));
    if(a.p_version && Math.floor(ms(a.p_version)) !== Math.floor(ms(filaDe(c, t).updated_at))) return Promise.resolve(ok('cambio'));
    var f = filaDe(c, t);
    if(f.estado !== 'abierta') return Promise.resolve(ok(f.estado));
    if(A.soloLectura) return Promise.resolve(err('No tenés permiso para responder en esta página.'));
    if(enVuelo[c]) return enVuelo[c];
    var doc = {clave: c, texto: txt, por: uid, cuando: ahoraISO()};
    C.respuestas.set(c, doc);   // optimista: la lista que se pide enseguida ya la ve decidida
    enVuelo[c] = escribir('respuestas/' + c, doc).then(function(){
      A.enviadas[c] = txt;
      delete enVuelo[c];
      var m = C.marcas.get(c);
      if(m && (m.marcas || (m.snooze_hasta && ms(m.snooze_hasta) > Date.now()))) setMarcas(c, {marcas: null, snooze_hasta: null}).catch(function(){});
      chequearCanal();
      return ok('decidida');
    }, function(e){ C.respuestas.delete(c); delete enVuelo[c]; return err(errEscritura(e)); });
    return enVuelo[c];
  },
  bm_snoozear: function(a){
    var c = a.p_clave, t = C.tandas.get(c), h = ms(a.p_hasta);
    if(!h || h <= Date.now() || h >= Date.now() + 8 * 24 * 3600e3) return Promise.resolve(err('hora invalida'));
    if(!t) return Promise.resolve(ok('no_existe'));
    var f = filaDe(c, t); if(f.estado !== 'abierta') return Promise.resolve(ok(f.estado));
    if(A.soloLectura) return Promise.resolve(err('No tenés permiso para cambiar nada en esta página.'));
    return setMarcas(c, {snooze_hasta: new Date(h).toISOString()}).then(function(){ return ok('abierta'); }, function(e){ return err(errEscritura(e)); });
  },
  bm_despertar: function(a){
    var c = a.p_clave, t = C.tandas.get(c); if(!t) return Promise.resolve(ok('no_existe'));
    var f = filaDe(c, t);
    if(f.estado !== 'abierta' || !f.snooze_hasta || ms(f.snooze_hasta) <= Date.now()) return Promise.resolve(ok(f.estado));
    if(A.soloLectura) return Promise.resolve(err('No tenés permiso para cambiar nada en esta página.'));
    return setMarcas(c, {snooze_hasta: ahoraISO()}).then(function(){ return ok('abierta'); }, function(e){ return err(errEscritura(e)); });
  },
  bm_archivar_pin: function(a){
    var c = a.p_clave, t = C.tandas.get(c); if(!t) return Promise.resolve(err('clave inexistente'));
    var f = filaDe(c, t);
    if(f.estado !== 'decidida' && f.estado !== 'recibida' && f.estado !== 'esperando') return Promise.resolve(ok({anterior: f.estado, cambiado: false}));
    if(A.soloLectura) return Promise.resolve(err('No tenés permiso para cambiar nada en esta página.'));
    return setMarcas(c, {archivada: true}).then(function(){ return ok({anterior: f.estado, cambiado: true}); }, function(e){ return err(errEscritura(e)); });
  },
  // lo que esta versión no tiene: obstáculos, errores técnicos, sesiones en vuelo de otros agentes
  bm_seguimiento: function(){ return Promise.resolve(ok({vuelo: [], pedidos: [], escucha_at: null, activos: 0})); },
  bm_acciones_lista: function(){ return Promise.resolve(ok({items: []})); },
  bm_errores_lista: function(){ return Promise.resolve(ok([])); },
  bm_error_visto: function(){ return Promise.resolve(ok(false)); },
  bm_accion_hecha: function(){ return Promise.resolve(err('no disponible')); },
  bm_accion_marcar: function(){ return Promise.resolve(err('no disponible')); },
  bm_push_clave: function(){ return Promise.resolve(ok(null)); },
  bm_push_suscribir: function(){ return Promise.resolve(err('no disponible')); }
};
window.supabase = {createClient: function(){
  return {rpc: function(nombre, params){
    var f = RPC[nombre];
    if(!f) return Promise.resolve(err('rpc desconocida: ' + nombre));
    return A.listo.then(function(listo){ return listo ? f(params || {}) : err('sin base'); });
  }};
}};

/* ---------- marcas a medio decidir: del navegador a la base (para seguir en otro dispositivo) ---------- */
A.guardarMarcas = function(todas){
  if(!db || A.soloLectura) return;
  Object.keys(todas || {}).forEach(function(c){
    var m = todas[c], j; try{ j = JSON.stringify(m); }catch(e){ return; }
    if(ultimoMarcas[c] === j) return;
    ultimoMarcas[c] = j;
    clearTimeout(pendMarcas[c]);
    pendMarcas[c] = setTimeout(function(){ setMarcas(c, {marcas: m}).catch(function(){}); }, 900);   // una escritura por pausa
  });
};
// lo que otro dispositivo dejó marcado: la página lo adopta una vez por clave, al abrir
A.marcasRemotas = function(){
  var o = {};
  C.marcas.forEach(function(m, c){
    if(m && m.marcas && typeof m.marcas === 'object' && m.marcas.items){ o[c] = m.marcas; try{ ultimoMarcas[c] = JSON.stringify(m.marcas); }catch(e){} }
  });
  return o;
};

/* ---------- canales para avisarle a Claude ---------- */
function chequearCanal(){
  var p = [];
  if(A.room && typeof A.room.canSendToClaudeSession === 'function')
    p.push(Promise.resolve(A.room.canSendToClaudeSession()).then(function(v){ A.canal.room = ['available', 'available_if_summoned', 'available_if_opened'].indexOf(v) >= 0; }, function(){ A.canal.room = false; }));
  if(A.comments && typeof A.comments.canSendToClaude === 'function')
    p.push(Promise.resolve(A.comments.canSendToClaude()).then(function(v){ A.canal.com = v === 'available'; }, function(){ A.canal.com = false; }));
  return Promise.all(p).then(function(){ if(A.repintar) A.repintar(); });
}

/* ---------- arranque: una sola suscripción por colección ---------- */
var primeros = 0, cambioT = null;
function aviso(){ clearTimeout(cambioT); cambioT = setTimeout(function(){ if(A.alCambiar) A.alCambiar(); }, 120); }
function suscribir(nombre, query, esTandas){
  var llego = false;
  function marcar(){ if(llego) return; llego = true; if(++primeros === 4) resolverListo(true); }
  query.onSnapshot(function(s){
    var m = new Map(); s.docs.forEach(function(d){ var x = d.data(); if(x) m.set(d.id, x); });
    C[nombre] = m;
    if(llego) aviso(); else marcar();
  }, function(){ if(esTandas){ if(!llego){ llego = true; resolverListo(false); } } else marcar(); });
}
Promise.all([usar('db'), usar('user'), usar('room'), usar('comments')]).then(function(r){
  db = r[0]; user = r[1]; A.room = r[2]; A.comments = r[3];
  if(!db){ resolverListo(false); return; }
  var pu = user ? Promise.resolve(user.id()).then(function(x){ uid = x || null; }, function(){}) : Promise.resolve();
  var pw = user ? Promise.resolve(user.can('data.write')).then(function(x){ if(x === false) A.soloLectura = true; }, function(){}) : Promise.resolve();
  return Promise.all([pu, pw]).then(function(){
    suscribir('tandas', db.collection('tandas').orderBy('creada', 'desc').limit(100), true);
    suscribir('respuestas', db.collection('respuestas').limit(200));
    suscribir('estado', db.collection('estado').limit(200));
    suscribir('marcas', db.collection('marcas').limit(200));
    chequearCanal();
  });
}).catch(function(){ resolverListo(false); });
})();

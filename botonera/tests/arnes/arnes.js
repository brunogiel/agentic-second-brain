/* Arnés de prueba de la web (sin Supabase, sin red).
 *
 * Sirve web/ con un servidor propio, le inyecta un config.js de mentira y reemplaza las dos librerías de /vendor/
 * (supabase-js y canvas-confetti) por stubs. El stub de supabase-js contesta las RPC `bm_*` con los datos de un
 * escenario y anota cada llamada en window.__rpcs. Todo lo que no sea el servidor local se corta: nada sale a la red.
 *
 * Uso desde un e2e:
 *   const A = require('./arnes/arnes');
 *   await A.levantar(); const { ctx, page } = await A.ctxNuevo(A.escenario('simple'), { ancho: 390, alto: 844 });
 *   ... await ctx.close(); await A.cerrar();
 *
 * Playwright: require('playwright') (instalado con `cd tests && npm install`).
 */
const fs = require('fs'), path = require('path'), http = require('http');
const RAIZ = path.join(__dirname, '..', '..');
const WEB = path.join(RAIZ, 'web');
const CATEGORIAS = JSON.parse(fs.readFileSync(path.join(RAIZ, 'skill', 'categorias.json'), 'utf8'));
const TOKEN = 'token-falso';
const PIN = '1234';

let chromium;
try { ({ chromium } = require('playwright')); }
catch (e) { console.error('Falta Playwright. Una vez: cd tests && npm install && npx playwright install chromium'); process.exit(2); }

// ───────────── RPC permitidas: las que definen las migraciones del paquete ─────────────
function rpcPermitidas() {
  const dir = path.join(RAIZ, 'supabase', 'migrations');
  const set = new Set();
  for (const f of fs.readdirSync(dir).filter(x => x.endsWith('.sql'))) {
    for (const m of fs.readFileSync(path.join(dir, f), 'utf8').matchAll(/function\s+public\.(bm_[a-z0-9_]+)/gi)) set.add(m[1].toLowerCase());
  }
  // las que suma el circuito (si una migración todavía no las define, igual se aceptan)
  ['bm_seguimiento', 'bm_archivar_pin', 'bm_trabadas', 'bm_vuelo_anotar', 'bm_vuelo_cerrar', 'bm_acciones_lista', 'bm_accion_hecha', 'bm_accion_marcar', 'bm_reemplazar'].forEach(x => set.add(x));
  return [...set].sort();
}

// ───────────── servidor ─────────────
const TIPOS = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.webmanifest': 'application/manifest+json' };
const CONFIG_JS = 'window.BOTONERA_CONFIG = { supabaseUrl: "https://botonera-e2e.example.test", supabaseKey: "sb_publishable_e2e" };';
let server, PORT, browser;
function levantar() {
  server = http.createServer((req, res) => {
    const p = decodeURIComponent(req.url.split('?')[0]);
    if (p === '/config.js') { res.writeHead(200, { 'content-type': TIPOS['.js'] }); return res.end(CONFIG_JS); }
    const f = path.join(WEB, p === '/' ? 'index.html' : p);
    if (!f.startsWith(WEB) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end('no'); }
    res.writeHead(200, { 'content-type': TIPOS[path.extname(f)] || 'application/octet-stream' });
    fs.createReadStream(f).pipe(res);
  });
  return new Promise(r => server.listen(0, '127.0.0.1', () => { PORT = server.address().port; r(); }));
}
async function cerrar() {
  try { if (browser) await browser.close(); } catch (e) {}
  browser = null;
  try { if (server) await new Promise(r => server.close(r)); } catch (e) {}
}
const url = () => `http://127.0.0.1:${PORT}/`;
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ───────────── datos inventados ─────────────
const ahora = Date.now();
const iso = msAtras => new Date(ahora - msAtras).toISOString();
const CAT = id => { const c = CATEGORIAS.find(x => x.id === id); return { id: c.id, nombre: c.nombre, color: c.color, icono: c.icono, orden: CATEGORIAS.indexOf(c), privada: !!c.privada }; };
function fila(clave, titulo, items, extra) {
  const e = Object.assign({ estado: 'abierta', created_at: iso(600000), updated_at: iso(300000), session_id: 'local_sesion-e2e', sesion_titulo: 'Sesión de prueba' }, extra || {});
  const row = { clave, titulo, estado: e.estado, session_id: e.session_id, sesion_titulo: e.sesion_titulo, skill: 'botonera', proyecto: null, n_items: items.length,
    created_at: e.created_at, updated_at: e.updated_at, decided_at: e.decided_at || null, received_at: e.received_at || null, applied_at: e.applied_at || null,
    esperando_at: e.esperando_at || null, espera_motivo: e.espera_motivo || null, snooze_hasta: e.snooze_hasta || null };
  if (e.trab_desde) { row.trab_desde = e.trab_desde; row.trab_recibida = !!e.trab_recibida; }
  return { row, html: '<html></html>', respuesta_texto: e.respuesta_texto || null, datos: { titulo, clave, categoria: CAT(e.cat || 'trabajo'), items } };
}
function card(n, titulo, extra) {
  return Object.assign({ n, titulo, contexto: `Contexto de prueba de «${titulo}».`, reco: 'va', reco_motivo: 'Motivo de prueba.', accion_va: 'Hacerlo', accion_no_va: 'Dejarlo',
    si_no_decidis: 'Queda como está.', impacto: { positivo: 'Algo mejora.', negativo: 'Algo cuesta.' } }, extra || {});
}
const cards = (k, n) => Array.from({ length: n }, (_, i) => card(i + 1, `Card ${k}${i + 1}`));
const PNG = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';

function escenario(nombre, extra) {
  const base = { filas: [], errores: [], acciones: { items: [] }, seguimiento: { vuelo: [], pedidos: [], escucha_at: null, activos: 0 }, pin: PIN };
  if (nombre === 'simple') {   // dos mazos de «Trabajo» (3 + 2 cards) y uno de «Casa» (1)
    const casa = fila('e2e-casa', 'Mazo de casa', cards('c', 1), { cat: 'casa' });
    base.filas = [fila('e2e-trabajo-a', 'Mazo de trabajo A', cards('a', 3)), fila('e2e-trabajo-b', 'Mazo de trabajo B', cards('b', 2)), casa];
  } else if (nombre === 'card') {   // 1 mazo de 4 cards: detalle+imagen, lisa con regla, «ya no aplica», y una para «Ahora no»
    base.filas = [fila('e2e-card', 'Mazo de la card', [
      card(1, 'Subir el precio de los envíos', { detalle: 'El detalle plegado: cuánto cuesta hoy cada envío y desde cuándo.', imagen: { src: PNG, alt: 'Captura de prueba' }, antecedentes: ['Se subió hace un año.'] }),
      card(2, 'Archivar los pedidos viejos'),
      card(3, 'Esta card ya no aplica', { reemplazada_por: 'e2e-card#4' }),
      card(4, 'Cambiar el proveedor de mails')])];
  } else if (nombre === 'snooze') {   // A (3 cards, la más vieja), B (2 cards) y una dormida
    base.filas = [fila('e2e-snz-a', 'Botonera A', cards('a', 3), { created_at: iso(7200000) }), fila('e2e-snz-b', 'Botonera B', cards('b', 2), { created_at: iso(3600000) }),
      fila('e2e-snz-d', 'Botonera dormida', cards('d', 2), { snooze_hasta: new Date(ahora + 6 * 3600e3).toISOString() })];
  } else if (nombre === 'sesiones') {   // tandas ya mandadas en varios estados + «En vuelo»
    const H = 3600e3;
    base.filas = [
      fila('e2e-recibida', 'Cambiar el precio', cards('r', 1), { estado: 'recibida', received_at: iso(5 * 60e3), decided_at: iso(10 * 60e3), trab_desde: iso(5 * 60e3), trab_recibida: true, updated_at: iso(5 * 60e3) }),
      fila('e2e-decidida', 'Revisar los avisos', cards('d', 1), { estado: 'decidida', decided_at: iso(40 * 60e3), trab_desde: iso(40 * 60e3), updated_at: iso(40 * 60e3) }),
      fila('e2e-esperando', 'Aprobar el texto', cards('e', 1), { estado: 'esperando', esperando_at: iso(2 * H), espera_motivo: 'Falta tu OK', updated_at: iso(2 * H) }),
      fila('e2e-aplicada', 'Ordenar la carpeta', cards('a', 1), { estado: 'aplicada', applied_at: iso(2 * H), updated_at: iso(2 * H) }),
      fila('e2e-vieja', 'Una tanda de hace una semana', cards('v', 1), { estado: 'archivada', updated_at: iso(7 * 24 * H) }),
      fila('e2e-trabada', 'Tanda trabada', cards('t', 1), { estado: 'recibida', received_at: iso(30 * H), decided_at: iso(31 * H), trab_desde: iso(30 * H), trab_recibida: true, updated_at: iso(30 * H) }),
      fila('bot-pausa', 'Tanda de un bot', cards('b', 1), { estado: 'decidida', decided_at: iso(5 * 24 * H), trab_desde: iso(5 * 24 * H), updated_at: iso(5 * 24 * H), session_id: 'bot-x' })];
    base.seguimiento.vuelo = [{ session_id: 'local_vuelo-1', titulo: 'Armando el informe', que_hace: 'Ordena los números', proximo: 'Publicar la card', estado: 'abierta', updated_at: iso(4 * 60e3), desde: iso(30 * 60e3) }];
  } else if (nombre === 'bloqueos') {   // obstáculos abiertos + trabada + errores
    const base2 = escenario('sesiones');
    base.filas = base2.filas;
    base.acciones = { items: [
      { origen: 'item', ref: '7', titulo: 'Pegar la llave de la API', por_que: 'Sin la llave no se puede publicar.', de: 'Sesión de prueba', fecha: iso(26 * 3600e3), frena: 'la publicación del informe', link: 'https://example.com/llaves', comando: '', estado: 'abierta', comentario: '' },
      { origen: 'item', ref: '8', titulo: 'Correr la migración', por_que: 'La base no tiene la tabla.', de: 'Sesión de prueba', fecha: iso(3 * 3600e3), frena: '', link: '', comando: 'supabase db push', estado: 'abierta', comentario: '' }] };
    base.errores = [{ id: 1, tipo: 'tarea', origen_id: 'tarea-1', titulo: 'Reporte semanal', motivo: 'Límite de uso alcanzado', ocurrio_at: iso(13 * 3600e3) },
      { id: 2, tipo: 'sesion', origen_id: 'e2e-vieja', titulo: 'Tanda archivada con respuesta sin aplicar', motivo: 'La sesión ya no está', ocurrio_at: iso(3 * 3600e3) }];
  } else if (nombre === 'completo') {   // todo junto: mazos abiertos + sesiones + bloqueos + errores + vuelo
    const s = escenario('simple'), b = escenario('bloqueos'), g = escenario('sesiones');
    base.filas = s.filas.concat(b.filas); base.acciones = b.acciones; base.errores = b.errores; base.seguimiento = g.seguimiento;
  } else if (nombre !== 'vacio') throw new Error('escenario desconocido: ' + nombre);
  return Object.assign(base, extra || {});
}

// ───────────── el stub que reemplaza a supabase-js (corre dentro de la página) ─────────────
function stub(FX, TOKEN) {
  const filas = FX.filas;
  window.__envios = []; window.__rpcs = []; window.__visto = []; window.__archivadas = []; window.__acciones = [];
  const clonar = o => JSON.parse(JSON.stringify(o));
  const ok = d => ({ data: d, error: null });
  const err = m => ({ data: null, error: { message: m } });
  const buscar = c => filas.filter(f => f.row.clave === c)[0] || null;
  let fallos = 0;
  window.__arnes = { falla: {}, retraso: {}, tokenMalo: false, filas, FX };
  function manejar(nombre, a) {
    a = a || {};
    if (window.__arnes.falla[nombre]) return err(window.__arnes.falla[nombre]);
    if (nombre === 'bm_entrar') {
      if (FX.bloqueo) return ok(FX.bloqueo);
      if (a.p_pin === FX.pin) return ok({ ok: true, token: TOKEN });
      fallos++;
      return ok({ ok: false, motivo: 'pin_incorrecto', fallos });
    }
    if (nombre === 'bm_salir') return ok(null);
    if (a.p_token !== TOKEN || window.__arnes.tokenMalo) return err('token inválido');
    if (nombre === 'bm_errores_lista') return ok(clonar(FX.errores));
    if (nombre === 'bm_error_visto') { const n = FX.errores.length; FX.errores = FX.errores.filter(e => e.id !== a.p_id); window.__visto.push(a.p_id); return ok(FX.errores.length < n); }
    if (nombre === 'bm_lista') return ok(filas.map(f => clonar(f.row)));
    if (nombre === 'bm_fila') {
      const f = buscar(a.p_clave); if (!f) return err('no existe');
      const r = clonar(f.row); r.html = f.html; r.datos = clonar(f.datos); r.respuesta_texto = f.respuesta_texto; r.resumen_aplicado = null; return ok(r);
    }
    if (nombre === 'bm_decidir_pin') {
      window.__envios.push(clonar(a));
      const g = buscar(a.p_clave); if (!g) return err('no existe');
      if (g.row.estado !== 'abierta') return ok('ya estaba ' + g.row.estado);
      g.row.estado = 'decidida'; g.row.decided_at = g.row.updated_at = new Date().toISOString(); g.respuesta_texto = a.p_respuesta;
      return ok('decidida');
    }
    if (nombre === 'bm_snoozear') {
      const g = buscar(a.p_clave); if (!g) return ok('no_existe');
      if (g.row.estado !== 'abierta') return ok(g.row.estado);
      g.row.snooze_hasta = a.p_hasta; return ok('abierta');
    }
    if (nombre === 'bm_despertar') {
      const g = buscar(a.p_clave); if (!g) return ok('no_existe');
      if (g.row.estado !== 'abierta') return ok(g.row.estado);
      g.row.snooze_hasta = new Date().toISOString(); return ok('abierta');
    }
    if (nombre === 'bm_seguimiento') return ok(clonar(FX.seguimiento));
    if (nombre === 'bm_archivar_pin') {
      window.__archivadas.push(a.p_clave);
      const g = buscar(a.p_clave); if (!g) return err('clave inexistente');
      if (['decidida', 'recibida', 'esperando'].indexOf(g.row.estado) < 0) return ok({ anterior: g.row.estado, cambiado: false });
      const ant = g.row.estado; g.row.estado = 'archivada'; g.row.updated_at = new Date().toISOString();
      return ok({ anterior: ant, cambiado: true });
    }
    if (nombre === 'bm_acciones_lista') return ok(clonar(FX.acciones));
    if (nombre === 'bm_accion_hecha') {
      window.__acciones.push({ rpc: nombre, ref: a.p_ref, comentario: a.p_comentario });
      const i = FX.acciones.items.findIndex(x => x.origen === a.p_origen && x.ref === a.p_ref);
      if (i < 0) return ok({ resultado: 'ya no esta trabado' });
      FX.acciones.items.splice(i, 1); return ok({ resultado: 'en_cola' });
    }
    if (nombre === 'bm_accion_marcar') {
      window.__acciones.push({ rpc: nombre, ref: a.p_ref, estado: a.p_estado, comentario: a.p_comentario });
      const x = FX.acciones.items.find(y => y.origen === a.p_origen && y.ref === a.p_ref); if (!x) return err('no existe');
      x.estado = a.p_estado; x.comentario = a.p_comentario || '';
      return ok({ origen: 'item', ref: a.p_ref, estado: x.estado, comentario: x.comentario });
    }
    if (nombre === 'bm_push_clave') return ok(null);
    if (nombre === 'bm_push_suscribir') return ok(true);
    return err('rpc desconocida: ' + nombre);
  }
  window.supabase = { createClient() {
    return { rpc(nombre, args) {
      window.__rpcs.push({ nombre, params: JSON.parse(JSON.stringify(args || {})) });
      const demora = 15 + (window.__arnes.retraso[nombre] || 0);
      return new Promise(res => setTimeout(() => res(manejar(nombre, args)), demora));
    } };
  } };
}

// ───────────── contexto del navegador ─────────────
// opciones: ancho, alto, escritorio (sin isMobile), sinTouch (ratón puro: hover y pointer fine; usar click en vez de tap), sinToken (arranca en la pantalla del PIN), ahora (ISO: fija el reloj de la página)
async function ctxNuevo(FX, op) {
  op = op || {};
  if (!browser) browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: op.ancho || 390, height: op.alto || 844 }, hasTouch: !op.sinTouch, isMobile: !op.escritorio, deviceScaleFactor: 1 });
  // terceros: las fuentes de Google se contestan vacías (lo único que la web pide afuera); cualquier otro host se corta y queda anotado
  await ctx.route(u => !['127.0.0.1', 'localhost'].includes(u.hostname), r => {
    const h = new URL(r.request().url()).hostname; ctx.terceros = ctx.terceros || new Set(); ctx.terceros.add(h);
    if (h === 'fonts.googleapis.com') return r.fulfill({ contentType: 'text/css', body: '' });
    if (h === 'fonts.gstatic.com') return r.fulfill({ contentType: 'font/woff2', body: '' });
    return r.abort();
  });
  await ctx.route(/\/vendor\/confetti\.min\.js/, r => r.fulfill({ contentType: 'text/javascript', body: 'window.confetti = function(){}; window.confetti.create = function(){ var f = function(){}; f.reset = function(){}; return f; };' }));
  await ctx.route(/\/vendor\/supabase\.min\.js/, r => r.fulfill({ contentType: 'text/javascript',
    body: `(${stub.toString()})(${JSON.stringify(FX).replace(/</g, '\\u003c')}, ${JSON.stringify(TOKEN)});` }));
  if (!op.sinToken) await ctx.addInitScript(t => { try { localStorage.setItem('bm-token', t); } catch (e) {} }, TOKEN);
  const page = await ctx.newPage();
  page.errores = []; page.consola = [];
  page.on('pageerror', e => page.errores.push(String(e.message)));
  page.on('console', m => { if (m.type() === 'error') page.consola.push(m.text()); });
  return { ctx, page };
}

// ───────────── helpers ─────────────
async function libre(page) {
  await page.waitForFunction(() => { const s = window.__swipe && window.__swipe(); return !s || !s.ocupado; }, null, { timeout: 8000 });
  await sleep(120);
}
async function tap(page, sel) { await page.locator(sel).first().tap(); }
async function textos(page, sel) { return page.locator(sel).allInnerTexts(); }
// home -> fila de una categoría (con una sola botonera abre el mazo; con varias, tarjetas) -> «Empezar a decidir»
async function entrarAlMazo(page, selFila) {
  await page.goto(url());
  await page.waitForSelector('.hrow', { timeout: 10000 });
  await page.tap(selFila || '.hrow');
  if (await page.locator('.htanda').first().isVisible().catch(() => false)) await page.tap('.htanda');
  await page.waitForSelector('[data-a="empezar"]', { timeout: 8000 });
  await page.tap('[data-a="empezar"]');
  await page.waitForSelector('.sw-act, .sw-op', { timeout: 8000 });
  await libre(page);
}
async function frente(page) { return page.evaluate(() => { const h = document.querySelector('#sw-card h2'); return h ? h.innerText.trim() : null; }); }
async function enviar(page) {
  await sleep(300);
  if (await page.locator('[data-a="enviar"]:visible').count()) await tap(page, '[data-a="enviar"]');
  else await tap(page, '[data-a="terminar"]');
  await page.waitForFunction(() => window.__envios && window.__envios.length > 0, null, { timeout: 8000 });
  await sleep(300);
  return page.evaluate(() => window.__envios[window.__envios.length - 1].p_respuesta);
}
async function sinScrollHorizontal(page) { return page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1 && document.body.scrollWidth <= document.body.clientWidth + 1); }
async function barraVisible(page) { return page.evaluate(() => { const n = document.getElementById('tabs'); if (!n) return false; const r = n.getBoundingClientRect(); return r.height > 0 && r.bottom <= window.innerHeight + 1 && getComputedStyle(n).display !== 'none'; }); }

// ───────────── reporte ─────────────
function nuevoReporte(nombre) {
  const RES = [];
  return {
    reg(caso, titulo, ok, detalle) { RES.push({ caso, titulo, ok: !!ok }); console.log(`[${caso}] ${ok ? 'PASA' : 'FALLA'} · ${titulo}${detalle ? '\n    ' + detalle : ''}`); },
    fin() { const p = RES.filter(r => r.ok).length; console.log(`\n${nombre}: ${p} pasan / ${RES.length - p} fallan`); return RES.length - p === 0; },
  };
}

module.exports = { levantar, cerrar, url, sleep, escenario, fila, card, cards, CAT, ctxNuevo, libre, tap, textos, entrarAlMazo, frente, enviar, sinScrollHorizontal, barraVisible,
  nuevoReporte, rpcPermitidas, TOKEN, PIN, iso, ahora };

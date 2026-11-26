/* E2E de Editar, +info, el contador de los mazos y la fila «Con error» de la web, con Playwright.
 * Regresión: el caso 8 cubre «Va después de editar perdía los cambios» y el 10b el comentario vacío en una card
 * sin campos. Correrlo antes de subir cualquier cambio a web/index.html: todos tienen que dar PASA.
 *
 * No necesita Supabase: sirve web/ con un servidor propio, le inyecta un config.js de mentira y reemplaza la
 * librería de Supabase por un stub que contesta las RPC (bm_lista, bm_fila, bm_decidir_pin, bm_errores_lista…)
 * con tandas de prueba. Nada sale a la red: los pedidos a otros hosts se cortan.
 *
 * Una vez:   cd tests && npm install && npx playwright install chromium
 * Uso:       node tests/e2e-editar.js [casos, ej. 1,8,10]
 * Salida:    una línea por caso en la consola; las capturas y results.md van a $E2E_OUT (por default, una carpeta
 *            temporal). Sale con 1 si algún caso no da PASA.
 */
let chromium;
try { ({ chromium } = require('playwright')); }
catch (e) {
  console.error('Falta Playwright. Una vez: cd tests && npm install && npx playwright install chromium');
  process.exit(2);
}
const fs = require('fs'), path = require('path'), http = require('http'), os = require('os');

const WEB = path.join(__dirname, '..', 'web');
const OUT = process.env.E2E_OUT || fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-editar-'));
const SOLO = (process.argv[2] || '').split(',').filter(Boolean);
const TOKEN = 'token-falso';
const CATEGORIAS = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'skill', 'categorias.json'), 'utf8'));
const CAT = id => { const c = CATEGORIAS.find(x => x.id === id); return { id: c.id, nombre: c.nombre, color: c.color, icono: c.icono, orden: CATEGORIAS.indexOf(c), privada: !!c.privada }; };

// ───────────────────────── servidor de web/ ─────────────────────────
const TIPOS = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.webmanifest': 'application/manifest+json' };
const CONFIG_JS = 'window.BOTONERA_CONFIG = { supabaseUrl: "https://botonera-e2e.example.test", supabaseKey: "sb_publishable_e2e" };';
let server, PORT;
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

// ───────────────────────── fixtures ─────────────────────────
const T1 = 'Subir el precio de los envíos';
const T2 = 'Archivar los pedidos viejos';
const ahora = Date.now();
const iso = msAtras => new Date(ahora - msAtras).toISOString();
function fila(clave, titulo, items, extra) {
  const row = { clave, titulo, estado: 'abierta', session_id: 'sesion-e2e', sesion_titulo: 'Prueba e2e', skill: 'botonera', proyecto: null, n_items: items.length,
    created_at: iso(600000), updated_at: iso(300000), decided_at: null, received_at: null, applied_at: null, esperando_at: null, espera_motivo: null };
  return { row, html: '<html></html>', respuesta_texto: null, datos: Object.assign({ titulo, clave, categoria: CAT('trabajo'), items }, extra || {}) };
}
function card(n, titulo, extra) {
  return Object.assign({ n, titulo, contexto: `Contexto de prueba de «${titulo}».`, reco: 'va', reco_motivo: 'Motivo de prueba.', accion_va: 'Hacerlo', accion_no_va: 'Dejarlo',
    impacto: { positivo: 'Algo mejora.', negativo: 'Algo cuesta.' } }, extra || {});
}
function fixture(nombre) {
  if (nombre === 'editar' || nombre === 'editar-opcion') {
    const campos = [{ id: 'precio', etiqueta: 'Precio del envío (ARS)', valor: 3500, tipo: 'numero' },
      { id: 'desde', etiqueta: 'Desde', valor: '2026-11-09', tipo: 'fecha' },
      { id: 'alcance', etiqueta: 'A quiénes', valor: 'Pedidos chicos', tipo: 'texto' }];
    if (nombre === 'editar-opcion') campos.push({ id: 'canal', etiqueta: 'Canal del aviso', valor: 'Mail', tipo: 'opcion', opciones: ['Mail', 'WhatsApp', 'SMS'] });
    return { filas: [fila('e2e-editar', 'Prueba de Editar', [
      card(1, T1, { accion_va: 'Subí el precio', accion_no_va: 'Dejalo como está', contexto: 'Los envíos cuestan más desde octubre.', campos }),
      card(2, T2, { accion_va: 'Archivalos', accion_no_va: 'Dejalos', contexto: 'Hay pedidos cerrados de hace más de un año.' })])], errores: [] };
  }
  if (nombre === 'opciones') {
    return { filas: [fila('e2e-opciones', 'Prueba de opciones', [
      card(1, 'Elegir el canal para los avisos', { reco: 'mail', accion_va: undefined, accion_no_va: undefined,
        opciones: [{ id: 'mail', etiqueta: 'Mail' }, { id: 'whatsapp', etiqueta: 'Mensaje de WhatsApp' }, { id: 'sms', etiqueta: 'SMS' }] }),
      card(2, 'Dónde publicar la novedad', { reco: 'blog', accion_va: undefined, accion_no_va: undefined, varias: true,
        opciones: [{ id: 'blog', etiqueta: 'Blog' }, { id: 'redes', etiqueta: 'Redes' }] })])], errores: [] };
  }
  if (nombre === 'home') {   // dos mazos de «Trabajo» (3 + 2 cards), uno de «Casa» (1) y tres errores sin ver
    const cards = (k, n) => Array.from({ length: n }, (_, i) => card(i + 1, `Card ${k}${i + 1}`));
    const casa = fila('e2e-casa', 'Mazo de casa', cards('c', 1));
    casa.datos.categoria = CAT('casa');
    return { filas: [fila('e2e-trabajo-a', 'Mazo de trabajo A', cards('a', 3)), fila('e2e-trabajo-b', 'Mazo de trabajo B', cards('b', 2)), casa],
      errores: [{ id: 1, tipo: 'tarea', origen_id: 'tarea-1', titulo: 'Reporte semanal', motivo: 'Límite de uso alcanzado', ocurrio_at: new Date(ahora - 13 * 3600e3).toISOString() },
        { id: 2, tipo: 'sesion', origen_id: 'e2e-vieja', titulo: 'Tanda archivada con tu respuesta sin aplicar: e2e-vieja', motivo: 'La sesión ya no está', ocurrio_at: new Date(ahora - 3 * 3600e3).toISOString() },
        { id: 3, tipo: 'tarea', origen_id: 'tarea-2', titulo: 'Copia de seguridad', motivo: 'Token vencido', ocurrio_at: new Date(ahora - 50 * 60e3).toISOString() }] };
  }
  throw new Error('fixture desconocida: ' + nombre);
}

// El stub que reemplaza a supabase-js: corre dentro de la página y contesta las RPC con las filas del fixture.
function stub(FX, TOKEN) {
  const filas = FX.filas;
  window.__envios = [];
  window.__visto = [];
  const clonar = o => JSON.parse(JSON.stringify(o));
  const ok = d => ({ data: d, error: null });
  const buscar = c => filas.filter(f => f.row.clave === c)[0] || null;
  function manejar(nombre, a) {
    a = a || {};
    if (nombre === 'bm_entrar') return ok({ ok: true, token: TOKEN });
    if (nombre === 'bm_salir') return ok(null);
    if (a.p_token !== TOKEN) return { data: null, error: { message: 'token invalido' } };
    if (nombre === 'bm_acciones_lista') return ok({ items: [] });
    if (nombre === 'bm_seguimiento') return ok({ vuelo: [], pedidos: [], escucha_at: null, activos: 0 });
    if (nombre === 'bm_errores_lista') return ok(clonar(FX.errores));
    if (nombre === 'bm_error_visto') {
      const antes = FX.errores.length;
      FX.errores = FX.errores.filter(e => e.id !== a.p_id);
      window.__visto.push(a.p_id);
      return ok(FX.errores.length < antes);
    }
    if (nombre === 'bm_lista') return ok(filas.map(f => clonar(f.row)));
    if (nombre === 'bm_fila') {
      const f = buscar(a.p_clave); if (!f) return { data: null, error: { message: 'no existe' } };
      const r = clonar(f.row);
      r.html = f.html; r.datos = clonar(f.datos); r.respuesta_texto = f.respuesta_texto; r.resumen_aplicado = null;
      return ok(r);
    }
    if (nombre === 'bm_decidir_pin') {
      window.__envios.push(clonar(a));
      const g = buscar(a.p_clave); if (!g) return { data: null, error: { message: 'no existe' } };
      if (g.row.estado !== 'abierta') return ok('ya estaba ' + g.row.estado);
      g.row.estado = 'decidida'; g.row.decided_at = g.row.updated_at = new Date().toISOString();
      g.respuesta_texto = a.p_respuesta;
      return ok('decidida');
    }
    return { data: null, error: { message: 'rpc desconocida: ' + nombre } };
  }
  window.supabase = { createClient() {
    return { rpc(nombre, args) { return new Promise(res => setTimeout(() => res(manejar(nombre, args)), 15)); } };
  } };
}

// ───────────────────────── helpers de la prueba ─────────────────────────
let browser;
async function ctxNuevo(fx) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true, deviceScaleFactor: 2 });
  // todo lo que no es el servidor local se corta; las dos librerías de /vendor/ se reemplazan
  await ctx.route(u => !['127.0.0.1', 'localhost'].includes(u.hostname), r => r.abort());
  await ctx.route(/\/vendor\/confetti\.min\.js/, r => r.fulfill({ contentType: 'text/javascript', body: 'window.confetti = function(){};' }));
  await ctx.route(/\/vendor\/supabase\.min\.js/, r => r.fulfill({ contentType: 'text/javascript',
    body: `(${stub.toString()})(${JSON.stringify(fixture(fx)).replace(/</g, '\\u003c')}, ${JSON.stringify(TOKEN)});` }));
  await ctx.addInitScript(t => { try { localStorage.setItem('bm-token', t); } catch (e) {} }, TOKEN);
  const page = await ctx.newPage();
  page.errores = [];
  page.on('pageerror', e => page.errores.push(String(e.message)));
  return { ctx, page };
}
const URL_WEB = () => `http://127.0.0.1:${PORT}/`;
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function shot(page, nombre) { await page.screenshot({ path: path.join(OUT, nombre + '.png') }); }
async function libre(page) { // espera a que no haya animación ni gesto
  await page.waitForFunction(() => { const s = window.__swipe && window.__swipe(); return !s || !s.ocupado; }, null, { timeout: 8000 });
  await sleep(120);
}
// home -> fila de la categoría (con una sola botonera abre el mazo) -> card de contexto -> «Empezar a decidir». Deja la card 1 al frente.
async function entrar(page) {
  await page.goto(URL_WEB());
  await page.waitForSelector('.hrow', { timeout: 10000 });
  await page.tap('.hrow');
  await page.waitForSelector('[data-a="empezar"]', { timeout: 8000 });
  await page.tap('[data-a="empezar"]');
  await page.waitForSelector('.sw-act, .sw-op', { timeout: 8000 });
  await libre(page);
}
async function frente(page) { return page.evaluate(() => { const h = document.querySelector('#sw-card h2'); return h ? h.innerText.trim() : null; }); }
async function tap(page, sel) { await page.locator(sel).first().tap(); }
async function esperarHoja(page) { await page.waitForSelector('.sw-sheet-in', { timeout: 5000 }); await sleep(150); }
async function abrirEditar(page) { await tap(page, '[data-a="editar"]'); await esperarHoja(page); }
// swipe real con eventos táctiles (CDP)
async function swipe(page, dir) {
  const cdp = await page.context().newCDPSession(page);
  const r = await page.evaluate(() => { const b = document.querySelector('#sw-card').getBoundingClientRect(); return { x: b.x + b.width / 2, y: b.y + b.height / 2 }; });
  const dx = dir === 'right' ? 220 : dir === 'left' ? -220 : 0, dy = dir === 'up' ? -260 : 0;
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: r.x, y: r.y }] });
  for (let i = 1; i <= 10; i++) {
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: r.x + dx * i / 10, y: r.y + dy * i / 10 }] });
    await sleep(16);
  }
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await cdp.detach();
  await sleep(300);
  await libre(page);
}
async function marcas(page) { return page.evaluate(() => JSON.parse(JSON.stringify(window.__swipe().marcas))); }
// cierra el envío y devuelve el p_respuesta EXACTO que recibió bm_decidir_pin
async function enviar(page) {
  await sleep(300);
  if (await page.locator('[data-a="enviar"]:visible').count()) await tap(page, '[data-a="enviar"]');
  else await tap(page, '[data-a="terminar"]');
  await page.waitForFunction(() => window.__envios && window.__envios.length > 0, null, { timeout: 8000 });
  await sleep(300);
  return page.evaluate(() => window.__envios[window.__envios.length - 1].p_respuesta);
}
function linea(resp, n) { return (resp || '').split('\n').find(l => l.startsWith(n + '. ')) || '(no hay línea ' + n + ')'; }
async function textoBoton(page, sel) { return (await page.locator(sel).first().innerText()).trim(); }
async function setCampo(page, sel, val) {
  const el = page.locator(sel);
  if ((await el.evaluate(e => e.tagName)) === 'SELECT') await el.selectOption(val);
  else await el.fill(String(val)); // en input[type=date] fill(YYYY-MM-DD) dispara input+change como el selector nativo
  await sleep(120);
}

const RES = [];
function reg(r) { RES.push(r); console.log(`\n[${r.caso}] ${r.estado} · ${r.titulo}\n  esperado: ${r.esperado}\n  obtenido: ${r.obtenido}${r.nota ? '\n  nota: ' + r.nota : ''}`); }
const veredicto = ok => ok ? 'PASA' : 'FALLA';

const E1 = `1. va con cambios · ${T1} → Subí el precio · campos: `;
const L1VA = `1. va · ${T1} → Subí el precio`;

const CASOS = {
  '1': async () => {
    const { ctx, page } = await ctxNuevo('editar');
    try {
      await entrar(page);
      await abrirEditar(page);
      await setCampo(page, '#sw-f0', 4200);
      const btn = await textoBoton(page, '[data-a="ed-listo"]');
      await shot(page, 'caso-01-hoja');
      await tap(page, '[data-a="ed-listo"]');
      await libre(page);
      const f2 = await frente(page);
      await tap(page, '[data-a="no"]'); await libre(page);   // la card 2 se decide «No va» para cerrar el mazo
      const resp = await enviar(page);
      const esp = E1 + 'precio=4200 (antes 3500)', ob = linea(resp, 1);
      reg({ caso: 1, titulo: 'Número 3500 → 4200, «Va con estos cambios»', esperado: esp, obtenido: ob, estado: veredicto(ob === esp && btn === 'Va con estos cambios'),
        nota: `botón de la hoja: «${btn}»; siguiente card: ${f2}` });
    } finally { await ctx.close(); }
  },
  '2': async () => {
    const { ctx, page } = await ctxNuevo('editar');
    try {
      await entrar(page);
      await abrirEditar(page);
      await setCampo(page, '#sw-f1', '2026-11-16');
      const antes = await page.locator('.sw-f[data-fid="desde"] .sw-fnota').innerText();
      await tap(page, '[data-a="ed-listo"]'); await libre(page);
      await tap(page, '[data-a="no"]'); await libre(page);
      const resp = await enviar(page);
      const esp = E1 + 'desde=2026-11-16 (antes 2026-11-09)', ob = linea(resp, 1);
      reg({ caso: 2, titulo: 'Fecha 2026-11-09 → 2026-11-16 con el input nativo', esperado: esp, obtenido: ob, estado: veredicto(ob === esp), nota: `nota «Antes»: ${antes.replace(/\s+/g, ' ')}` });
    } finally { await ctx.close(); }
  },
  '3': async () => {
    const { ctx, page } = await ctxNuevo('editar');
    try {
      await entrar(page);
      await abrirEditar(page);
      await setCampo(page, '#sw-f2', 'Todos los pedidos');
      await tap(page, '[data-a="ed-listo"]'); await libre(page);
      await tap(page, '[data-a="no"]'); await libre(page);
      const resp = await enviar(page);
      const esp = E1 + 'alcance=Todos los pedidos (antes Pedidos chicos)', ob = linea(resp, 1);
      reg({ caso: 3, titulo: 'Texto «Pedidos chicos» → «Todos los pedidos»', esperado: esp, obtenido: ob, estado: veredicto(ob === esp) });
    } finally { await ctx.close(); }
  },
  '4': async () => {
    const { ctx, page } = await ctxNuevo('editar-opcion');
    try {
      await entrar(page);
      await abrirEditar(page);
      const ops = await page.locator('#sw-f3 option').allInnerTexts();
      await setCampo(page, '#sw-f3', 'SMS');
      await tap(page, '[data-a="ed-listo"]'); await libre(page);
      await tap(page, '[data-a="no"]'); await libre(page);
      const resp = await enviar(page);
      const esp = E1 + 'canal=SMS (antes Mail)', ob = linea(resp, 1);
      reg({ caso: 4, titulo: 'Campo de tipo opcion: Mail → SMS', esperado: esp, obtenido: ob, estado: veredicto(ob === esp && ops.join() === 'Mail,WhatsApp,SMS'), nota: 'opciones del select: ' + ops.join(', ') });
    } finally { await ctx.close(); }
  },
  '5': async () => {
    const { ctx, page } = await ctxNuevo('editar');
    try {
      await entrar(page);
      await abrirEditar(page);
      await setCampo(page, '#sw-f0', 4500);
      await setCampo(page, '#sw-f1', '2026-11-16');
      await page.locator('#sw-com').fill('Solo hasta fin de mes.'); await sleep(150);
      const resumen = (await page.locator('.sw-resumen').innerText()).trim();
      await tap(page, '[data-a="ed-listo"]'); await libre(page);
      await tap(page, '[data-a="no"]'); await libre(page);
      const resp = await enviar(page);
      const esp = E1 + 'precio=4500 (antes 3500); desde=2026-11-16 (antes 2026-11-09) · comentario: Solo hasta fin de mes.', ob = linea(resp, 1);
      reg({ caso: 5, titulo: 'Dos campos cambiados + comentario', esperado: esp, obtenido: ob, estado: veredicto(ob === esp && /^2 cambios/.test(resumen)), nota: `resumen de la hoja: «${resumen}»` });
    } finally { await ctx.close(); }
  },
  '6': async () => {
    const { ctx, page } = await ctxNuevo('editar');
    try {
      await entrar(page);
      await abrirEditar(page);
      await setCampo(page, '#sw-f0', 4200);
      const btnCambiado = await textoBoton(page, '[data-a="ed-listo"]');
      const cambioVis = await page.evaluate(() => { const w = document.querySelector('.sw-f[data-fid="precio"]'); const t = w.querySelector('.sw-tag'), n = w.querySelector('.sw-fnota');
        const vis = e => { const cs = getComputedStyle(e), b = e.getBoundingClientRect(); return cs.display !== 'none' && cs.visibility !== 'hidden' && b.width > 0 && b.height > 0; };
        return { clase: w.classList.contains('cambio'), tag: vis(t), nota: vis(n), re: vis(w.querySelector('.sw-fre')), notaTxt: n.innerText.replace(/\s+/g, ' ') }; });
      await shot(page, 'caso-06-cambiado');
      await tap(page, '.sw-f[data-fid="precio"] [data-a="ed-volver"]'); await sleep(200);
      const val = await page.locator('#sw-f0').inputValue();
      const btn = await textoBoton(page, '[data-a="ed-listo"]');
      const nCambio = await page.locator('.sw-f.cambio').count();
      await tap(page, '[data-a="ed-listo"]'); await libre(page);
      await tap(page, '[data-a="no"]'); await libre(page);
      const resp = await enviar(page);
      const ob = linea(resp, 1);
      reg({ caso: 6, titulo: 'Cambiar y «Volver al original»', esperado: `botón «Va como está», valor 3500 y línea \`${L1VA}\``, obtenido: ob,
        estado: veredicto(ob === L1VA && btn === 'Va como está' && val === '3500' && nCambio === 0),
        nota: `botón tras volver: «${btn}»; valor: ${val}; campos «cambiado»: ${nCambio}; con el campo cambiado el botón decía «${btnCambiado}»` });
      // 6b: lo que se ve de un campo cambiado: «Cambiado», «Antes: X» y «Volver al original»
      reg({ caso: '6b', titulo: 'Un campo cambiado muestra «Cambiado», «Antes: X» y «Volver al original»', esperado: 'las tres marcas visibles', obtenido: JSON.stringify(cambioVis),
        estado: veredicto(cambioVis.clase && cambioVis.tag && cambioVis.nota && cambioVis.re && /Antes:\s*3500/.test(cambioVis.notaTxt)) });
    } finally { await ctx.close(); }
  },
  '7': async () => {
    const { ctx, page } = await ctxNuevo('editar');
    try {
      await entrar(page);
      await abrirEditar(page);
      const btn = await textoBoton(page, '[data-a="ed-listo"]');
      await tap(page, '[data-a="ed-listo"]'); await libre(page);
      await tap(page, '[data-a="no"]'); await libre(page);
      const resp = await enviar(page);
      const ob = linea(resp, 1);
      reg({ caso: 7, titulo: 'Editar sin cambiar nada → «Va como está»', esperado: L1VA, obtenido: ob, estado: veredicto(ob === L1VA && btn === 'Va como está'), nota: `botón: «${btn}»` });
    } finally { await ctx.close(); }
  },
  '8': async () => {
    // Cambiar, salir con ‹ Volver (sin confirmar) y decidir Va: el cambio no se pierde. Por botón, swipe, flecha y sin comentario.
    for (const via of ['boton', 'swipe', 'teclado', 'boton-sin-comentario']) {
      const conCom = via !== 'boton-sin-comentario';
      const viaAccion = via === 'boton-sin-comentario' ? 'boton' : via;
      const { ctx, page } = await ctxNuevo('editar');
      try {
        await entrar(page);
        await abrirEditar(page);
        await setCampo(page, '#sw-f0', 4200);
        if (conCom) { await page.locator('#sw-com').fill('Con comentario también'); await sleep(100); }
        await tap(page, '[data-a="cerrar"]'); await sleep(400);               // ‹ Volver, sin «Va con estos cambios»
        const pend = await page.evaluate(() => { const p = document.querySelector('.sw-pend'); return p ? p.innerText.replace(/\s+/g, ' ').trim() : null; });
        await shot(page, `caso-08-${via}-tras-volver`);
        await abrirEditar(page);   // la hoja recuerda lo escrito
        const reabierto = { precio: await page.locator('#sw-f0').inputValue(), comentario: await page.locator('#sw-com').inputValue() };
        await tap(page, '[data-a="cerrar"]'); await sleep(400);
        if (viaAccion === 'boton') await tap(page, '[data-a="go"]');
        else if (via === 'swipe') await swipe(page, 'right');
        else await page.keyboard.press('ArrowRight');
        await libre(page);
        await tap(page, '[data-a="no"]'); await libre(page);
        const resp = await enviar(page);
        const ob = linea(resp, 1);
        const esp = E1 + 'precio=4200 (antes 3500)' + (conCom ? ' · comentario: Con comentario también' : '');
        const pendOk = !!pend && /^1 cambio pendiente/.test(pend);
        const recuerda = reabierto.precio === '4200' && reabierto.comentario === (conCom ? 'Con comentario también' : '');
        reg({ caso: '8-' + via, titulo: `Cambiar en Editar, salir con ‹ Volver y decidir con ${viaAccion === 'boton' ? 'el botón Va' : via === 'swipe' ? 'swipe a la derecha' : 'flecha derecha'}${conCom ? '' : ' (sin comentario)'}`,
          esperado: esp + ' (y la card muestra «1 cambio pendiente» tras ‹ Volver)', obtenido: ob, estado: veredicto(ob === esp && pendOk && recuerda),
          nota: `pendiente visible tras ‹ Volver: ${JSON.stringify(pend)}; al reabrir Editar: ${JSON.stringify(reabierto)}` });
      } finally { await ctx.close(); }
    }
  },
  '9': async () => {
    const { ctx, page } = await ctxNuevo('editar');
    try {
      await entrar(page);
      await swipe(page, 'right');
      await tap(page, '[data-a="no"]'); await libre(page);
      const resp = await enviar(page);
      const ob = linea(resp, 1);
      reg({ caso: 9, titulo: 'Swipe a la derecha directo, sin Editar', esperado: L1VA, obtenido: ob, estado: veredicto(ob === L1VA) });
    } finally { await ctx.close(); }
  },
  '10': async () => {
    const { ctx, page } = await ctxNuevo('editar');
    try {
      await entrar(page);
      await tap(page, '[data-a="go"]'); await libre(page);             // card 1: «Va»
      const f2 = await frente(page);
      await abrirEditar(page);
      const nCampos = await page.locator('.sw-f').count();
      const btn = await textoBoton(page, '[data-a="vc-listo"]');
      const hayCom = await page.locator('textarea[data-com]').isVisible();
      await page.locator('#sw-com').fill('Mejor en cajas por año.'); await sleep(120);
      await tap(page, '[data-a="vc-listo"]'); await libre(page);
      const resp = await enviar(page);
      const esp = `2. va con cambios · ${T2} → Archivalos · comentario: Mejor en cajas por año.`, ob = linea(resp, 2);
      reg({ caso: 10, titulo: 'Card sin campos: Editar abre solo el comentario', esperado: esp, obtenido: ob,
        estado: veredicto(ob === esp && nCampos === 0 && btn === 'Listo' && hayCom), nota: `card al frente: ${f2}; campos en la hoja: ${nCampos}; botón: «${btn}»; comentario visible: ${hayCom}` });
    } finally { await ctx.close(); }
    // 10b: Editar sin campos y Listo SIN escribir nada es un va liso
    const c2 = await ctxNuevo('editar');
    try {
      await entrar(c2.page);
      await tap(c2.page, '[data-a="go"]'); await libre(c2.page);
      await abrirEditar(c2.page);
      await tap(c2.page, '[data-a="vc-listo"]'); await libre(c2.page);
      const resp = await enviar(c2.page);
      const ob = linea(resp, 2), espB = `2. va · ${T2} → Archivalos`;
      reg({ caso: '10b', titulo: 'Card sin campos: Editar → Listo sin escribir nada', esperado: espB + ' (sin texto no hay «va con cambios»)', obtenido: ob, estado: veredicto(ob === espB) });
    } finally { await c2.ctx.close(); }
  },
  '11': async () => {
    const { ctx, page } = await ctxNuevo('editar');
    try {
      await entrar(page);
      await tap(page, '[data-a="masinfo"]'); await esperarHoja(page);
      const tit = (await page.locator('.sw-st').innerText()).trim();
      const ops = await page.locator('.sw-rot-op b').allInnerTexts();
      await tap(page, '[data-id="dibujo-corto"]'); await tap(page, '[data-id="otro-ejemplo"]');
      await page.locator('#sw-com').fill('¿Cuánto subió el gasto el último mes?'); await sleep(120);
      await tap(page, '[data-a="ro-listo"]'); await libre(page);
      await tap(page, '[data-a="no"]'); await libre(page);   // card 2 «No va»
      const resp = await enviar(page);
      const esp = `1. rot · ${T1} → Dibujo corto + Otro ejemplo · comentario: ¿Cuánto subió el gasto el último mes?`, ob = linea(resp, 1);
      reg({ caso: 11, titulo: '+info en una card: 5 opciones + comentario, sin decidir', esperado: esp, obtenido: ob,
        estado: veredicto(ob === esp && tit === '+info' && ops.join('|') === 'Más contexto|Dibujo corto|Dibujo largo|Escribilo distinto|Otro ejemplo'), nota: `título de la hoja: «${tit}»; opciones: ${ops.join(', ')}` });
    } finally { await ctx.close(); }
  },
  '12': async () => {
    const { ctx, page } = await ctxNuevo('opciones');
    try {
      await entrar(page);
      const nEditar = await page.locator('[data-a="editar"]').count();
      const opsVis = await page.locator('[data-a="op"]').allInnerTexts();
      await shot(page, 'caso-12-card-opciones');
      await tap(page, '[data-a="op"][data-id="mail"]'); await libre(page);
      const nEditar2 = await page.locator('[data-a="editar"]').count();   // card 2 = casillas (varias): también Editar
      const otraVis = await page.locator('[data-a="op"][data-id="otra"], input[data-chk="otra"]').count();   // «Otra cosa» ya no se pinta: vive en Editar
      const chk = await page.locator('input[data-chk]').count();
      const resp = await enviar(page);
      const esp = '1. eligió mail · Elegir el canal para los avisos → Mail', ob = linea(resp, 1);
      reg({ caso: 12, titulo: 'Card con opciones: elegir una (Editar presente, sin «Otra cosa»)', esperado: esp, obtenido: ob,
        estado: veredicto(ob === esp && nEditar === 1 && nEditar2 === 1 && otraVis === 0 && chk === 2),
        nota: `Editar en la card 1: ${nEditar}; opciones visibles: ${JSON.stringify(opsVis)}; card 2 (casillas=${chk}): Editar=${nEditar2}; «Otra cosa» pintada: ${otraVis}` });
    } finally { await ctx.close(); }
  },
  '13': async () => {
    const { ctx, page } = await ctxNuevo('editar');
    try {
      await entrar(page);
      await abrirEditar(page);
      const vis = () => page.evaluate(() => { const t = document.querySelector('textarea[data-com]'); if (!t) return { existe: false };
        const b = t.getBoundingClientRect(), cs = getComputedStyle(t); return { existe: true, visible: cs.display !== 'none' && cs.visibility !== 'hidden' && b.width > 0 && b.height > 0, dentroDeLaPantalla: b.top >= 0 && b.bottom <= innerHeight }; });
      const sinCambios = await vis();
      await setCampo(page, '#sw-f0', 4200);
      const conCambios = await vis();
      await shot(page, 'caso-13-hoja');
      await tap(page, '[data-a="cerrar"]'); await sleep(300);
      await tap(page, '[data-a="go"]'); await libre(page);
      await abrirEditar(page);
      const sinCampos = await vis();
      reg({ caso: 13, titulo: 'El comentario libre se ve siempre en la hoja de Editar', esperado: 'textarea visible en los 3 estados',
        obtenido: JSON.stringify({ sinCambios, conCambios, cardSinCampos: sinCampos }),
        estado: veredicto(sinCambios.visible && sinCambios.dentroDeLaPantalla && conCambios.visible && sinCampos.visible) });
    } finally { await ctx.close(); }
  },
  '14': async () => {
    const { ctx, page } = await ctxNuevo('editar');
    try {
      await entrar(page);
      await abrirEditar(page);
      await setCampo(page, '#sw-f0', 4200);
      await setCampo(page, '#sw-f2', 'Todos los pedidos');
      await page.locator('#sw-com').fill('Esto sobrevive a la recarga'); await sleep(200);
      await shot(page, 'caso-14-antes-de-recargar');
      await page.goto(URL_WEB());   // recarga EN MEDIO de la hoja abierta: las marcas viven en localStorage
      await page.waitForSelector('.hrow', { timeout: 10000 });
      await tap(page, '.hrow');
      await page.waitForSelector('[data-a="empezar"]'); await tap(page, '[data-a="empezar"]'); await page.waitForSelector('.sw-act'); await libre(page);
      await abrirEditar(page);
      const rec = { precio: await page.locator('#sw-f0').inputValue(), alcance: await page.locator('#sw-f2').inputValue(), comentario: await page.locator('#sw-com').inputValue() };
      await tap(page, '[data-a="ed-listo"]'); await libre(page);
      await tap(page, '[data-a="no"]'); await libre(page);
      const resp = await enviar(page);
      const esp = E1 + 'precio=4200 (antes 3500); alcance=Todos los pedidos (antes Pedidos chicos) · comentario: Esto sobrevive a la recarga', ob = linea(resp, 1);
      reg({ caso: 14, titulo: 'Lo escrito sobrevive una recarga en medio', esperado: esp, obtenido: ob,
        estado: veredicto(ob === esp && rec.precio === '4200' && rec.alcance === 'Todos los pedidos' && rec.comentario === 'Esto sobrevive a la recarga'), nota: `valores al reabrir: ${JSON.stringify(rec)}` });
    } finally { await ctx.close(); }
  },
  '15': async () => {
    // cambios guardados + «No va»: la respuesta es un no va liso, sin campos
    const { ctx, page } = await ctxNuevo('editar');
    try {
      await entrar(page);
      await abrirEditar(page);
      await setCampo(page, '#sw-f0', 4200);
      await tap(page, '[data-a="cerrar"]'); await sleep(300);
      await tap(page, '[data-a="no"]'); await libre(page);
      await tap(page, '[data-a="no"]'); await libre(page);
      const resp = await enviar(page);
      const ob = linea(resp, 1), esp = `1. no va · ${T1} → Dejalo como está`;
      reg({ caso: '15', titulo: 'Cambiar en Editar, ‹ Volver y decidir «No va»', esperado: esp + ' (sin campos: es un no)', obtenido: ob, estado: veredicto(ob === esp) });
    } finally { await ctx.close(); }
  },
  // Editar en opciones: a) una marcada + comentario, con Cmd/Ctrl+Enter; b) ninguna marcada + comentario = «eligió otra»
  '16': async () => {
    const { ctx, page } = await ctxNuevo('opciones');
    try {
      await entrar(page);
      await tap(page, '.sw-op.ed'); await sleep(400);
      const pre = await page.evaluate(() => [...document.querySelectorAll('input[data-edop]:checked')].map(i => i.getAttribute('data-edop')));
      await page.locator('input[data-edop="whatsapp"]').click(); await sleep(150);
      const uno = await page.evaluate(() => [...document.querySelectorAll('input[data-edop]:checked')].map(i => i.getAttribute('data-edop')));
      await page.locator('textarea[data-com]').fill('pero solo para clientes nuevos');
      await page.keyboard.press(process.platform === 'darwin' ? 'Meta+Enter' : 'Control+Enter'); await libre(page);
      // card 2 (casillas): Editar, desmarcar la recomendada, Listo vacío no pasa, escribir y Listo
      await tap(page, '.sw-op.ed'); await sleep(400);
      for (const id of await page.evaluate(() => [...document.querySelectorAll('input[data-edop]:checked')].map(i => i.getAttribute('data-edop'))))
        await page.locator(`input[data-edop="${id}"]`).click();
      await tap(page, '[data-a="op-ed-listo"]'); await sleep(300);
      const sigue = await page.locator('.sw-ed').count();
      await page.locator('textarea[data-com]').fill('ninguna, mejor un video');
      await tap(page, '[data-a="op-ed-listo"]'); await libre(page);
      const resp = await enviar(page);
      const e1 = '1. eligió whatsapp · Elegir el canal para los avisos → Mensaje de WhatsApp · comentario: pero solo para clientes nuevos', o1 = linea(resp, 1);
      const e2 = '2. eligió otra · Dónde publicar la novedad → Otra cosa · comentario: ninguna, mejor un video', o2 = linea(resp, 2);
      reg({ caso: 16, titulo: 'Editar en opciones: elegir + comentar (Cmd/Ctrl+Enter) y ninguna + comentar', esperado: e1 + ' / ' + e2, obtenido: o1 + ' / ' + o2,
        estado: veredicto(o1 === e1 && o2 === e2 && sigue === 1 && pre.join() === 'mail' && uno.join() === 'whatsapp'),
        nota: `marcada al abrir: ${pre}; tras tocar WhatsApp: ${uno}; Listo vacío sin marcas: ${sigue ? 'se quedó' : 'cerró'}` });
    } finally { await ctx.close(); }
  },
  // el home: contador «N mazos · M cards» y fila «Con error»
  '17': async () => {
    const { ctx, page } = await ctxNuevo('home');
    try {
      await page.goto(URL_WEB());
      await page.waitForSelector('.hrow', { timeout: 10000 });
      await sleep(600);
      const filas = await page.evaluate(() => [...document.querySelectorAll('.hrow')].map(r => ({ nombre: r.querySelector('b').innerText.trim(), sub: r.querySelector('.hs').innerText.trim() })));
      await shot(page, 'caso-17-home');
      const t = filas.find(f => f.nombre === 'Trabajo'), c = filas.find(f => f.nombre === 'Casa');
      reg({ caso: 17, titulo: 'Las filas del home cuentan «N mazos · M cards»', esperado: 'Trabajo: 2 mazos · 5 cards; Casa: 1 mazo · 1 card', obtenido: JSON.stringify(filas),
        estado: veredicto(t && c && t.sub === '2 mazos · 5 cards' && c.sub === '1 mazo · 1 card') });
    } finally { await ctx.close(); }
  },
  '18': async () => {
    const { ctx, page } = await ctxNuevo('home');
    try {
      await page.goto(URL_WEB());
      await page.waitForSelector('.hrow', { timeout: 10000 });
      await page.tap('[data-tab="bloqueos"]');   // la fila «Con error» vive en Bloqueos
      await page.waitForSelector('.herr', { timeout: 10000 });
      const antes = await page.evaluate(() => ({ titulo: document.querySelector('.herr-k').textContent.trim(), items: [...document.querySelectorAll('.herr-i b')].map(b => b.innerText.trim()),
        tipos: [...document.querySelectorAll('.herr-w')].map(w => w.innerText.split(' · ')[0]) }));
      await shot(page, 'caso-18-con-error');
      await page.locator('.herr-v').first().tap(); await sleep(400);
      const visto = await page.evaluate(() => window.__visto.slice());
      const despues = await page.evaluate(() => ({ titulo: document.querySelector('.herr-k') ? document.querySelector('.herr-k').textContent.trim() : null, n: document.querySelectorAll('.herr-i').length }));
      for (let i = 0; i < 2; i++) { await page.locator('.herr-v').first().tap(); await sleep(300); }
      const vacio = await page.locator('.herr').count();
      reg({ caso: 18, titulo: 'Fila «Con error»: lista los errores sin ver y «Visto» los saca', esperado: 'Con error · 3 → tocar Visto → Con error · 2 → … → la fila desaparece',
        obtenido: JSON.stringify({ antes, visto, despues, vacio }),
        estado: veredicto(antes.titulo === 'Con error · 3' && antes.items.length === 3 && antes.tipos.includes('Tarea programada') && antes.tipos.includes('Respuesta sin aplicar')
          && visto.length === 1 && despues.titulo === 'Con error · 2' && despues.n === 2 && vacio === 0) });
    } finally { await ctx.close(); }
  },
};

(async () => {
  await levantar();
  browser = await chromium.launch();
  const orden = Object.keys(CASOS).sort((a, b) => Number(a) - Number(b));
  for (const k of orden) {
    if (SOLO.length && !SOLO.includes(k)) continue;
    try { await CASOS[k](); }
    catch (e) { reg({ caso: k, titulo: 'ERROR del script', esperado: '', obtenido: String(e && e.stack || e).split('\n').slice(0, 4).join(' / '), estado: 'NO SE PUDO' }); }
  }
  await browser.close();
  server.close();
  const md = ['| Caso | Título | Esperado | Obtenido | Estado |', '|---|---|---|---|---|']
    .concat(RES.map(r => `| ${r.caso} | ${(r.titulo || '').replace(/\|/g, '\\|')} | ${(r.esperado || '').replace(/\|/g, '\\|')} | ${(r.obtenido || '').replace(/\|/g, '\\|')} | ${r.estado} |`));
  fs.writeFileSync(path.join(OUT, 'results.md'), md.join('\n') + '\n');
  console.log('\n=== RESUMEN ===');
  RES.forEach(r => console.log(String(r.caso).padEnd(8), r.estado.padEnd(11), r.titulo));
  const pasan = RES.filter(r => r.estado === 'PASA').length;
  console.log(`\n${pasan}/${RES.length} casos pasan · capturas y results.md en ${OUT}`);
  process.exit(pasan === RES.length ? 0 : 1);
})();

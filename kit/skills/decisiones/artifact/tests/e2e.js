#!/usr/bin/env node
/* Prueba de punta a punta de la página privada de Claude (pagina.html) contra un `window.claude` falso.
   pagina.html es la web de la botonera con la base de Claude en lugar de Supabase: acá se prueba que el adaptador
   y los pocos cambios (avisar a Claude, marcas, estado de Claude) andan, con la web de verdad adentro.

   Uso (Playwright ya instalado en tu máquina; no se instala nada):
     NODE_PATH=/ruta/a/node_modules node kit/skills/decisiones/artifact/tests/e2e.js
   Si Chromium no está instalado: npx playwright install chromium
   Un solo navegador a la vez; se cierra siempre al terminar. */
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const AQUI = __dirname;
const RAIZ = path.resolve(AQUI, '..');                       // .../decisiones/artifact
const DEC = path.resolve(RAIZ, '..');                        // .../decisiones
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'tarjetas-'));
let pasan = 0, fallan = 0;
const fallos = [];
function check(nombre, ok, detalle) {
  if (ok) { pasan++; console.log('  ok    ' + nombre); }
  else { fallan++; fallos.push(nombre); console.log('  FALLA ' + nombre + (detalle !== undefined ? '  -> ' + JSON.stringify(detalle) : '')); }
}
function armar(datos, nombre) {
  const salida = path.join(TMP, nombre + '.json');
  execFileSync('python3', [path.join(DEC, 'armar.py'), '--artifact', datos, salida], { stdio: 'pipe' });
  return JSON.parse(fs.readFileSync(salida, 'utf8'));
}
const DOC = armar(path.join(DEC, 'ejemplo', 'datos-artifact.json'), 'pan');      // 6 tarjetas: Anuncios (Agencia Faro)
const CASA = armar(path.join(AQUI, 'fixture-casa.json'), 'casa');                // 2 tarjetas: Casa
const HOSTIL = JSON.parse(fs.readFileSync(path.join(AQUI, 'fixture-extra.json'), 'utf8'));   // a mano, con html y script a propósito
const CLAVE = DOC.clave, CLAVE_CASA = CASA.clave;

const server = http.createServer((req, res) => {
  const f = path.join(RAIZ, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(RAIZ) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': f.endsWith('.html') ? 'text/html; charset=utf-8' : f.endsWith('.js') ? 'text/javascript' : 'application/json' });
  res.end(fs.readFileSync(f));
});
const sleep = ms => new Promise(r => setTimeout(r, ms));
let browser, base;
const errores = [], terceros = new Set();

async function ctxNuevo(ancho, alto, extra) {
  const ctx = await browser.newContext({ viewport: { width: ancho || 390, height: alto || 844 }, hasTouch: !(extra && extra.sinTouch), isMobile: !(extra && extra.sinTouch), deviceScaleFactor: 1 });
  // lo único que la página pide afuera son las fuentes de Google; se contestan vacías. Cualquier otro host se corta y se anota.
  await ctx.route(u => u.hostname !== '127.0.0.1', r => {
    const h = new URL(r.request().url()).hostname; terceros.add(h);
    if (h === 'fonts.googleapis.com') return r.fulfill({ contentType: 'text/css', body: '' });
    if (h === 'fonts.gstatic.com') return r.fulfill({ contentType: 'font/woff2', body: '' });
    return r.abort();
  });
  return ctx;
}
async function abrir(params, opts) {
  opts = opts || {};
  const ctx = opts.ctx || await ctxNuevo(opts.ancho, opts.alto, opts);
  if (opts.sinStorage) await ctx.addInitScript(() => {
    const roto = { get() { throw new Error('storage bloqueado'); } };
    Object.defineProperty(window, 'localStorage', roto); Object.defineProperty(window, 'sessionStorage', roto);
  });
  const page = await ctx.newPage();
  page.ctx = ctx;
  page.on('pageerror', e => errores.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errores.push('consola: ' + m.text()); });
  await page.goto(base + '/tests/arnes.html' + (params ? '?' + params : ''));
  await page.waitForSelector('#raiz');
  if (opts.seed !== false) {
    const docs = opts.docs || [DOC, CASA];
    await page.evaluate(ds => ds.forEach(d => window.__fake.seed('tandas/' + d.clave, d)), docs);
  }
  return page;
}
const cerrar = async p => { try { await p.ctx.close(); } catch (e) {} };
const doc = (page, p) => page.evaluate(p => { const v = window.__fake.docs.get(p); return v ? JSON.parse(JSON.stringify(v)) : null; }, p);
const escritos = page => page.evaluate(() => window.__fake.escritos.map(e => e.path));
const home = page => page.evaluate(() => (document.getElementById('home') || document.body).innerText);
const sinScrollX = page => page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1 && document.body.scrollWidth <= document.body.clientWidth + 1);
const tap = (page, sel) => page.locator(sel).first().tap();
async function libre(page) {
  await page.waitForFunction(() => { const s = window.__swipe && window.__swipe(); return !s || !s.ocupado; }, null, { timeout: 8000 });
  await sleep(120);
}
async function entrarCat(page, cat) {
  await page.waitForSelector('.hrow', { timeout: 10000 });
  await tap(page, cat ? `.hrow[data-cat="${cat}"]` : '.hrow');
  if (await page.locator('.htanda').first().isVisible().catch(() => false)) await tap(page, '.htanda');
  await page.waitForSelector('[data-a="empezar"]', { timeout: 8000 });
  await tap(page, '[data-a="empezar"]');
  await page.waitForSelector('.sw-act, .sw-op', { timeout: 8000 });
  await libre(page);
}
async function enviar(page) {
  await sleep(300);
  await page.locator('[data-a="enviar"]:visible, [data-a="terminar"]:visible').first().waitFor({ timeout: 8000 });
  const b = page.locator('[data-a="enviar"]:visible').first();
  if (await b.count()) await b.tap(); else await tap(page, '[data-a="terminar"]');
}
// las dos tarjetas de la casa: Va y Va, y Enviar. Deja la respuesta en respuestas/<clave>
async function mazoCasa(page) {
  await entrarCat(page, 'casa');
  await tap(page, '[data-a="go"]'); await libre(page);
  await tap(page, '[data-a="go"]'); await libre(page);
  await enviar(page);
  await page.waitForFunction(c => window.__fake.docs.has('respuestas/' + c), CLAVE_CASA, { timeout: 8000 });
  await sleep(300);
}
async function arrastrar(page, dx) {
  const b = await page.locator('#sw-card').boundingBox();
  const y = b.y + b.height / 2, x0 = b.x + b.width / 2;
  await page.mouse.move(x0, y); await page.mouse.down();
  await page.mouse.move(x0 + dx / 2, y, { steps: 6 }); await page.mouse.move(x0 + dx, y, { steps: 6 });
  await page.mouse.up();
}

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  base = 'http://127.0.0.1:' + server.address().port;
  try { browser = await chromium.launch(); }
  catch (e) { console.log('NO SE PUDO ABRIR CHROMIUM: ' + e.message.split('\n')[0] + '\n(instalalo con: npx playwright install chromium)'); process.exit(2); }
  try {
    /* ===== A. flujo completo, con room disponible ===== */
    console.log('\nA. flujo completo (room disponible)');
    let p = await abrir('');
    await p.waitForSelector('.hrow');
    let t = await home(p);
    const cargas0 = await p.evaluate(() => window.__cargas);
    check('home: una fila por categoría (Casa y Anuncios), con sus tarjetas', (await p.locator('.hrow').count()) === 2 && /Anuncios/.test(t) && /Casa/.test(t) && /6 tarjetas/.test(t) && /2 tarjetas/.test(t), t);
    check('home: sin pantalla de PIN, sin «Salir», sin avisos al celu', !(await p.locator('#b-salir, #i-pin, [data-home="avisos"]').count()) && !/PIN|Salir|Activar avisos|Agregala a inicio/.test(await p.evaluate(() => document.body.innerText)));
    check('título de la página: «Tus pendientes»', (await p.title()) === 'Tus pendientes', await p.title());
    check('home 390 px: sin scroll horizontal', await sinScrollX(p));
    check('sin script de afuera, sin service worker, sin manifest', await p.evaluate(() => !document.querySelector('script[src]') && !document.querySelector('link[rel="manifest"]') && !document.querySelector('link[rel*="icon"]')));
    await entrarCat(p, 'anuncios');
    t = await p.evaluate(() => document.querySelector('.sw').innerText);
    check('mazo: pantalla de contexto con la introducción', /Propuestas de Agencia Faro/.test(t) || /Cinco propuestas|Claude encontró/.test(t), t.slice(0, 160));
    t = await p.evaluate(() => document.querySelector('.sw').innerText);
    check('tarjeta 1: dice «Claude recomienda» (no «el agente») y «Si no decidís»', /Claude recomienda: Sumar las palabras/.test(t) && !/agente/i.test(t) && /Si no decidís/.test(t), t.slice(0, 300));
    check('tarjeta 1: nada viene premarcado', Object.values(await p.evaluate(() => window.__swipe().marcas)).every(m => !m.m));
    check('tarjeta 1: sin scroll horizontal', await sinScrollX(p));
    // Editar con campos
    await tap(p, '[data-a="editar"]'); await p.waitForSelector('#sw-f0');
    check('Editar: abre los campos cargados', (await p.inputValue('#sw-f1')) === '1.2' && (await p.inputValue('#sw-f2')) === 'Tratamientos');
    await p.fill('#sw-f1', '1.5'); await sleep(150);
    await tap(p, '[data-a="ed-listo"]'); await libre(p);
    // tarjeta 2 (sí/no con dibujo): Va
    check('tarjeta 2: la del presupuesto trae su dibujo antes → después', /presupuesto diario/i.test(await p.evaluate(() => document.querySelector('#sw-card h2').innerText)) && (await p.locator('.sw-card img[src^="data:image/svg+xml"]').count()) >= 1);
    await tap(p, '[data-a="go"]'); await libre(p);
    // opción única
    check('tarjeta 3: la opción recomendada se ve marcada como recomendada', (await p.locator('.sw-op.rec').count()) === 1 && /Claude recomienda esta/.test(await p.locator('.sw-op.rec').innerText()));
    await tap(p, '[data-a="op"][data-id="turno"]'); await libre(p);
    // varias
    await tap(p, 'input[data-chk="sonrisa"]'); await tap(p, 'input[data-chk="pulso"]'); await tap(p, '[data-a="op-listo"]'); await libre(p);
    // la 5, con el gesto de deslizar a la izquierda (No va)
    check('tarjeta 5: la tarjeta que sigue es la de Marta', /Marta/.test(await p.evaluate(() => document.querySelector('#sw-card h2').innerText)));
    await arrastrar(p, -170); await libre(p);
    // revisión
    t = await p.evaluate(() => document.querySelector('.sw').innerText);
    check('tarjeta 6 (revisión): «Qué hice», «Qué verifiqué», «Qué te queda mirar» y el botón Revisado', /Qué hice/.test(t) && /Qué verifiqué/.test(t) && /Qué te queda mirar/.test(t) && (await p.locator('[data-a="rev-ok"]').count()) === 1, t.slice(0, 260));
    check('tarjeta 6 (revisión): se ve el link', /ejemplo\.com/.test(t), t);
    await tap(p, '[data-a="rev-ok"]'); await libre(p);
    await p.waitForSelector('[data-a="enviar"]:visible', { timeout: 8000 });
    t = await p.evaluate(() => document.querySelector('.sw').innerText);
    check('cierre: cuenta lo marcado (5 Va, la revisión cuenta como Va · 1 No va)', /Marcaste todo/.test(t) && /5 Va · 1 No va · 0 sin marcar/.test(t), t.slice(0, 200));
    await p.fill('#sw-fin', 'gracias');
    await sleep(200);
    await p.locator('[data-a="enviar"]:visible').first().dblclick();
    await p.waitForFunction(c => window.__fake.docs.has('respuestas/' + c), CLAVE, { timeout: 8000 });
    await sleep(500);
    check('Enviar: doble toque escribe UNA sola vez', (await p.evaluate(c => window.__fake.escrituras['respuestas/' + c], CLAVE)) === 1, await p.evaluate(() => window.__fake.escrituras));
    const R = await doc(p, 'respuestas/' + CLAVE);
    const lineas = (R.texto || '').split('\n');
    const esp = [
      '/botonera respuesta · ' + CLAVE,
      '1. va con cambios · Sumar palabras clave a Dental Sonrisa → Sumar las palabras · campos: puja=1.5 (antes 1.2)',
      '2. va · Subir el presupuesto diario de Gimnasio Pulso → Subir el presupuesto',
      '3. eligió turno · Elegir el título de la landing de Dental Sonrisa → Turno hoy, sin esperas',
      '4. eligió sonrisa, pulso · Qué clientes reciben el reporte del lunes → Clínica Dental Sonrisa, Gimnasio Pulso',
      '5. no va · Responderle a Marta, de La Espiga → Esperar al jueves',
      '6. revisado · Revisar el reporte de Gimnasio Pulso',
      'notas: gracias'];
  check('respuestas/<clave>.texto: línea por línea, la primera es el encabezado «/botonera respuesta ·»', JSON.stringify(lineas) === JSON.stringify(esp), lineas);
    check('respuestas/<clave>: clave, por y cuando', R.clave === CLAVE && R.por === 'u_prueba' && !isNaN(Date.parse(R.cuando)), R);
    t = await p.evaluate(() => document.querySelector('.sw').innerText);
    check('Enviado: «enviada», «Tu respuesta quedó guardada» y el paso de avisar', /enviada/.test(t) && /Tu respuesta quedó guardada/.test(t) && /Avisar a Claude/.test(t) && /Claude te va a pedir que confirmes/.test(t) && /o volvé al chat y escribí “listo”/.test(t) && /Copiar respuesta/.test(t), t);
    await p.locator('[data-av="room"]').dblclick();
    await p.waitForFunction(() => window.__fake.enviados.length >= 1, null, { timeout: 5000 });
    await sleep(400);
    const env = await p.evaluate(() => window.__fake.enviados.map(e => JSON.parse(JSON.stringify(e))));
    check('Avisar: doble toque manda UN solo aviso', env.length === 1, env.length);
    check('Avisar: el mensaje lleva tipo respuesta_tarjetas, la clave y el texto', env[0] && env[0].data.tipo === 'respuesta_tarjetas' && env[0].data.clave === CLAVE && env[0].data.texto === R.texto && env[0].options.deliver === 'send', env[0] && env[0].data);
    check('Avisar: el botón queda bloqueado y dice el resultado en criollo', (await p.locator('[data-av="room"]').isDisabled()) && /Claude recibió el aviso/.test(await p.evaluate(() => document.querySelector('.av').innerText)));
    check('mazo cerrado: 390 px sin scroll horizontal', await sinScrollX(p));
    check('la página no escribió en tandas ni en estado (solo respuestas y marcas)', (await escritos(p)).every(x => /^(respuestas|marcas)\//.test(x)), await escritos(p));
    // volver al home y mirar Sesiones
    await tap(p, '[data-a="salir"]'); await sleep(500);
    await tap(p, '[data-tab="sesiones"]'); await sleep(600);
    t = await home(p);
    check('Sesiones: la tanda enviada aparece «Mandada», en «Trabajando ahora»', /trabajando ahora/i.test(t) && /Propuestas de Agencia Faro/.test(t) && /Mandada/.test(t), t);
    // Claude simulado: estado/<clave> y después tandas.estado = aplicada, sin recargar la página
    await p.evaluate(c => window.__fake.seed('estado/' + c, { texto: 'Cambiando la lista de precios', cuando: new Date().toISOString() }), CLAVE);
    await p.waitForFunction(() => /Trabajando/.test(document.getElementById('home').innerText), null, { timeout: 8000 });
    await p.locator('.hfin').first().tap(); await sleep(300);
    t = await home(p);
    check('Sesiones: lo que escribe Claude se ve («Claude está trabajando» + su texto)', /Claude está trabajando/.test(t) && /Cambiando la lista de precios/.test(t) && !/agente/i.test(t), t);
    await p.evaluate(([c, d]) => window.__fake.seed('tandas/' + c, Object.assign({}, d, { estado: 'aplicada', resumen: '1. Sumé las palabras clave.\n2. Subí el presupuesto.' })), [CLAVE, DOC]);
    await p.waitForFunction(() => /hechas hoy/i.test(document.getElementById('home').innerText), null, { timeout: 8000 });
    await sleep(300);
    if (!/Sumé las palabras/.test(await home(p))) { await p.locator('.hfin').first().tap(); await sleep(300); }
    t = await home(p);
    check('Sesiones: «aplicada» + resumen se ven en «Hechas hoy» sin recargar la página', /hechas hoy/i.test(t) && /Hecha/.test(t) && /Sumé las palabras clave/.test(t) && (await p.evaluate(() => window.__cargas)) === cargas0, t);
    check('sesiones: 390 px sin scroll horizontal', await sinScrollX(p));
    // la pestaña Bloqueos queda con su estado vacío (esta versión no tiene obstáculos ni errores)
    await tap(p, '[data-tab="bloqueos"]'); await sleep(500);
    t = await home(p);
    check('Bloqueos: estado vacío («Nada bloqueado»)', /Nada bloqueado/.test(t), t);
    check('el menú de abajo tiene las tres pestañas', (await p.locator('#tabs .tab').count()) === 3);
    check('lo que la página escribió: solo respuestas/ y marcas/', (await escritos(p)).every(x => /^(respuestas|marcas)\//.test(x)), await escritos(p));
    await cerrar(p);

    /* ===== B. snooze, despertar y marcas a medio decidir (todo va a marcas/<clave>) ===== */
    console.log('\nB. snooze, despertar y marcas');
    p = await abrir('');
    await p.waitForSelector('.hrow');
    await tap(p, '.hrow[data-cat="casa"]');
    await p.waitForSelector('[data-a="empezar"]');
    await tap(p, '[data-a="snooze"]'); await p.waitForSelector('[data-a="snz-op"]');
    await tap(p, '[data-a="snz-op"]');
    await p.waitForFunction(c => { const m = window.__fake.docs.get('marcas/' + c); return m && m.snooze_hasta; }, CLAVE_CASA, { timeout: 8000 });
    let m = await doc(p, 'marcas/' + CLAVE_CASA);
    check('snooze: marcas/<clave>.snooze_hasta queda en el futuro (y menos de 8 días)', Date.parse(m.snooze_hasta) > Date.now() && Date.parse(m.snooze_hasta) < Date.now() + 8 * 24 * 3600e3, m);
    check('snooze: no se tocó tandas/', !(await escritos(p)).some(x => x.startsWith('tandas/')));
    await p.waitForSelector('[data-a="home"]', { timeout: 8000 }); await tap(p, '[data-a="home"]'); await sleep(400);
    await p.waitForSelector('.hsnz', { timeout: 8000 });
    t = await home(p);
    check('snooze: la tanda pasa a «Snoozeadas» y sale de las categorías', /Snoozeadas/i.test(t) && /Cosas de la casa/.test(t) && (await p.locator('.hrow').count()) === 1, t);
    await tap(p, '[data-home="despertar"]');
    await p.waitForFunction(c => { const m = window.__fake.docs.get('marcas/' + c); return m && Date.parse(m.snooze_hasta) <= Date.now() + 50; }, CLAVE_CASA, { timeout: 8000 });
    await p.waitForFunction(() => document.querySelectorAll('.hrow').length === 2, null, { timeout: 8000 });
    check('despertar: la tanda vuelve a su categoría', (await p.locator('.hrow').count()) === 2 && !/Snoozeadas/i.test(await home(p)));
    // marca a medio decidir: Va en la primera tarjeta y salir
    await entrarCat(p, 'casa');
    await tap(p, '[data-a="go"]'); await libre(p);
    await p.waitForFunction(c => { const m = window.__fake.docs.get('marcas/' + c); return m && m.marcas && m.marcas.items && m.marcas.items['1'] && m.marcas.items['1'].m === 'go'; }, CLAVE_CASA, { timeout: 8000 });
    m = await doc(p, 'marcas/' + CLAVE_CASA);
    check('marcas: la tarjeta a medio decidir queda en marcas/<clave> (para seguir en otro dispositivo)', m.marcas.items['1'].m === 'go' && m.clave === CLAVE_CASA, m);
    check('marcas: no escribió en tandas/ ni en estado/', (await escritos(p)).every(x => /^(respuestas|marcas)\//.test(x)));
    await cerrar(p);
    // otro dispositivo: sin nada en su navegador, con esas marcas ya en la base
    p = await abrir('', { docs: [CASA] });
    await p.evaluate(([c, mm]) => window.__fake.seed('marcas/' + c, mm), [CLAVE_CASA, m]);
    await p.waitForFunction(() => /1 tarjeta\b/.test(document.getElementById('home').innerText), null, { timeout: 8000 });
    check('marcas: otro dispositivo adopta lo marcado (la tanda muestra 1 tarjeta por decidir de 2)', /1 tarjeta\b/.test(await home(p)), await home(p));
    await cerrar(p);

    /* ===== C. los tres caminos de avisar ===== */
    console.log('\nC. avisar a Claude: solo comentarios, ningún canal');
    p = await abrir('canroom=no_session&cancomment=available', { docs: [CASA] });
    await mazoCasa(p);
    t = await p.evaluate(() => document.querySelector('.sw').innerText);
    check('solo comentarios: el botón es «Avisarle a Claude con un comentario»', /Avisarle a Claude con un comentario/.test(t) && !/^Avisar a Claude$/m.test(t) && !(await p.locator('[data-av="room"]').count()), t);
    await p.locator('[data-av="com"]').dblclick();
    await p.waitForFunction(() => window.__fake.comentarios.length >= 1, null, { timeout: 5000 }); await sleep(300);
    const com = await p.evaluate(() => window.__fake.comentarios);
    check('solo comentarios: un solo comentario «respuesta a las tarjetas · <clave>» con el texto', com.length === 1 && com[0].text.startsWith('respuesta a las tarjetas · ' + CLAVE_CASA + '\n/botonera respuesta · ' + CLAVE_CASA), com);
    check('solo comentarios: queda el resultado en criollo y el botón bloqueado', /Comentario enviado/.test(await p.evaluate(() => document.querySelector('.av').innerText)) && (await p.locator('[data-av="com"]').isDisabled()));
    await cerrar(p);
    p = await abrir('canroom=no_session&cancomment=off', { docs: [CASA] });
    await mazoCasa(p);
    t = await p.evaluate(() => document.querySelector('.sw').innerText);
    check('ningún canal: queda «o volvé al chat y escribí “listo”» y Copiar respuesta, sin botón de avisar', !(await p.locator('[data-av="room"], [data-av="com"]').count()) && /o volvé al chat y escribí “listo”/.test(t) && /Copiar respuesta/.test(t), t);
    await ctxPermisos(p);
    await p.locator('[data-av="copiar"]').tap(); await sleep(400);
    check('Copiar respuesta: confirma que copió', /Copiado\. Pegalo en el chat con Claude/.test(await p.evaluate(() => document.querySelector('.av').innerText)));
    await cerrar(p);

    /* ===== D. sin base, solo lectura, almacenamiento bloqueado ===== */
    console.log('\nD. sin base, solo lectura, sin almacenamiento');
    p = await abrir('db=null', { seed: false });
    await p.waitForSelector('.entrada');
    t = await p.evaluate(() => document.body.innerText);
    check('sin base: «Esta página necesita que entres a Claude con tu cuenta»', /Esta página necesita que entres a Claude con tu cuenta/.test(t), t);
    await cerrar(p);
    p = await abrir('write=0', { docs: [CASA] });
    await entrarCat(p, 'casa');
    await tap(p, '[data-a="go"]'); await libre(p); await tap(p, '[data-a="go"]'); await libre(p);
    await enviar(p); await p.waitForSelector('.sw-be.mal, .sw-err', { timeout: 8000 });
    t = await p.evaluate(() => document.querySelector('.sw-be.mal, .sw-err').innerText);
    check('solo lectura: Enviar dice que no tiene permiso y no escribe nada', /No tenés permiso para responder/.test(t) && !(await p.evaluate(() => window.__fake.escritos.some(e => e.path.startsWith('respuestas/')))), t);
    await cerrar(p);
    p = await abrir('', { docs: [CASA], sinStorage: true });
    await p.waitForSelector('.hrow', { timeout: 8000 });
    await tap(p, '.hrow'); await p.waitForSelector('[data-a="empezar"]'); await tap(p, '[data-a="empezar"]'); await p.waitForSelector('.sw-act'); await libre(p);
    await tap(p, '[data-a="go"]'); await libre(p);
    check('localStorage y sessionStorage que fallan: la página anda igual (marca una tarjeta)', (await p.evaluate(() => window.__swipe().marcas))['casa-2026-03-12|1'].m === 'go');
    await cerrar(p);

    /* ===== E. datos hostiles y cambios en vivo ===== */
    console.log('\nE. datos hostiles, tanda sin categoría, cambios en vivo');
    p = await abrir('', { docs: [HOSTIL] });
    await p.waitForSelector('.hrow');
    t = await home(p);
    check('una tanda sin categoría cae en «Pendientes»', /Pendientes/.test(t), t);
    await tap(p, '.hrow'); await p.waitForSelector('[data-a="empezar"]'); await tap(p, '[data-a="empezar"]'); await p.waitForSelector('.sw-act, .sw-op'); await sleep(300);
    await tap(p, '[data-a="go"]'); await libre(p); await sleep(200);
    check('la segunda tarjeta trae un dibujo y va como imagen (el svg no ejecuta nada)', (await p.locator('.sw-card img[src^="data:image/svg+xml"]').count()) >= 1);
    check('título con html: se muestra como texto, no se ejecuta', (await p.evaluate(() => window.__xss === undefined)) && (await p.evaluate(() => !document.querySelector('.sw img[src="x"]'))));
    check('dibujo con <script> y onclick: nada se ejecuta', await p.evaluate(() => window.__xss === undefined));
    await p.evaluate(d => window.__fake.seed('tandas/nueva-1', Object.assign({}, d, { clave: 'nueva-1', titulo: 'Una tanda nueva', creada: new Date().toISOString(), origen: { categoria: 'Casa' } })), CASA);
    await p.evaluate(() => { const b = document.querySelector('[data-a="salir"]'); if (b) b.click(); });
    await p.waitForFunction(() => /Una tanda nueva|Casa/.test(document.getElementById('home').innerText), null, { timeout: 8000 });
    check('una tanda que llega mientras la página está abierta aparece sola (sin recargar)', /Casa/.test(await home(p)));
    await cerrar(p);

    /* ===== F. anchos y errores ===== */
    console.log('\nF. 1280 px y errores');
    p = await abrir('', { ancho: 1280, alto: 900, sinTouch: true });
    await p.waitForSelector('.hrow');
    check('1280 px: home sin scroll horizontal', await sinScrollX(p));
    await p.locator('.hrow[data-cat="anuncios"]').click(); await p.waitForSelector('[data-a="empezar"]');
    check('1280 px: pantalla de contexto sin scroll horizontal', await sinScrollX(p));
    await p.locator('[data-a="empezar"]').click(); await p.waitForSelector('.sw-act'); await libre(p);
    check('1280 px: tarjeta sin scroll horizontal', await sinScrollX(p));
    await cerrar(p);
    check('cero errores de página ni de consola en toda la corrida', errores.length === 0, errores);
    const ext = [...terceros].filter(h => !/^fonts\.(googleapis|gstatic)\.com$/.test(h));
    check('cero pedidos de red fuera de Google Fonts', ext.length === 0, [...terceros]);
  } finally {
    try { await browser.close(); } catch (e) {}
    server.close();
  }
  console.log(`\n${pasan} pasan / ${fallan} fallan`);
  if (fallan) { console.log('Fallan: ' + fallos.join(' | ')); process.exit(1); }
})();

async function ctxPermisos(page) { try { await page.ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: base }); } catch (e) {} }

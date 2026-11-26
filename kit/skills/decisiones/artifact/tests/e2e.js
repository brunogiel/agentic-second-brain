#!/usr/bin/env node
/* Prueba de punta a punta de la página privada (pagina.html) contra el arnés con un window.claude falso.

   Uso (Playwright ya instalado en tu máquina; no se instala nada):
     NODE_PATH=/ruta/a/node_modules node kit/skills/decisiones/artifact/tests/e2e.js
   Si Chromium no está instalado: npx playwright install chromium

   Arma el ejemplo con armar.py --artifact, levanta un servidor local solo para esta carpeta y recorre:
   cargar -> decidir las 4 tarjetas (Editar con campos, una opción, +info, deslizar) -> Enviar -> el documento
   respuestas/<clave> y su `texto` línea por línea -> doble toque -> variantes sin room, sin room ni comments,
   sin base, solo lectura, 390 px sin scroll horizontal y dibujos dentro de su recuadro. */
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

// 1. el documento sale de armar.py, igual que en la vida real
const salida = path.join(TMP, 'doc.json');
execFileSync('python3', [path.join(DEC, 'armar.py'), '--artifact', path.join(DEC, 'ejemplo', 'datos-artifact.json'), salida], { stdio: 'pipe' });
const DOC = JSON.parse(fs.readFileSync(salida, 'utf8'));
const EXTRA = JSON.parse(fs.readFileSync(path.join(AQUI, 'fixture-extra.json'), 'utf8'));
const CLAVE = DOC.clave;

// 2. servidor estático solo de la carpeta artifact/
const server = http.createServer((req, res) => {
  const f = path.join(RAIZ, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(RAIZ) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': f.endsWith('.html') ? 'text/html; charset=utf-8' : f.endsWith('.js') ? 'text/javascript' : 'application/json' });
  res.end(fs.readFileSync(f));
});

const sleep = ms => new Promise(r => setTimeout(r, ms));
let browser, base;
const errores = [];

async function abrir(params, opts) {
  opts = opts || {};
  const ctx = await browser.newContext({ viewport: { width: opts.ancho || 390, height: opts.alto || 844 }, hasTouch: false });
  const page = await ctx.newPage();
  page.on('pageerror', e => errores.push(String(e)));
  await page.goto(base + '/tests/arnes.html' + (params ? '?' + params : ''));
  await page.waitForSelector('#main');
  if (opts.seed !== false) {
    await page.evaluate(([c, d]) => window.__fake.seed('tandas/' + c, d), [CLAVE, DOC]);
  }
  return page;
}
async function swipe(page, dx) {
  const b = await page.locator('.card').boundingBox();
  const y = Math.max(b.y, 0) + 20;
  const x0 = dx > 0 ? b.x + 6 : b.x + b.width - 6;
  await page.mouse.move(x0, y); await page.mouse.down();
  await page.mouse.move(x0 + dx / 2, y, { steps: 4 }); await page.mouse.move(x0 + dx, y, { steps: 4 });
  await page.mouse.up();
}
const doc = (page, p) => page.evaluate(p => { const v = window.__fake.docs.get(p); return v ? JSON.parse(JSON.stringify(v)) : null; }, p);
const texto = page => page.locator('#main').textContent();   // textContent: no aplica el text-transform de los títulos
const sinScrollX = page => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 0.5);

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  base = 'http://127.0.0.1:' + server.address().port;
  try { browser = await chromium.launch(); }
  catch (e) { console.log('NO SE PUDO ABRIR CHROMIUM: ' + e.message.split('\n')[0] + '\n(instalalo con: npx playwright install chromium)'); process.exit(2); }

  /* ===== A. flujo completo, con room disponible ===== */
  console.log('\nA. flujo completo (room disponible)');
  let p = await abrir('');
  await p.waitForSelector('.tarj');
  let t = await texto(p);
  check('home: aparece la tarjeta de pendientes con su título', t.includes(DOC.titulo) && t.includes('Para decidir'), t.slice(0, 120));
  check('home: ninguna palabra técnica a la vista (tanda, doc, db, Artifact)', !/tanda|\bdoc\b|\bdb\b|artifact/i.test(t), t);
  check('home 390 px: sin scroll horizontal', await sinScrollX(p));
  await p.click('.tarj');
  await p.waitForSelector('.card');
  t = await texto(p);
  check('mazo: se ve la introducción y "Qué pasó hasta acá"', t.includes('Antes de empezar') && t.includes('Qué pasó hasta acá') && t.includes('Si no decidís'));
  check('mazo: nada viene premarcado', (await p.locator('[aria-pressed="true"]').count()) === 0);
  check('mazo: la recomendada (Va) lleva borde y está a la derecha', await p.evaluate(() => {
    const bs = [...document.querySelectorAll('.card .btn[data-r]')]; const va = bs.find(b => b.dataset.r === 'va'), no = bs.find(b => b.dataset.r === 'no');
    return va.classList.contains('rec') && !no.classList.contains('rec') && va.getBoundingClientRect().left > no.getBoundingClientRect().left;
  }));
  check('tarjeta 1: sin scroll horizontal a 390 px', await sinScrollX(p));
  check('tarjeta 1: el dibujo está dentro de su viewBox', await p.evaluate(() => {
    const svg = document.querySelector('.dib svg'); const [x, y, w, h] = svg.getAttribute('viewBox').split(' ').map(Number);
    return [...svg.querySelectorAll('rect,text,path')].every(e => { const b = e.getBBox(); return b.x >= x - 1 && b.y >= y - 1 && b.x + b.width <= x + w + 1 && b.y + b.height <= y + h + 1; });
  }));
  // Editar con campos
  await p.click('[data-x="editar"]');
  check('Editar: abre los campos precargados', (await p.inputValue('#f-1-precio')) === '4200' && (await p.inputValue('#f-1-desde')) === '2026-04-01');
  await p.fill('#f-1-precio', '4300');
  await p.click('#editar-listo');
  await p.waitForSelector('[data-op="mie"]');
  check('Editar: Listo pasa a la tarjeta 2', (await texto(p)).includes('Elegir el día del reparto'));
  // opción única
  check('tarjeta 2: la opción recomendada lleva borde', await p.locator('[data-op="mie"].rec').count() === 1);
  await p.click('[data-op="mie"]');
  await p.waitForSelector('[data-x="info"]');
  check('opción: elegirla pasa a la tarjeta 3', (await texto(p)).includes('sumar canales') || (await texto(p)).includes('Sumar canales'));
  // +info en la tarjeta 3
  await p.click('[data-x="info"]');
  await p.click('[data-info="Dibujo corto"]');
  await p.click('[data-info="Dibujo largo"]');
  check('+info: corto y largo no se suman', (await p.getAttribute('[data-info="Dibujo corto"]', 'aria-pressed')) === 'false' && (await p.getAttribute('[data-info="Dibujo largo"]', 'aria-pressed')) === 'true');
  await p.click('[data-info="Dibujo corto"]');
  await p.click('[data-info="Otro ejemplo"]');
  await p.fill('#c-3', 'no entiendo cuánto cuesta');
  await p.click('#info-listo');
  await p.waitForSelector('[data-r="rev"]');
  // revisión: deslizar a la derecha
  check('tarjeta 4 (revisión): botón «Revisado» y bloques', (await texto(p)).includes('Qué hice') && (await texto(p)).includes('Revisado'));
  await swipe(p, 160);
  await p.waitForSelector('#enviar');
  t = await texto(p);
  check('revisar: conteo (3 decididas, 1 para explicar de nuevo)', t.includes('3 decididas · 1 para explicar de nuevo · 0 para después · 0 sin marcar'), t.match(/\d+ decididas[^\n]*/));
  check('revisar: se ve el bloque «Para tu información» con el fyi', t.includes('Para tu información') && t.includes('Pedí presupuesto de harina'));
  await p.fill('#notas', 'gracias');
  await p.dblclick('#enviar');
  await p.waitForSelector('#avisar');
  await sleep(300);
  check('Enviar: doble toque escribe UNA sola vez', (await p.evaluate(c => window.__fake.escrituras['respuestas/' + c], CLAVE)) === 1, await p.evaluate(() => window.__fake.escrituras));
  const R = await doc(p, 'respuestas/' + CLAVE);
  const esperado = [
    '/brain-decide respuesta · ' + CLAVE,
    '1. va con cambios · Subir el pan de masa madre → Subir el precio · campos: precio=4300 (antes 4200)',
    '2. eligió mie · Elegir el día del reparto a cafés → Los miércoles',
    '3. rot · Sumar canales para recibir pedidos → Dibujo corto + Otro ejemplo · comentario: no entiendo cuánto cuesta',
    '4. revisado · Revisar la lista de precios nueva',
    'notas: gracias'
  ];
  const lineas = R.texto.split('\n');
  esperado.forEach((e, i) => check('texto línea ' + i, lineas[i] === e, { tiene: lineas[i], esperaba: e }));
  check('texto: ni una línea de más', lineas.length === esperado.length, lineas.length);
  check('respuestas: forma del documento', R.clave === CLAVE && R.por === 'u_prueba' && /^\d{4}-\d\d-\d\dT/.test(R.cuando) && R.notas === 'gracias' && R.items.length === 4);
  check('respuestas: campos / opcion / rot', R.items[0].respuesta === 'va con cambios' && R.items[0].campos.precio.antes === 4200 && R.items[0].campos.precio.ahora === '4300'
    && R.items[1].opcion === 'mie' && JSON.stringify(R.items[2].rot) === '["Dibujo corto","Otro ejemplo"]' && R.items[3].respuesta === 'revisado');
  t = await texto(p);
  check('aviso: botón principal y texto de ayuda', t.includes('Avisar a Claude') && t.includes('Claude te va a pedir que confirmes.'));
  check('aviso: siempre debajo "o volvé al chat" y Copiar respuesta', t.includes('o volvé al chat y escribí "listo"') && t.includes('Copiar respuesta'));
  check('aviso: no aparece el botón del comentario a la vez (UNA opción principal)', (await p.locator('#avisar-comentario').count()) === 0);
  await p.dblclick('#avisar');
  await sleep(250);
  const env = await p.evaluate(() => window.__fake.enviados);
  check('Avisar: doble toque manda UN solo aviso', env.length === 1, env.length);
  check('Avisar: deliver "send" y el texto canónico', env[0] && env[0].options.deliver === 'send' && env[0].data.texto === R.texto && env[0].data.clave === CLAVE);
  check('Avisar: resultado en criollo', (await texto(p)).includes('Claude recibió el aviso') || (await texto(p)).includes('Aviso enviado'));
  check('enviada: sin scroll horizontal', await sinScrollX(p));
  // el estado en vivo lo escribe Claude
  await p.evaluate(c => window.__fake.seed('estado/' + c, { texto: 'trabajando en tu respuesta', cuando: new Date().toISOString() }), CLAVE);
  await p.waitForFunction(() => document.querySelector('#estado-vivo') && document.querySelector('#estado-vivo').textContent.includes('trabajando'));
  check('estado en vivo: "Claude: trabajando…"', true);
  await p.evaluate(c => window.__fake.seed('tandas/' + c, Object.assign(window.__fake.docs.get('tandas/' + c), { estado: 'aplicada', resumen: '1. precio nuevo cargado\n2. reparto los miércoles' })), CLAVE);
  await p.click('#volver');
  await p.waitForSelector('.tarj');
  t = await texto(p);
  check('home: «Lo decidido» con el resumen que dejó Claude', t.includes('Lo decidido') && t.includes('precio nuevo cargado') && t.includes('Hecho'), t);
  check('suscripciones: una por consulta (3) sin repetir al navegar', (await p.evaluate(() => window.__fake.suscripciones)) === 3, await p.evaluate(() => window.__fake.suscripciones));
  await p.context().close();

  /* ===== B. sin room: aparece el comentario ===== */
  console.log('\nB. sin room (queda el comentario)');
  p = await abrir('room=null');
  await p.click('.tarj'); await p.waitForSelector('.card');
  await swipe(p, 160);       // 1: va (lo recomendado)
  await p.click('[data-op="mie"]');
  await p.click('[data-op="whatsapp"]'); await p.click('#listo-varias');
  await p.click('[data-r="rev"]');
  await p.waitForSelector('#enviar'); await p.click('#enviar'); await p.waitForSelector('#avisar-comentario');
  check('sin room: no hay «Avisar a Claude»', (await p.locator('#avisar').count()) === 0);
  check('sin room: «Avisarle a Claude con un comentario»', (await texto(p)).includes('Avisarle a Claude con un comentario'));
  await p.dblclick('#avisar-comentario'); await sleep(250);
  const com = await p.evaluate(() => window.__fake.comentarios);
  check('comentario: doble toque manda UNO, con la respuesta', com.length === 1 && com[0].text.includes('1. va · Subir el pan de masa madre → Subir el precio'), com);
  check('sin room: sigue el «o volvé al chat» y Copiar', (await texto(p)).includes('o volvé al chat y escribí "listo"') && (await p.locator('#copiar').count()) === 1);
  await p.context().close();

  /* ===== C. sin room ni comments ===== */
  console.log('\nC. sin room ni comments');
  p = await abrir('room=null&comments=null');
  await p.click('.tarj'); await p.waitForSelector('.card');
  await p.keyboard.press('ArrowRight');
  await p.click('[data-op="vie"]'); await p.click('[data-op="web"]'); await p.click('#listo-varias');
  await p.click('[data-r="rev"]'); await p.waitForSelector('#enviar'); await p.click('#enviar'); await p.waitForSelector('#copiar');
  t = await texto(p);
  check('sin nada: solo «volvé al chat» + Copiar', !t.includes('Avisar a Claude') && !t.includes('con un comentario') && t.includes('o volvé al chat y escribí "listo"') && t.includes('Copiar respuesta'));
  const R3 = await doc(p, 'respuestas/' + CLAVE);
  check('flecha derecha = Va, y varias elegidas', R3.texto.split('\n')[1].startsWith('1. va · ') && R3.texto.split('\n')[3] === '3. eligió web · Sumar canales para recibir pedidos → Formulario en la web');
  await p.context().close();

  /* ===== D. room que no puede enviar (no_session) y comments off ===== */
  console.log('\nD. room y comments no disponibles ahora');
  p = await abrir('canroom=no_session&cancomment=off');
  await p.click('.tarj'); await p.waitForSelector('.card');
  for (let i = 0; i < 2; i++) await p.keyboard.press('ArrowRight');
  await p.click('[data-op="web"]'); await p.click('#listo-varias'); await p.click('[data-r="rev"]');
  await p.waitForSelector('#enviar'); await p.click('#enviar'); await p.waitForSelector('#copiar');
  check('no_session + off: ninguna opción de aviso', (await p.locator('#avisar, #avisar-comentario').count()) === 0);
  await p.context().close();

  /* ===== E. sin base ===== */
  console.log('\nE. sin base (db null)');
  p = await abrir('db=null', { seed: false });
  await sleep(300);
  t = await texto(p);
  check('db null: mensaje en criollo y nada roto', t.includes('no se puede conectar con Claude') && (await p.locator('.tarj').count()) === 0, t);
  await p.context().close();

  /* ===== F. sin tarjetas todavía ===== */
  console.log('\nF. todavía no hay tarjetas');
  p = await abrir('', { seed: false });
  await sleep(300);
  check('vacío: "Todavía no hay nada para decidir…"', (await texto(p)).includes('Todavía no hay nada para decidir. Claude carga las tarjetas después de publicar esta página.'));
  await p.context().close();

  /* ===== G. la base no contesta ===== */
  console.log('\nG. la base no contesta en 10 s');
  p = await abrir('mudo=1', { seed: false });
  await sleep(10600);
  check('mudo: avisa que tarda', (await texto(p)).includes('tardando más de lo normal'));
  await p.context().close();

  /* ===== H. sin permiso de escritura ===== */
  console.log('\nH. solo lectura');
  p = await abrir('write=0');
  check('solo lectura: aviso en el home', (await texto(p)).includes('tu acceso no deja mandar respuestas'));
  await p.click('.tarj'); await p.waitForSelector('.card');
  await p.click('#ver-todas');
  await p.click('#ir-revisar');
  await p.waitForSelector('#enviar');
  check('solo lectura: Enviar deshabilitado y Copiar disponible', (await p.isDisabled('#enviar')) && (await texto(p)).includes('Copiar respuesta'));
  await p.context().close();

  /* ===== I. tarjetas sueltas: deslizar, comentario, regla, después, deshacer, lista, seguridad ===== */
  console.log('\nI. sí/no, varias, regla, después, deshacer, seguridad');
  p = await abrir('', { seed: false });
  await p.evaluate(d => window.__fake.seed('tandas/' + d.clave, d), EXTRA);
  await p.click('.tarj'); await p.waitForSelector('.card');
  await p.waitForTimeout(100);
  check('seguridad: el título con <img onerror> sale como texto', (await p.locator('h2 img').count()) === 0 && (await texto(p)).includes('<img src=x'));
  check('sección: se ve el nombre y el avance', (await texto(p)).includes('Stock · 0/2'));
  await swipe(p, -160);
  await p.waitForSelector('[data-r="va"]');
  check('deslizar a la izquierda = No va y pasa a la siguiente', (await texto(p)).includes('Liquidar las macetas rotas'));
  check('seguridad: el dibujo con <script>, onclick y foreignObject no corre ni se pinta', await p.evaluate(() => window.__xss === undefined && !document.querySelector('.dib script, .dib foreignObject, .dib [onclick]') && document.querySelectorAll('.dib rect').length === 2));
  check('botones con acciones propias', (await texto(p)).includes('Liquidarlas') && (await texto(p)).includes('Guardarlas'));
  await p.click('#deshacer');
  await p.waitForSelector('[data-r="no"]');
  check('Deshacer vuelve a la tarjeta 1 con su marca anterior borrada', (await texto(p)).includes('Pedir 40 helechos') && (await p.locator('[aria-pressed="true"]').count()) === 0);
  await p.click('[data-x="comentario"]');
  await p.fill('#c-1', 'solo si hay oferta');
  await p.click('[data-x="regla"]');
  await p.click('[data-r="va"]');
  await p.waitForSelector('[data-r="va"]');
  await p.click('[data-x="despues"]');
  await p.waitForSelector('[data-op="inv"]');
  await p.click('[data-op="inv"]'); await p.click('[data-op="otra1"]');
  check('varias: dos elegidas', (await p.locator('[data-op][aria-pressed="true"]').count()) === 2);
  await p.click('[data-op="otra1"]');
  await p.click('#listo-varias');
  await p.waitForSelector('#enviar');
  await p.click('#enviar'); await p.waitForSelector('#copiar');
  const R4 = (await doc(p, 'respuestas/' + EXTRA.clave)).texto.split('\n');
  check('línea con comentario y sufijo · regla', R4[1] === '1. va · Pedir 40 helechos <img src=x onerror="window.__xss=1"> · comentario: solo si hay oferta · regla', R4[1]);
  check('línea de Después', R4[2] === '2. después · Liquidar las macetas rotas', R4[2]);
  check('línea de varias', R4[3] === '3. eligió inv · Elegir las fotos de la portada → Invernadero', R4[3]);
  check('seguridad: nada se ejecutó en toda la sesión', await p.evaluate(() => window.__xss === undefined));
  await p.context().close();

  /* ===== J. 390 px: ninguna pantalla desborda, y modo oscuro legible ===== */
  console.log('\nJ. 390 px, lista y modo oscuro');
  p = await abrir('');
  await p.emulateMedia({ colorScheme: 'dark' });
  await p.click('.tarj'); await p.waitForSelector('.card');
  await p.click('#ver-todas'); await p.waitForSelector('.card >> nth=3');
  check('lista: las 4 tarjetas, sin scroll horizontal', (await p.locator('.card').count()) === 4 && (await sinScrollX(p)));
  const fondo = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
  check('oscuro: el fondo del body es oscuro', fondo === 'rgb(18, 20, 23)', fondo);
  check('oscuro: texto de la tarjeta claro', await p.evaluate(() => { const c = getComputedStyle(document.querySelector('.card h2')).color.match(/\d+/g).map(Number); return c[0] > 150; }));
  await p.context().close();

  check('sin errores de JavaScript en toda la corrida', errores.length === 0, errores);
  await browser.close(); server.close();
  console.log('\n' + pasan + ' pasan, ' + fallan + ' fallan');
  if (fallan) { console.log('Fallas: ' + fallos.join(' | ')); process.exit(1); }
})().catch(e => { console.error(e); process.exit(1); });

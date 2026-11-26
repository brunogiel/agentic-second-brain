#!/usr/bin/env node
/* Prueba de «mismo diseño»: la web real (con el arnés de botonera/tests/arnes) y la página de Claude (con el falso claude),
   con los MISMOS datos, a 390x844. Compara getComputedStyle y rectángulos de los elementos clave en el home de Decisiones, en la
   pantalla de contexto de un mazo y en una tarjeta abierta, y guarda las capturas (real-*.png y artifact-*.png).

   Uso: NODE_PATH=<carpeta con playwright> [OUT=<carpeta de capturas>] node kit/skills/decisiones/artifact/tests/mismo-diseno.js
   Sale con 1 si algún estilo difiere, o un rectángulo se corre más de 0,5 px, fuera de las diferencias declaradas. */
const fs = require('fs'), path = require('path'), http = require('http'), os = require('os');
const REPO = path.resolve(__dirname, '..', '..', '..', '..', '..');
const A = require(path.join(REPO, 'botonera', 'tests', 'arnes', 'arnes.js'));
const { chromium } = require('playwright');
const RAIZ = path.resolve(__dirname, '..');
const OUT = (process.env.OUT || fs.mkdtempSync(path.join(os.tmpdir(), 'mismo-diseno-'))).replace(/\/?$/, '/');
fs.mkdirSync(OUT, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));

const FX = A.escenario('simple');
// los mismos datos para la página de Claude: la `datos` de cada fila, más lo que agrega Claude
const DOCS = FX.filas.map(f => Object.assign({}, f.datos, { creada: f.row.created_at, actualizada: f.row.updated_at, estado: 'abierta', origen: { sesion_titulo: f.row.sesion_titulo } }));

const srv = http.createServer((q, r) => {
  const f = path.join(RAIZ, decodeURIComponent(q.url.split('?')[0]));
  if (!f.startsWith(RAIZ) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'content-type': f.endsWith('.html') ? 'text/html; charset=utf-8' : 'text/javascript' }); r.end(fs.readFileSync(f));
});

const PROPS = ['backgroundColor', 'color', 'fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing', 'textTransform', 'borderTopWidth', 'borderTopStyle', 'borderTopColor',
  'borderBottomWidth', 'borderBottomColor', 'borderLeftWidth', 'borderLeftColor', 'borderTopLeftRadius', 'borderBottomRightRadius', 'boxShadow',
  'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'display', 'opacity'];
const HOME = [
  ['body', 'body'], ['.wrap', '.wrap'], ['barra de arriba .top', '.top'], ['cartel de avisos .home-avisos (solo en la real)', '.home-avisos'],
  ['título .top h1 (el texto cambia)', '.top h1'], ['fila de categoría .hrow', '.hrow'], ['ícono de la categoría .hic', '.hrow .hic'],
  ['nombre .htx b', '.hrow .htx b'], ['subtítulo .hs', '.hrow .hs'], ['barra de avance .hbar', '.hrow .hbar'], ['play .hpl', '.hrow .hpl'],
  ['menú de abajo .tabs', '.tabs'], ['botones del menú .tabs-in', '.tabs-in'], ['pestaña Sesiones .tab', '.tab[data-tab="sesiones"]'],
  ['nombre de la pestaña .tab-n', '.tab[data-tab="sesiones"] .tab-n'], ['botón redondo .dec-btn', '.tab-dec .dec-btn'], ['punto rojo .bdg', '.tab-dec .bdg']];
const CARD = [
  ['contenedor .sw', '.sw'], ['tarjeta #sw-card', '#sw-card'], ['título de la tarjeta h2', '#sw-card h2'], ['botón No va .sw-act.no', '.sw-act.no'],
  ['botón Editar .sw-act.vcp', '.sw-act.vcp'], ['botón Va .sw-act.go', '.sw-act.go'], ['barra de botones .sw-acc', '.sw-acc'], ['pistas .sw-keys', '.sw-keys'],
  ['recomendación .sw-reco', '.sw-reco'], ['contexto de la tarjeta', '#sw-card p'], ['barra de abajo del mazo .sw-bar', '.sw-bar'], ['cabecera ‹ Salir', '.sw-top']];
// diferencias declaradas, solo de tamaño y nunca de estilo
const SOLO_TAMANO = {
  'body': 'el cartel de avisos del celu solo está en la web real (alto del body)',
  '.wrap': 'el cartel de avisos del celu solo está en la web real (alto del contenedor)',
  'título .top h1 (el texto cambia)': 'el título dice «Tus pendientes» en vez de «Botonera» (ancho del texto)'};
const AUSENTE_EN_CLAUDE = { 'cartel de avisos .home-avisos (solo en la real)': 'la página privada no puede registrar un service worker: no hay avisos al celu' };
const TOL = 0.5;

const medir = (page, lista) => page.evaluate(([lista, props]) => {
  const out = {};
  lista.forEach(([nom, sel]) => {
    const e = document.querySelector(sel);
    if (!e) { out[nom] = null; return; }
    const cs = getComputedStyle(e), r = e.getBoundingClientRect(), o = { _rect: [r.x, r.y, r.width, r.height] };
    props.forEach(p => { o[p] = cs[p]; });
    out[nom] = o;
  });
  return out;
}, [lista, PROPS]);

async function ctxCom(browser) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true, deviceScaleFactor: 1 });
  await ctx.route(u => !['127.0.0.1', 'localhost'].includes(u.hostname), r => {
    const h = new URL(r.request().url()).hostname;
    if (h === 'fonts.googleapis.com') return r.fulfill({ contentType: 'text/css', body: '' });
    if (h === 'fonts.gstatic.com') return r.fulfill({ contentType: 'font/woff2', body: '' });
    return r.abort();
  });
  return ctx;
}
async function recorrer(page, nombre) {   // home -> pantalla de contexto de un mazo -> primera tarjeta
  const r = {};
  await page.waitForSelector('.hrow', { timeout: 10000 }); await sleep(900);
  r.home = await medir(page, HOME);
  await page.screenshot({ path: OUT + nombre + '-home.png' });
  await page.tap('.hrow');
  await page.waitForSelector('.htanda', { timeout: 8000 }); await page.tap('.htanda');
  await page.waitForSelector('[data-a="empezar"]', { timeout: 8000 }); await sleep(500);
  r.ctx = await medir(page, CARD);
  await page.screenshot({ path: OUT + nombre + '-contexto.png' });
  await page.tap('[data-a="empezar"]'); await page.waitForSelector('.sw-act'); await sleep(900);
  r.card = await medir(page, CARD);
  await page.screenshot({ path: OUT + nombre + '-card.png' });
  return r;
}

(async () => {
  let ok = false, browser;
  try {
    await A.levantar();
    await new Promise(r => srv.listen(0, '127.0.0.1', r));
    const base = 'http://127.0.0.1:' + srv.address().port;
    browser = await chromium.launch();
    let real, art;
    {   // 1. la web real, con su arnés (que reemplaza supabase-js por un stub en memoria)
      const { ctx, page } = await A.ctxNuevo(FX, { ancho: 390, alto: 844 });
      await page.clock.setFixedTime(A.ahora);
      await page.goto(A.url());
      real = await recorrer(page, 'real');
      await ctx.close();
    }
    {   // 2. la página de Claude, con el falso claude
      const ctx = await ctxCom(browser);
      const page = await ctx.newPage();
      await page.clock.setFixedTime(A.ahora);
      await page.goto('http://127.0.0.1:' + srv.address().port + '/tests/arnes.html');
      await page.waitForSelector('#raiz');
      await page.evaluate(ds => ds.forEach(d => window.__fake.seed('tandas/' + d.clave, d)), DOCS);
      art = await recorrer(page, 'artifact');
      await ctx.close();
    }
    // 3. comparar
    let iguales = 0, declaradas = 0, malas = 0;
    const filas = [];
    function comparar(etapa, a, b) {
      Object.keys(a).forEach(nom => {
        const x = a[nom], y = b[nom];
        if (!x && !y) return;
        if (!x || !y) {
          if (!x && AUSENTE_EN_CLAUDE[nom]) return;
          if (x && !y && AUSENTE_EN_CLAUDE[nom]) { declaradas++; filas.push(`[${etapa}] ${nom}: solo en la real (declarada: ${AUSENTE_EN_CLAUDE[nom]})`); return; }
          malas++; filas.push(`[${etapa}] ${nom}: FALTA en ${x ? 'la página de Claude' : 'la web real'}`); return;
        }
        const estilo = Object.keys(x).filter(k => k !== '_rect' && x[k] !== y[k]);
        const dRect = x._rect.map((v, i) => Math.abs(v - y._rect[i]));
        const rectMal = Math.max(...dRect) > TOL;
        if (estilo.length) { malas++; filas.push(`[${etapa}] ${nom}: ESTILO DIFIERE: ` + estilo.map(k => `${k}: ${x[k]} vs ${y[k]}`).join(' | ')); }
        else if (rectMal && SOLO_TAMANO[nom]) { declaradas++; filas.push(`[${etapa}] ${nom}: mismo estilo; tamaño distinto (declarada: ${SOLO_TAMANO[nom]})`); }
        else if (rectMal) { malas++; filas.push(`[${etapa}] ${nom}: RECTÁNGULO DIFIERE ${JSON.stringify(x._rect.map(v => +v.toFixed(1)))} vs ${JSON.stringify(y._rect.map(v => +v.toFixed(1)))}`); }
        else { iguales++; filas.push(`[${etapa}] ${nom}: igual (${Object.keys(x).length - 1} propiedades + rectángulo)`); }
      });
    }
    comparar('home', real.home, art.home); comparar('contexto', real.ctx, art.ctx); comparar('tarjeta', real.card, art.card);
    filas.forEach(f => console.log(f));
    console.log(`\nIGUALES ${iguales} · DIFERENCIAS DECLARADAS ${declaradas} · DIFERENCIAS NO DECLARADAS ${malas}\nCapturas en ${OUT}`);
    ok = malas === 0;
  } finally {
    try { if (browser) await browser.close(); } catch (e) {}
    srv.close(); await A.cerrar();
  }
  process.exit(ok ? 0 : 1);
})().catch(e => { console.error(e); process.exit(1); });

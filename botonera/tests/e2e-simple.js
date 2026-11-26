/* E2E de la estructura de la web: 3 pestañas con el menú de abajo (Sesiones · Decidir al medio · Bloqueos), a 390 y a 1280 px,
 * abre en Decidir, una vista por vez (sin columnas), sin pestaña Input, sin «+ Nueva tarea», sin chip de mail, sin aviso de reuniones,
 * y CERO llamadas a RPC que no estén en la lista permitida (las `bm_*` de supabase/migrations/ más las del circuito).
 * Uso: NODE_PATH=<carpeta con playwright> node tests/e2e-simple.js   (un navegador, un archivo por vez)
 */
const A = require('./arnes/arnes');
const R = A.nuevoReporte('e2e-simple');
const PERMITIDAS = new Set(A.rpcPermitidas());
const PROHIBIDO = /Input|Nueva tarea|reuniones|escucha apagada|Para leer|Inbox|Tirar|Semana del|Dictar/i;

async function vista(ancho, alto, esc) {
  const { ctx, page } = await A.ctxNuevo(A.escenario('completo'), { ancho, alto, escritorio: ancho > 700 });
  try {
    await page.goto(A.url()); await page.waitForSelector('.hrow', { timeout: 10000 }); await A.sleep(500);
    const tabs = await page.evaluate(() => [...document.querySelectorAll('#tabs .tab')].map(b => ({ id: b.getAttribute('data-tab'), on: b.classList.contains('on'), dec: b.classList.contains('tab-dec') })));
    R.reg(`${esc}-tabs`, `${ancho}px: 3 pestañas en orden sesiones · decisiones · bloqueos, Decidir al medio y abierta`, tabs.map(t => t.id).join(',') === 'sesiones,decisiones,bloqueos' && tabs[1].dec && tabs[1].on && tabs.filter(t => t.on).length === 1, JSON.stringify(tabs));
    R.reg(`${esc}-barra`, `${ancho}px: el menú de abajo se ve y no hay scroll horizontal`, (await A.barraVisible(page)) && (await A.sinScrollHorizontal(page)));
    const cols = await page.evaluate(() => ({ tres: document.body.classList.contains('tres'), colNt: !!document.querySelector('.col-nt'), home: document.getElementById('home').getBoundingClientRect().width }));
    R.reg(`${esc}-columnas`, `${ancho}px: una vista por vez, sin columnas`, !cols.tres && !cols.colNt && cols.home <= 800, JSON.stringify(cols));
    const vistos = {};
    for (const t of ['sesiones', 'decisiones', 'bloqueos']) {
      await page.tap(`[data-tab="${t}"]`); await A.sleep(500);
      const txt = await page.evaluate(() => document.getElementById('home').innerText);
      vistos[t] = txt;
      const ok = !PROHIBIDO.test(txt) && (await A.barraVisible(page)) && (await A.sinScrollHorizontal(page));
      R.reg(`${esc}-${t}`, `${ancho}px: pestaña ${t} sin restos de lo que no va, menú visible, sin scroll horizontal`, ok, ok ? '' : txt.slice(0, 200));
    }
    const unaPorVez = /Trabajo/.test(vistos.decisiones) && !/Trabajando ahora|Bloqueos ·/i.test(vistos.decisiones) && /Trabajando ahora/i.test(vistos.sesiones) && !/Mazo de|Trabajo\n/.test(vistos.sesiones) && /Bloqueos · /.test(vistos.bloqueos);
    R.reg(`${esc}-una-vez`, `${ancho}px: cada pestaña muestra solo lo suyo`, unaPorVez, unaPorVez ? '' : JSON.stringify(vistos).slice(0, 700));
    const body = await page.evaluate(() => document.body.innerText);
    R.reg(`${esc}-chip`, `${ancho}px: sin botón «+ Nueva tarea», sin pestaña Input`, !(await page.locator('#b-nt,[data-pt="nt-abrir"],[data-pt="nt-preset"],[data-tab="leer"]').count()) && !/Nueva tarea/.test(body));
    const rpcs = await page.evaluate(() => window.__rpcs.map(r => r.nombre));
    const fuera = [...new Set(rpcs.filter(n => !PERMITIDAS.has(n)))];
    R.reg(`${esc}-rpc`, `${ancho}px: cero llamadas a RPC fuera de la lista permitida (${[...new Set(rpcs)].length} distintas)`, fuera.length === 0, fuera.length ? 'fuera de lista: ' + fuera.join(', ') : [...new Set(rpcs)].sort().join(', '));
    R.reg(`${esc}-errores`, `${ancho}px: sin errores de página ni de consola`, page.errores.length === 0 && page.consola.length === 0, page.errores.concat(page.consola).join(' | '));
  } finally { await ctx.close(); }
}

(async () => {
  let ok = false;
  try {
    await A.levantar();
    await vista(390, 844, 'm');
    await vista(1280, 900, 'd');
  } finally { ok = R.fin(); await A.cerrar(); }
  process.exit(ok ? 0 : 1);
})();

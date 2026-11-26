/* E2E del link «Abrir la conversación»: solo se arma para sesiones de la app de Claude Code (session_id `local_…`).
 * Otra sesión (Codex, Cursor, `bot-…`, ninguna) no lleva link ni un claude:// roto. En un dispositivo táctil el link se oculta (hover:none y pointer:coarse).
 * Uso: NODE_PATH=<carpeta con playwright> node tests/e2e-link.js
 */
const A = require('./arnes/arnes');
const R = A.nuevoReporte('e2e-link');
const SIDS = { 'local_x': 'claude://claude.ai/epitaxy/local_x', 'codex-x': null, 'bot-pausa': null, '': null };

async function abrirFila(page, raton) {
  const toc = l => raton ? l.click() : l.tap();
  await page.goto(A.url()); await page.waitForSelector('#tabs', { timeout: 10000 });
  await toc(page.locator('[data-tab="sesiones"]')); await page.waitForSelector('.hfin', { timeout: 6000 });
  await toc(page.locator('.hfin').first()); await A.sleep(300);
}
function esc(sid) {
  const e = A.escenario('vacio');
  e.filas = [A.fila('e2e-l', 'Tanda con sesión', A.cards('l', 1), { estado: 'recibida', received_at: A.iso(5 * 60e3), decided_at: A.iso(9 * 60e3), trab_desde: A.iso(5 * 60e3), trab_recibida: true, session_id: sid })];
  return e;
}
(async () => {
  let ok = false;
  try {
    await A.levantar();
    for (const [sid, esperado] of Object.entries(SIDS)) {
      const { ctx, page } = await A.ctxNuevo(esc(sid), { ancho: 1280, alto: 900, escritorio: true, sinTouch: true });
      try {
        await abrirFila(page, true);
        const links = await page.evaluate(() => [...document.querySelectorAll('a.lnk-ses')].map(a => ({ href: a.getAttribute('href'), visible: a.getBoundingClientRect().width > 0 })));
        const todos = await page.evaluate(() => [...document.querySelectorAll('a')].map(a => a.getAttribute('href') || ''));
        const bien = esperado ? links.length === 1 && links[0].href === esperado && links[0].visible : links.length === 0 && !todos.some(h => /^claude:/.test(h));
        R.reg('escritorio-' + (sid || 'sin-id'), `Escritorio, session_id «${sid || '(ninguno)'}»: ${esperado ? 'link ' + esperado : 'sin link ni claude:// roto'}`, bien, JSON.stringify(links));
      } finally { await ctx.close(); }
    }
    // dispositivo táctil: la regla CSS oculta el link (queda en el DOM con display:none)
    const { ctx, page } = await A.ctxNuevo(esc('local_x'), { ancho: 390, alto: 844 });   // isMobile + hasTouch: hover:none y pointer:coarse
    try {
      await abrirFila(page);
      const m = await page.evaluate(() => ({ coarse: matchMedia('(hover:none) and (pointer:coarse)').matches, disp: [...document.querySelectorAll('a.lnk-ses')].map(a => getComputedStyle(a).display) }));
      R.reg('tactil', 'Con emulación táctil el link existe pero está oculto (display:none)', m.coarse && m.disp.length === 1 && m.disp[0] === 'none', JSON.stringify(m));
      await page.goto(A.url() + '?linkcelu=1'); await page.waitForSelector('#tabs'); await page.tap('[data-tab="sesiones"]'); await page.waitForSelector('.hfin'); await page.locator('.hfin').first().tap(); await A.sleep(300);
      const v = await page.evaluate(() => [...document.querySelectorAll('a.lnk-ses')].map(a => getComputedStyle(a).display));
      R.reg('linkcelu', 'Con ?linkcelu=1 el link se muestra aunque sea táctil', v.length === 1 && v[0] !== 'none', JSON.stringify(v));
      R.reg('errores', 'Sin errores de página ni de consola', page.errores.length === 0 && page.consola.length === 0, page.errores.concat(page.consola).join(' | '));
    } finally { await ctx.close(); }
  } finally { ok = R.fin(); await A.cerrar(); }
  process.exit(ok ? 0 : 1);
})();

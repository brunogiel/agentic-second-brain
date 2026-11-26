/* E2E de la card: detalle plegado, imagen a pantalla completa, rótulos neutros («El agente recomienda», «Si no decidís»),
 * «Después» (ya no «Al inbox»), «Ya no aplica» fuera del mazo y la respuesta que sale.
 * Uso: NODE_PATH=<carpeta con playwright> node tests/e2e-card.js
 */
const A = require('./arnes/arnes');
const R = A.nuevoReporte('e2e-card');
(async () => {
  let ok = false;
  try {
    await A.levantar();
    const { ctx, page } = await A.ctxNuevo(A.escenario('card'));
    try {
      await A.entrarAlMazo(page);
      const sw = await page.evaluate(() => document.querySelector('.sw').innerText);
      R.reg('rotulos', 'La card dice «El agente recomienda» y «Si no decidís»; ningún nombre propio', /El agente recomienda: Hacerlo/.test(sw) && /Si no decidís: Queda como está/.test(sw) && !/BRUNO|CLAUDE|Bruno/.test(sw), sw.slice(0, 200));
      R.reg('despues', 'Existe «Después» y no «Al inbox»', /Después/.test(sw) && !/Al inbox/i.test(sw));
      const det = await page.evaluate(() => { const d = document.querySelector('#sw-card details, .sw-card details, .sw details'); return d ? { abierto: d.open, txt: d.querySelector('summary').innerText } : null; });
      R.reg('detalle', 'El detalle viene plegado bajo «Ver el detalle»', !!det && !det.abierto && /Ver el detalle/.test(det.txt), JSON.stringify(det));
      const imgs = await page.evaluate(() => [...document.querySelectorAll('.sw img')].filter(i => /^data:image\/png/.test(i.src)).length);
      R.reg('imagen', 'La card muestra su imagen', imgs >= 1, 'imágenes data: ' + imgs);
      await page.locator('.sw .sw-img').first().tap(); await A.sleep(500);
      const abierta = await page.locator('.img-full').first().isVisible().catch(() => false);
      R.reg('imagen-full', 'Tocar la imagen la abre a pantalla completa y Escape la cierra', abierta && (await (async () => { await page.keyboard.press('Escape'); await A.sleep(400); return !(await page.locator('.img-full').first().isVisible().catch(() => false)); })()));
      await A.libre(page);
      // «Ya no aplica»: la card 3 no entra al mazo
      const marcas = await page.evaluate(() => Object.keys(window.__swipe().marcas));
      R.reg('ya-no-aplica', 'La card reemplazada no está en el mazo (quedan 3 de 4)', marcas.length === 3 && !marcas.includes('e2e-card|3'), marcas.join(','));
      // Después: marca interna «después»
      await A.tap(page, '[data-a="despues"]'); await A.libre(page);
      const m1 = await page.evaluate(() => window.__swipe().marcas['e2e-card|1']);
      R.reg('marca-despues', '«Después» marca la card 1 como «de»', m1 && m1.m === 'de', JSON.stringify(m1));
      await A.tap(page, '[data-a="go"]'); await A.libre(page);
      await A.tap(page, '[data-a="no"]'); await A.libre(page);
      const resp = await A.enviar(page);
      const lineas = resp.split('\n');
      R.reg('respuesta', 'La respuesta sale «1. después · …», «2. va · …», «4. no va · …»', /^1\. después · Subir el precio/.test(lineas.find(l => l.startsWith('1. ')) || '') && /^2\. va · /.test(lineas.find(l => l.startsWith('2. ')) || '') && /^4\. no va · /.test(lineas.find(l => l.startsWith('4. ')) || '') && !lineas.some(l => l.startsWith('3. ')), resp);
      R.reg('errores', 'Sin pageerror ni console.error', page.errores.length === 0 && page.consola.length === 0, page.errores.concat(page.consola).join(' | '));
    } finally { await ctx.close(); }
  } finally { ok = R.fin(); await A.cerrar(); }
  process.exit(ok ? 0 : 1);
})();

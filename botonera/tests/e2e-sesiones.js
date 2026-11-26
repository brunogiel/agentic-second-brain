/* E2E de Sesiones (seguimiento): «Trabajando ahora» (en curso + En vuelo de bm_seguimiento), «Hechas hoy», Archivo, el detalle de cada fila,
 * el link «Abrir la conversación» y Archivar con Deshacer (la RPC bm_archivar_pin sale recién a los 5 s).
 * Sin tareas del celu, sin «Que la retome otra», sin aviso de escucha ni de reuniones.
 * Uso: NODE_PATH=<carpeta con playwright> node tests/e2e-sesiones.js
 */
const A = require('./arnes/arnes');
const R = A.nuevoReporte('e2e-sesiones');
const home = page => page.evaluate(() => document.getElementById('home').innerText);
async function abrir(page) { await page.goto(A.url()); await page.waitForSelector('#tabs', { timeout: 10000 }); await page.tap('[data-tab="sesiones"]'); await page.waitForSelector('.hfin', { timeout: 6000 }); await A.sleep(400); }

(async () => {
  let ok = false;
  try {
    await A.levantar();
    let { ctx, page } = await A.ctxNuevo(A.escenario('sesiones'));
    try {
      await abrir(page);
      const t = await home(page);
      R.reg('grupos', '«Trabajando ahora · 5» (4 tandas + 1 en vuelo) y «Hechas hoy · 1»; la trabada no está acá', /Trabajando ahora · 5/i.test(t) && /Hechas hoy · 1/i.test(t) && !/Tanda trabada/.test(t) && /Armando el informe/.test(t), t.slice(0, 260));
      R.reg('archivo', 'Hay un «Archivo · 1 ›» al pie', /Archivo · 1/.test(t));
      R.reg('sin-resto', 'Sin «escucha», «reuniones», «retome» ni «Nueva tarea»', !/escucha|reuniones|retome|Nueva tarea|Retomando|En cola/i.test(t), t.slice(0, 100));
      const filas = await A.textos(page, '.hfin b');
      R.reg('estados', 'Cada fila lleva su pastilla (Te espera, Trabajando, Mandada)', /Te espera/.test(t) && /Mandada/.test(t) && filas.length === 6, filas.join(' | '));
      // detalle de una tanda recibida
      await page.locator('.hfin', { hasText: 'Cambiar el precio' }).tap(); await A.sleep(300);
      const ab = await page.evaluate(() => document.querySelector('.hfin-ab').innerText);
      const href = await page.locator('.hfin-ab .lnk-ses').getAttribute('href').catch(() => null);
      R.reg('detalle', 'Abrir una fila dice «El agente está trabajando · hace N min» y trae el link a la conversación y «Archivar»', /El agente está trabajando · hace \d+ min/.test(ab) && href === 'claude://claude.ai/epitaxy/local_sesion-e2e' && /Archivar/.test(ab), ab.replace(/\n/g, ' / ') + ' · ' + href);
      // En vuelo
      await page.locator('.hfin', { hasText: 'Armando el informe' }).tap(); await A.sleep(300);
      const vu = await page.locator('.hfin-ab', { hasText: 'Armando el informe' }).innerText();
      R.reg('vuelo', 'La fila En vuelo muestra qué hace, lo próximo y la última noticia', /Ordena los números · próximo: Publicar la card/.test(vu) && /Última noticia: hace 4 min/.test(vu) && !/Archivar/.test(vu), vu.replace(/\n/g, ' / '));
      // Archivo
      await page.locator('.arch-l').tap(); await A.sleep(300);
      const t2 = await home(page);
      R.reg('archivo-abre', 'Tocar «Archivo» muestra la tanda archivada', /Una tanda de hace una semana/.test(t2), t2.slice(-160));
      R.reg('errores-1', 'Sin errores de página ni de consola', page.errores.length === 0 && page.consola.length === 0, page.errores.concat(page.consola).join(' | '));
    } finally { await ctx.close(); }

    // Archivar con Deshacer: no llama a la RPC; sin Deshacer, la llama a los 5 s
    ({ ctx, page } = await A.ctxNuevo(A.escenario('sesiones')));
    try {
      await abrir(page);
      await page.locator('.hfin', { hasText: 'Revisar los avisos' }).tap(); await A.sleep(300);
      await page.locator('.hfin-ab .hseg-b').tap(); await A.sleep(400);
      const t = await home(page);
      const toast = await page.locator('.snz-toast').first().innerText().catch(() => '');
      R.reg('archivar-sale', 'Archivar saca la fila al toque y avisa «Archivada · … Deshacer»', !/Revisar los avisos/.test(t.split('Archivo')[0]) && /Archivada · Revisar/.test(toast) && /Deshacer/.test(toast), toast.replace(/\n/g, ' '));
      await page.locator('[data-seg="deshacer"]').tap(); await A.sleep(400);
      R.reg('deshacer', 'Deshacer devuelve la fila y no llama a bm_archivar_pin', /Revisar los avisos/.test(await home(page)) && (await page.evaluate(() => window.__archivadas.length)) === 0);
      await page.locator('.hfin-ab .hseg-b').tap();   // la fila sigue abierta tras Deshacer
      await A.sleep(5800);
      const arch = await page.evaluate(() => window.__archivadas.slice());
      R.reg('archivar-rpc', 'Sin Deshacer, a los 5 s llama a bm_archivar_pin con la clave de la tanda', arch.length === 1 && arch[0] === 'e2e-decidida', JSON.stringify(arch));
      R.reg('errores-2', 'Sin errores de página ni de consola', page.errores.length === 0 && page.consola.length === 0, page.errores.concat(page.consola).join(' | '));
    } finally { await ctx.close(); }
  } finally { ok = R.fin(); await A.cerrar(); }
  process.exit(ok ? 0 : 1);
})();

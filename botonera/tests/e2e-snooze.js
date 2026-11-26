/* E2E del snooze y de «Ahora no»: fila «Snoozeadas», sheet «¿Cuándo vuelve?», aviso con Deshacer, Despertar ahora,
 * y «Ahora no» (las cards sin marcar van a «Después» y la respuesta sale con su nota).
 * Uso: NODE_PATH=<carpeta con playwright> node tests/e2e-snooze.js
 */
const A = require('./arnes/arnes');
const R = A.nuevoReporte('e2e-snooze');

async function abrirA(page) {
  await page.goto(A.url()); await page.waitForSelector('.hrow', { timeout: 10000 });
  await page.tap('.hrow'); await page.waitForSelector('.htanda', { timeout: 6000 });
  await page.tap('.htanda'); await page.waitForSelector('[data-a="snooze"]', { timeout: 8000 }); await A.sleep(300);
}
const rpcs = (page, n) => page.evaluate(x => window.__rpcs.filter(r => r.nombre === x).map(r => r.params), n);

(async () => {
  let ok = false;
  try {
    await A.levantar();
    // 1) fila Snoozeadas en el home y Despertar ahora
    let { ctx, page } = await A.ctxNuevo(A.escenario('snooze'));
    try {
      await page.goto(A.url()); await page.waitForSelector('.hrow', { timeout: 10000 }); await A.sleep(400);
      const txt = await page.evaluate(() => document.getElementById('home').innerText);
      R.reg('fila', 'El home muestra «Snoozeadas (1)» con «Despertar ahora»', /Snoozeadas \(1\)/.test(txt) && /Despertar ahora/.test(txt) && /Vuelve/.test(txt), txt.slice(0, 200));
      await page.tap('[data-home="despertar"]'); await A.sleep(900);
      const d = await rpcs(page, 'bm_despertar');
      const txt2 = await page.evaluate(() => document.getElementById('home').innerText);
      R.reg('despertar', 'Despertar ahora llama a bm_despertar y la botonera vuelve a «Por decidir»', d.length === 1 && d[0].p_clave === 'e2e-snz-d' && !/Snoozeadas/.test(txt2) && /3 mazos/.test(txt2), JSON.stringify(d) + ' · ' + txt2.slice(0, 120));
      R.reg('errores-1', 'Sin errores de página ni de consola', page.errores.length === 0 && page.consola.length === 0, page.errores.concat(page.consola).join(' | '));
    } finally { await ctx.close(); }

    // 2) snooze desde la card negra y Deshacer
    ({ ctx, page } = await A.ctxNuevo(A.escenario('snooze')));
    try {
      await abrirA(page);
      await A.tap(page, '[data-a="snooze"]'); await page.waitForSelector('.sw-snz-op', { timeout: 5000 }); await A.sleep(300);
      const ops = await A.textos(page, '.sw-snz-op .rot');
      const hoja = await page.evaluate(() => document.querySelector('.sw-snz-hoja').innerText);
      R.reg('hoja', 'La hoja «¿Cuándo vuelve?» ofrece opciones y «Ahora no»', ops.length >= 2 && ops.includes('Mañana') && /Ahora no/.test(hoja) && /a Después/.test(hoja) && !/Diferido|inbox/i.test(hoja), ops.join(' | '));
      await A.tap(page, '[data-id="manana"]'); await A.sleep(900);
      const s = await rpcs(page, 'bm_snoozear');
      R.reg('snoozear', 'Elegir «Mañana» llama a bm_snoozear con la clave y una hora futura', s.length === 1 && s[0].p_clave === 'e2e-snz-a' && Date.parse(s[0].p_hasta) > Date.now(), JSON.stringify(s));
      const aviso = await page.locator('.snz-toast').first().innerText().catch(() => '');
      R.reg('aviso', 'Aparece «Snoozeada hasta … · Deshacer»', /Snoozeada hasta/.test(aviso) && /Deshacer/.test(aviso), aviso);
      await page.locator('[data-snz="deshacer"]').first().tap(); await A.sleep(900);
      const dd = await rpcs(page, 'bm_despertar');
      R.reg('deshacer', 'Deshacer llama a bm_despertar de la misma botonera', dd.length >= 1 && dd[dd.length - 1].p_clave === 'e2e-snz-a', JSON.stringify(dd));
      R.reg('errores-2', 'Sin errores de página ni de consola', page.errores.length === 0 && page.consola.length === 0, page.errores.concat(page.consola).join(' | '));
    } finally { await ctx.close(); }

    // 3) «Ahora no» desde la card negra: las 3 cards sin marcar van a Después
    ({ ctx, page } = await A.ctxNuevo(A.escenario('snooze')));
    try {
      await abrirA(page);
      await A.tap(page, '[data-a="snooze"]');
      await page.waitForSelector('.sw-snz-ahora', { timeout: 5000 }); await A.sleep(300);
      const txtAh = await page.locator('.sw-snz-ahora').innerText();
      R.reg('ahora-no-txt', '«Ahora no» dice cuántas cards sin marcar van a Después', /3 cards sin marcar van a Después/.test(txtAh), txtAh);
      await A.tap(page, '.sw-snz-ahora'); await A.sleep(1200);
      const env = await page.evaluate(() => window.__envios.slice());
      const r = env.length ? env[env.length - 1].p_respuesta : '';
      R.reg('ahora-no-rpc', '«Ahora no» manda 1, 2 y 3 «después» y la nota «Ahora no · seguí sin…»', env.length === 1 && /(^|\n)1\. después · /.test(r) && /(^|\n)2\. después · /.test(r) && /(^|\n)3\. después · /.test(r) && /Ahora no · seguí sin las respuestas de estas 3 cards/.test(r) && /a Después/.test(r) && !/Diferido|inbox/i.test(r), r);
      R.reg('errores-3', 'Sin errores de página ni de consola', page.errores.length === 0 && page.consola.length === 0, page.errores.concat(page.consola).join(' | '));
    } finally { await ctx.close(); }
  } finally { ok = R.fin(); await A.cerrar(); }
  process.exit(ok ? 0 : 1);
})();

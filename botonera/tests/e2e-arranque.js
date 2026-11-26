/* E2E de arranque: PIN (stub) -> home -> cada pestaña -> abrir un mazo -> decidir -> enviar -> salir.
 * Con page.on('pageerror') y console.error en 0, y un chequeo que falla si la página llama a una RPC que no esté en la lista permitida.
 * También prueba la pantalla del PIN: PIN incorrecto, y el bloqueo temporal con y sin el tiempo en la respuesta de bm_entrar.
 * Uso: NODE_PATH=<carpeta con playwright> node tests/e2e-arranque.js
 */
const A = require('./arnes/arnes');
const R = A.nuevoReporte('e2e-arranque');
const PERMITIDAS = new Set(A.rpcPermitidas());

async function pin(page, v) { await page.fill('#i-pin', v); await A.sleep(500); }

async function flujo() {
  const { ctx, page } = await A.ctxNuevo(A.escenario('completo'), { sinToken: true });
  try {
    await page.goto(A.url()); await page.waitForSelector('#i-pin', { timeout: 10000 });
    R.reg('pin-pantalla', 'Sin sesión pide el PIN y no llama a ninguna RPC', (await page.evaluate(() => window.__rpcs.length)) === 0);
    await pin(page, '9999');
    const m1 = await page.locator('#aviso').innerText();
    R.reg('pin-malo', 'PIN incorrecto: dice cuántos intentos quedan', /Te quedan 9 intentos/.test(m1), m1);
    await pin(page, '1234');
    await page.waitForSelector('.hrow', { timeout: 10000 });
    R.reg('home', 'Con el PIN bueno entra al home en Decisiones', (await page.evaluate(() => window.__pestanas().tab)) === 'decisiones');
    for (const t of ['sesiones', 'bloqueos', 'decisiones']) {
      await page.tap(`[data-tab="${t}"]`); await A.sleep(450);
      R.reg('tab-' + t, `Pestaña ${t} abre`, (await page.evaluate(() => window.__pestanas().tab)) === t);
    }
    await A.entrarAlMazo(page, '.hrow:has-text("Casa")');
    await A.tap(page, '[data-a="go"]'); await A.libre(page);
    const resp = await A.enviar(page);
    R.reg('decidir', 'Abrir un mazo, decidir y enviar: bm_decidir_pin recibe «1. va · …»', /(^|\n)1\. va · Card c1/.test(resp), resp);
    await A.sleep(600);
    await A.tap(page, '[data-a="home"]'); await page.waitForSelector('#b-salir', { state: 'visible', timeout: 8000 }); await A.sleep(400);
    await page.tap('#b-salir'); await page.waitForSelector('#i-pin', { timeout: 8000 });
    const rpcs = await page.evaluate(() => window.__rpcs.map(r => r.nombre));
    R.reg('salir', 'Salir llama a bm_salir y vuelve a la pantalla del PIN', rpcs.includes('bm_salir') && !(await page.evaluate(() => localStorage.getItem('bm-token'))));
    const fuera = [...new Set(rpcs.filter(n => !PERMITIDAS.has(n)))];
    R.reg('rpc', 'Cero RPC fuera de la lista permitida', fuera.length === 0, fuera.length ? fuera.join(', ') : [...new Set(rpcs)].sort().join(', '));
    R.reg('errores', 'Sin pageerror ni console.error', page.errores.length === 0 && page.consola.length === 0, page.errores.concat(page.consola).join(' | '));
    R.reg('terceros', 'Lo único que pide a terceros son las fuentes de Google', [...(ctx.terceros || [])].every(h => /^fonts\.(googleapis|gstatic)\.com$/.test(h)), [...(ctx.terceros || [])].join(', '));
  } finally { await ctx.close(); }
}

async function bloqueo(nombre, resp, regex) {
  const { ctx, page } = await A.ctxNuevo(A.escenario('simple', { bloqueo: resp }), { sinToken: true });
  try {
    await page.goto(A.url()); await page.waitForSelector('#i-pin', { timeout: 10000 });
    await pin(page, '1234');
    const m = await page.locator('#aviso').innerText();
    R.reg(nombre, `Bloqueo del PIN: ${nombre}`, regex.test(m) && !(await page.locator('.hrow').count()) && page.errores.length === 0, m);
  } finally { await ctx.close(); }
}

(async () => {
  let ok = false;
  try {
    await A.levantar();
    await flujo();
    await bloqueo('con-espera', { ok: false, motivo: 'bloqueado', hasta: new Date(Date.now() + 15 * 60e3).toISOString(), espera_seg: 900 }, /^Demasiados intentos\. Probá de nuevo en 15 minutos\. .*pin\.py desbloquear/);
    await bloqueo('con-hasta', { ok: false, motivo: 'bloqueado', hasta: new Date(Date.now() + 30 * 60e3 + 5000).toISOString() }, /^Demasiados intentos\. Probá de nuevo en 31 minutos\. .*pin\.py desbloquear/);
    await bloqueo('sin-tiempo', { ok: false, motivo: 'bloqueado' }, /^Demasiados intentos\. Probá de nuevo más tarde\. .*pin\.py desbloquear/);
  } finally { ok = R.fin(); await A.cerrar(); }
  process.exit(ok ? 0 : 1);
})();

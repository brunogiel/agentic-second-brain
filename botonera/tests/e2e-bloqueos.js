/* E2E de Bloqueos: «Con error» (Visto), «Te esperan a vos» (Listo / No puedo / Comentar con el contrato de bm_acciones_lista,
 * bm_accion_hecha y bm_accion_marcar) y las trabadas (solo «Archivar»; sin «Que la retome otra», sin «Nueva tarea»).
 * Uso: NODE_PATH=<carpeta con playwright> node tests/e2e-bloqueos.js
 */
const A = require('./arnes/arnes');
const R = A.nuevoReporte('e2e-bloqueos');
const home = page => page.evaluate(() => document.getElementById('home').innerText);
async function abrir(page) { await page.goto(A.url()); await page.waitForSelector('#tabs', { timeout: 10000 }); await A.sleep(500); await page.tap('[data-tab="bloqueos"]'); await page.waitForSelector('.hac', { timeout: 6000 }); await A.sleep(400); }
const cierre = (page, n) => R.reg(n, 'Sin errores de página ni de consola', page.errores.length === 0 && page.consola.length === 0, page.errores.concat(page.consola).join(' | '));

(async () => {
  let ok = false;
  try {
    await A.levantar();
    let { ctx, page } = await A.ctxNuevo(A.escenario('bloqueos'));
    try {
      await abrir(page);
      const t = await home(page);
      const nBadge = await page.evaluate(() => window.__pestanas().regN);
      R.reg('lista', 'Bloqueos lista errores, obstáculos y la trabada, y el número de la pestaña es 5', /Con error · 2/.test(t) && /Bloqueos · 5/.test(t) && /Pegar la llave de la API/.test(t) && /Tanda trabada/.test(t) && nBadge === 5, `regN=${nBadge}`);
      R.reg('orden', 'Los obstáculos que frenan trabajo van arriba', t.indexOf('Pegar la llave') < t.indexOf('Correr la migración'));
      R.reg('frena', 'Muestra «Frena: …», el link https con su sitio y el comando con «Copiar»', /Frena: la publicación del informe/.test(t) && /example\.com\/llaves ↗/.test(t) && /supabase db push/.test(t) && /Copiar/.test(t));
      const rel = await page.locator('.hac-link').first().getAttribute('rel'), tgt = await page.locator('.hac-link').first().getAttribute('target');
      R.reg('link', 'El link se abre en pestaña nueva con noopener', tgt === '_blank' && /noopener/.test(rel));
      const trab = await page.locator('.hac', { hasText: 'Tanda trabada' }).innerText();
      R.reg('trabada', 'La trabada trae solo «Archivar» (sin «Que la retome otra»)', /Archivar/.test(trab) && !/retome/i.test(trab) && /Se frenó · sin novedad hace 30 h/.test(trab), trab.replace(/\n/g, ' / '));
      R.reg('sin-nt', 'Sin «Nueva tarea», sin escucha ni reuniones', !/Nueva tarea|escucha|reuniones/i.test(t) && !(await page.locator('#b-nt').count()));
      // Visto
      await page.locator('.herr-v').first().tap(); await A.sleep(500);
      R.reg('visto', '«Visto» saca el error y llama a bm_error_visto', (await page.evaluate(() => window.__visto)).join() === '1' && /Con error · 1/.test(await home(page)));
      // Listo con comentario
      await page.tap('[data-pt="acc-hecho"][data-k="item|7"]'); await A.sleep(300);
      await page.locator('.lac-ta').fill('Ya la pegué'); await A.sleep(100);
      await page.tap('[data-pt="acc-mandar"][data-k="item|7"]'); await A.sleep(900);
      const a1 = await page.evaluate(() => window.__acciones.slice());
      const rp = await page.evaluate(() => window.__rpcs.filter(r => r.nombre === 'bm_accion_hecha').map(r => r.params));
      R.reg('listo', '«Listo» + comentario llama a bm_accion_hecha (origen item, ref «7») y la fila sale', rp.length === 1 && rp[0].p_origen === 'item' && rp[0].p_ref === '7' && rp[0].p_comentario === 'Ya la pegué' && !/Pegar la llave/.test(await home(page)), JSON.stringify(rp));
      const toast = await page.locator('.snz-toast').first().innerText().catch(() => '');
      R.reg('toast', 'El aviso dice «Listo: el agente sigue solo» (sin hablar de escucha)', /Listo: el agente sigue solo/.test(toast), toast);
      // No puedo
      await page.tap('[data-pt="acc-nopuedo"][data-k="item|8"]'); await A.sleep(300);
      await page.locator('.lac-ta').fill('No tengo permisos'); await A.sleep(100);
      await page.tap('[data-pt="acc-mandar"][data-k="item|8"]'); await A.sleep(900);
      const m = await page.evaluate(() => window.__rpcs.filter(r => r.nombre === 'bm_accion_marcar').map(r => r.params));
      R.reg('no-puedo', '«No puedo» llama a bm_accion_marcar con estado no_puedo y muestra el motivo', m.length === 1 && m[0].p_estado === 'no_puedo' && m[0].p_comentario === 'No tengo permisos' && /No puedo: No tengo permisos/.test(await home(page)), JSON.stringify(m));
      // Archivar trabada con Deshacer / a los 5 s
      await page.locator('.hac', { hasText: 'Tanda trabada' }).locator('[data-home="seg-archivar"]').tap(); await A.sleep(500);
      R.reg('archivar-trabada', 'Archivar saca la trabada al toque con aviso y Deshacer', !/Tanda trabada/.test(await home(page)) && /Archivada · Tanda trabada/.test(await page.locator('.snz-toast').first().innerText().catch(() => '')));
      await A.sleep(5800);
      const arch = await page.evaluate(() => window.__archivadas.slice());
      R.reg('archivar-rpc', 'A los 5 s llama a bm_archivar_pin con la clave de la tanda', arch.length === 1 && arch[0] === 'e2e-trabada', JSON.stringify(arch));
      cierre(page, 'errores-1');
    } finally { await ctx.close(); }

    // Comentar exige texto
    ({ ctx, page } = await A.ctxNuevo(A.escenario('bloqueos')));
    try {
      await abrir(page);
      await page.tap('[data-pt="acc-comentar"][data-k="item|8"]'); await A.sleep(300);
      await page.tap('[data-pt="acc-mandar"][data-k="item|8"]'); await A.sleep(300);
      const err = await page.locator('.hac-err').first().innerText().catch(() => '');
      const sin = await page.evaluate(() => window.__rpcs.filter(r => r.nombre === 'bm_accion_marcar').length);
      await page.locator('.lac-ta').fill('Mirá el paso 3'); await A.sleep(100);
      await page.tap('[data-pt="acc-mandar"][data-k="item|8"]'); await A.sleep(800);
      const m = await page.evaluate(() => window.__rpcs.filter(r => r.nombre === 'bm_accion_marcar').map(r => r.params));
      R.reg('comentar', '«Comentar» sin texto pide el comentario y no llama; con texto marca «comentada»', /Escribí el comentario/.test(err) && sin === 0 && m.length === 1 && m[0].p_estado === 'comentada' && /Comentario: Mirá el paso 3/.test(await home(page)), err + ' · ' + JSON.stringify(m));
      cierre(page, 'errores-2');
    } finally { await ctx.close(); }

    // Sin nada bloqueado y lectura fallida
    ({ ctx, page } = await A.ctxNuevo(A.escenario('vacio')));
    try {
      await page.goto(A.url()); await page.waitForSelector('#tabs', { timeout: 10000 }); await A.sleep(400);
      await page.tap('[data-tab="bloqueos"]'); await A.sleep(700);
      R.reg('vacio', 'Sin nada: «Nada bloqueado ✓»', /Nada bloqueado/.test(await home(page)));
      cierre(page, 'errores-3');
    } finally { await ctx.close(); }
  } finally { ok = R.fin(); await A.cerrar(); }
  process.exit(ok ? 0 : 1);
})();

// bm-avisar: manda un Web Push a cada dispositivo de bm_push. La llaman solo los cron de la base, con su secreto.
// El payload va cifrado (RFC 8291) y firmado con VAPID (RFC 8292) con WebCrypto, sin dependencias.
// Las claves VAPID se generan acá la primera vez y quedan en Vault: nadie las ve.
// El contacto de la firma VAPID sale de bm_config (lo pone bm_instalar).
import { createClient } from "npm:@supabase/supabase-js@2.45.4";
import { armarPush, generarVapid } from "./webpush.ts";

Deno.serve(async (req) => {
  const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
    auth: { persistSession: false },
  });
  const { data: datos, error } = await sb.rpc("bm_avisos_datos");
  if (error || !datos?.secreto) return new Response("sin datos", { status: 500 });
  if (req.headers.get("x-bm-avisar") !== datos.secreto) return new Response("no", { status: 401 });

  if (!datos.vapid_privada) {
    const v = await generarVapid();
    const g = await sb.rpc("bm_avisos_guardar_vapid", { p_publica: v.publica, p_privada: v.privadaJwk });
    if (g.error) return new Response("no pude guardar las claves", { status: 500 });
    datos.vapid_publica = v.publica;
    datos.vapid_privada = v.privadaJwk;
  }

  const m = await req.json().catch(() => ({}));
  if (!m.titulo) return Response.json({ ok: true, init: true });

  // viaja solo lo que armó la base: conteos y nombres de categoría
  const payload = JSON.stringify({ titulo: m.titulo, cuerpo: m.cuerpo || "", tag: m.tag || "aviso" });
  const ok: string[] = [], muertos: string[] = [], fallidos: string[] = [];
  let ultimoError: string | null = null;

  await Promise.all((datos.dispositivos as { endpoint: string; p256dh: string; auth: string }[]).map(async (d) => {
    try {
      const p = await armarPush(d, payload, datos.vapid_publica, datos.vapid_privada, datos.contacto || "mailto:botonera@example.com", m.tag || "aviso");
      const r = await fetch(d.endpoint, { method: "POST", headers: p.headers, body: p.body });
      const txt = r.ok ? "" : (await r.text()).slice(0, 120);
      if (r.ok) { await r.body?.cancel(); ok.push(d.endpoint); }
      else if (r.status === 404 || r.status === 410) muertos.push(d.endpoint);
      else { fallidos.push(d.endpoint); ultimoError = `${new URL(d.endpoint).host} ${r.status} ${txt}`; }
    } catch (e) {
      fallidos.push(d.endpoint);
      ultimoError = String(e);
    }
  }));

  const res = await sb.rpc("bm_avisos_resultado", {
    p_ok: ok, p_muertos: muertos, p_fallidos: fallidos, p_claves: m.claves || [], p_error: ultimoError,
  });
  if (res.error) return new Response("no pude guardar el resultado", { status: 500 });
  return Response.json({ ok: ok.length, muertos: muertos.length, fallidos: fallidos.length });
});

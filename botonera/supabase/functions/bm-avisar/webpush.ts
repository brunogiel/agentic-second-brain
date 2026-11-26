// Web Push con WebCrypto: cifrado aes128gcm (RFC 8291 + 8188) y firma VAPID (RFC 8292).
const te = new TextEncoder();

export function b64u(b: ArrayBuffer | Uint8Array): string {
  const u = b instanceof Uint8Array ? b : new Uint8Array(b);
  return btoa(String.fromCharCode(...u)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export function deB64u(s: string): Uint8Array {
  const r = atob(s.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - s.length % 4) % 4));
  return Uint8Array.from(r, (c) => c.charCodeAt(0));
}

function unir(...partes: Uint8Array[]): Uint8Array {
  const out = new Uint8Array(partes.reduce((n, p) => n + p.length, 0));
  let i = 0;
  for (const p of partes) { out.set(p, i); i += p.length; }
  return out;
}

async function hkdf(sal: Uint8Array, ikm: Uint8Array, info: Uint8Array, largo: number): Promise<Uint8Array> {
  const k = await crypto.subtle.importKey("raw", ikm, "HKDF", false, ["deriveBits"]);
  return new Uint8Array(await crypto.subtle.deriveBits({ name: "HKDF", hash: "SHA-256", salt: sal, info }, k, largo * 8));
}

export async function generarVapid(): Promise<{ publica: string; privadaJwk: string }> {
  const par = await crypto.subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]);
  return {
    publica: b64u(await crypto.subtle.exportKey("raw", par.publicKey)),
    privadaJwk: JSON.stringify(await crypto.subtle.exportKey("jwk", par.privateKey)),
  };
}

async function firmarVapid(endpoint: string, privadaJwk: string, contacto: string): Promise<string> {
  const cab = b64u(te.encode(JSON.stringify({ typ: "JWT", alg: "ES256" })));
  const cuerpo = b64u(te.encode(JSON.stringify({
    aud: new URL(endpoint).origin,
    exp: Math.floor(Date.now() / 1000) + 12 * 3600,
    sub: contacto,
  })));
  const k = await crypto.subtle.importKey("jwk", JSON.parse(privadaJwk), { name: "ECDSA", namedCurve: "P-256" }, false, ["sign"]);
  const firma = await crypto.subtle.sign({ name: "ECDSA", hash: "SHA-256" }, k, te.encode(cab + "." + cuerpo));
  return cab + "." + cuerpo + "." + b64u(firma);
}

// clave y sal opcionales: solo para probar contra el vector del RFC 8291
export async function cifrar(
  texto: Uint8Array, p256dh: Uint8Array, auth: Uint8Array,
  par?: CryptoKeyPair, sal?: Uint8Array,
): Promise<Uint8Array> {
  const eph = par ?? await crypto.subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]);
  const pubEph = new Uint8Array(await crypto.subtle.exportKey("raw", eph.publicKey));
  const pubUa = await crypto.subtle.importKey("raw", p256dh, { name: "ECDH", namedCurve: "P-256" }, false, []);
  const ecdh = new Uint8Array(await crypto.subtle.deriveBits({ name: "ECDH", public: pubUa }, eph.privateKey, 256));

  const s = sal ?? crypto.getRandomValues(new Uint8Array(16));
  const ikm = await hkdf(auth, ecdh, unir(te.encode("WebPush: info\0"), p256dh, pubEph), 32);
  const cek = await hkdf(s, ikm, te.encode("Content-Encoding: aes128gcm\0"), 16);
  const nonce = await hkdf(s, ikm, te.encode("Content-Encoding: nonce\0"), 12);

  const k = await crypto.subtle.importKey("raw", cek, "AES-GCM", false, ["encrypt"]);
  const cifrado = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv: nonce }, k, unir(texto, new Uint8Array([2]))));

  const rs = new Uint8Array([0, 0, 16, 0]); // 4096
  return unir(s, rs, new Uint8Array([pubEph.length]), pubEph, cifrado);
}

export async function armarPush(
  d: { endpoint: string; p256dh: string; auth: string },
  payload: string, vapidPublica: string, vapidPrivada: string, contacto: string, tema: string,
): Promise<{ headers: Record<string, string>; body: Uint8Array }> {
  const body = await cifrar(te.encode(payload), deB64u(d.p256dh), deB64u(d.auth));
  return {
    body,
    headers: {
      "Content-Encoding": "aes128gcm",
      "Content-Type": "application/octet-stream",
      "TTL": String(24 * 3600),
      "Urgency": "normal",
      // base64url: Apple rechaza un tema de largo inválido, como «vence» (BadWebPushTopic). 24 bytes dan 32 caracteres
      "Topic": b64u(te.encode(tema).slice(0, 24)),
      "Authorization": `vapid t=${await firmarVapid(d.endpoint, vapidPrivada, contacto)}, k=${vapidPublica}`,
    },
  };
}

// Vector de prueba del RFC 8291, Appendix A. Correr: deno test --no-check webpush_test.ts
import { b64u, cifrar, deB64u } from "./webpush.ts";

Deno.test("cifra igual que el RFC 8291", async () => {
  const texto = new TextEncoder().encode("When I grow up, I want to be a watermelon");
  const asPub = "BP4z9KsN6nGRTbVYI_c7VJSPQTBtkgcy27mlmlMoZIIgDll6e3vCYLocInmYWAmS6TlzAC8wEqKK6PBru3jl7A8";
  const asPriv = "yfWPiYE-n46HLnH0KqZOF1fJJU3MYrct3AELtAQ-oRw";
  const uaPub = "BCVxsr7N_eNgVRqvHtD0zTZsEc6-VV-JvLexhqUzORcxaOzi6-AYWXvTBHm4bjyPjs7Vd8pZGH6SRpkNtoIAiw4";
  const auth = "BTBZMqHH6r4Tts7J_aSIgg";
  const sal = "DGv6ra1nlYgDCS1FRnbzlw";
  const esperado =
    "DGv6ra1nlYgDCS1FRnbzlwAAEABBBP4z9KsN6nGRTbVYI_c7VJSPQTBtkgcy27mlmlMoZIIgDll6e3vCYLocInmYWAmS6TlzAC8wEqKK6PBru3jl7A_yl95bQpu6cVPTpK4Mqgkf1CXztLVBSt2Ks3oZwbuwXPXLWyouBWLVWGNWQexSgSxsj_Qulcy4a-fN";

  const pub = deB64u(asPub);
  const x = b64u(pub.slice(1, 33)), y = b64u(pub.slice(33, 65));
  const jwk = { kty: "EC", crv: "P-256", x, y, ext: true };
  const privateKey = await crypto.subtle.importKey("jwk", { ...jwk, d: asPriv }, { name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]);
  const publicKey = await crypto.subtle.importKey("jwk", jwk, { name: "ECDH", namedCurve: "P-256" }, true, []);

  const out = await cifrar(texto, deB64u(uaPub), deB64u(auth), { privateKey, publicKey }, deB64u(sal));
  if (b64u(out) !== esperado) throw new Error("no coincide:\n" + b64u(out) + "\n" + esperado);
});

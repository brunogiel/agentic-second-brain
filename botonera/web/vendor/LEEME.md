# Librerías de terceros servidas desde este sitio

La página las carga desde `/vendor/` (mismo origen). No se pide nada a una CDN.

| Archivo | Paquete | Versión | Origen | sha256 | Licencia |
|---|---|---|---|---|---|
| `supabase.min.js` | `@supabase/supabase-js` (build UMD) | 2.45.4 | https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.min.js | `96277ec00e19df476d7396a8a2586b41ed1033dcf680f5aa79b0c556059792b8` | MIT (`LICENSE-supabase-js.txt`) |
| `confetti.min.js` | `canvas-confetti` | 1.9.3 | https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js | `cfc4a191c3ae300777c25e27aa81cb2d25bb898c8632aa61787f305876a981c8` | ISC (`LICENSE-canvas-confetti.txt`) |

Bajados el 2026-11-26 con `curl` a la URL exacta de arriba (versión fija).
SHA-384 de `confetti.min.js`: `sha384-sPwMflxqfAN+Q5mvlkLmHiX3PORGbZSXHiSGPTXT9VHCD/AB+b+r+vJWsqprv+7k`, el mismo que la página ya fijaba antes como `integrity`.

Para actualizar: bajá la versión nueva, reemplazá el archivo, recalculá el sha256 (`shasum -a 256 archivo`) y anotalo acá.

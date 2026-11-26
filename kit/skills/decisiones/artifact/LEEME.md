# La página de Claude: cómo se regenera

`pagina.html` es **la misma web que `botonera/web/index.html`** (mismo html, mismo css, mismo js de mazo, tarjeta, hojas, snooze, lista y confeti) en un solo archivo, con la base de la página de Claude en lugar de Supabase. No se edita a mano: se deriva.

```
python3 kit/skills/decisiones/artifact/derivar.py          # regenera pagina.html desde botonera/web/index.html
python3 kit/skills/decisiones/artifact/derivar.py --check  # sale con 1 si pagina.html no coincide
```

Cada cambio exige que el texto original aparezca las veces esperadas. Si la web cambia por ese lado, `derivar.py` falla en voz alta (no genera una página rota) y hay que ajustar ese cambio. Cada bloque cambiado o agregado en `pagina.html` lleva un comentario `ARTIFACT`.

## Los cambios, en el orden en que se aplican

1. **`<head>`**: título «Tus pendientes»; sin íconos, manifest ni `apple-touch-icon` (una página privada no sirve archivos aparte). Se agrega el css del paso de avisar a Claude y `.top{min-height}` (la barra de arriba conserva el alto que tiene con el botón Salir). Las fuentes de Google siguen por `<link>`.
2. **Datos**: se saca `supabase.min.js` y `config.js`. Va inline `adaptador.js`: un objeto con la misma interfaz que usa la web (`createClient().rpc(nombre, params)` → `Promise<{data, error}>`) que contesta cada RPC con la base de la página (`claude.use("db")`). Se saca la validación de la config de Supabase.
3. **Sin PIN**: la pantalla del PIN pasa a ser el aviso «Esta página necesita que entres a Claude con tu cuenta» (`db` ausente) o «Todavía no pude leer tus tarjetas» (la base tarda más de 10 s). Se saca el botón Salir y su oyente.
4. **Marcas a medio decidir**: `persistirMarcas` además las manda a `marcas/<clave>` (una escritura por pausa), y `cargarLista` adopta una vez por clave lo que otro dispositivo dejó marcado.
5. **Sin avisos al celu**: el bloque de Web Push (service worker, suscripción, cartel «Activar avisos») se reemplaza por stubs. `segRpcKeepalive` deja de usar `fetch` directo.
6. **Confeti**: `confeti.js` (unas 40 líneas, inline) reemplaza a `canvas-confetti`; no se carga ningún script de afuera.
7. **Rótulos**: «Claude recomienda», «Claude está trabajando», «Esto propuso Claude» en vez de «el agente»; «tarjeta/tarjetas» en vez de «card/cards» en los textos visibles (la lista exacta está en `derivar.py`).
8. **Sin «Ver la botonera original»**: necesita el html de la tanda, que esta página no guarda.
9. **Sesiones**: lo que Claude escribe en `estado/<clave>` se ve en el detalle de la fila.
10. **Avisar a Claude** (`avisar.js`): después de Enviar, en las dos pantallas de cierre del mazo y en el home. Un botón «Avisar a Claude» (`room`), o «Avisarle a Claude con un comentario» (`comments`), y siempre «o volvé al chat y escribí “listo”» + «Copiar respuesta». Cada botón se bloquea tras el primer toque. El mensaje lleva `tipo: 'respuesta_tarjetas'`, `clave` y `texto`.
11. **Arranque**: `init()` entra directo con la cuenta de Claude y espera al adaptador.

## Documentos de la base

| Documento | Lo escribe | Contenido |
|---|---|---|
| `tandas/<clave>` | Claude | lo que arma `armar.py --artifact` (`datos` de la web, con `categoria` embebida) + `creada`, `estado` (`abierta`, `aplicada`, `archivada`), `resumen`, `actualizada`? |
| `respuestas/<clave>` | la página | `{clave, texto, por, cuando}`; `texto` empieza con `/botonera respuesta · <clave>` |
| `estado/<clave>` | Claude | `{texto, cuando}` |
| `marcas/<clave>` | la página | `{clave, marcas?, snooze_hasta?, archivada?, por, cuando}` |

Reglas de acceso (van **exactas** al publicar):

```json
{"db": {"rules": [
    {"path": "tandas", "read": "view", "write": "admin"},
    {"path": "estado", "read": "view", "write": "admin"},
    {"path": "respuestas", "read": "view", "write": "interact"},
    {"path": "marcas", "read": "view", "write": "interact"}]},
 "user": {}, "room": {}, "comments": {}}
```

Cómo el adaptador convierte documentos en lo que la web espera de `bm_lista`: una tanda `abierta` con documento en `respuestas` es «decidida»; si además hay `estado/<clave>.texto`, es «recibida» (la web dice «Claude está trabajando»); `tandas.estado: "aplicada"` es «aplicada», con `resumen`; `marcas.archivada` la lleva a «archivada»; `marcas.snooze_hasta` (o `tandas.snooze_hasta`) la duerme.

## Qué no tiene (a propósito)

PIN, avisos al celu, service worker, obstáculos y errores técnicos (Bloqueos solo muestra respuestas sin novedad hace más de 24 h), sesiones en vuelo de otros agentes, «Ver la botonera original».

## Pruebas

```
NODE_PATH=<carpeta con playwright> node kit/skills/decisiones/artifact/tests/e2e.js           # flujo completo con un window.claude falso
NODE_PATH=<carpeta con playwright> node kit/skills/decisiones/artifact/tests/mismo-diseno.js   # la web real y esta página, con los mismos datos
```

`tests/fake-claude.js` es el `window.claude` falso (db, user, room y comments en memoria; se configura por la URL). `mismo-diseno.js` usa el arnés de `botonera/tests/arnes` para correr la web real y compara estilos y rectángulos de 30 elementos clave.

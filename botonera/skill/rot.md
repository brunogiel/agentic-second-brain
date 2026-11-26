# rot: reescribir una card que la persona no entendió

Esta guía es autocontenida: no depende de ningún otro skill. La lee el agente cuando vuelve una respuesta de la botonera con una línea `N. rot · …`.

## Cuándo se usa

En la web, cada card tiene un botón **+info** («rot»). Lo toca quien no entendió la card. No es un Va ni un No va: es un pedido de «explicámelo mejor». Vuelve así dentro de la respuesta:

```
3. rot · Qué día sale el newsletter → Dibujo corto + Otro ejemplo · comentario: no entiendo qué cambia
```

La parte `→ …` son las opciones que tocó la persona (una o varias, unidas con ` + `). Sin `→`, es un pedido genérico: reescribí con un dibujo corto y contexto más claro.

## Las 5 opciones

| Opción | Qué hacer |
|---|---|
| **Más contexto** | Arrancá desde afuera: qué proyecto o herramienta es, qué se venía haciendo y por qué esta decisión aparece ahora. Recién después, la pregunta. El `contexto` puede llegar a 30 palabras. |
| **Dibujo corto** | Un `dibujo` SVG que explique (ver abajo) y una sola línea de contexto. |
| **Dibujo largo** | El dibujo muestra antes y después, paso a paso. Sube el techo de `antecedentes` a 3 viñetas. |
| **Escribilo distinto** | Las mismas ideas con otras palabras, sin jerga ni siglas. Mismo largo o más corto. |
| **Otro ejemplo** | Cambiá el caso abstracto por uno concreto de la vida o el trabajo de la persona, con nombres y números reales. |

Si vienen sumadas (`Dibujo corto + Otro ejemplo`), se cumplen las dos.

## Reglas de la reescritura

1. **Dibujo que explique, no que decore.** Antes → después, A contra B, un flujo o una cantidad. Si el dibujo no aclara nada, no lo pongas.
2. **Contexto de 15 palabras o menos** (30 con «Más contexto»).
3. **Como mucho 2 antecedentes** (3 con «Dibujo largo»).
4. **La misma decisión y los mismos botones**: mismos `accion_va` / `accion_no_va`, mismas `opciones` y mismos `campos`, con los mismos ids. No cambia qué se decide, solo cómo se cuenta.
5. **Si la línea trae un comentario, la reescritura lo contesta.** Si el comentario es una pregunta, la respuesta va en el `contexto` o en un `antecedente`.
6. Los techos de `armar.py` siguen valiendo y el script los hace cumplir: título ≤9 palabras, contexto ≤25, `reco_motivo` ≤15, cada antecedente y `si_no_decidis` ≤15, `detalle` ≤60, cada plan de `aplicar` ≤40. Si falla, recortá; no subas el techo.

## Dibujos: lo que se puede usar

El `dibujo` es `{"viewBox": "0 0 240 100", "alt": "qué muestra", "svg": "…"}`. `armar.py` limpia el SVG: solo sobreviven estas etiquetas: `svg g path rect circle ellipse line polyline polygon text tspan title desc defs marker use`. Nada de `style`, scripts, handlers ni imágenes externas.

Los colores no se escriben: se usan clases, y la página las pinta en claro y en oscuro.

| Clase | Para qué |
|---|---|
| `a` | trazo (líneas, flechas, contornos) |
| `fa` | relleno del color del trazo |
| `b` | relleno de acento |
| `t` | texto fuerte |
| `tm` | texto suave (notas, etiquetas chicas) |
| `go` / `no` | relleno verde / rojo (lo que va / lo que no) |
| `sgo` / `sno` | trazo verde / rojo |
| `box` | caja con fondo y borde |

**Ejemplo 1: antes → después** (dentro del campo `svg`, con `viewBox` `0 0 240 100`):

```html
<rect class="box" x="10" y="22" width="88" height="50" rx="8"/>
<text class="tm" x="54" y="42" text-anchor="middle">Antes</text>
<text class="t" x="54" y="60" text-anchor="middle">3 mails</text>
<line class="a" x1="104" y1="47" x2="136" y2="47"/>
<polygon class="fa" points="136,41 148,47 136,53"/>
<rect class="box" x="152" y="22" width="78" height="50" rx="8"/>
<text class="tm" x="191" y="42" text-anchor="middle">Después</text>
<text class="t" x="191" y="60" text-anchor="middle">1 resumen</text>
```

**Ejemplo 2: A contra B** (dos barras con su cantidad):

```html
<text class="tm" x="10" y="26">A · hoy</text>
<rect class="no" x="70" y="14" width="150" height="16" rx="4"/>
<text class="t" x="226" y="27" text-anchor="end">12 h</text>
<text class="tm" x="10" y="64">B · propuesta</text>
<rect class="go" x="70" y="52" width="50" height="16" rx="4"/>
<text class="t" x="126" y="65">4 h</text>
```

Poné siempre un `alt` que diga lo que muestra el dibujo con palabras.

## Cómo publicar la card reescrita

1. Armá un JSON nuevo con **solo esa card** (más las que hayan quedado pendientes de esa tanda). Mismo `n` que tenía, la `clave` de la tanda con sufijo: `<clave>-r2` (si ya era `-r2`, `-r3`).
2. Publicá marcando la vieja como reemplazada:
   ```bash
   python3 ~/.claude/skills/botonera/armar.py --publicar --reemplaza <clave>#<n> <tmp>/datos.json <tmp>/botonera.html
   ```
   Con eso la card vieja queda «Ya no aplica» con un link a la nueva. Para un rango de cards de la misma tanda: `--reemplaza <clave>#1:3`.
3. Esperá la respuesta de la nueva clave como siempre (`esperar.py <clave>-r2`, o `--una-vez` si tu agente no tiene segundo plano; mirá SKILL.md).
4. El resto de la tanda original se cierra con `marcar.py` como siempre: el `rot` no cuenta como Va.

## Si no hay sesión viva

Si la respuesta con `rot` la leés con `retomar.py` (la sesión que preguntó ya no está), la línea `rot` te llega marcada como «reescribir con rot.md». Reescribila igual con esta guía. Si por algo no podés (falta el contexto de la card o no podés publicar), dejala pendiente y avisale a la persona en una línea: «no pude reescribir la card N; queda pendiente».

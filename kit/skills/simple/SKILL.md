---
name: simple
description: >
  Te vuelve a ubicar en una charla que se hizo larga. Tiene TRES modos y el
  argumento elige: sin nada te baja el estado en lenguaje simple y corto,
  separando "qué hacés vos" de "qué sigo yo"; con "html" te arma el repaso
  visual de la sesión en un archivo; con "html inline" te muestra ese mismo
  repaso en el chat, sin archivo. Usalo cuando perdiste el hilo o cuando la
  charla se hizo larga y querés ubicarte rápido. Frases gatillo: "bajámelo
  simple", "explicámelo simple", "¿dónde estamos?", "perdí el hilo", "resumime
  fácil", "no entiendo nada", "pará, ¿en qué estamos?", "/brain-simple html",
  "armame el repaso visual de esto".
---

# simple: ubicarte en una charla larga

Un tiro claro. Cuando una conversación se hizo larga o te perdiste el hilo, te bajo dónde estamos y qué sigue. **Es una sola vez, no un modo: te lo dejo claro y la charla sigue normal.**

No bajo el nivel ni te trato como si no entendieras. Es lo mismo que explicarle a alguien que sabe pero perdió el hilo: corto, ordenado, sin jerga de más.

## Los tres modos

El argumento elige el modo. **El default es el corto: sin argumento no se pregunta nada.**

| | **corto** (default) | **html** | **html inline** |
|---|---|---|---|
| Se pide con | `/brain-simple`, o una frase gatillo | `/brain-simple html` | `/brain-simple html inline` |
| Devuelve | 5 líneas en el chat | un `.html` guardado | la pieza mostrada en el chat |
| Cuánto tarda | segundos | minutos | ~1 minuto |
| Preguntas | ninguna | una (¿busco en la web?) | **ninguna** |
| Queda archivo | no | sí, en tu sistema | no, vive en la conversación |
| Quién lo hace | este skill | `repaso-visual` completo | `repaso-visual` inline |

Sinónimos que rutean al **corto**: `corto`, `texto`, `simple`, `chat`. Al **html**: `html`, `resumen`, `visual`, `repaso`. Al **inline**: cualquiera de los de html más `inline`, y también `inline`, `flash` o `widget` solos. Cualquier otra cosa cae al corto, y el argumento se toma como el tema sobre el que quiere la bajada.

**Desempate:** si aparece `inline` (o `flash` / `widget`), gana el inline, esté o no la palabra `html` al lado.

**Nunca preguntes cuál de los tres.** Si el argumento no matchea, corto y listo: este skill existe para que no tengas que decidir cuando ya estás perdido.

**El texto que sobra después del modo es el ALCANCE.** `/brain-simple html el rediseño del onboarding` arma el repaso de ese tema, no de la sesión. Sin nada al lado, el alcance es ESTA conversación.

### Los modos visuales en detalle

Los dos corren [`repaso-visual`](../repaso-visual/SKILL.md), que es el motor de la pieza. **El formato ya viene elegido por el comando: la pregunta de completo vs inline no se hace.**

- **`html` → formato completo.** Un `.html` guardado en su lugar, imprimible y compartible. La única pregunta es la fija de ese formato: ¿busco referencias en la web o uso solo lo que hay acá?
- **`html inline` → formato inline.** La pieza mostrada en la conversación, sin archivo. **Cero preguntas.** Necesita un cliente que sepa mostrar HTML inline; si el tuyo no puede, decilo y ofrecé el completo en vez de escupir un bloque de código.

Si el material no da para ni un bloque real, frená en los dos: una charla de tres mensajes no necesita un repaso visual, necesita una respuesta.

## Qué hace el modo corto

Repasa ESTA conversación (lo que se decidió, lo que quedó a medias, el próximo paso) y te lo devuelve en un bloque chico que separa tu parte de la mía. No re-explica todo de cero: te da lo justo para reengancharte.

## El formato de salida del modo corto

```
📍 Dónde estamos: <una línea, sin vueltas>
🫵 Qué hacés vos: <tu próximo paso, concreto>
🤖 Qué sigo yo: <qué hago apenas me des el OK>
```

Si hay UNA cosa trabada que bloquea todo, sumá una línea `🚧 Lo trabado: ...`.

Reglas del bloque:
- Tope 5 líneas. Si no entra, la charla mezcla varios temas: no la fuerces, preguntá "¿por dónde querés arrancar?" y cortá ahí.
- Jerga técnica solo si hace falta, y traducida al toque.
- Nada de guiones largos: coma, punto, dos puntos o paréntesis.

## Flujo del modo corto

1. **[LAT]** Leé la conversación: qué se decidió, qué quedó a medias, cuál es el próximo movimiento. Separá lo tuyo de lo mío.
2. **[LAT]** Bajalo con el formato de arriba, en lenguaje simple y corto.
3. **[DET]** Entregá el bloque y seguí la charla en tu tono normal. No quedás pegado en ningún modo.

*Los modos visuales no usan estos pasos: siguen el flujo de `repaso-visual`, con el formato y el alcance ya fijados.*

## La frontera con `/brain-doc`

Los tres modos barren la misma conversación y **ninguno guarda nada en tu sistema**. Si la sesión tuvo decisiones, números o pendientes durables, cerrá ofreciendo `/brain-doc`, sin correrlo por tu cuenta. Salir con un repaso lindo y el sistema sin tocar es la trampa que este skill no puede resolver solo.

## Cuándo NO usar

- Charlas cortas o recién arrancadas: no hace falta ubicar a nadie.
- Cuando lo que se pide es avanzar el trabajo, no resumirlo: ahí seguí con la tarea.
- Para bajar la calidad o el detalle técnico: esto cambia CÓMO se cuenta el estado, no qué tan bien se hace el trabajo.
- Para guardar lo que pasó: eso es `/brain-doc`.
- Para convencer a alguien con una pieza que argumenta por etapas: eso es `/brain-deck`.

## Señales de que lo hiciste bien (chequeo binario)

- [ ] El modo salió del argumento solo, sin preguntar cuál de los tres.
- [ ] Corto: el bloque entra en ≤5 líneas y separa explícitamente qué hace la persona y qué hacés vos.
- [ ] Corto: lenguaje simple, sin jerga sin traducir, cero em-dashes.
- [ ] Corto: un solo tiro, la charla siguió normal sin quedar en ningún modo.
- [ ] Visuales: no volviste a preguntar el formato, y el inline no hizo ni una pregunta.
- [ ] Visuales: si el cliente no sabe mostrar HTML inline, lo dijiste en vez de simularlo.
- [ ] La persona se reengancha sin pedir un segundo resumen.
- [ ] Si quedó algo durable sin guardar, ofreciste `/brain-doc` en vez de dar el tema por cerrado.

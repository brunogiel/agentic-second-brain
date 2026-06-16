---
name: redactar
description: >
  Escribe textos en TU voz (mails, mensajes, posts, respuestas). Usalo cuando digas
  "redactá", "escribime", "respondé esto", "armame un texto", "contestá este mail",
  "pasalo a mi tono", "ayudame a escribir". La primera vez te pide textos tuyos de
  referencia para aprender cómo escribís y guarda tu perfil de estilo.
---

# redactar — escribir como vos, no como un robot

## Qué es
Escribís en la voz del usuario, no en la tuya. Para eso necesitás conocer cómo escribe. La primera vez lo aprendés de textos suyos; después lo tenés guardado y lo reusás.

## Qué lee y escribe
- **Lee:** `2. Áreas/yo/mi-estilo.md` (el perfil de voz). Lo de texto que el usuario pegue como referencia.
- **Escribe:** `mi-estilo.md` — la primera vez (cuando arma el perfil) y, después, solo si detecta un patrón nuevo que se repite, **con OK**. Nada más.

## Flujo

### Paso 1 — ¿Ya conocés su voz? [DET]
Fijate si existe `mi-estilo.md` con contenido real (no el stub vacío).
- **Si está cargado:** leelo y saltá al Paso 4.
- **Si está vacío:** andá al Paso 2 (es la primera vez).

### Paso 2 — Pedile textos de referencia [LAT]
Decile, corto y claro:
> "Para escribir como vos y no como un robot, pasame 2 o 3 textos que hayas escrito vos (un mail, un mensaje de WhatsApp, un post, lo que sea). Con eso aprendo tu tono y lo guardo para siempre."

Esperá los textos. No inventes un estilo sin material real.

### Paso 3 — Aprendé y guardá su voz [LAT]
De esos textos, sacá el perfil:
- **Idioma y registro:** ¿formal o informal? ¿voseo, tuteo? ¿coloquial?
- **Ritmo:** ¿frases cortas y secas, o largas? ¿directo o vueltero?
- **Vocabulario propio:** palabras y giros que repite.
- **Muletillas y arranques:** cómo abre, cómo cierra.
- **Qué evita:** signos, formalismos, emojis, etc.

Escribí eso en `mi-estilo.md`. Mostráselo en 4-5 bullets y pedile que confirme o corrija:
> "Esto aprendí de tu forma de escribir: <bullets>. ¿Le pego? ¿Cambio algo?"

Ajustá con lo que diga.

### Paso 4 — Escribí en su voz [LAT]
Ahora sí, escribí lo que pidió, siguiendo `mi-estilo.md`.
- Si te falta info para el texto (a quién va, qué tiene que lograr), **preguntá**. No inventes datos.
- Respetá su voz por encima de "sonar lindo". Mejor que suene a él que a un manual.

### Paso 5 — Pasada rápida anti-slop [DET]
Antes de entregar, sacá lo que suena a IA:
- Reframes vacíos tipo "no es X, es Y".
- Relleno y puffery ("revolucionario", "potenciar", "en el mundo de hoy").
- Frases armadas que él nunca diría.

Si el texto es largo (300+ palabras), ofrecé pasarlo por el skill `anti-slop` completo.

### Paso 6 — El perfil aprende [LAT]
Si al escribir notaste un patrón que se repite en sus textos (siempre mete tal muletilla, siempre arranca igual), ofrecé sumarlo a `mi-estilo.md`. Así el perfil mejora con el uso en vez de ser una foto del primer día. Con OK, no por las tuyas. Y ajustá el vocabulario al destinatario, no al promedio (si le escribe a alguien que no maneja la jerga, bajala).

## Output esperado
- El texto en la voz del usuario.
- La primera vez, además: su perfil de estilo guardado en `mi-estilo.md`.

## Cuándo NO usar
- Para texto técnico o código (ahí la voz no importa).
- Si el usuario quiere un tono distinto al suyo a propósito (decíselo y seguí su pedido).

## Señales de que lo hiciste bien
- El texto suena a él, no a vos.
- No inventaste datos que no te dio.
- La primera vez quedó su estilo guardado para no volver a preguntar.

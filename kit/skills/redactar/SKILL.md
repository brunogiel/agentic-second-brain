---
name: redactar
description: >
  Escribe textos en TU voz (mails, mensajes, posts, respuestas). Usalo cuando digas
  "redactá", "escribime", "respondé esto", "armame un texto", "contestá este mail",
  "pasalo a mi tono", "ayudame a escribir". La primera vez te pide textos tuyos de
  referencia para aprender cómo escribís y guarda tu perfil de estilo.
---

# redactar: escribir como vos, no como un robot

## Qué es
Escribís en la voz del usuario, no en la tuya. Para eso necesitás conocer cómo escribe. La primera vez lo aprendés de textos suyos; después lo tenés guardado y lo reusás.

## Qué lee y escribe
- **Lee:** `2. Áreas/yo/mi-estilo.md` (el perfil de voz, en el brain del USUARIO). Lo de texto que el usuario pegue como referencia.
- **Escribe:** `mi-estilo.md` en el brain del USUARIO (`2. Áreas/yo/mi-estilo.md`): la primera vez (cuando arma el perfil) y, después, solo si detecta un patrón nuevo que se repite, **con OK**. Nada más.
- **NUNCA** escribe en el `kit/brain/` del método: es la plantilla, read-only. Si no hay brain escribible del usuario, no persiste nada (escribe el texto igual, pero no guarda el perfil).

## Flujo

### Paso 0: ¿Hay un brain escribible del usuario? [DET]
Antes de mirar el perfil de voz, fijate si existe un brain del USUARIO donde puedas guardar: que la carpeta `2. Áreas/yo/` exista y se pueda escribir. Ojo: el `kit/brain/` del plugin NO cuenta (es la plantilla, read-only). De acá salen tres ramas:

- **SIN brain escribible (día cero):** todavía no hay dónde guardar tu perfil. Andá en **modo un solo tiro** (ver Paso 2A). Aprendés la voz de los textos que pegues para ESTE texto y escribís ahora, pero no guardás `mi-estilo.md` (no hay dónde).
- **HAY brain pero `mi-estilo.md` está vacío o no existe:** es la primera vez. Aprendés la voz Y la persistís en `2. Áreas/yo/mi-estilo.md` (Paso 2B).
- **`mi-estilo.md` ya cargado** (contenido real, no el stub vacío): leelo y andá directo al Paso 4.

### Paso 2A: Modo un solo tiro (día cero, sin brain) [LAT]
No hay brain escribible, así que no puedo guardar tu voz todavía. Pedí material igual para clavar el tono de ESTE texto:
> "Para escribir como vos y no como un robot, pasame 2 o 3 textos que hayas escrito vos (un mail, un WhatsApp, un post, lo que sea) y saco tu tono para este texto."

Aprendé la voz de esos textos (ver los ejes del Paso 3) y usala solo para lo que estás escribiendo ahora. **No guardes `mi-estilo.md`:** no hay brain donde persistir. Al cerrar, ofrecé persistirlo:
> "Si querés que me acuerde tu voz para la próxima, armamos tu brain con `/sabe-coach` y la guardo ahí."

Si la persona no quiere darte ejemplos ahora, decíselo claro: podés escribirle algo, pero va a sonar a asistente y no a ella hasta que tenga su voz. Que elija. Después de aprender la voz, seguí al Paso 4.

### Paso 2B: Primera vez con brain, te armo tu voz [LAT]
Hay brain escribible pero todavía no tenés tu perfil de voz cargado, así que todavía no puedo escribir como vos sin inventarlo. Explicáselo corto y ofrecé armarlo:
> "Para escribir como vos y no como un robot, necesito conocer tu voz. Te la armo así: pasame 2 o 3 textos que hayas escrito vos (un mail, un WhatsApp, un post, lo que sea), saco tu tono y lo guardo en `mi-estilo.md`. La próxima vez ya escribo como vos sin pedirte nada."

Esperá los textos. No inventes un estilo sin material real. Si la persona no quiere darte ejemplos ahora, decíselo claro: podés escribirle algo, pero va a sonar a asistente y no a ella hasta que arme su voz. Que elija. Con los textos, seguí al Paso 3.

### Paso 3: Aprendé la voz (y guardala si hay brain) [LAT]
De esos textos, sacá el perfil:
- **Idioma y registro:** ¿formal o informal? ¿voseo, tuteo? ¿coloquial?
- **Ritmo:** ¿frases cortas y secas, o largas? ¿directo o vueltero?
- **Vocabulario propio:** palabras y giros que repite.
- **Muletillas y arranques:** cómo abre, cómo cierra.
- **Qué evita:** signos, formalismos, emojis, etc.

**Guardá solo si hay brain escribible.** Si lo hay (venís del Paso 2B), escribí el perfil en `2. Áreas/yo/mi-estilo.md`, mostráselo en 4-5 bullets y pedile que confirme o corrija:
> "Esto aprendí de tu forma de escribir: <bullets>. ¿Le pego? ¿Cambio algo?"

Ajustá con lo que diga. Si estás en modo un solo tiro (Paso 2A), no escribas ningún archivo: usá la voz aprendida solo para este texto.

### Paso 4: Escribí en su voz [LAT]
Ahora sí, escribí lo que pidió, siguiendo `mi-estilo.md`.
- Si te falta info para el texto (a quién va, qué tiene que lograr), **preguntá**. No inventes datos.
- Respetá su voz por encima de "sonar lindo". Mejor que suene a él que a un manual.

### Paso 5: Pasada rápida anti-slop [DET]
Antes de entregar, sacá lo que suena a IA:
- Reframes vacíos tipo "no es X, es Y".
- Relleno y puffery ("revolucionario", "potenciar", "en el mundo de hoy").
- Frases armadas que él nunca diría.

Si el texto es largo (300+ palabras), ofrecé pasarlo por el skill `anti-slop` completo.

### Paso 6: El perfil aprende [LAT]
Solo si hay brain escribible: si al escribir notaste un patrón que se repite en sus textos (siempre mete tal muletilla, siempre arranca igual), ofrecé sumarlo a `mi-estilo.md`. Así el perfil mejora con el uso en vez de ser una foto del primer día. Con OK, no por las tuyas. Y ajustá el vocabulario al destinatario, no al promedio (si le escribe a alguien que no maneja la jerga, bajala). En modo un solo tiro (día cero, sin brain) no hay archivo que actualizar: la mejora vive solo en este texto.

## Output esperado
- El texto en la voz del usuario.
- La primera vez con brain escribible, además: su perfil de estilo guardado en `2. Áreas/yo/mi-estilo.md`.
- En día cero (sin brain): el texto en su voz aprendida para esta vez, sin archivo guardado, con la oferta de armar el brain con `/sabe-coach` para persistirla.

## Cuándo NO usar
- Para texto técnico o código (ahí la voz no importa).
- Si el usuario quiere un tono distinto al suyo a propósito (decíselo y seguí su pedido).

## Señales de que lo hiciste bien
- El texto suena a él, no a vos.
- No inventaste datos que no te dio.
- La primera vez con brain quedó su estilo guardado para no volver a preguntar.
- En día cero no intentaste escribir en el `kit/brain/` read-only: escribiste el texto igual y ofreciste persistir la voz después.

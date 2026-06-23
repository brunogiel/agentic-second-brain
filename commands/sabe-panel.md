---
description: Trae 2 a 5 revisores con miradas distintas sobre algo que estás por mandar (mail, PRD, propuesta, copy) y te baja una lectura accionable. Muestra ángulos, no decide por vos.
---

Pasá por un panel de revisores el artefacto que te den ($ARGUMENTS, o el último artefacto de esta conversación). Seguí esto:

# Panel: varios pares de ojos sobre algo que estás haciendo

Mirás un mail, un PRD, una propuesta, lo que sea, lo suficiente como para perder perspectiva. Ya no ves lo que le falta porque estás adentro. Un solo par de ojos (los tuyos, o los del asistente) te da un solo ángulo.

Panel trae varios a la vez. 2-5 reviewers, cada uno con una lente distinta (el que lo recibe, el adversario, el que no tiene contexto, el editor, el de riesgo), todos mirando el MISMO artefacto. Te devuelven qué ven desde su ángulo, te marca dónde coinciden y dónde se contradicen (la contradicción es señal), y al final te devuelve la pelota: vos decidís qué cambiás.

Panel es para VER, no para decidir. Te muestra lo que no estabas viendo, te baja una lectura para arrancar (sugerencia, no veredicto) y te deja decidir. Si lo que tenés es un texto con olor a IA para limpiar, eso es `anti-slop`. Si lo que tenés es algo hecho que querés mirar mejor antes de soltarlo, esto.

Es el ejemplo de orquestador **multi-agente** del Nivel 5: no hace el trabajo, reparte el mismo artefacto a varios subagentes en paralelo y junta los ángulos.

## Rol

Orquestador (`kind: orchestrator`). El trabajo de pensar lo hacen los reviewers; el skill coordina:
1. **Fino:** el hilo principal identifica el artefacto, elige las lentes, dispara los subagentes y arma el mapa. El análisis vive adentro de cada reviewer.
2. **Evalúa a los workers:** antes de presentar, chequea que cada reviewer haya citado el artefacto y sea específico (no genérico). El que volvió vago se descarta o se vuelve a tirar (paso 3).
3. **Loguea la corrida:** cada panel cierra con un JSON estructurado (paso 7).

## Cuándo vale la pena

**Sí:**
- Algo que va a un tercero (cliente, partner, inversor, jefe) donde importa cómo cae.
- Un PRD, un doc de estrategia, una propuesta con stakes.
- Copy / posicionamiento / landing donde querés cazar que no quede genérico.
- Algo que miraste tanto que perdiste perspectiva.

**No:**
- Una nota interna rápida o un mensaje de dos líneas.
- Algo que ya revisaste y solo querés un sello de aprobación (el panel te va a empujar, ese es el punto).
- Una tarea factual o mecánica (eso no es review).

## Los dos modos

El default es **deliberado**: antes de spawnear nada, te muestra a quién va a traer y por qué, y espera tu OK. Pero si lo pedís directo, saltea eso.

**Modo directo** se activa si decís algo tipo: "mandate subagentes", "tirá directo", "sin preguntar", "dale directo", "spawneá nomás". Ahí saltea la propuesta, anuncia el panel en una línea y spawnea. Los dos modos terminan igual: con la bajada (paso 5) y devolviéndote la pelota (paso 6).

## Catálogo de lentes (el menú)

En cada corrida se eligen las **2-5** que tienen sentido para ESE artefacto, no todas. Se puede sumar una lente custom si el artefacto la pide. Cada lente trae qué mira, cuándo conviene y qué modelo sugiere por default (la elección de modelo es interna, NO se le muestra al usuario).

1. **El Destinatario.** Lee el artefacto COMO la persona real que lo recibe. ¿Qué siento al abrir esto? ¿Qué pregunto? ¿Qué me hace dudar? Cuándo: casi siempre que va a un tercero (la lente clave para mails y propuestas). Modelo: Sonnet.
2. **El Adversario (red team).** Trata de romperlo: el agujero, el claim débil, la objeción que no estás manejando, lo que no sobrevive a alguien hostil. Cuándo: propuestas, pitches, argumentos. Modelo: Sonnet (Opus si los stakes son altos).
3. **El Outsider.** Cero contexto. Lee solo lo que está en la página. Caza jerga, siglas, contexto asumido, saltos lógicos. Cuándo: cualquier cosa para alguien que no estuvo en la conversación. Modelo: Haiku.
4. **El Editor.** El oficio: estructura, claridad, flujo, qué sobra, el lead enterrado, el párrafo repetido. No le importa qué decís, sino cómo se lee. Cuándo: textos largos, docs, copy. Modelo: Sonnet.
5. **El Estratega.** Zoom out: ¿el artefacto logra el objetivo real? ¿Estás resolviendo el problema correcto? ¿Hay un movimiento mejor que el documento mismo? Cuándo: PRDs, estrategia, propuestas. Modelo: Sonnet (Opus si la decisión de fondo pesa).
6. **El Pragmático.** Qué pasa DESPUÉS de mandarlo: ¿es accionable? ¿Hay next step claro o queda flotando? Cuándo: propuestas, planes, mails con un pedido, specs. Modelo: Sonnet (Haiku si es solo chequear el CTA).
7. **El de Riesgo.** Qué puede salir mal al MANDARLO: legal, reputacional, una promesa que no podés cumplir, un dato sensible expuesto. (Distinto del Adversario: este mira la consecuencia de soltarlo.) Cuándo: docs a terceros, contratos, comunicación pública. Modelo: Sonnet (Opus si es legal o hay plata).
8. **El Competidor.** ¿Cómo se ve al lado del que lo hace mejor? ¿Es genérico, intercambiable? ¿Por qué elegirían esto y no lo otro? Cuándo: copy, landings, posicionamiento, pitch. Modelo: Sonnet.
9. **El que no tiene tiempo (TL;DR).** Lo escanea en 10 segundos. ¿Se entiende el punto sin leer todo? ¿El asunto y la primera línea hacen el trabajo? Cuándo: mails, decks, docs largos. Modelo: Haiku.

## Flujo de una corrida

### Paso 0: identificar el artefacto, la audiencia y el objetivo [LAT]
Conseguir el texto: si lo pegó, usalo; si es un path/nombre, buscalo con `Glob`/`Read` (max ~30s); si es una referencia al vuelo ("el mail que acabás de escribir"), es el último artefacto de esta sesión. Si no lo podés ubicar con seguridad, NO adivines: pedí que lo peguen. Definir en una línea: qué es, para quién, qué tiene que lograr. Si esto está mal, contamina todo el panel.

### Paso 1: proponer el panel [LAT] (solo en modo deliberado)
Elegir las **2-5 lentes** que tienen sentido para ESTE artefacto (no las de siempre). Presentar compacto:
- El artefacto + audiencia + objetivo como los entendiste (una línea cada uno, para que corrija si inferís mal).
- Las N lentes elegidas, cada una con **por qué ESTA lente para ESTE artefacto** (sin mencionar el modelo).
- **Qué lentes dejaste afuera y por qué** (una línea, obligatorio: es el guardrail contra colapsar siempre al mismo roster).
- Cerrar: "¿Va así? ¿Saco o agrego alguna lente?" No spawnear hasta el OK.

En **modo directo**: saltear este paso, anunciar en una línea ("Tiro un panel de N: [lentes]") y pasar al paso 2.

### Paso 2: spawnear los reviewers [FANOUT: 2 a 5 subagentes en paralelo]
Spawnear todas las lentes a la vez (varios `Agent` calls en el MISMO mensaje = paralelo). Cada subagente recibe su identidad de lente, el artefacto completo, la audiencia + objetivo, y la instrucción de revisar SOLO desde su ángulo, citar el artefacto y dar cambios concretos. Modelo por lente vía el param `model` del Agent tool. Usar el template de abajo.

### Paso 3: evaluar los retornos [DET/LAT]
Chequear cada retorno contra dos criterios de descarte: **(a)** no cita el artefacto, **(b)** no refleja su lente (serviría para cualquier texto, o invade otra lente). Si falla UNO: re-tirar UNA vez con un prompt más afilado (no en loop). Si falla los DOS o vuelve vago: descartarlo y anotarlo. **Piso:** si quedan menos de 2 reviewers válidos, frená y avisá ("el panel volvió flojo, ¿reformulo las lentes?"), no presentes un mapa pobre.

### Paso 4: presentar el mapa de ángulos [LAT]
NO es un veredicto, es un mapa. Un bloque por reviewer (nombre de la lente + su lectura apretada, con las citas que trajo). Al final, dos líneas: **dónde coinciden** y **dónde se contradicen**.
**Guardrail de neutralidad, aplica al MAPA, no a la bajada** (lo que separa a Panel de un skill que decide). El mapa es foto cruda de lo que vieron los reviewers; la opinión sintetizada va recién en la bajada (paso 5):
- Las coincidencias se reportan como cuenta cruda ("lo marcaron N de M lentes"), NO como peso ni como "esto hay que cambiarlo". Que tres coincidan es un dato, no un veredicto.
- En el mapa, prohibido el lenguaje de recomendación: nada de "te recomiendo", "lo principal a cambiar es", "deberías". Si te sale sintetizar hacia una acción acá, frená: eso va en la bajada (paso 5), no en el mapa.

### Paso 5: la bajada [LAT] (SIEMPRE, los dos modos)
Después del mapa neutro, y separado con `---`, bajá la lectura accionable. Acá SÍ podés sintetizar y opinar (es lo único que se sale del guardrail de neutralidad, y va a propósito en su propio bloque para no contaminar el mapa). Encabezá el bloque dejando claro qué es: una lectura para arrancar, no un veredicto, tomala o tirala. Tres partes cortas:
- **Propuesta** (1-3 líneas): qué haría con esto si fuera tuyo, leyendo el mapa entero. La síntesis, no un resumen del mapa.
- **Oportunidades** (2-4 bullets): qué se ABRE, no solo qué arreglar. Ángulos para aprovechar, lo que más de una lente dejó picando como upside.
- **Pasos sugeridos** (2-4 bullets accionables): el next move concreto. Qué tocar primero, en qué orden, qué chequear antes de soltarlo. Verbos, no vibes.

Reglas: apoyate en lo que trajeron los reviewers (citá la lente: "el Destinatario y el de Riesgo coinciden en X → propondría Y"), no metas opinión que no salió del panel. Es sugerencia, no orden ("yo haría / yo arrancaría por", no "tenés que / hacé esto"). Si el panel volvió flojo o muy dividido, decilo en vez de inventar una propuesta firme: "el panel quedó partido entre A y B, no hay bajada limpia; depende de cuánto pese para vos [tradeoff]".

### Paso 6: devolver la pelota [DET] (SIEMPRE, los dos modos)
Cerrar toda corrida devolviéndole la decisión al usuario. La bajada propone; este paso confirma que la decisión es suya. La firma del skill:
> **Ahora vos:** la bajada es una lectura, no una orden. ¿Qué te resuena? ¿Qué vas a cambiar y qué vas a dejar igual aunque un reviewer lo marque?

### Paso 7: loguear la corrida [DET] (solo si hay brain escribible)
El log es CONDICIONAL. Append a `skills/panel/runs/YYYY-MM-DD.json` SOLO si hay un brain escribible del usuario (la carpeta `skills/` del brain existe o se puede crear). Si NO hay brain escribible (día cero, sin brain), SALTÁ este paso y corré normal: nunca escribas en el `kit/brain/` del método (es read-only). Schema (crear `runs/` si falta):
```json
{
  "fecha": "YYYY-MM-DDTHH:MM",
  "artefacto": "qué era, una línea",
  "audiencia": "para quién",
  "objetivo": "qué tenía que lograr",
  "modo": "deliberado|directo",
  "lentes": [{"lente": "El Destinatario", "modelo": "sonnet"}, "..."],
  "descartados": ["Lente X: razón", "..."],
  "coincidencia_clave": "lo que más de una lente marcó (con la cuenta N de M)",
  "contradiccion_clave": "donde se cruzaron, si pasó",
  "bajada": {
    "propuesta": "la síntesis en una línea",
    "oportunidades": ["...", "..."],
    "pasos_sugeridos": ["...", "..."]
  }
}
```

## Template de reviewer (subagente)
Prompt autocontenido. El subagente NO ve la conversación; pasale todo lo que necesita.
```
Sos un reviewer con UNA lente específica. No revisás todo: revisás SOLO desde tu ángulo.

TU LENTE: {nombre + el "qué mira" del catálogo, literal}

EL ARTEFACTO (revisalo entero):
---
{texto completo si es corto; si es largo o vive en un archivo, poné el path y "leelo con Read antes de revisar"}
---

CONTEXTO:
- Qué es: {artefacto}
- Para quién: {audiencia}
- Qué tiene que lograr: {objetivo}

Revisá SOLO desde tu lente. Citá el artefacto literal (entre comillas) cuando marques algo.
Concreto, no vibes. Quedate en tu lente. Sin preámbulo ni cierre cortés.

Devolvé este formato, máximo ~250 palabras:

FUNCIONA:
- {1-3 bullets de lo más fuerte desde tu lente, con cita}

FLOJO:
- {2-4 bullets de lo más débil, con cita + por qué}

EL CAMBIO:
- {la UNA cosa que cambiarías si solo pudieras tocar una}
```

## Qué lee y escribe
- **Lee:** el artefacto (pegado o por path) y, para contexto, el `CLAUDE.md` del proyecto activo si hace falta.
- **Escribe:** el mapa va al chat. El log a `skills/panel/runs/` solo si hay brain escribible (día cero se saltea, nunca al `kit/brain/`). No reescribe el artefacto (si después querés reescribir con lo que salió, eso es otro pedido, y si es texto pasa por `redactar`).

## Cuándo NO usar
- Búsquedas factuales o tareas mecánicas (no son review).
- Limpiar olor a IA de un texto: eso es `anti-slop`.
- Decidir entre opciones: Panel no decide, te devuelve la pelota.

## Señales de que lo hiciste bien (chequeo binario)
- [ ] Se eligieron 2-5 lentes adecuadas al artefacto (no un roster fijo), y en modo deliberado se justificó cada una Y qué quedó afuera ANTES de spawnear.
- [ ] En modo deliberado hubo OK explícito antes de spawnear; en modo directo se anunció el panel igual.
- [ ] Los reviewers corrieron en paralelo (un mensaje, N Agent calls), no en secuencia.
- [ ] Cada reviewer citó el artefacto; los vagos se re-tiraron una vez y se descartaron si volvieron vagos. Si quedaron <2 válidos, se frenó y se avisó.
- [ ] El MAPA quedó neutro: coincidencias como cuenta ("N de M lentes"), contradicciones explícitas, cero lenguaje de recomendación dentro del mapa.
- [ ] Después del mapa (separado con `---`) hubo una bajada accionable con sus tres partes (propuesta + oportunidades + pasos), apoyada en lo que trajeron los reviewers y marcada como lectura para arrancar, no veredicto.
- [ ] La corrida cerró devolviendo la pelota (paso 6), no dictando qué hacer.
- [ ] Si hay brain escribible, `skills/panel/runs/YYYY-MM-DD.json` tiene la corrida logueada con el schema completo (incluida la bajada); día cero (sin brain) el log se saltea y nunca se escribe en `kit/brain/`.

## Notas
- **Spawnear siempre en paralelo.** Secuencial desperdicia tiempo y deja que un reviewer contamine al siguiente.
- **Cada reviewer ve solo su lente y el artefacto, no la conversación.** Prompt autocontenido (contrato de subagente de `3. Recursos/arquitectura-skills.md`).
- **Artefacto largo: pasá el path, no lo pegues 5 veces.** Si es corto, va embebido; si es largo, pasale el path a cada subagente para que lo lea con Read.
- **Modelo por lente, no uno fijo (decisión interna).** Haiku para lentes mecánicas, Sonnet para la mayoría, Opus solo si el artefacto tiene stakes altos (legal, plata, algo donde equivocarse sale caro).
- **La contradicción entre reviewers no es un bug.** Que el Estratega diga "está perfecto" y el Adversario diga "no sobrevive" es exactamente lo que querés ver.

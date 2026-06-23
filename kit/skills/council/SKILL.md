---
name: council
kind: orchestrator
description: >
  Pasa una decisión con peso por un concilio de asesores que la analizan en
  paralelo, se revisan entre sí a ciegas y la cierran con un veredicto. Spawnea
  4-5 subagentes, cada uno pensando desde un ángulo distinto (el contrarian, el
  de primeros principios, el expansivo, el outsider, el ejecutor), después se
  revisan anónimo entre ellos, y un chairman sintetiza todo en UNA recomendación
  con su primer paso. A diferencia de `panel` (que solo te muestra ángulos y te
  devuelve la pelota), el council DECIDE: el chairman se la juega por una salida.
  Usalo cuando digas "council this", "llevá esto al concilio", "pasá esto por el
  concilio", "no me decido entre X e Y", "estoy entre dos opciones", "qué harías",
  "validame esta decisión", "pressure-test esto", "stress-test esto", "debatí esto",
  "decisión con peso", "es el movimiento correcto?". NO lo uses para preguntas
  factuales (tienen una respuesta sola), tareas de creación o resumen, ni "should
  I" triviales sin un tradeoff real. SÍ cuando hay incertidumbre genuina, varias
  opciones, y equivocarse sale caro.
---

# Council: un concilio que te cierra la decisión

Le preguntás a una IA y te da una respuesta. Puede ser buenísima. Puede ser mediocre. No tenés cómo saberlo porque viste un solo ángulo.

El council arregla eso. Corre tu decisión por 4-5 asesores independientes, cada uno pensando desde un ángulo que choca con los otros. Después se revisan entre sí a ciegas. Después un chairman sintetiza todo en una recomendación que te dice dónde coinciden, dónde se cruzan, qué blind spot cazaron, y qué deberías hacer.

Está adaptado del LLM Council de Karpathy: despachar a varios modelos, peer review anónimo, síntesis de un chairman. Acá hacemos lo mismo dentro de Claude, con subagentes que piensan desde lentes distintas en vez de modelos distintos.

Es el ejemplo de orquestador **multi-agente** del Nivel 5: el hilo principal no piensa, reparte la misma decisión a varios subagentes en paralelo y junta los veredictos.

**Council vs panel** (no son lo mismo): `panel` te muestra ángulos sobre algo que estás haciendo y te devuelve la pelota, no decide. `council` se la juega: el chairman sintetiza hacia UNA recomendación con su primer paso. Para VER mejor un artefacto antes de soltarlo → `panel`. Para DECIDIR algo con stakes → council.

## Rol

Orquestador (`kind: orchestrator`). El trabajo de pensar lo hacen los asesores; el skill coordina:
1. **Fino:** el hilo principal enmarca la decisión, valida el contexto, dispara los subagentes y arma el veredicto. El análisis vive adentro de cada asesor, reviewer y chairman.
2. **Evalúa a los workers:** la ronda de peer review anónimo (paso 3) ES la evaluación sobre los asesores; antes de pasar al chairman, chequea que cada asesor se haya quedado en su lente y sea específico (no genérico). El que volvió vago o genérico se descarta o se vuelve a tirar UNA vez.
3. **Loguea la corrida:** cada concilio cierra con un JSON estructurado (paso 7).

## Cuándo vale la pena

El council es para decisiones donde equivocarse sale caro.

**Sí:**
- "¿Lanzo el workshop de bajo precio o el curso caro?"
- "¿Cuál de estos 3 ángulos de posicionamiento es el más fuerte?"
- "Estoy pensando en pivotear de X a Y. ¿Estoy loco?"
- "¿Contrato a alguien o automatizo primero?"
- Cualquier decisión con incertidumbre real, varias opciones, y un costo alto si la pifiás.

**No:**
- "¿Cuál es la capital de Francia?" (una respuesta sola, es búsqueda factual).
- "Escribime un tweet" (tarea de creación, no una decisión).
- "Resumime este artículo" (procesamiento, no juicio).
- Un "¿debería X?" trivial sin tradeoff real (eso se contesta directo).

El council brilla cuando hay incertidumbre genuina y el costo de pifiarla es alto. Si ya sabés la respuesta y solo querés que te la validen, el council probablemente te diga cosas que no querés escuchar. Ese es el punto.

## Los cinco asesores

Cada asesor piensa desde un ángulo distinto. No son cargos ni personas: son estilos de pensamiento que naturalmente se contradicen entre sí. Por default van los 5; en una decisión chica podés bajar a 4 (el outsider es el primero que sale si el contexto es muy interno).

1. **El Contrarian.** Busca activamente qué está mal, qué falta, qué va a fallar. Asume que la idea tiene una falla fatal y trata de encontrarla. No es pesimista: es el amigo que te salva de un mal negocio haciendo la pregunta que estás evitando.
2. **El de Primeros Principios.** Ignora la pregunta de superficie y pregunta "¿qué estamos tratando de resolver de verdad?". Saca los supuestos, reconstruye el problema desde abajo. A veces el output más valioso del council es este asesor diciendo "estás haciendo la pregunta equivocada".
3. **El Expansivo.** Busca el upside que todos los demás se están perdiendo. ¿Qué podría ser más grande? ¿Qué oportunidad adyacente está escondida? No le importa el riesgo (de eso se encarga el Contrarian): le importa qué pasa si esto funciona mejor de lo esperado.
4. **El Outsider.** Cero contexto sobre vos, tu rubro o tu historia. Responde puro a lo que tiene enfrente. El más subestimado: caza la maldición del conocimiento, lo que es obvio para vos pero confuso para cualquier otro.
5. **El Ejecutor.** Le importa una sola cosa: ¿esto se puede hacer de verdad, y cuál es el camino más rápido? Mira cada idea desde "OK, ¿pero qué hago el lunes a la mañana?". Si una idea suena brillante pero no tiene un primer paso claro, el Ejecutor lo dice.

**Por qué estos cinco:** tres tensiones naturales. Contrarian vs Expansivo (downside vs upside). Primeros Principios vs Ejecutor (repensar todo vs hacelo ya). El Outsider en el medio manteniendo a todos honestos.

## Flujo de una corrida

### Paso 1: enmarcar la decisión (con contexto) [LAT]

**A. Buscar contexto, opcional y genérico.** Si sirve, leé rápido los 2-3 archivos que le darían piso a los asesores: si existe, el `CLAUDE.md` del proyecto/workspace activo; si existe, `2. Áreas/yo/sobre-mi.md` para saber quién decide y desde dónde; los archivos que el usuario referenció; corridas previas del council (para no volver a conciliar lo mismo). `Glob` + `Read` rápido, max ~30s. Si no hay nada de esto, seguís igual con lo que trajo el usuario.

**B. Enmarcar la decisión.** Reformulá la pregunta cruda + el contexto en un prompt claro y neutro que reciben los 5 asesores: (1) la decisión central, (2) el contexto clave del usuario, (3) el contexto clave de los archivos, (4) qué está en juego. No metas tu opinión. Si la pregunta es muy vaga, hacé UNA sola pregunta de aclaración y seguí.

**C. Validar el contexto con el usuario antes de convocar. Obligatorio.** Mandá una validación compacta: la decisión enmarcada tal cual, los 5-10 hechos clave que extrajiste (quién es quién, etapa, restricciones, stakes, números), y un solo pedido: "¿Es correcto? ¿Algo para ajustar antes de convocar al concilio?". **No spawnees asesores hasta el OK explícito.** Una premisa equivocada se propaga por 5 asesores y 5 reviewers y contamina el veredicto entero. Si el usuario corrige algo, actualizá y re-validá.

### Paso 2: convocar al concilio [FANOUT: 4-5 subagentes en paralelo]

Spawneá los 5 asesores a la vez (varios `Agent` calls en el MISMO mensaje = paralelo). Cada uno recibe: su identidad + estilo de pensamiento, la decisión enmarcada, y la instrucción de responder independiente, sin hedging, metiéndose de lleno en su ángulo. 150-300 palabras cada uno. Usá el template de abajo. Modelo por asesor vía el param `model` del Agent tool (decisión interna, no se le muestra al usuario): la mayoría en el modelo medio; subí al grande solo si la decisión pesa fuerte (plata, irreversible).

### Paso 3: peer review [FANOUT: 5 subagentes en paralelo] [DET/LAT]

El paso que hace que esto sea más que "preguntar 5 veces". Juntá las 5 respuestas, anonimizalas como Respuesta A-E (randomizá el mapeo para evitar sesgo de posición). Spawneá 5 reviewers; cada uno ve las 5 respuestas anónimas y contesta: (1) la respuesta más fuerte y por qué, (2) el blind spot más grande, (3) qué se les escapó a TODAS. Menos de 200 palabras cada uno.

**Evaluación de los asesores (acá vive la obligación 2 del Rol).** Antes de pasar al chairman, chequeá cada respuesta de asesor contra dos criterios de descarte: **(a)** no se quedó en su lente (serviría para cualquier asesor, o invade otra lente), **(b)** es genérica, no toca la decisión concreta. Si falla uno: re-tirá ese asesor UNA vez con un prompt más afilado (no en loop). Si vuelve vago: descartalo y anotalo. **Piso:** si quedan menos de 3 asesores válidos, frená y avisá ("el concilio volvió flojo, ¿reformulo la decisión?"), no armes un veredicto pobre.

### Paso 4: síntesis del chairman [LAT]

Un subagente recibe todo: la decisión enmarcada, las respuestas de los asesores ya des-anonimizadas, los 5 peer reviews. Produce el VEREDICTO: dónde coincide el concilio, dónde se cruza, qué blind spots cazaron, la recomendación, y la única cosa para hacer primero. El chairman PUEDE estar en contra de la mayoría si el razonamiento del que disiente es el más fuerte. Acá está la diferencia con `panel`: el chairman se la juega por una salida, no deja la pelota flotando.

### Paso 5: presentar el veredicto en el chat [DET]

Mostrá el veredicto completo directo en el chat como markdown. NO generes un HTML ni archivos. Formato:

```
## Veredicto del Concilio: {tema en una línea}

### Dónde coincide el concilio
### Dónde se cruza el concilio
### Blind spots que cazó el concilio
### La recomendación
### La única cosa para hacer primero
```

Escaneable, en bullets. La recomendación NO puede ser "depende": el chairman se juega una salida (puede traer su condición, pero elige).

### Paso 6: guardar el transcript (opcional) [DET]

Solo si el usuario lo pide o la decisión es lo bastante importante como para volver a ella. Escribí `council-transcript-[timestamp].md` en la carpeta del proyecto activo, o en `output/` si no hay proyecto activo.

### Paso 7: loguear la corrida [DET]

Siempre, haya transcript o no. Append a `skills/council/runs/YYYY-MM-DD.json` (crear `runs/` si falta; si ya existe el archivo del día, append a su array). Schema:

```json
{
  "fecha": "YYYY-MM-DDTHH:MM",
  "decision_consultada": "la decisión enmarcada, una línea",
  "asesores": ["Contrarian", "Primeros Principios", "Expansivo", "Outsider", "Ejecutor"],
  "descartados": ["Asesor X: razón", "..."],
  "veredicto_chairman": "la recomendación, una línea",
  "disidencias": ["asesor + su disidencia en una línea", "..."]
}
```

## Template de asesor (subagente)

Prompt autocontenido. El subagente NO ve la conversación; pasale todo lo que necesita.

```
Sos UN asesor de un concilio. Pensás desde UNA lente específica, de lleno, sin hedging.

TU LENTE: {nombre + la descripción literal del estilo de pensamiento del catálogo}

LA DECISIÓN (enmarcada, neutra):
---
{decisión central + contexto del usuario + contexto de archivos + qué está en juego}
---

Respondé SOLO desde tu lente. No trates de ser equilibrado: ese es el trabajo
de los otros asesores. Concreto, atado a ESTA decisión, no a una genérica.
Sin preámbulo ni cierre cortés.

Máximo 300 palabras. Decí lo que ves desde tu ángulo y cerrá con tu llamado:
qué harías vos con esto, visto solo desde tu lente.
```

Template de reviewer (la ronda anónima):

```
Sos un reviewer del concilio. Tenés 5 respuestas anónimas (A-E) a la misma decisión.
No sabés quién dijo qué, y no te importa: evaluá por mérito, no por estilo.

LAS RESPUESTAS:
{A-E, anonimizadas, mapeo randomizado}

Contestá en menos de 200 palabras:
1. La respuesta más fuerte y por qué.
2. El blind spot más grande de todas.
3. Qué se les escapó a TODAS.
```

Template del chairman:

```
Sos el chairman del concilio. Recibís: la decisión enmarcada, las 5 respuestas de
los asesores (con nombre), y los 5 peer reviews anónimos.

Tu trabajo es DECIDIR, no resumir. Sintetizá hacia UNA recomendación.
Podés estar en contra de la mayoría si el que disiente tiene el razonamiento más
fuerte (explicá por qué).

Devolvé exacto este formato:
## Dónde coincide el concilio
## Dónde se cruza el concilio
## Blind spots que cazó el concilio
## La recomendación  (una salida concreta, no "depende")
## La única cosa para hacer primero
```

## Qué lee y escribe

- **Lee:** la decisión que trae el usuario y los archivos que referenció. Para contexto, si existen: el `CLAUDE.md` del proyecto activo y `2. Áreas/yo/sobre-mi.md` (quién decide). Todo opcional: si no están, el council corre igual.
- **Escribe:** el veredicto va al chat. El log siempre a `skills/council/runs/`. El transcript completo solo si lo piden (paso 6). No reescribe el artefacto ni ejecuta la decisión: te da la recomendación, la decisión la tomás vos.

## Cuándo NO usar

- Preguntas factuales o búsquedas (tienen una respuesta sola, contestala directo).
- Tareas de creación (escribir algo) o de procesamiento (resumir): no son decisiones.
- Un "¿debería?" trivial sin tradeoff real.
- VER mejor un artefacto antes de soltarlo (PRD, mail, copy): eso es `panel`, que muestra ángulos y te devuelve la pelota. El council es para DECIDIR.

## Señales de que lo hiciste bien (chequeo binario)

- [ ] La validación de contexto (paso 1C) pasó ANTES de spawnear cualquier asesor, con OK explícito del usuario.
- [ ] Las dos rondas de fanout corrieron en paralelo (un mensaje, varios `Agent` calls cada una), no en secuencia.
- [ ] El peer review fue anónimo con mapeo de letras randomizado.
- [ ] Se evaluó a los asesores antes del chairman: los genéricos o fuera de lente se re-tiraron una vez y se descartaron si volvieron vagos. Si quedaron <3 válidos, se frenó y se avisó.
- [ ] El veredicto tiene las 5 secciones y una recomendación que NO es "depende": el chairman se jugó una salida.
- [ ] No se generó HTML ni archivos de reporte; el veredicto vive en el chat.
- [ ] `skills/council/runs/YYYY-MM-DD.json` tiene la corrida logueada con el schema completo.

## Notas

- **Spawneá siempre los asesores en paralelo.** Secuencial desperdicia tiempo y deja que una respuesta temprana contamine a la siguiente.
- **Anonimizá siempre el peer review.** Si los reviewers saben quién dijo qué, defieren a ciertos estilos en vez de evaluar por mérito.
- **El chairman puede ir contra la mayoría.** Si 4 de 5 dicen "hacelo" pero el que disiente tiene el razonamiento más fuerte, ponete del lado del que disiente y explicá por qué.
- **No concilies trivialidades.** Si hay una respuesta sola, contestala y listo.
- **Cada subagente ve solo su prompt, no la conversación.** Prompt autocontenido (contrato de subagente del Nivel 5).
- **La contradicción entre asesores no es un bug.** Que el Expansivo diga "esto puede ser enorme" y el Contrarian diga "esto se cae" es exactamente lo que querés ver: el chairman se para en la tensión.

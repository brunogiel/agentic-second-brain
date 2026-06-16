<!--
  REFERENCE — el manual que crece (SecondBrain).
  Plantilla en español. No se lee de corrido: es consulta, vas a una sección cuando la necesitás.
  Al instalar, este archivo vive OCULTO en .secondbrain/reference.md. El usuario no lo ve en Finder; el coach lo lee cuando hace falta.
-->

# reference.md: El manual

Esto no se lee de un tirón. Es una caja de herramientas: venís acá cuando querés subir un escalón. Tu `CLAUDE.md` raíz alcanza para arrancar. Esto es para cuando quieras crecer. ¿No sabés por dónde seguir? Pedile **`/second-brain-coach`**.

---

## 1. El porqué: por qué unas carpetas cambian tu asistente

Pensalo en 3 capas:

1. **El modelo** (Claude). Es un cerebro que genera texto. Solo. No sabe quién sos.
2. **El harness** (Claude Code, Cowork, Cursor). Es el cuerpo: le da manos para tocar archivos, memoria, y un loop para trabajar solo.
3. **Tus carpetas** (este sistema). Son lo que el harness lee para volverse *tu* asistente.

La frase clave: **tus carpetas personalizan el asistente, no son el asistente.** Por eso un archivo de texto bien puesto cambia tanto el resultado: el asistente lo lee al arrancar y deja de improvisar sobre quién sos. Ese es todo el truco. El resto es ordenar.

---

## 2. PARA: cómo ordenás cualquier cosa

Una sola pregunta para decidir dónde va algo: *¿esto qué es?*

- **1. Proyectos/** : tiene un objetivo y termina. ("Lanzar la landing", "Cerrar el balance de marzo").
- **2. Áreas/** : una responsabilidad que no termina. ("Salud", "Finanzas", "Mi rol en la empresa").
- **3. Recursos/** : material de referencia que sirve a varios proyectos. ("Mis plantillas", "Frameworks que uso").
- **4. Archivo/** : lo terminado o lo que pausaste. No lo borrás, lo sacás de la vista.

Regla práctica: si dudás entre Proyecto y Área, preguntate *¿esto se termina algún día?* Si sí, Proyecto. Si no, Área. Cuando un proyecto se cierra, pasalo a Archivo (no lo borres, sirve de historia).

---

## 2b. El inbox: capturar sin decidir

Antes de PARA hay un paso que casi todos se saltan: **capturar**. PARA te dice dónde va algo *cuando ya sabés qué es*. Pero la mayoría de las cosas llegan turbias: una idea suelta, un link para leer, una decisión que no está madura. Si te obligás a clasificarlas en el momento, frenás; y lo que no clasificás, lo perdés.

Por eso `0. Inbox/` va **adelante de todo**: es la bandeja donde tirás algo y seguís. Un archivo por cosa, una línea alcanza (`AAAA-MM-DD-de-que-va.md`). Sin esfuerzo: la gracia es que sea sin fricción.

Cada tanto (no a diario) **cocinás** el inbox: a cada item le das destino → ✅ resolver (se vuelve proyecto/tarea/nota y sale), 🔄 sigue turbio (lo dejás, anotando qué falta para decidir), 🗑 descartar (a `4. Archivo/inbox-cocidos/`, no se borra). 

La distinción clave: **capturar no es archivar.** Si algo ya es claro y accionable, va directo a su lugar. El inbox es para lo que todavía no. Frases que mandan algo acá: *"dejalo para después"*, *"metelo al inbox"*, *"no lo quiero decidir ahora"*.

---

## 3. Cada proyecto tiene su propio cerebro

Adentro de cada proyecto va un `CLAUDE.md` (hay una plantilla en `.secondbrain/plantilla-proyecto.md`) con:
- **Contexto:** qué es, quién participa, qué estado tiene, qué links importan.
- **Cómo trabajar acá (opcional):** la "persona" del asistente para ESTE proyecto. Mismo modelo, distinto compañero: un proyecto de plata quiere uno escéptico que verifique números; uno de escritura, uno que no te corrija el tono. Dos líneas alcanzan ("sé escéptico", "sé breve", "paso a paso").
- **Log de decisiones:** una línea con fecha cada vez que decidís algo importante. ("2026-06-01: elegimos X en vez de Y porque Z").
- **Próximo paso:** una línea de qué sigue y con qué contexto — el "handoff" a tu yo futuro.

El log es oro: la próxima vez que abrís el proyecto (vos o el asistente), no tenés que reconstruir por qué hiciste las cosas. Está escrito. Y no hace falta que lo lleves a mano: los skills `cerrar-sesion` (deja el log y el próximo paso al día al terminar) y `abrir-sesion` (te briefea al retomar) automatizan ese ciclo. El modelo es stateless; este archivo no.

---

## 4. Memoria: qué guardar y qué no

`MEMORIA.md` es donde el asistente acumula hechos que valen para todo, no para un proyecto. ("Soy alérgico a X", "Mi tono en mails es informal", "Prefiero que me preguntes antes de asumir").

Guardá lo que **no** se deduce solo de tus archivos. No guardes lo que ya está escrito en otro lado (eso es duplicar). Si algo resultó ser falso, borralo.

**Por qué importa capturar:** el modelo arranca de cero cada vez (es *stateless*), tus archivos no. Cada cosa que anotás, la próxima sesión ya la sabe. Por eso el sistema se vuelve más *vos* con el uso: no porque el asistente sea más inteligente, sino porque tu memoria es más rica. El que captura, gana.

---

## 5. Skills: cuándo y cómo

> La versión completa y a mano vive como Recurso en `3. Recursos/arquitectura-skills.md`. Acá va el resumen.

Un **skill** es una receta guardada: instrucciones que el asistente sigue cuando una frase lo dispara. Mientras nadie lo llama, no hace nada. Por eso podés tener muchos sin que te molesten.

**Cuándo crear uno: la regla de 3.** ¿Le pediste lo mismo 3 veces? Convertilo en skill. Antes de eso es prematuro.

Regla de diseño: el harness fino, el skill gordo. Toda la inteligencia vive en el `SKILL.md`, no en mil instrucciones sueltas que repetís cada vez.

**Anatomía mínima de un skill que funciona** (un archivo `SKILL.md` en una carpeta):
- **Descripción con frases reales** que lo disparan (no "hace reportes", sino "cargá la factura", "subí el resumen"). Esa descripción es lo que hace que se dispare solo cuando lo necesitás.
- **Contexto en 2 líneas:** qué hace y para quién, en términos de tu trabajo, no de código.
- **Cuándo SÍ y cuándo NO** usarlo (los bordes importan tanto como el centro).
- **Pasos marcados `[DET]` o `[LAT]`** (mirá la sección 6).
- **Qué archivos lee y escribe**, para no pisar nada por accidente.
- **Cómo se ve un buen resultado:** qué devuelve y 2-3 señales de que salió bien.

**Errores típicos al hacer skills (evitalos):**
- **Clonar un skill cambiando un dato.** Si tenés "skill-para-Ana" y "skill-para-Juan" iguales salvo el nombre, parametrizá: que tome el nombre como dato de entrada.
- **Pedirle al modelo que haga cuentas grandes.** Contar, sumar o cruzar 500 filas es código (DET), no criterio. El modelo se equivoca en lo combinatorio.
- **Meter todo en un mega-skill.** Si una parte sirve para varias cosas (por ejemplo, tu forma de escribir), sacala a su propio skill chico y reusala en vez de enterrarla.
- **Skill sin señales de éxito.** Si al terminar no sabés si salió bien más allá de "parece OK", falta definir cómo se mide.

---

## 6. DET vs LAT: el click que mejora todo lo que pedís

Cuando le das una instrucción (o escribís un skill), separá cada paso en dos tipos:

- **DET (determinístico):** mecánico, siempre igual, no requiere pensar. *"Abrí este archivo", "sumá la columna C", "mandá el mail a esta dirección".*
- **LAT (latente):** requiere criterio del asistente. *"Decidí qué leads priorizar", "escribí el resumen en mi tono", "elegí el mejor título".*

Por qué importa:
- Los pasos **DET** conviene clavarlos exactos (o que los haga código), así el asistente no improvisa donde no debe.
- Los pasos **LAT** son donde le dejás pensar de verdad. Ahí le das contexto y libertad, no una receta rígida.

El error típico del principiante es tratar todo como LAT ("hacelo lindo") o todo como DET ("seguí estos 40 pasos"). Cuando separás, tus pedidos se vuelven claros y tus skills, confiables. Marcá cada paso `[DET]` o `[LAT]` y vas a ver la diferencia.

---

## 7. Qué es un script y por qué importa

Un **script** es un pedacito de código que hace siempre lo mismo, sin pensar: leer un archivo, contar filas, comparar dos números, bajar algo de internet. Es la forma de clavar un paso **DET**.

La idea de fondo: **lo mecánico lo hace un script, no el modelo adivinando.** El modelo es genial para el criterio (LAT), pero es caro y se puede equivocar en lo repetitivo y combinatorio. Un script no se cansa, no improvisa, y cuesta cero.

- **Si usás Claude Code (terminal):** un script de verdad es un archivo `.sh` o `.py` que el asistente corre. Ejemplo: un script que compara la versión del kit con la tuya.
- **Si usás Cowork (sin terminal):** no hace falta un archivo de código. "El script" es el paso mecánico que el asistente hace con sus herramientas de forma confiable (bajar el dato, compararlo). El concepto es el mismo: la parte mecánica se ejecuta igual siempre, no se improvisa.

No te asustes con la palabra. Tu primer script va a ser de tres líneas (mirá la sección 8).

---

## 8. Tu primer skill: leé el que ya viene, después armá el tuyo

El kit ya trae un skill funcionando, **`actualizar`** (vive en `~/.claude/skills/actualizar/`): chequea si SecondBrain tiene mejoras y, con tu OK, las baja. No hace falta que lo armes: **ábrilo para ver cómo es un skill por dentro** (el frontmatter con las frases que lo disparan, los pasos `[DET]`/`[LAT]`, su scriptito `check-update.sh`). Ese es tu ejemplo de referencia.

Después armá **el tuyo**: algo que repitas de verdad (regla de 3). Va en `skills/<nombre>/SKILL.md` (carpeta a la vista) + su fila en la tabla "Mis skills" del `CLAUDE.md` (esa fila es lo que lo dispara). El skill `crear-skill` te guía.

Abajo, la anatomía del `actualizar` como modelo de lo que tiene que tener cualquier skill:

**Qué hace (el patrón a copiar):**
1. **[DET]** Leer la versión publicada del kit (el archivo `VERSION` del repo) y compararla con la tuya (`.secondbrain/VERSION`).
2. **[LAT]** Si hay una nueva, contarte qué cambió (del `CHANGELOG`) y preguntarte: *"¿te la instalo?"*.
3. **[DET]** Si decís que sí, bajar lo nuevo.

Fijate cómo el paso 1 y el 3 son mecánicos (script) y el 2 es criterio (el asistente decide cómo contártelo y espera tu OK). Eso es DET vs LAT en vivo.

**El `SKILL.md` mínimo** (así viene `actualizar`; los tuyos van en `skills/<nombre>/SKILL.md` + su fila en la tabla):

```
---
name: actualizar
description: >
  Chequea si el kit SecondBrain tiene una versión nueva y, si vos querés, la instala.
  Usalo cuando digas "¿hay updates?", "actualizá el kit", "fijate si salió algo nuevo",
  "actualizá SecondBrain".
---

# actualizar: bajar las mejoras del kit

## Flujo
1. [DET] Leé la versión publicada (VERSION del repo) y la local (.secondbrain/VERSION).
2. [LAT] Si la publicada es más nueva: mostrá qué cambió (CHANGELOG) y preguntá "¿te la instalo?".
3. [DET] Con el OK: bajá los archivos nuevos y actualizá .secondbrain/VERSION.

## Cuándo NO usar
- Para actualizar tus propios proyectos (esto es solo el kit).

## Señales de que salió bien
- Sabés si estás al día o no, sin entrar a internet a mano.
- Nada se bajó sin tu OK.
```

El "script" (el paso DET de comparar versiones) en Claude Code es el `check-update.sh` que viene con el skill. En Cowork, el asistente hace ese chequeo con sus herramientas. La receta es la misma.

Cuando armás el tuyo siguiendo este molde, ese es tu Nivel 3. Y el próximo escalón sale solo: poner `actualizar` a correr automático (Nivel 4, sección 10).

---

## 9. Skill vs agente

- **Skill = receta.** Corre dentro de tu sesión, con vos presente. Puede preguntarte.
- **Agente = proceso que corre solo.** Arranca limpio (sin tu charla), hace su tarea, termina. Puede dispararse por horario.

Empezás con skills. Los agentes vienen después, cuando una tarea ya no necesita que estés ahí.

---

## 10. Rutinas: poner algo a correr solo

Una **rutina** es un skill (o una tarea) que corre en horario, sin que estés. La primera buena rutina es poner `actualizar` (que ya viene) a correr los lunes: que mire si el kit tiene mejoras.

- **En Claude Code / Cowork:** se agenda con la función de tareas programadas del cliente (pedile al asistente "agendá esto para los lunes a las 9").
- **Anotala** en la sección "Rutinas" de tu `CLAUDE.md` raíz, así sabés qué tenés corriendo (y el coach lo detecta).

**Una rutina sin log es ciega.** Como corre sin que estés, si falla no te enterás. La regla mínima: que al terminar deje **una línea de registro** en un archivito (por ejemplo `<la rutina>/last_run.txt`): *qué corrió, salió bien sí/no, cuándo, y un número clave si aplica*. Con eso, de un vistazo sabés si el sistema viene funcionando mientras dormís. No hace falta más que eso para empezar; lo elaborado (histórico, semáforo de salud) es de la sección 16, posgrado.

Bonus: una rutina arranca en contexto limpio, hace lo suyo y termina. No te infla las sesiones donde estás laburando. Son baratas por diseño.

---

## 11. Orquestador vs worker (más adelante todavía)

Cuando tengas varias recetas, una puede coordinar a las otras:
- **Worker:** hace una tarea concreta.
- **Orquestador:** no hace el trabajo, decide qué worker corre y junta los resultados.

Tu `/second-brain-coach` es un orquestador chiquito: no hace tu sistema, te lleva de la mano para que lo armes vos.

---

## 12. Si programás: el split código / contexto

Una sola regla: **el código vive en su repo, el contexto vive en este sistema.**
- Código → `~/Code/<proyecto>/` (con git).
- Contexto, decisiones, notas → tu carpeta de Proyecto acá.
- En el repo, un `CLAUDE.md` corto apunta de vuelta a este sistema, así el asistente sabe dónde está todo.

Y si el desarrollo es en serio (epics, PRDs, un equipo), eso es un deporte aparte: hay métodos dedicados al ciclo de desarrollo agéntico, como [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD). No compiten con esto: SecondBrain se queda con tu contexto y decisiones; el método de dev maneja la construcción dentro del repo. Conviven en este mismo split.

Si no programás, esta sección no te toca.

---

## 13. Liviano para correr (que no te queme el plan)

Tu sistema tiene que andar barato, sobre todo si estás en el plan de $20. La idea de fondo: **el sistema crece a lo ancho, no a lo alto.** Más archivitos chicos, no archivos gordos que se leen siempre. Bien ruteado, tener 50 archivitos sale MÁS barato que 3 enormes, porque cada sesión lee solo la rebanada que toca.

Y no es solo plata: **el contexto inflado también rinde peor.** El asistente trabaja en su "memoria de trabajo" (la ventana de contexto, su RAM); cuando la llenás de cosas que no tocan, recuerda y razona peor (a esto se le dice *context rot*). Por eso el `CLAUDE.md` raíz es **RAM curada**: un mapa fino, no un volcado. No lo engordes — lo barato y lo que rinde van de la mano.

Las 3 capas de costo:
1. **Lo que se lee SIEMPRE** = el `CLAUDE.md` raíz. Tiene que ser un mapa fino (punteros + atajos), no contenido. Nunca lo engordes.
2. **Lo que se lee al entrar a un proyecto** = el `CLAUDE.md` de ese proyecto. Dormido hasta que lo tocás.
3. **Lo que se lee cuando una frase lo dispara** = los skills. Viajan dormidos.

El truco del status: `ESTADO.md` es un archivo chico (nivel + proyectos activos + qué cambió). El asistente lo lee al arrancar y de ahí sabe **qué leer y qué no**, sin escanear todo el árbol.

---

## 14. Topología: proceso oculto, entregables a la vista

La regla, en **3 baldes** (así tu carpeta se ve limpia y sabés qué es qué):

1. **👁 VISIBLE en tu SB — lo tuyo.** Tu contexto: las carpetas PARA + `0. Inbox/`, tu identidad (`2. Áreas/yo/`), tu progreso (`ESTADO.md`), el `CLAUDE.md` raíz (router) + `AGENTS.md`. Y **`skills/`: los skills que usás** (redactar, anti-slop, triage, auditar, crear-skill, abrir/cerrar-sesion + los que armes vos). Los ves, los abrís, aprendés cómo están. No vienen todos de una: el coach te los va sumando a medida que avanzás.

2. **🔒 OCULTO en tu SB — el proceso (`.secondbrain/`).** Esta doctrina (`reference.md`), la `plantilla-proyecto.md`, el **catálogo** `skills-disponibles/` (las versiones-fuente de los skills de uso, de donde el coach copia a `skills/` cuando adoptás uno) y el control de versión. Empieza con punto: no se ve en Finder, pero sincroniza igual.

3. **🔒 GLOBAL e invisible (`~/.claude/skills/`) — solo el motor de armado.** El coach, `actualizar` y `migrar`. Se llaman por nombre (`/second-brain-coach`); no viven en tu carpeta ni aparecen en `skills/`. (En Cowork, sin global, el motor viaja dentro de la carpeta — el único caso en que está adentro.)

Vos solo ves lo que usás. El proceso y el motor trabajan de fondo.

> **Cómo se disparan (y por qué es portable).** Tus skills de uso viven en `skills/` a secas — carpeta normal, a la vista, sin nada oculto. Lo que los dispara es **la tabla "Mis skills" de tu `CLAUDE.md`**: tu asistente lee el `CLAUDE.md` al arrancar cada sesión y, cuando decís una frase que matchea una fila (frase → skill), va y sigue ese `skills/<nombre>/SKILL.md`. Por eso funcionan **igual en Claude Code, Cowork y Codex**: los tres leen el `CLAUDE.md` (en Codex, vía `AGENTS.md` que apunta ahí). No dependen de una carpeta `.claude/skills/` específica de Claude. La regla práctica: **un skill sin su fila en la tabla no existe para el asistente** — siempre anotalo.

---

## 15. Buenas costumbres
- **No creés cosas sin pedido.** El asistente no debería inventar archivos, READMEs ni carpetas porque sí. Que pregunte.
- **Una decisión, una línea en el log.** Te lo agradecés en 3 meses.
- **Revisá de a uno.** Pedile las cosas de a una y mirá antes de seguir. El asistente es rápido, vos sos el que decide.
- **Empezá chico y medí.** No armes el sistema entero hoy. Subí un escalón, usalo una semana, subí el siguiente.

---

## 16. Orquestar y mantener (Niveles 5-6)

Cuando ya tenés varios skills y una rutina, el sistema da para más. Ojo: esto **no es posgrado** — son los dos últimos escalones del espinazo. No viene armado: lo armás a tu medida. Acá los conceptos.

**Nivel 5 — Orquestar.** Un orquestador es una receta que NO hace el trabajo: coordina a otros skills (o a subagentes) y junta los resultados.
- **Orquestador con estado:** llama a varios en orden y arrastra contexto entre pasos. Para procesos de varios pasos que se repiten.
- **Multi-agente:** varios asistentes en paralelo, cada uno con su parte, y uno que junta. Para trabajo grande que no entra en una sola cabeza. Caso potente: **varias miradas sobre la misma decisión** — un pedido corre 4 lentes (el que defiende, el abogado del diablo que hace el pre-mortem, el que verifica los números, el que mira el equipo) y después sintetiza. Un lente sesga; cuatro dan una decisión más honesta. (Ya hecho: tu skill `council`.)
- **Cómo se aprende:** igual que un skill — usás uno de ejemplo (el de PPT, que arma una presentación coordinando varios skills/subagentes) para ver el patrón, y después armás el tuyo. El "cómo se arma" está en `arquitectura-skills.md`.

**Nivel 6 — Mantener.** Un sistema que no se revisa se pudre callado. Dos herramientas del kit:
- **`auditar-sistema`:** el chequeo de salud (tipo sábado) — archivos huérfanos, skills que dejaron de cumplir, rutinas que fallan mudas.
- **`evaluar-skill` (evals):** medís un skill contra su propia rúbrica en una corrida real y aplicás una mejora, en vez de "parece que anduvo". El cierre del loop ("autoresearch"): `evaluar-skill` detecta el fallo → vos (o `crear-skill`) aplicás el arreglo → repetís. Respeta "propone, vos decidís": nunca pisa un skill solo.

**Frontera real (opt-in, posgrado de verdad):** lo que sí esperás a que todo lo anterior te quede chico — agentes 100% autónomos que actúan sin tu OK, y la auto-mejora corriendo en loop cerrado sin vos en el medio. La mayoría no lo necesita.

---

## 17. Conectar herramientas (MCP) y subagentes

Dos cosas que, cuando las entendés, te cambian lo que podés hacer. No son del día uno, pero tampoco son posgrado: valen la pena.

**Conectar herramientas (MCP).** Por default tu asistente toca archivos. Con MCP (un estándar para enchufarle herramientas) le das acceso a tus apps: Gmail, tu calendario, una base de datos, lo que sea. Recién ahí puede leer tu inbox, agendar, consultar tus datos. Ejemplo concreto: conectás Gmail por MCP y entonces sí podés tener una rutina que te arma el digest de los mails de la mañana. El MCP es la diferencia entre un asistente que solo ordena tus carpetas y uno que opera tu mundo. Una forma de pensarlo: **el MCP es la plomería (le da acceso a la herramienta); el skill es el cerebro (sabe cómo usarla).** Cómo se conecta depende del cliente (Claude Code, Cowork): pedile a tu asistente que te guíe para enchufar el que necesites. Esto es parte del **Nivel 4** y **no requiere programar** — es configurar un conector, no escribir código.

> **Ojo con el combo riesgoso.** Cuando le das a la vez (1) acceso a datos privados, (2) la posibilidad de leer contenido de afuera que no controlás (un mail, una web) y (3) capacidad de mandar cosas para afuera (responder mails, postear), abrís la puerta a que un contenido malicioso le "dicte" acciones. No es para asustarte: es para que, antes de automatizar algo que mezcle las tres, lo revises y, si hay dudas, lo dejes con tu OK en el medio.

**Subagentes.** Un subagente es otro asistente que lanzás para una parte del laburo, en paralelo, con su propio contexto limpio. Sirve para cosas grandes: revisar 20 archivos a la vez, investigar varios temas en simultáneo, o separar un trabajo en pedazos que corren juntos y después se juntan. La regla: usalo cuando una tarea es grande o tiene partes independientes. Para lo chico y secuencial, no hace falta, suma ruido. Los subagentes en paralelo son el corazón del multi-agente del **Nivel 5** (sección 16); usarlos dentro de tu propio código es la rama "si programás".

Las dos se combinan con lo de antes: una rutina (sección 10) que conecta una herramienta por MCP y reparte el trabajo en subagentes es, básicamente, un asistente que trabaja solo mientras dormís.

---

## La escalera (tu índice de crecimiento)
- **Nivel 0:** el asistente te conoce (`sobre-mi` + `como-trabajo`) y capturás en `0. Inbox/` (sección 2b).
- **Nivel 1:** tu primer proyecto con su `CLAUDE.md`.
- **Nivel 2:** la tabla de atajos en tu `CLAUDE.md` raíz.
- **Nivel 3:** tu primer skill propio (leyendo el `actualizar` de ejemplo, sección 8).
- **Nivel 4:** el sistema trabaja para vos — tu primera rutina (poné `actualizar` a correr solo, con log, sección 10) + conectar una herramienta por MCP para que `triage` arme el brief del día (sección 17; no requiere programar).
- **Nivel 5:** orquestás — usás un orquestador de ejemplo (el de PPT) y después armás el tuyo, multiagente (sección 16).
- **Nivel 6:** mantenés el sistema — tu primera revisión con `auditar-sistema` + afinás un skill con `evaluar-skill` (sección 16).
- **Rama (si programás), fuera del conteo:** el split código / contexto + subagentes en tu código.
- **Más allá:** frontera real (agentes autónomos, auto-mejora en loop), opt-in.

¿No sabés en qué escalón estás? Pedile **`/second-brain-coach`**.

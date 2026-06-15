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

## 3. Cada proyecto tiene su propio cerebro

Adentro de cada proyecto va un `CLAUDE.md` con dos cosas:
- **Contexto:** qué es, quién participa, qué estado tiene, qué links importan.
- **Log de decisiones:** una línea con fecha cada vez que decidís algo importante. ("2026-06-01: elegimos X en vez de Y porque Z").

El log es oro: la próxima vez que abrís el proyecto (vos o el asistente), no tenés que reconstruir por qué hiciste las cosas. Está escrito.

---

## 4. Memoria: qué guardar y qué no

`MEMORIA.md` es donde el asistente acumula hechos que valen para todo, no para un proyecto. ("Soy alérgico a X", "Mi tono en mails es informal", "Prefiero que me preguntes antes de asumir").

Guardá lo que **no** se deduce solo de tus archivos. No guardes lo que ya está escrito en otro lado (eso es duplicar). Si algo resultó ser falso, borralo.

---

## 5. Skills: cuándo y cómo

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

## 8. Armá tu primer skill, paso a paso: el chequeador de updates

Tu primer skill conviene que sea uno **útil y chico**: uno que chequee si este kit (SecondBrain) tiene mejoras nuevas, así las bajás. De paso, armarlo te enseña qué es un skill y qué es un script.

**Qué tiene que hacer:**
1. **[DET]** Leer la versión publicada del kit (el archivo `VERSION` del repo) y compararla con la tuya (`.secondbrain/VERSION`).
2. **[LAT]** Si hay una nueva, contarte qué cambió (del `CHANGELOG`) y preguntarte: *"¿te la instalo?"*.
3. **[DET]** Si decís que sí, bajar lo nuevo.

Fijate cómo el paso 1 y el 3 son mecánicos (script) y el 2 es criterio (el asistente decide cómo contártelo y espera tu OK). Eso es DET vs LAT en vivo.

**El `SKILL.md` mínimo** (en `.claude/skills/actualizar/SKILL.md`):

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

El "script" (el paso DET de comparar versiones) en Claude Code es un comando que baja el `VERSION` del repo y lo compara. En Cowork, el asistente hace ese chequeo con sus herramientas. La receta es la misma.

Cuando lo termines, ese es tu Nivel 3. Y el próximo escalón sale solo: ponerlo a correr automático (Nivel 4, sección 10).

---

## 9. Skill vs agente

- **Skill = receta.** Corre dentro de tu sesión, con vos presente. Puede preguntarte.
- **Agente = proceso que corre solo.** Arranca limpio (sin tu charla), hace su tarea, termina. Puede dispararse por horario.

Empezás con skills. Los agentes vienen después, cuando una tarea ya no necesita que estés ahí.

---

## 10. Rutinas: poner algo a correr solo

Una **rutina** es un skill (o una tarea) que corre en horario, sin que estés. La primera buena rutina es la del chequeador de updates: que mire los lunes si el kit tiene mejoras.

- **En Claude Code / Cowork:** se agenda con la función de tareas programadas del cliente (pedile al asistente "agendá esto para los lunes a las 9").
- **Anotala** en la sección "Rutinas" de tu `CLAUDE.md` raíz, así sabés qué tenés corriendo (y el coach lo detecta).

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

Si no programás, esta sección no te toca.

---

## 13. Liviano para correr (que no te queme el plan)

Tu sistema tiene que andar barato, sobre todo si estás en el plan de $20. La idea de fondo: **el sistema crece a lo ancho, no a lo alto.** Más archivitos chicos, no archivos gordos que se leen siempre. Bien ruteado, tener 50 archivitos sale MÁS barato que 3 enormes, porque cada sesión lee solo la rebanada que toca.

Las 3 capas de costo:
1. **Lo que se lee SIEMPRE** = el `CLAUDE.md` raíz. Tiene que ser un mapa fino (punteros + atajos), no contenido. Nunca lo engordes.
2. **Lo que se lee al entrar a un proyecto** = el `CLAUDE.md` de ese proyecto. Dormido hasta que lo tocás.
3. **Lo que se lee cuando una frase lo dispara** = los skills. Viajan dormidos.

El truco del status: `ESTADO.md` es un archivo chico (nivel + proyectos activos + qué cambió). El asistente lo lee al arrancar y de ahí sabe **qué leer y qué no**, sin escanear todo el árbol.

---

## 14. Topología: proceso oculto, entregables a la vista

Para que tu carpeta se vea limpia, el sistema separa lo tuyo de su maquinaria:
- **A la vista (lo tuyo):** tus carpetas PARA, tu identidad (`sobre-mi`, `como-trabajo`), tu progreso (`ESTADO.md`), y el `CLAUDE.md` raíz (router fino).
- **Oculto (el proceso):** la carpeta `.secondbrain/` con esta doctrina (`reference.md`), los templates y el control de versión. Empieza con punto, así no se ve en Finder. Igual sincroniza por Drive/iCloud.
- **El coach y los skills:** en `.claude/skills/`. El coach es la puerta de entrada.

Vos solo ves lo que hacés. El proceso trabaja de fondo.

---

## 15. Buenas costumbres
- **No creés cosas sin pedido.** El asistente no debería inventar archivos, READMEs ni carpetas porque sí. Que pregunte.
- **Una decisión, una línea en el log.** Te lo agradecés en 3 meses.
- **Revisá de a uno.** Pedile las cosas de a una y mirá antes de seguir. El asistente es rápido, vos sos el que decide.
- **Empezá chico y medí.** No armes el sistema entero hoy. Subí un escalón, usalo una semana, subí el siguiente.

---

## 16. Más allá (track avanzado, opcional)

Si ya venís usando asistentes y la escalera te quedó chica, esto es el mapa de lo que sigue. No viene armado: es a medida tuya. Acá te dejo los conceptos y cuándo te sirven.

- **Orquestadores con estado:** una receta que coordina varias y arrastra contexto entre pasos. Para procesos de varios pasos que se repiten.
- **Agentes que corren solos:** procesos que arrancan por horario o evento, sin vos. Para tareas que ya no te necesitan presente.
- **Multi-agente:** varios asistentes en paralelo, cada uno con su parte, y uno que junta. Para trabajo grande que no entra en una sola cabeza.
- **Evals:** medir si una receta hace bien su trabajo, de forma repetible, en vez de "parece que anduvo". Para cuando algo importa y lo corrés seguido.

Regla de oro acá: no metas esto hasta que la escalera 0 a 5 te quede realmente corta. Es posgrado. La mayoría no lo necesita.

---

## 17. Conectar herramientas (MCP) y subagentes

Dos cosas que, cuando las entendés, te cambian lo que podés hacer. No son del día uno, pero tampoco son posgrado: valen la pena.

**Conectar herramientas (MCP).** Por default tu asistente toca archivos. Con MCP (un estándar para enchufarle herramientas) le das acceso a tus apps: Gmail, tu calendario, una base de datos, lo que sea. Recién ahí puede leer tu inbox, agendar, consultar tus datos. Ejemplo concreto: conectás Gmail por MCP y entonces sí podés tener una rutina que te arma el digest de los mails de la mañana. El MCP es la diferencia entre un asistente que solo ordena tus carpetas y uno que opera tu mundo. Cómo se conecta depende del cliente (Claude Code, Cowork): pedile a tu asistente que te guíe para enchufar el que necesites.

**Subagentes.** Un subagente es otro asistente que lanzás para una parte del laburo, en paralelo, con su propio contexto limpio. Sirve para cosas grandes: revisar 20 archivos a la vez, investigar varios temas en simultáneo, o separar un trabajo en pedazos que corren juntos y después se juntan. La regla: usalo cuando una tarea es grande o tiene partes independientes. Para lo chico y secuencial, no hace falta, suma ruido.

Las dos se combinan con lo de antes: una rutina (sección 10) que conecta una herramienta por MCP y reparte el trabajo en subagentes es, básicamente, un asistente que trabaja solo mientras dormís.

---

## La escalera (tu índice de crecimiento)
- **Nivel 0:** el asistente te conoce (`sobre-mi` + `como-trabajo`).
- **Nivel 1:** tu primer proyecto con su `CLAUDE.md`.
- **Nivel 2:** la tabla de atajos en tu `CLAUDE.md` raíz.
- **Nivel 3:** tu primer skill (el chequeador de updates, sección 8).
- **Nivel 4:** tu primera rutina (poné el chequeador a correr solo, sección 10).
- **Nivel 5:** (si programás) el split código / contexto.
- **Más allá:** track avanzado (sección 16), opt-in.

¿No sabés en qué escalón estás? Pedile **`/second-brain-coach`**.

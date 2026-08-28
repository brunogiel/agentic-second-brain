---
name: construir
kind: orchestrator
description: >
  Orquesta el ciclo de desarrollo entero, de cero a donde elijas. Arranca desde nada (crea el
  worktree y el branch si hacen falta), saca el spec, construye, verifica, hace code review en
  subagentes paralelos, aplica los patches y entrega por la ruta que hayas elegido, devolviendo
  el link del preview. También ingiere un plan multifrente ya escrito y lo ejecuta como grafo de
  dependencias. Usalo con "construí esto y subilo", "hacé todo el ciclo", "llevalo a producción",
  "dejámelo en un preview", "ejecutá este plan", "dejalo listo para el lunes". NO lo uses para un
  fix de una línea que hacés a mano en diez segundos, ni para decidir entre opciones (eso es
  `council`), ni para limpiar texto (eso es `anti-slop`).
---

# construir — el ciclo entero en una invocación

## Rol

Es un orquestador, no un worker: coordina los comandos de git y los skills de verificación y
review, y no tiene lógica propia. Clasifica el trabajo, delega, verifica, escala lo difícil a la
herramienta correcta y deja el log de la corrida. El trabajo real vive en las piezas que cablea.

**Lo que cablea:**

- **Git:** los comandos de `dev/commands/` — `/dev-branch`, `/dev-listo`, `/dev-subir`,
  `/dev-integrar`, `/dev-mergear`, `/dev-limpiar`.
- **Spec:** el skill `spec` del kit, que lee el código, pregunta solo los huecos que el código no
  responde y devuelve requisitos numerados. Si el repo usa otro sistema de specs, ese manda.
- **Verificación:** el verificador de código para lo que corre; el skill `verificar` del kit para
  lo que sale a terceros.
- **Review:** code review en **subagentes paralelos**, siempre.
- **Escalada:** `council` para un juicio complejo, `panel` para una decisión de artefacto.

## Por qué existe

Los comandos de git ya resuelven cada paso por separado. Lo que se pierde es el hand-holding:
pedir el commit, después integrar, después subir, después limpiar, uno por uno, cada vez. Esto
encadena todo en una sola invocación, decide solo lo obvio y consulta lo crítico. **No reemplaza
los comandos: los cablea.**

## Frontera entre el spec y esto

El spec queda **agnóstico de la ruta de entrega**: describe el feature (intención, tareas,
criterios de aceptación, su propia verificación), no los pasos de entrega. Esos viven en el log
de la corrida. El spec responde "¿está bien construido el feature?"; esto responde "¿lo construí,
lo revisé y lo dejé donde pediste?". Si se mezclan, el artefacto del feature se ensucia con
mecánica que cambia según la ruta.

## Parámetros

- `objetivo`: una tarea en criollo, o el path a un plan `.md` ya escrito. Si es un plan, se
  **ingiere**, no se genera de nuevo.
- `ruta`: `prod` | `pr` | `batch` | `staged`. Se **recomienda con postura**, leyendo el tamaño y
  el radio de impacto del cambio.
- `modo`: `presente` (default) | `desatendido`. Cambia qué hacer ante un bloqueante humano.

## Dos formas de entrar

1. **Cambio suelto:** un frente, pipeline lineal. Setup → spec → build → verify → review → envío.
2. **Plan multifrente:** el `.md` se parsea en frentes, dependencias, criterios de aceptación y
   base-ref. Se paraleliza lo que se puede, se espera, se integra.

El cambio suelto es el caso degenerado del plan con un solo frente. Mismo flujo.

## El arranque: UNA sola pregunta

Antes de tocar nada, y en **una sola llamada** a la herramienta de preguntas, no en prosa y nunca
de a una:

| Chip | Opciones |
|---|---|
| **Ruta** | `prod` directo · `pr` PR y preview · `batch` a integración · `staged` integra y frena |
| **Spec** | Con spec · Sin spec (fix chico) |
| **Worktree** | Usar el actual · Crear uno nuevo |

Tres reglas:

- **Lo que ya te dijeron en el prompt no se pregunta.** "Dejalo listo para integración" resuelve
  la ruta; estar ya en un worktree aislado resuelve el worktree. Esos chips se saltan y se declara
  en una línea qué se asumió. Re-preguntar lo que ya te dijeron **es exactamente el hand-holding
  que este skill existe para matar.**
- **Tu recomendación va primera y marcada.** Cambio chico y aislado, pocos archivos, sin
  dependencias sin mergear → **prod directo**. Grande, multi-frente, o día de varias ramas →
  `batch`. **No defaultees a `batch`:** la doctrina del integration branch es para días de varias
  ramas en paralelo, no para un cambio suelto.
- **Si no queda ningún chip sin responder, no preguntes nada:** declarás los supuestos en dos
  líneas y arrancás.

Después de esa llamada, corré hasta el terminal elegido sin volver a interrumpir, salvo blocker
duro.

## Flujo

1. **Arranque** [LATENT]: parseá el objetivo. Si es un plan, armá los frentes, sus dependencias y
   la base-ref. Hacé la pregunta única.
2. **Setup** [DET]: si no estás en un worktree aislado, corré `/dev-branch`. Un worktree por frente.
3. **Spec** [LATENT]: sacá el spec con requisitos numerados. **No pases al build sin ellos:** el
   review del paso 6 los recorre uno por uno. Si ingeriste un plan, este paso ya está hecho.
4. **Build** [FANOUT]: los frentes con archivos disjuntos corren en paralelo como subagentes, cada
   uno commiteando solo lo suyo. Es la regla 1 del integration: un solo dueño por working tree.
5. **Verify** [FANOUT]: por frente, con el verificador que corresponda. Si el plan trae criterios
   de aceptación, usá esos.
6. **Review** [FANOUT]: code review en subagentes paralelos, **recorriendo los requisitos uno por
   uno**, y cada hallazgo nombra cuál falla. **Aplicá los patches.** Si algo pinta riesgoso,
   mandá un subagente dedicado a re-revisar ese punto.
7. **Envío** [DET]: juntá los frentes y entregá según la ruta.
   - `batch` → `/dev-listo` por branch, quedan esperando a `/dev-integrar`.
   - `pr` → `/dev-integrar` → un PR → preview → link.
   - `staged` → igual que `pr` pero **frená ahí**, sin ofrecer el merge.
   - `prod` → `/dev-integrar` (o `/dev-subir` si es un solo frente) → checks verdes →
     `/dev-mergear` → URL de producción. **Guardrail:** solo si el diff es chico, independiente y
     los checks están verdes. Si es grande, bajá a `pr` y avisá.
8. **Park** [LATENT]: juntá lo que quedó bloqueado por falta de algo humano (una cuenta, una key,
   una URL) en un "necesito de vos", con qué falta y qué placeholder dejaste.
9. **Limpieza** [DET]: **se dispara con el merge, no con la ruta.** Apenas un merge a `main`
   aterriza, corré `/dev-limpiar` **acto seguido y sin preguntar** sobre lo obvio: el branch local
   y remoto, y el worktree de lo que acaba de entrar. Lo ambiguo se consulta.

   Está escrito así por un motivo: si lo atás a "la ruta `prod`", no se dispara nunca en el caso
   real, porque esa ruta termina en un handoff y el merge puede pasar varios turnos después.
   Para entonces la corrida ya "terminó" y la limpieza queda huérfana. **El evento es el merge.**

   > ⚠ **Trampa real con worktrees.** Desde un worktree, `gh pr merge --squash --delete-branch`
   > mergea bien pero **falla al final** con `fatal: 'main' is already used by worktree at ...`,
   > porque `gh` intenta pararte en el `main` local que tiene tomado el repo principal. El merge
   > quedó hecho y el branch remoto **no** se borró. No leas ese error como "falló el merge":
   > confirmá el estado del PR y borrá el remoto a mano.

10. **Log** [DET]: escribí el log de la corrida.

## Escalera de autonomía

Decidí solo lo obvio, escalá lo difícil, y **avisá siempre qué invocaste**.

| Situación | Solo | Escala |
|---|---|---|
| Hueco de producto en el spec | lo asumís **solo** en modo desatendido, y queda visible como supuesto | en modo presente lo pregunta el skill `spec` |
| Verificar código | el verificador | juicio muy complejo → `council`, avisando |
| Verificar algo que sale a terceros | `verificar` | idem `council` si se complica |
| Decisión de artefacto | si es obvia | `panel`, avisando |
| Bloqueante humano | `presente`: **frená** y pedí destrabar · `desatendido`: parkealo y seguí | siempre lo listás al final |
| Limpieza post-merge | **disparás solo**, sin preguntar | lo ambiguo, consultás |

**Blockers que te frenan aunque estés desatendido:** la verificación no pasa y no la podés
arreglar, el review marca algo de seguridad, o hay checks en rojo al mergear. Los bloqueantes
*humanos* no te frenan si estás desatendido: se parkean.

## Qué verificar según el tipo

- **Código:** ejercitá el camino feliz más uno o dos bordes, de verdad, no por inspección. Si hay
  spec, sus pasos de verificación ya están escritos: corrélos requisito por requisito.
- **Contenido que sale a terceros:** `verificar`, con fact-check.
- **El conjunto integrado:** type-check, lint y build en verde sobre el preview.

## Output esperado

Un solo handoff al cerrar:

- 🔗 **PR** y 👀 **preview**, o 🚀 **URL de producción** si la ruta fue `prod`.
- 📋 **Qué revisar:** checklist derivado del diff real, por pantalla o flujo. Nunca genérico.
- 🙋 **Necesito de vos:** lo parkeado, con qué falta y qué placeholder quedó.
- 🧠 **Escaladas:** qué invocaste y qué dijo.
- 🧹 **Limpieza:** reportala **hecha**, no la ofrezcas. Si algo quedó sin borrar, decí qué y por qué.
- 🔢 **Menú numerado de próximos pasos** según la ruta. Siempre un menú, nunca un único CTA tipo
  "decime si mergeo". Tras un preview: `[1] Mergear` · `[2] Tengo ajustes` · `[3] Mandar a
  integración`. Tu recomendación va primera.

## Success metrics

- Cero pasos de hand-holding entre "arrancá" y el handoff, salvo blocker duro o bloqueante humano.
- Ningún build arranca sin requisitos numerados.
- Toda escalada queda avisada: nunca una decisión de peso tomada en silencio.
- Nada bloqueado se inventa: se parkea. Cero cuentas falsas, cero datos fabricados.
- La ruta `staged` nunca toca `main`. La ruta `prod` nunca mergea con checks en rojo sin OK.
- El handshake se resuelve en **una sola pregunta**, con la ruta recomendada marcada y leída del
  radio de impacto. Nunca preguntas de a una, nunca un default silencioso.
- Cero chips por cosas que ya te dijeron en el prompt.
- El handoff cierra con el menú numerado.

## Qué NO hace

- No decide entre opciones estratégicas: eso es `council`.
- No limpia texto: eso es `anti-slop`.
- No mergea en ruta `staged`, ni sube un diff grande solo en ruta `prod`: baja a `pr`.
- No corre para un fix trivial de una línea. Ahí es más rápido a mano.

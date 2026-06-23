<!--
  SUPER MD — archivo raíz de tu sistema (Agentic Second Brain).
  Es un ROUTER fino: es lo que se lee SIEMPRE al arrancar, así que se mantiene corto.
  La doctrina completa NO vive acá: la maneja el coach (vive global con él). Esto es solo el router.
  Lo que ve el usuario empieza en la línea de abajo.
-->

# CLAUDE.md — <Tu nombre>

> Esto es lo primero que tu asistente (Claude Code o Cowork) lee al arrancar una sesión.
> Es un mapa, no un manual: te ubica y apunta a dónde está cada cosa.
> ¿No sabés por dónde seguir? Escribí **`/asb-coach`**. Te ubica y te propone el próximo paso. Propone, vos decidís.

---

## Reglas de arranque (las sigue siempre)
1. Leé este archivo (es corto).
2. Leé `ESTADO.md` para ubicarte rápido (dónde estás, qué hay activo). Si el estado ya lo dice, no escanees todo.
3. Si el pedido es de un proyecto, leé SOLO `1. Proyectos/<ese proyecto>/CLAUDE.md`, no todo el árbol.
4. Datos personales o de cómo trabajo: `2. Áreas/yo/sobre-mi.md` y `2. Áreas/yo/como-trabajo.md`.
5. La doctrina (cómo crece el sistema, skills, convenciones) la maneja el coach (vive global con él). Para crecer o entender algo, escribí `/asb-coach`.
6. Tus skills de uso viven en `skills/` (carpeta a la vista) y se disparan por la tabla "Mis skills" de abajo: cuando una frase mía matchea una fila, seguí ese skill. (El motor del kit —coach, etc.— se invoca por nombre, ej. `/asb-coach`.)
7. Si te tiro algo turbio para después ("metelo al inbox", "no lo quiero decidir ahora"), va a `0. Inbox/` (mirá su `INBOX.md`).
8. Si retomo ("¿en qué estaba?"), briefeame leyendo `ESTADO.md` (y el log del proyecto activo). Antes de cerrar, dejá `ESTADO.md` al día —"última vez" + "próximo paso"— para que la próxima sesión arranque sabiendo.

## Quién soy
- **Nombre:** <...>
- **En una línea, qué quiero del asistente:** <...>
- Detalle: `2. Áreas/yo/sobre-mi.md` · cómo trabajo: `2. Áreas/yo/como-trabajo.md`

## Mi sistema (PARA)
Una pregunta para ordenar cualquier cosa: *¿esto qué es?*
- **0. Inbox/** : captura sin decidir. Lo turbio cae acá y se "cocina" después (ver `0. Inbox/INBOX.md`).
- **1. Proyectos/** : tiene objetivo y fecha (se termina).
- **2. Áreas/** : responsabilidad que no termina (salud, finanzas, tu rol).
- **3. Recursos/** : referencia que sirve a varios proyectos.
- **4. Archivo/** : lo terminado o pausado.

Cada proyecto tiene su propio `CLAUDE.md` adentro (contexto + log de decisiones).

## Atajos (frase → dónde ir)
Cuando tengas varios proyectos, esta tabla rutea al asistente apenas decís algo.
| Si digo… | Andá a… |
|---|---|
| *(ejemplo)* "mis gastos del mes" | `1. Proyectos/Gastos/` |
| `<tu frase típica>` | `<tu carpeta>` |

## Mis skills (los ves, los usás)
Los skills que usás viven en `skills/` (carpeta a la vista; los abrís y editás). **Esta tabla es el router:** mi asistente la lee al arrancar y, cuando digo una frase de la izquierda, va y sigue ese skill. Anotá cada uno con su frase gatillo — **un skill sin fila acá no se dispara.**
| Si digo… | Skill |
|---|---|
| *(ejemplo)* "pasalo a mi tono" | `skills/redactar/` |
| `<tu frase>` | `skills/<tu skill>/` |

> Anda igual en Claude Code, Cowork y Codex, porque los tres leen este `CLAUDE.md` (en Codex, vía `AGENTS.md` que apunta acá). Aparte está el motor del kit (el coach y demás): se invoca por nombre (`/asb-coach`) y no vive acá.

## Rutinas (lo que corre solo)
Tareas que se ejecutan en horario, sin que estés. (Vacío hasta que armes la primera; el coach te ayuda.)
| Rutina | Cuándo | Qué hace |
|---|---|---|
| *(ejemplo)* chequear updates del kit | lunes | mira si Agentic Second Brain tiene mejoras |

## Si además programás (opcional)
El código vive en su repo (`~/Code/<proyecto>/`); el contexto se queda acá. En el repo, un `CLAUDE.md` corto apunta de vuelta. Si no programás, ignorá esto. Detalle: pedíselo al coach.

---
> El método (doctrina, plantillas, versión) vive global con el coach (`~/.claude/skills/agentic-second-brain-coach/`), **no en esta carpeta**. Tu carpeta es solo tuya. Para crecer, escribí **`/asb-coach`**.

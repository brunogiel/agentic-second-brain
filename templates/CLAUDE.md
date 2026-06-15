<!--
  SUPER MD — archivo raíz de tu sistema (SecondBrain).
  Es un ROUTER fino: es lo que se lee SIEMPRE al arrancar, así que se mantiene corto.
  La doctrina completa NO vive acá: vive en .secondbrain/reference.md (se lee solo cuando hace falta).
  Lo que ve el usuario empieza en la línea de abajo.
-->

# CLAUDE.md — <Tu nombre>

> Esto es lo primero que tu asistente (Claude Code o Cowork) lee al arrancar una sesión.
> Es un mapa, no un manual: te ubica y apunta a dónde está cada cosa.
> ¿No sabés por dónde seguir? Escribí **`/second-brain-coach`**. Te ubica y te propone el próximo paso. Propone, vos decidís.

---

## Reglas de arranque (las sigue siempre)
1. Leé este archivo (es corto).
2. Leé `ESTADO.md` para ubicarte rápido (dónde estás, qué hay activo). Si el estado ya lo dice, no escanees todo.
3. Si el pedido es de un proyecto, leé SOLO `1. Proyectos/<ese proyecto>/CLAUDE.md`, no todo el árbol.
4. Datos personales o de cómo trabajo: `sobre-mi.md` y `como-trabajo.md`.
5. La doctrina (cómo crece el sistema, skills, convenciones) vive en `.secondbrain/reference.md`. Leela solo cuando la necesites.

## Quién soy
- **Nombre:** <...>
- **En una línea, qué quiero del asistente:** <...>
- Detalle: [sobre-mi.md](sobre-mi.md) · cómo trabajo: [como-trabajo.md](como-trabajo.md)

## Mi sistema (PARA)
Una pregunta para ordenar cualquier cosa: *¿esto qué es?*
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

## Rutinas (lo que corre solo)
Tareas que se ejecutan en horario, sin que estés. (Vacío hasta que armes la primera; el coach te ayuda.)
| Rutina | Cuándo | Qué hace |
|---|---|---|
| *(ejemplo)* chequear updates del kit | lunes | mira si SecondBrain tiene mejoras |

## Si además programás (opcional)
El código vive en su repo (`~/Code/<proyecto>/`); el contexto se queda acá. En el repo, un `CLAUDE.md` corto apunta de vuelta. Si no programás, ignorá esto. Detalle en `.secondbrain/reference.md`.

---
> El proceso del sistema (doctrina, templates, versión) vive en `.secondbrain/` (oculto). No hace falta que lo toques: lo maneja el coach. Para crecer, escribí **`/second-brain-coach`**.

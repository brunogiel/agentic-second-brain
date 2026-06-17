<!--
  ESCALERA.md — el tracker de progreso del usuario, a la vista. Lo MANTIENE el coach:
  tacha lo cumplido, mueve "Nivel actual" y "Próximo paso". Es la versión visible y gamificada
  de la checklist del coach. (El ESTADO.md es otra cosa: el tablero fino que el asistente lee siempre.)
-->

# 🪜 Mi escalera SecondBrain

> Tu progreso. El coach lo mantiene: lo actualiza cuando trabajan juntos y te lo muestra cuando
> le decís **"¿cómo vengo?"** o **"¿qué hacemos hoy?"**. Vos lo mirás para ver qué lograste y qué falta.
> Y al final está **[📦 Todo lo que trae el kit](#-todo-lo-que-trae-el-kit-lo-tenés)**: el catálogo completo (skills + archivos) para chequear, en un solo lugar, qué tenés y qué te falta.

> 🎯 **Truco que sirve siempre:** cuando le pidas algo grande, cerrá con *"preguntame lo que necesites primero"*. En vez de adivinar el prompt, te hace 3-4 preguntas y clava la respuesta. Sirve para llenar tu identidad, definir un proyecto, armar un skill — todo.

**Nivel actual: 0**  ·  Progreso: ░░░░░░░  (0 / 7)
**Próximo paso:** <lo llena el coach — la tarea concreta que sigue>

---

## ☐ Nivel 0 — Te conoce + capturás
*Deja de adivinar quién sos, y nada se te pierde.*
- [ ] Identidad cargada (`sobre-mi` + `como-trabajo`, sin `<...>`)
- [ ] Sabés capturar: lo turbio va al `0. Inbox/` en vez de perderse

## ☐ Nivel 1 — Tu primer proyecto
*Nunca más explicás un proyecto dos veces.*
- [ ] Un proyecto en `1. Proyectos/` con su `CLAUDE.md` (contexto + log de decisiones)

## ☐ Nivel 2 — Atajos
*Decís "mis gastos" y ya sabe dónde mirar.*
- [ ] 3 o más proyectos
- [ ] Tabla de atajos con filas reales en tu `CLAUDE.md`

## ☐ Nivel 3 — Tu primer skill
*Una frase dispara una receta entera.*
- [ ] Abriste el `actualizar` de ejemplo para ver cómo es un skill por dentro
- [ ] Armaste tu primer skill propio (en `skills/` + su fila en la tabla "Mis skills")

## ☐ Nivel 4 — El sistema trabaja para vos
*Corre solo y mira tus herramientas, no solo tus archivos.*
- [ ] Una rutina corriendo, con su log de corrida
- [ ] Conectaste una herramienta (Gmail, calendario, Notion…) y algo la usa — ej: `triage` te arma el brief del día

## ☐ Nivel 5 — Orquestás
*Varios skills laburando juntos en una sola tarea.*
- [ ] Usaste un orquestador de ejemplo (el de PPT: arma una presentación coordinando varios skills) para ver cómo es por dentro
- [ ] Armaste tu propio orquestador multiagente (un skill que reparte el trabajo y junta los resultados)

## ☐ Nivel 6 — Mantenés el sistema
*Un sistema que no se revisa se pudre callado.*
- [ ] Le diste tu primera revisión con `auditar-sistema` (salud del sistema, tipo sábado)
- [ ] Afinaste un skill con `evaluar-skill` (lo medís contra su rúbrica y aplicás una mejora)

---

## 🔧 Si programás (rama opcional — enganchás cuando toca, no cuenta para el nivel)
*Código en su repo, contexto acá, sin mezclar.*
- [ ] Moviste el código a su repo + dejaste un puntero de vuelta
- [ ] (más adelante) usás subagentes en tu propio código para tareas grandes

## 🚀 Más allá (frontera real, opt-in)
Agentes 100% autónomos que actúan sin tu OK, auto-mejora de skills en loop cerrado. Posgrado de verdad: la mayoría no lo necesita. Si llegaste hasta acá, ya volás solo.

> Marca de niveles: tachás un nivel cuando todos sus ítems están ✓. El coach mueve "Nivel actual" y la barra.

---

## 📦 Todo lo que trae el kit (¿lo tenés?)

> El mapa completo de lo que ofrece SecondBrain, en un solo lugar, para que sepas **qué hay** y **qué te falta**.
> Los **archivos base** y el **motor** vienen al instalar (ya los tenés). Los **skills de uso** vienen dormidos en el catálogo del kit y el coach te los va sumando cuando tocan — por eso acá ves cuáles ya activaste (`[x]`) y cuáles te esperan (`[ ]`).
> El coach mantiene estas marcas. ¿Te falta algo que debería estar? Escribí **`actualizar`** (el kit baja lo último). ¿Querés activar un skill antes de tiempo? Decile al coach *"sumame `<nombre>`"*.

### 🗂 Archivos base (vienen al instalar, no se pisan)
- [x] `CLAUDE.md` — el router: lo primero que tu asistente lee al arrancar.
- [x] `ESTADO.md` — el tablero fino (dónde estás, qué hay activo).
- [x] `ESCALERA.md` — este tracker.
- [x] `AGENTS.md` — puntero para que Codex/Cursor encuentren tu `CLAUDE.md`.
- [x] `0. Inbox/INBOX.md` — el protocolo de captura.
- [x] `2. Áreas/yo/sobre-mi.md` — quién sos.
- [x] `2. Áreas/yo/como-trabajo.md` — cómo trabajás.
- [x] `2. Áreas/yo/mi-estilo.md` — tu voz (para escribir como vos).
- [x] `2. Áreas/yo/MEMORIA.md` — datos que no se deducen de los archivos.
- [x] `3. Recursos/arquitectura-skills.md` — la doctrina para armar buenos skills.
- [x] `3. Recursos/anti-slop-writing.md` — las reglas para que tus textos no huelan a IA.
- [ ] `2. Áreas/yo/soul.md` — tu hoja de personaje (se suma cuando aparece, hablando).
- [ ] `2. Áreas/yo/dev-prefs.md` — preferencias de dev (se suma si programás).

### 🔒 Motor (global e invisible, viene siempre)
- [x] `second-brain-coach` — tu guía; lo invocás con `/second-brain-coach` o *"¿qué hago ahora?"*.
- [x] `actualizar` — baja las mejoras del kit; *"¿hay updates?"*, *"¿estoy al día?"*.
- [x] `migrar-de-claude-projects` — trae tus Projects de la app de Claude al sistema; *"migrá mis proyectos de claude"*.

### 👁 Skills de uso (el coach te los suma cuando tocan — tachás al activarlos)
> `[x]` = ya lo tenés en `skills/` con su fila en la tabla "Mis skills" del `CLAUDE.md`. `[ ]` = está disponible en el catálogo, todavía no lo activaste. Entre paréntesis, el nivel donde suele aparecer.
- [ ] `redactar` *(cuando escribís)* — escribe en tu voz: mails, posts, respuestas; *"pasalo a mi tono"*.
- [ ] `anti-slop` *(cuando escribís)* — le saca el olor a IA a un texto; *"limpiá este texto"*, *"sacale el slop"*.
- [ ] `crear-skill` *(N3)* — te guía a armar tu primer skill bien hecho; *"creá un skill"*.
- [ ] `triage` *(N4)* — el brief del día (mail + agenda + tareas por MCP); *"qué tengo hoy"*, *"briefeame"*.
- [ ] `ppt-builder` *(N5)* — orquestador con estado: arma un deck por etapas coordinando varios skills; *"armame el ppt de X"*.
- [ ] `panel` *(N5)* — orquestador multiagente: 2-5 reviewers con lentes distintas sobre lo mismo; *"paneá esto"*, *"ojos frescos"*.
- [ ] `auditar-sistema` *(N6)* — chequeo de salud del sistema (tipo sábado); *"auditá el sistema"*.
- [ ] `evaluar-skill` *(N6)* — mide un skill contra su propia rúbrica y lo afina; *"evaluá el skill X"*.

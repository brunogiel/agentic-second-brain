# Changelog

## 2.6.0
- **Skills de uso movidos a `templates/skills/`** (no son del motor, son lo que se instala en el SB del usuario). En el repo, `.claude/skills/` queda SOLO con el motor (coach + actualizar + migrar); los skills de uso son el catálogo-fuente en `templates/skills/`. `install.sh` los fetchea de ahí.
- **Nuevo skill `evaluar-skill`** (versión genérica del eval-skill de Bruno): mide un skill contra su propio `SKILL.md` (la rúbrica) en una corrida real y propone mejoras sin aplicarlas. Cierra el loop de calidad. El coach lo ofrece cuando ya tenés varios skills.
- **Skills de uso enriquecidos** para cumplir su propia arquitectura (auditoría de subagente): sección "Qué lee y escribe" en los que la omitían; `anti-slop` suma output con tabla de cambios + modo "Limpio ✅" + 5ª regla (meta-señalización) + troubleshooting + señales binarias; `auditar-sistema` suma reglas duras + output con formato fijo ("✅ Sin cambios necesarios" obligatoria + cierre de aprobación); `crear-skill` suma checklist de los 5 criterios mínimos; `redactar` suma loop de perfil-que-aprende; `triage` suma modo degradado.
- **soul.md vs proyecto — resuelto:** el bloque del proyecto pasa de "Cómo trabajar acá" a **"Rol acá"** (solo lo que cambia del soul). `soul.md` suma **"Qué manda cuando hay conflicto"** (precedencia explícita) + andamiaje de voz + "cómo evoluciona".
- **Templates menos pelados:** `mi-estilo.md` suma apertura/cierre/firma, tabla de adaptación por canal y "prohibido duro".
- **Ejemplos de referencia** (`templates/ejemplos.md` → `.secondbrain/ejemplos.md`): layouts por perfil (freelancer / pyme / PM / básico) que el coach usa al arrancar con alguien nuevo.
- **Coach goal-driven:** nueva sección "Tu objetivo: hacerlo avanzar" — el coach es proactivo, diagnostica, empuja al próximo escalón y no deja al usuario sin próximo paso.

## 2.5.1
- Fix de coherencia: el coach (`second-brain-coach`, ladder N3) todavía decía que el primer skill propio va en `.claude/skills/` — resto del modelo viejo que se contradecía con el resto del kit. Ahora dice `skills/` + su fila en la tabla "Mis skills", alineado con la doctrina de routing por tabla (v2.5.0).

## 2.5.0
- **Portabilidad real (Code + Cowork + Codex):** los skills de uso pasan a una **`skills/` a secas y visible** (sin `.claude/skills/`, sin symlink) y se disparan por la **tabla "Mis skills" del `CLAUDE.md`** (frase → skill). Como los tres harnesses leen el `CLAUDE.md` (Codex vía `AGENTS.md`), funcionan igual en todos. Antes el kit dependía de `.claude/skills/` (descubrimiento nativo de Claude), que **en Codex no dispara**. El patrón está tomado del SB real de Bruno, que ya corría así (skills pelada + tabla del router).
- **`install.sh`:** crea `skills/` a secas (saca el symlink y el `.claude/skills/` del SB del usuario). El motor (3) sigue global e invisible; el catálogo (7 skills de uso) sigue en `.secondbrain/skills-disponibles/`.
- **Coach y `crear-skill`:** al sumar un skill, copian a `skills/<x>/` y **anotan la fila en la tabla "Mis skills"** — ese paso es ahora lo que lo hace disparar (no es cosmético; sin la fila, el skill no se activa).
- **`AGENTS.md`:** ahora le explica a Codex cómo usar la tabla de skills (antes solo apuntaba al `CLAUDE.md`).
- **Doctrina y READMEs** reescritos: el disparo es por la tabla del `CLAUDE.md`, no por carpeta oculta; el cerebro **y los skills de uso** son portables, y solo el comando `/second-brain-coach` queda atado a Claude.

## 2.4.0
- **Topología reescrita a 3 baldes** (matchea la regla: lo que el usuario usa = visible; el motor de armado = oculto):
  - **👁 Visible en el SB:** el contexto (PARA, identidad, `CLAUDE.md`, `ESTADO`, `Inbox`) + **`skills/` con los skills que el usuario USA**. No se instalan todos de una: el coach los va sumando a medida que el usuario avanza.
  - **🔒 Oculto en el SB (`.secondbrain/`):** doctrina (`reference.md`) + `plantilla-proyecto.md` + el **catálogo** `skills-disponibles/` (las versiones-fuente de los skills de uso) + versión.
  - **🔒 Global e invisible (`~/.claude/skills/`): SOLO el motor de armado** — coach + `actualizar` + `migrar`. Se llaman por nombre; no viven en la carpeta ni aparecen en `skills/`.
- **`install.sh`:** instala solo el motor (3) global y deja los 7 skills de uso en el catálogo oculto; crea `skills/` vacía. (Antes metía los 10 skills globales y dejaba `skills/` vacío.)
- **Coach:** nuevo mecanismo "Sumar un skill de uso (desde el catálogo)": copia `.secondbrain/skills-disponibles/<x>/` → `skills/<x>/` con OK, y lo anota en "Mis skills". Mapa de cuándo ofrecer cada uno (sesión temprano; redactar/anti-slop al escribir; crear-skill en N3; auditar/triage en N4).
- **Doctrina y READMEs** (`reference.md` §14, `arquitectura-skills.md`, ambos README) reescritos al modelo de 3 baldes, aclarando que `skills/` (visible) está respaldada por `.claude/skills/` (plomería de disparo).

## 2.3.0
- **`triage-mails` → `triage` (brief del día multi-fuente):** el skill deja de ser solo del inbox. Ahora arma un **brief** arriba (cómo viene el día en 2-4 líneas) y debajo los **accionables generales**, cruzando tus fuentes: mail (el piso), **calendario** (reporte de citas) y tu **chat/tareas** de trabajo (Slack, Jira, Linear, Trello, Notion comments, lo que uses). Es agnóstico al stack: trabaja con los MCP que tengas conectados y **ofrece** sumar calendario y chat/tareas la primera vez. Con el mail solo ya arranca; sigue siendo leer-y-proponer (no manda, no archiva, no cierra tickets sin OK). Renombrado en `install.sh`, ambos README y el coach (N4).

## 2.2.0
- **Skills de sesión (el play de retención):** `abrir-sesion` (lee `ESTADO.md` + el log reciente del proyecto y te briefea al retomar) y `cerrar-sesion` (al terminar deja el `ESTADO.md`, el log de decisiones y el **próximo paso** al día). Capturar al cerrar + retomar al abrir es lo que hace que la 2da sesión se sienta distinta. Inspirado en el "automatizá la disciplina" del deck de Muslera y en los handoff prompts de BMAD. Ruteados desde las reglas de arranque del `CLAUDE.md` raíz.
- **Persona por proyecto:** nueva plantilla `templates/proyecto-CLAUDE.md` (Qué es / **Cómo trabajar acá** / Estado / Decisiones / Próximo paso / Links). El `CLAUDE.md` de cada proyecto puede definir el carácter del asistente para ESE proyecto ("sé escéptico" / "sé breve"). El coach lo ofrece en N1; `install.sh` deja la plantilla en `.secondbrain/`.
- **Track avanzado (§16) ampliado:** multi-persona sobre una decisión (4 lentes → síntesis, estilo `council`) y el **loop de auto-mejora de skills** (patrón autoresearch de Karpathy: proponer cambio → correr `eval` como rúbrica → aplicar/descartar con tu OK).
- **Eval-first en `crear-skill`:** ofrece anotar 2-3 casos de prueba antes de escribir el skill (práctica #1 de la doctrina oficial de Anthropic).
- **Posicionamiento vs BMAD:** README y `reference.md` §12 aclaran que para desarrollo de software serio (epics/PRDs/equipo) se combina con un método de dev como BMAD-METHOD — no compiten, conviven en el split código/contexto (N5).

## 2.1.0
- **Fix de fondo (topología de skills):** los skills del usuario pasan a `.claude/skills/` (que es el único lugar donde el harness los descubre y los dispara por frontmatter). Antes vivían en un `skills/` pelado que Claude Code no escanea, así que **nunca se disparaban solos**. Queda un atajo visible `skills/` → `.claude/skills/` para verlos y editarlos, y la tabla "Mis skills" del `CLAUDE.md` como mapa humano. Se aclara en toda la doctrina la diferencia entre **disparo por frontmatter** y **ruteo por tabla**.
- **El motor ahora vive en `.claude/skills/` del repo:** abrir la carpeta (zip/clone) en Cowork deja el coach disponible al toque, sin terminal. El `install.sh` además lo deja global en `~/.claude/skills/` para Claude Code. Arregla el chicken-and-egg del camino sin terminal.
- **`actualizar` ahora viene hecho** como skill del kit (con `check-update.sh`): el auto-update pasa de promesa a algo que funciona. El Nivel 3 se reformula: leés el `actualizar` de ejemplo y después armás *tu* primer skill.
- **Captura/inbox:** nueva carpeta `0. Inbox/` con su `INBOX.md` (protocolo de capturar sin decidir y "cocinar" después). Se enseña temprano (Nivel 0). Tapaba el hueco más grande vs un PKM real.
- **`AGENTS.md`** incluido (puntero a `CLAUDE.md`): instrumenta la portabilidad multi-harness que el README prometía. Se matiza el claim "agnóstico": el *cerebro* (texto) es portable; el *motor* (skills/comandos) es de Claude.
- **`install.sh` robusto:** descarga atómica a tempdir (si algo falla, no deja el sistema a medias), precheck de red, y deja de pisar `reference.md` y lo tuyo. Resumen final con próximo paso.
- **Nivel 4 con sustancia:** se enseña el **log de corrida** ("una rutina sin log es ciega").
- **README:** la propuesta de valor sube al primer renglón (el ángulo "cerebro para tu asistente") y la escalera suma columna "qué ganás".
- **Alineación con mejores prácticas externas** (Anthropic, Karpathy, kepano, Simon Willison, deck Bluelabel de Muslera): doctrina de skills en 3ª persona + nombre en gerundio + divulgación progresiva (`arquitectura-skills.md`); `reference.md` nombra el *context rot* y el `CLAUDE.md` como "RAM curada" (§13), el learning-loop "el modelo es stateless, los archivos no" (§4), MCP=plomería/skills=cerebro + nota del combo riesgoso (§17); gancho de la "2da sesión" en README y coach.

## 2.0.6
- `soul.md` pasa a ser una **hoja de personaje** (formato SOUL.md): identidad, verdades de base, cómo veo las cosas, voz y tono, límites. Define quién es el asistente cuando habla por vos, no solo tus valores pasivos. El coach ahora ofrece guardar también opiniones marcadas, voz y líneas que no se cruzan.

## 2.0.5
- Aclarado dónde viven los skills: los **generales** en `skills/` (raíz del SB), los **de un proyecto** en `1. Proyectos/<proyecto>/skills/`. No van en `3. Recursos/` (eso es referencia). Doctrina en `arquitectura-skills.md`.

## 2.0.4
- Los skills que arma el usuario ahora son **visibles**: viven en `skills/` de su carpeta (no más en el oculto `.claude/skills/`) y se rutean desde el `CLAUDE.md` raíz (sección "Mis skills"). El motor del kit (coach y demás) sigue global y oculto, que es la máquina.

## 2.0.3
- La doctrina de skills sale a la luz como **Recurso visible**: `3. Recursos/arquitectura-skills.md` (regla de 3, DET/LAT, anatomía, errores típicos, checklist). El `reference.md` oculto la resume y apunta ahí; el `crear-skill` la usa.

## 2.0.2
- Los skills del kit (el motor que usa el coach) van globales en `~/.claude/skills/`; los skills que el usuario arma quedan en `.claude/skills/` de su SB y viajan con él.
- README: el sistema es agnóstico al modelo y al harness (Claude Code, Cowork, Codex, Cursor, lo que venga). El cerebro son archivos de texto, portables.

## 2.0.1
- Footprint mínimo: la raíz queda con `CLAUDE.md` + `ESTADO.md`; los básicos de identidad (`sobre-mi`, `como-trabajo`, `mi-estilo`, `MEMORIA`) viven en PARA, en `2. Áreas/yo/`. `soul` y `dev-prefs` los suma el coach a medida que subís.

## 2.0.0
- Coach renombrado a `second-brain-coach`: es el punto de entrada único del sistema.
- Apertura en 3 modos (aprender / hacelo por mí / hacelo yo) + perilla de experiencia (en bolas / avanzado).
- El coach enseña el concepto de cada escalón, no solo te ubica.
- Onboarding: pregunta si ya tenés una carpeta de trabajo; si sí, la analiza y la adopta sin pisar nada.
- Escalera ampliada: se suma Nivel 4 (rutinas); el split código pasa a Nivel 5.
- Auto-update: tu primer skill es el chequeador de updates del kit (de paso aprendés qué es un script).
- Liviano para correr: el `CLAUDE.md` raíz pasa a router fino + `ESTADO.md` como tablero.
- Topología: el proceso vive oculto en `.secondbrain/`; a la vista quedan solo tus entregables.
- Templates nuevos: `soul.md` (se llena hablando) + `dev-prefs.md`.
- Skills-joya dormidos: `crear-skill`, `auditar-sistema`, `triage-mails`, `migrar-de-claude-projects`.
- Sirve al principiante y al avanzado (track "más allá" opt-in); pensado para Cowork, migra a Code.

## 1.0.0
- Versión inicial: PARA, super MD, `reference.md`, skills (coach / redactar / anti-slop), templates, `install.sh`.

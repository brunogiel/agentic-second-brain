# Agentic Second Brain

Claude arranca cada sesión sin saber quién sos, cómo trabajás ni dónde está lo importante. Agentic Second Brain es una carpeta de texto que lee al inicio, así deja de improvisar.

No es un segundo cerebro para que lo leas *vos*. Es un sistema operativo personal desde el que trabaja tu asistente: tu contexto, proyectos, skills y rutinas en archivos de texto, para que el agente sepa qué cargar y cuándo.

Instalás un coach y ese coach arma el sistema con vos, de a un escalón. Sirve en **Cowork** y **Claude Code**. También lo puede usar **Codex** o cualquier agente que lea `AGENTS.md`.

---

## Por qué funciona

El modelo genera texto. El cliente (Cowork, Claude Code, Codex) le da manos para leer y escribir archivos. Tu carpeta le da contexto: quién sos, qué proyectos tenés, qué reglas seguir y dónde buscar.

El cambio se nota en la segunda sesión: ya no tenés que volver a explicar lo mismo.

## El toolkit (listo el día cero)

Estos no los armás vos. El plugin trae un set de slash commands que funcionan apenas lo instalás, antes de configurar nada:

| Comando | Qué hace |
|---|---|
| `/asb` | El conserje: te lista las herramientas y te manda al coach |
| `/asb-slop` | Saca el olor a IA de un texto en una pasada |
| `/asb-write` | Redacta o reescribe en tu voz |
| `/asb-prompt` | Convierte un pedido crudo en un prompt listo para pegar en cualquier chat de IA |
| `/asb-panel` | 2 a 5 revisores con miradas distintas sobre algo antes de mandarlo |
| `/asb-council` | Un concilio de 5 asesores para una decisión con peso |
| `/asb-deck` | Arma una presentación por etapas, de bruto a final |
| `/asb-audit` | Chequeo de salud de tu segundo cerebro |
| `/asb-doc` | Cierra la sesión: rutea todo lo durable a su lugar |
| `/asb-simple` | ¿Perdiste el hilo? Estado en simple: dónde estamos, qué hacés vos, qué sigo yo |

Esta es la capa horizontal: herramientas genéricas que sirven igual para todos. El coach (`/asb-coach`) arma la capa vertical: tus proyectos, tu identidad y tus propias skills. Usar estas herramientas es además la forma más rápida de entender qué es un skill antes de armar el tuyo.

Funcionan como comandos en Cowork y en Claude Code, sin configurar nada. En Cowork además las podés disparar describiendo lo que querés.

## Instalación

### Cowork (sin terminal)

1. En **Complementos personales** tocá el **+**, elegí **Crear plugin -> Agregar marketplace** y pegá: `brunogiel/agentic-second-brain`
   (atajo si podés escribir: `/plugin marketplace add brunogiel/agentic-second-brain`).
2. Instalá el plugin **agentic-second-brain**
   (o escribí `/plugin install agentic-second-brain@agentic-second-brain`).
3. Abrí o creá una carpeta donde quieras que viva tu brain (Drive, iCloud o Dropbox).
4. Usá uno de:
   - `/asb` — el conserje: tu toolkit y dónde vas parado (empezá por acá)
   - `/asb-coach` — el coach: arma tu sistema, te ubica y propone el próximo paso

El coach pregunta antes de crear archivos. No arma carpetas por atrás. En Cowork el plugin se actualiza solo.

### Claude Code

```bash
curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/install.sh | bash
```

Después abrí la carpeta donde querés trabajar y escribí:

```text
/asb        # el conserje: tu toolkit + dónde vas parado (empezá por acá)
/asb-coach  # el coach: arma tu sistema, te ubica + propone el próximo paso
```

El script instala el método y los comandos de forma global. No toca tu carpeta del brain.

## Qué se instala

Hay dos partes:

- **El método:** vive fuera de tu carpeta. En Cowork es un plugin. En Claude Code vive en `~/.claude/skills/`. Ahí están el coach, sus plantillas y el catálogo del kit.
- **Tu brain:** vive en tu carpeta sincronizada. Ahí quedan tus archivos, tus proyectos, tu identidad y los skills que decidas usar.

La carpeta final del usuario se ve así:

```text
CLAUDE.md
ESTADO.md
ESCALERA.md
AGENTS.md
0. Inbox/
1. Proyectos/
2. Áreas/yo/
3. Recursos/
4. Archivo/
skills/
```

El directorio `kit/` pertenece al método, no a tu brain final. Dentro del repo se divide así:

- `kit/brain/`: plantillas para crear la carpeta base.
- `kit/skills/`: catálogo de skills que el coach puede activar de a uno.

## Si ya tenés un sistema

No tenés que migrar. El coach mira tu estructura y la respeta.

La regla es simple: tiene que existir un router claro (`CLAUDE.md` o `AGENTS.md`) que diga dónde vive cada cosa. Si tu estructura ya funciona, el coach no la renombra ni te fuerza PARA. Solo propone mejoras puntuales: inbox, atajos, logs de decisión, skills o estado de sesión.

## Qué toca y cómo deshacerlo

- El instalador de Claude Code solo instala el método global.
- El coach crea archivos en tu brain solo si decís que sí.
- Si un archivo ya existe, no lo pisa.
- Las actualizaciones refrescan el método, no tu carpeta.
- Desinstalar borra el motor, no tus datos.

En Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/uninstall.sh | SB_YES=1 bash
```

En Cowork, desinstalá el plugin desde la UI o con:

```text
/plugin uninstall agentic-second-brain
```

## La escalera

No armás todo el primer día. Subís de a un paso.

| Nivel | Qué armás | Para qué sirve |
|---|---|---|
| **0** | Identidad + inbox | El asistente sabe quién sos y no se pierden ideas sueltas |
| **1** | Primer proyecto con `CLAUDE.md` | No volvés a explicar contexto ni decisiones |
| **2** | Atajos frase -> carpeta | Decís "mis gastos" y sabe dónde mirar |
| **3** | Primer skill propio | Una frase dispara una receta que repetís |
| **4** | Rutina + herramienta conectada | El sistema puede leer mail, calendario o tareas |
| **5** | Orquestador | Varios skills trabajan juntos |
| **6** | Auditoría y mejora | Revisás que el sistema no se degrade |
| **Si programás** | Código separado del contexto | El repo tiene código; el brain guarda decisiones |

El coach lee `ESTADO.md` y `ESCALERA.md`, te dice dónde estás y propone un solo próximo paso.

## Portabilidad

Tu brain son archivos de texto. Podés abrir la misma carpeta en Cowork, Claude Code, Codex o Cursor.

Los skills de uso viven en `skills/` y se activan desde la tabla **Mis skills** de `CLAUDE.md`. Codex y Cursor llegan a esa tabla por `AGENTS.md`.

Lo único específico de Claude es el motor de armado: `/asb-coach` y, en Claude Code, `actualizar`. Si usás otro agente, `AGENTS.md` trae un fallback para operar el sistema a mano.

## Qué trae

- `CLAUDE.md`: router principal.
- `ESTADO.md`: tablero corto para retomar rápido.
- `ESCALERA.md`: tracker de progreso y catálogo del kit.
- `AGENTS.md`: puntero para agentes no-Claude.
- `0. Inbox/`: captura sin decidir.
- `2. Áreas/yo/sobre-mi.md`: quién sos.
- `2. Áreas/yo/como-trabajo.md`: cómo querés que trabaje el asistente.
- `2. Áreas/yo/mi-estilo.md`: tu voz para redactar.
- `2. Áreas/yo/MEMORIA.md`: hechos que valen para todo.
- `3. Recursos/arquitectura-skills.md`: cómo armar skills.
- `3. Recursos/anti-slop-writing.md`: reglas para limpiar textos con olor a IA.
- `skills/`: skills activados por vos.

Skills disponibles en el catálogo:

- `redactar`: escribe en tu voz.
- `anti-slop`: limpia textos.
- `crear-skill`: arma un skill nuevo.
- `evaluar-skill`: revisa un skill contra su propia rúbrica.
- `auditar-sistema`: chequea la salud del brain.
- `triage`: arma un brief del día con mail, agenda y tareas conectadas.
- `ppt-builder`: coordina una pieza en etapas.
- `panel`: trae varias miradas sobre un texto, propuesta o documento.
- `council`: un concilio de asesores para una decisión con peso.
- `prompt-optimizer`: convierte un pedido crudo en un prompt listo para pegar.
- `documenta`: rutea lo durable de una sesión a su lugar canónico.
- `simple`: un estado corto y en lenguaje simple de la conversación actual.

La mayoría de las skills del catálogo mapean a un comando `/asb-*` (lo ves en `ESCALERA.md`). Algunas (`crear-skill`, `triage`, `evaluar-skill`) no tienen comando suelto: el coach las activa cuando llegás a su nivel.

## Filosofía

- Propone, vos decidís.
- Un paso por vez.
- Archivos chicos, leídos cuando hacen falta.
- Los skills duermen hasta que una frase los activa.
- Tu carpeta queda limpia: solo lo tuyo.

## Autor

Hecho por [Bruno Gielczynsky](https://www.linkedin.com/in/brunogiel/). Parte de una familia de métodos de AI instalables junto con [Empat.ia](https://github.com/brunogiel/Empat.ia).

## Licencia

MIT. Usalo, forkealo, hacelo tuyo.

# Agentic Second Brain

Claude arranca cada sesión sin saber quién sos, cómo trabajás ni dónde está lo importante. Agentic Second Brain lo corta: una carpeta de texto plano que lee al inicio, así deja de improvisar.

A diferencia de las notas que guardás para vos, esta carpeta es compartida: vos y tu asistente la leen y editan, pero el que trabaja desde ella es el agente, cargando lo que cada tarea necesita para actuar.

Instalás un coach y arma el resto con vos, de a un escalón. Sirve en **Cowork** y **Claude Code**; **Codex** y otros agentes usan la misma carpeta vía `AGENTS.md`.

> English version: [README.en.md](README.en.md).

---

## La diferencia se nota en la segunda sesión

La sentís la segunda vez que abrís Claude: ya no volvés a explicar el mismo contexto.

```text
Sesión 1, sin brain:
  Vos: soy diseñador freelance, mi stack es X, estoy con el rebrand de Acme,
       el tono va relajado... (cada sesión, de cero)

Sesión 2, con el brain:
  Vos:    redactá el mail de novedades de Acme
  Claude: (ya sabe quién sos, el proyecto, tu tono) Acá va un borrador...
```

Ese salto es todo el punto.

## El toolkit, listo el día uno

El plugin trae slash commands que funcionan apenas lo instalás, sin configurar nada:

| Comando | Qué hace |
|---|---|
| `/asb` | El conserje: te muestra las herramientas y dónde vas parado |
| `/asb-coach` | Arma tu sistema personal, de a un escalón (el motor del método) |
| `/asb-slop` | Saca el olor a IA de un texto en una pasada |
| `/asb-write` | Redacta o reescribe en tu voz |
| `/asb-prompt` | Convierte un pedido crudo en un prompt listo para pegar en cualquier chat de IA |
| `/asb-panel` | 2 a 5 revisores con miradas distintas sobre algo antes de mandarlo |
| `/asb-council` | Un concilio de 5 asesores para una decisión con peso |
| `/asb-deck` | Arma una presentación por etapas, de bruto a final |
| `/asb-audit` | Chequeo de salud de tu segundo cerebro |
| `/asb-doc` | Cierra la sesión: rutea todo lo durable a su lugar |
| `/asb-simple` | ¿Perdiste el hilo? Estado en simple: dónde estamos, qué hacés vos, qué sigo yo |

Las del toolkit son de fábrica y sirven igual para todos; `/asb-coach` arma la parte que es tuya (tus proyectos, tu identidad, tus propias skills). Un *skill* es una receta guardada que dispara una frase: usar estas es la forma más rápida de ver qué es uno antes de armar el tuyo.

Corren como slash commands en Cowork y en Claude Code, sin configurar nada. En Cowork además las podés disparar describiendo lo que querés.

## Instalación

### Cowork (sin terminal)

1. Escribí `/setup-cowork install agentic-second-brain@agentic-second-brain` (el nombre se repite porque es `plugin@marketplace`).
2. Abrí o creá la carpeta donde quieras que viva tu brain. Mejor una sincronizada: Drive, iCloud o Dropbox.
3. Escribí `/asb` para arrancar. Pregunta antes de crear nada, nunca arma carpetas por atrás, y en Cowork el plugin se actualiza solo.

### Claude Code

```bash
curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/install.sh | bash
```

Instala el método y los comandos de forma global y no toca tu carpeta del brain. Después abrí la carpeta donde querés trabajar y escribí `/asb` para arrancar.

## Por qué funciona

El modelo genera texto. El cliente (Cowork, Claude Code, Codex) le da manos para leer y escribir archivos. Tu carpeta le da el contexto. El beneficio: tu ventana de contexto queda barata y despejada, porque en vez de cargar todo, el agente trae el archivo o dos que la tarea necesita.

Eso funciona por el layout. Es PARA (proyectos, áreas, recursos, archivo) más un inbox, con un router chico (`CLAUDE.md`) arriba que mapea dónde vive cada cosa. Los archivos son chicos y de un solo tema, así el router apunta y el agente trae, y vos podés abrir o editar cualquier pieza a mano sin romper nada.

Dos partes quedan separadas. **El método** vive fuera de tu carpeta (un plugin en Cowork, `~/.claude/skills/` en Claude Code) y trae el coach, las plantillas y el catálogo del kit. **Tu brain** es tu carpeta sincronizada, y guarda solo lo tuyo. Termina viéndose así (nombres base, renombrá a gusto):

```text
CLAUDE.md        # el router que tu asistente lee primero
ESTADO.md        # tablero corto, para retomar rápido
ESCALERA.md      # tu progreso + el catálogo del kit
AGENTS.md        # puntero para agentes no-Claude
0. Inbox/        # captura sin decidir
1. Proyectos/    # proyectos, una carpeta cada uno
2. Áreas/yo/     # quién sos, cómo trabajás, tu voz
3. Recursos/     # referencias reusables
4. Archivo/      # terminado o dormido
skills/          # los skills que activaste
```

## Si ya tenés un sistema

No tenés que migrar. El coach mira tu estructura y la respeta.

La regla es simple: tiene que existir un router claro (`CLAUDE.md` o `AGENTS.md`) que diga dónde vive cada cosa. Si tu estructura ya funciona, el coach no la renombra ni te fuerza PARA. Solo propone mejoras puntuales: inbox, atajos, logs de decisión, skills o estado de sesión.

## Qué toca y cómo deshacerlo

- El instalador de Claude Code solo instala el método global.
- El coach crea archivos en tu brain solo si decís que sí.
- Si un archivo ya existe, no lo pisa.
- Las actualizaciones refrescan el método, no tu carpeta.
- Desinstalar borra el motor, no tus datos.

Para desinstalar en Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/uninstall.sh | SB_YES=1 bash
```

En Cowork, desinstalá el plugin desde la UI o escribí `/plugin uninstall agentic-second-brain`.

## La escalera

No armás todo el primer día. Subís de a un paso.

| Nivel | Qué armás | Para qué sirve |
|---|---|---|
| **0** | Identidad + inbox | El asistente sabe quién sos y no se pierden ideas sueltas |
| **1** | Primer proyecto con `CLAUDE.md` | No volvés a explicar contexto ni decisiones |
| **2** | Atajos frase -> carpeta | Decís "mis gastos" y sabe dónde mirar |
| **3** | Primer skill propio | Una frase dispara una receta que repetís |
| **4** | Rutina + herramienta conectada | El sistema puede leer mail, calendario o tareas |
| **5** | Orquestador | Varios skills trabajan juntos en una tarea |
| **6** | Auditoría y mejora | Revisás que el sistema no se degrade |
| **Si programás** | Código separado del contexto | El repo tiene código; el brain guarda decisiones |

El coach lee `ESTADO.md` y `ESCALERA.md`, te dice dónde estás y propone un solo próximo paso.

## Portabilidad

Tu brain son archivos de texto. Podés abrir la misma carpeta en Cowork, Claude Code, Codex o Cursor. Los skills de uso viven en `skills/` y se disparan desde la tabla **Mis skills** de `CLAUDE.md`, que Codex y Cursor alcanzan por `AGENTS.md`. Lo único específico de Claude es el motor de armado (`/asb-coach`, y en Claude Code el updater `actualizar`); para otros agentes, `AGENTS.md` trae un fallback.

## Skills

La mayoría del kit es el toolkit de arriba. Sumá `/asb-triage` (tu brief del día) cuando conectes una fuente por MCP: mail, calendario o tareas. Dos skills más no tienen comando, y el coach las suma a medida que subís: `crear-skill` (armá el tuyo) y `evaluar-skill` (medí un skill contra su rúbrica).

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

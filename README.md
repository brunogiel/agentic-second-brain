# Agentic Second Brain

Claude starts every session without knowing who you are, how you work, or where the important stuff lives. Agentic Second Brain is a plain-text folder it reads at startup, so it stops guessing.

It is not a second brain for *you* to read. It is a personal operating system your assistant works from: your context, projects, skills, and routines as plain files, so the agent knows what to load and when.

You install one coach. The coach helps you build the rest one step at a time. It works with **Cowork** and **Claude Code**. **Codex** and other agents can use the same folder through `AGENTS.md`.

> Method content is in Spanish. Spanish version: [README.es.md](README.es.md).

---

## Why it works

The model writes text. The client (Cowork, Claude Code, Codex) gives it hands to read and edit files. Your folder gives it context: who you are, what projects exist, what rules to follow, and where to look.

You feel the difference in the second session: you do not have to explain the same context again.

## The toolkit (ready on day zero)

You do not have to build these. The plugin ships a set of slash commands that work the moment you install it, before you set up anything:

| Command | What it does |
|---|---|
| `/asb` | Front desk: lists your tools and points you to the coach |
| `/asb-slop` | Strips the AI smell from a text in one pass |
| `/asb-write` | Writes or rewrites in your voice |
| `/asb-prompt` | Turns a rough ask into a paste-ready prompt for any AI chat |
| `/asb-panel` | 2 to 5 reviewers, different lenses, on something before you send it |
| `/asb-council` | A council of 5 advisors for a decision with real stakes |
| `/asb-deck` | Builds a presentation in stages, rough to final |
| `/asb-audit` | Health check of your second brain |
| `/asb-doc` | Closes a session: routes everything durable to its place |
| `/asb-simple` | Lost the thread? Plain-language recap: where we are, your move, mine |

This is the horizontal layer: generic power tools that work the same for everyone. The coach (`/asb-coach`) builds the vertical layer: your projects, identity, and your own skills. Using these tools is also the fastest way to learn what a skill is before you build your own.

These work as slash commands in both Cowork and Claude Code, with no setup. In Cowork you can also trigger them just by describing what you want.

## Install

### Cowork (no terminal)

1. In the **Customize** panel, under **Personal plugins**, click **+** and choose **Create plugin -> Add marketplace**. Paste: `brunogiel/agentic-second-brain`
   (shortcut if you can type: `/plugin marketplace add brunogiel/agentic-second-brain`).
2. Install the **agentic-second-brain** plugin
   (or type `/plugin install agentic-second-brain@agentic-second-brain`).
3. Open or create the folder where your brain should live. A synced folder is best: Drive, iCloud, or Dropbox.
4. Use one of:
   - `/asb` — the front desk: your toolkit and where you stand (start here)
   - `/asb-coach` — the coach: sets up your system, locates you, proposes the next step

The coach asks before creating files. It does not build folders behind your back. In Cowork, the plugin updates itself.

### Claude Code

```bash
curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/install.sh | bash
```

Then open the folder where you want to work and type:

```text
/asb        # front desk: your toolkit + where you stand (start here)
/asb-coach  # the coach: sets up your system, locates you, proposes next step
```

The script installs the method and commands globally. It does not touch your brain folder.

## What gets installed

There are two parts:

- **The method:** lives outside your folder. In Cowork, it is a plugin. In Claude Code, it lives in `~/.claude/skills/`. This is where the coach, templates, and kit catalog live.
- **Your brain:** lives in your synced folder. This is where your files, projects, identity, and adopted skills live.

The user's final folder looks like this:

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

The `kit/` directory belongs to the method, not to the final brain. In this repo it is split like this:

- `kit/brain/`: templates for the base brain folder.
- `kit/skills/`: catalog of skills the coach can activate one at a time.

## Already have a system?

You do not have to migrate. The coach reads your structure and keeps it.

The rule is simple: there must be a clear router (`CLAUDE.md` or `AGENTS.md`) that says where things live. If your structure already works, the coach does not rename it or force PARA. It only proposes small improvements: inbox, shortcuts, decision logs, skills, or session state.

## What it touches

- The Claude Code installer only installs the global method.
- The coach creates files in your brain only after you approve.
- Existing files are not overwritten.
- Updates refresh the method, not your folder.
- Uninstall removes the engine, not your data.

In Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/uninstall.sh | SB_YES=1 bash
```

In Cowork, uninstall the plugin from the UI or type:

```text
/plugin uninstall agentic-second-brain
```

## The ladder

You do not build everything on day one. You climb one step at a time.

| Level | What you build | What it gives you |
|---|---|---|
| **0** | Identity + inbox | The assistant knows who you are and loose ideas are not lost |
| **1** | First project with `CLAUDE.md` | You stop re-explaining context and decisions |
| **2** | Phrase -> folder shortcuts | Say "my expenses" and it knows where to look |
| **3** | First custom skill | One phrase triggers a repeated recipe |
| **4** | Routine + connected tool | The system can read mail, calendar, or tasks |
| **5** | Orchestrator | Several skills work together |
| **6** | Audit and tuning | You keep the system from degrading |
| **If you code** | Code separated from context | The repo keeps code; the brain keeps decisions |

The coach reads `ESTADO.md` and `ESCALERA.md`, tells you where you are, and proposes one next step.

## Portability

Your brain is plain text. You can open the same folder in Cowork, Claude Code, Codex, or Cursor.

Use-skills live in `skills/` and are activated through the **Mis skills** table in `CLAUDE.md`. Codex and Cursor reach that table through `AGENTS.md`.

The only Claude-specific piece is the setup engine: `/asb-coach` and, in Claude Code, `actualizar`. If you use another agent, `AGENTS.md` includes a fallback workflow.

## What's inside

- `CLAUDE.md`: main router.
- `ESTADO.md`: short status file for resuming quickly.
- `ESCALERA.md`: progress tracker and kit catalog.
- `AGENTS.md`: pointer for non-Claude agents.
- `0. Inbox/`: capture without deciding.
- `2. Áreas/yo/sobre-mi.md`: who you are.
- `2. Áreas/yo/como-trabajo.md`: how you want the assistant to work.
- `2. Áreas/yo/mi-estilo.md`: your writing voice.
- `2. Áreas/yo/MEMORIA.md`: facts that apply everywhere.
- `3. Recursos/arquitectura-skills.md`: how to build skills.
- `3. Recursos/anti-slop-writing.md`: rules for cleaning AI-sounding text.
- `skills/`: skills you have activated.

Available catalog skills:

- `redactar`: writes in your voice.
- `anti-slop`: cleans text.
- `crear-skill`: builds a new skill.
- `evaluar-skill`: checks a skill against its own rubric.
- `auditar-sistema`: checks the health of the brain.
- `triage`: builds a daily brief from connected mail, calendar, and tasks.
- `ppt-builder`: coordinates a communication piece in stages.
- `panel`: brings several lenses to a text, proposal, or document.
- `council`: a council of advisors for a decision with real stakes.
- `prompt-optimizer`: turns a rough ask into a paste-ready prompt.
- `documenta`: routes what matters from a session to its canonical place.
- `simple`: a short, plain-language status of the current conversation.

Most catalog skills map to an `/asb-*` command (shown in `ESCALERA.md`). A few (`crear-skill`, `triage`, `evaluar-skill`) have no standalone command: the coach activates them when you reach their level.

## Philosophy

- Propose, you decide.
- One step at a time.
- Small files, read only when needed.
- Skills stay dormant until a phrase activates them.
- Your folder stays clean: only your stuff.

## Credit

Made by [Bruno Gielczynsky](https://www.linkedin.com/in/brunogiel/). Part of a family of installable AI methods alongside [Empat.ia](https://github.com/brunogiel/Empat.ia).

## License

MIT. Use it, fork it, make it yours.

# Agentic Second Brain

*Your second brain, agentic.* Your assistant knows where your stuff lives and what to do with your requests, from the first message.

Claude starts every session not knowing who you are, how you work, or where things live. Agentic Second Brain fixes that: a folder with plain-text files it reads at startup, so it stops guessing.

Unlike notes you keep for yourself, this folder is shared: you and your assistant both read and edit it, but the agent is the one working from it, loading what each task needs to act.

You install one coach, and it builds the rest with you, one step at a time. Works with **Cowork** and **Claude Code**; **Codex** and other agents use the same folder through `AGENTS.md`.

> Official version (Spanish): [README.md](README.md).

---

## The difference shows up in session two

You feel it the second time you open Claude: you do not explain the same context again.

```text
Session 1, no brain:
  You: I'm a freelance designer, my stack is X, I'm on the Acme rebrand,
       keep the tone casual... (every session, from scratch)

Session 2, with the brain:
  You:    draft the Acme update email
  Claude: (already knows who you are, the project, your tone) Here's a draft...
```

That gap is the whole point.

## The toolkit, ready on day one

The plugin ships slash commands that work the moment you install it, with no setup:

| Command | What it does |
|---|---|
| `/brain` | Front desk: shows your tools and where you stand |
| `/brain-coach` | Builds your personal system, one step at a time (the engine) |
| `/brain-slop` | Strips the AI smell from a text in one pass |
| `/brain-write` | Writes or rewrites in your voice |
| `/brain-prompt` | Turns a rough ask into a paste-ready prompt for any AI chat |
| `/brain-panel` | 2 to 5 reviewers, different lenses, on something before you send it |
| `/brain-council` | A council of 5 advisors for a decision with real stakes |
| `/brain-verify` | The gate before you send: checks the output meets the ask and fact-checks its data |
| `/brain-deck` | Builds a presentation in stages, rough to final |
| `/brain-audit` | Health check of your second brain |
| `/brain-doc` | Closes a session: routes everything durable to its place |
| `/brain-simple` | Lost the thread? Plain-language recap: where we are, your move, mine |
| `/brain-newskill` | Build a new skill following the anatomy that works |
| `/brain-evalskill` | Grade a skill against its rubric and propose fixes (doesn't apply them) |

The toolkit commands are stock and work the same for everyone. `/brain-coach` is the engine: its job is, above all, to help you **generate and maintain your second-brain architecture** (your projects, identity, and your own skills), one step at a time. A *skill* is a saved recipe a phrase triggers; using the toolkit ones is the fastest way to see what one is before you write your own.

Beyond the toolkit, `/brain-triage` (your daily brief) is the first configurable skill: the coach teaches you to set it up once you connect a source over MCP — mail, calendar, or tasks.

They run as slash commands in both Cowork and Claude Code, with no setup. In Cowork you can also trigger them by describing what you want.

## Install

### Cowork (no terminal)

1. Type `/setup-cowork install brain@agentic-second-brain` (the name repeats because it is `plugin@marketplace`).
2. Open or create the folder where your brain should live. A synced folder is best: Drive, iCloud, or Dropbox.
3. Type `/brain` to start. It asks before creating anything, never builds folders behind your back, and in Cowork the plugin updates itself.

### Claude Code

```bash
curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/install.sh | bash
```

It installs the method and commands globally and does not touch your brain folder. Then open the folder where you want to work and type `/brain` to start.

## How it works

The model under the hood (Opus, Fable, Haiku, GPT-5) writes text. The client (Cowork, Claude Code, Codex) gives it hands to read and edit files. Your folder gives it the context. The payoff: your context window stays cheap and uncluttered, because instead of loading everything, the agent fetches the one or two files a task needs.

That works because of the layout. **This repo uses the PARA method** (projects, areas, resources, archive) plus an inbox, because it orders everything by how actionable it is and gives the agent a clear map of where things live. On top sits a small **master index** (`CLAUDE.md`) that points to where everything is. Files stay small and single-purpose, so the index points and the agent fetches only what the task needs, and you can open or edit any piece by hand without anything breaking.

Two parts stay separate. **This method** lives outside your folder so it doesn't interfere with your files (a plugin in Cowork, `~/.claude/skills/` in Claude Code) and holds the coach, templates, and kit catalog. **Your context, on the other hand, lives in your folder**, and holds only your stuff. It ends up looking like this (starter names, rename to taste):

```text
CLAUDE.md        # the master index your assistant reads first
ESTADO.md        # short status, to resume fast
ESCALERA.md      # your progress + the kit catalog
AGENTS.md        # pointer for non-Claude agents
0. Inbox/        # capture without deciding
1. Proyectos/    # projects, one folder each
2. Áreas/yo/     # who you are, how you work, your voice
3. Recursos/     # reusable references
4. Archivo/      # done or dormant
skills/          # the skills you have activated
```

## Already have a system?

You do not have to migrate. The coach reads your structure and keeps it.

The rule is simple: there must be a clear master index (`CLAUDE.md` or `AGENTS.md`) that says where things live. If your structure already works, the coach does not rename it or force PARA. It only proposes small improvements: inbox, shortcuts, decision logs, skills, or session state.

## What it touches

- The Claude Code installer only installs the global method.
- The coach creates files in your brain only after you approve.
- Existing files are not overwritten.
- Updates refresh the method, not your folder.
- Uninstall removes the engine, not your data.

To uninstall in Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/uninstall.sh | SB_YES=1 bash
```

In Cowork, uninstall the plugin from the UI or type `/plugin uninstall brain`.

## The ladder

You do not build everything on day one. You climb one step at a time.

| Level | What you build | What it gives you |
|---|---|---|
| **0** | Identity + inbox | The assistant knows who you are and loose ideas are not lost |
| **1** | First project with `CLAUDE.md` | You stop re-explaining context and decisions |
| **2** | Phrase -> folder shortcuts | Say "my expenses" and it knows where to look |
| **3** | First custom skill | One phrase triggers a repeated recipe |
| **4** | Routine + connected tool | The system can read mail, calendar, or tasks |
| **5** | Orchestrator | Several skills work together on one task |
| **6** | Audit and tuning | You keep the system from degrading |
| **If you code** | Code separated from context | The repo keeps code; the brain keeps decisions |

The coach reads `ESTADO.md` and `ESCALERA.md`, tells you where you are, and proposes one next step.

## Portability

Your brain is plain text. You can open the same folder in Cowork, Claude Code, Codex, or Cursor. Use-skills live in `skills/` and are triggered through the **Mis skills** table in `CLAUDE.md`, which Codex and Cursor reach through `AGENTS.md`. Since each skill is a plain-text folder, you can copy any of them out of `skills/` into another agent and use it there: they don't depend on Claude. The only Claude-specific piece is the setup engine (`/brain-coach`, and in Claude Code the `actualizar` updater); for other agents, `AGENTS.md` has a fallback workflow.

## Philosophy

- Propose, you decide.
- One step at a time.
- Small files, read only when needed.
- Skills stay dormant until a phrase activates them.
- Your folder stays clean: only your stuff.

## Author

[Bruno Gielczynsky](https://www.linkedin.com/in/brunogiel/)

## License

MIT. Use it, fork it, make it yours.

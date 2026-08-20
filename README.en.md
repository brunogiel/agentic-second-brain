# Agentic Second Brain

*Your second brain, agentic.* Your assistant knows where your stuff lives and what to do with your requests, from the first message.

Claude starts every session not knowing who you are, how you work, or where things live. Agentic Second Brain fixes that: a folder with plain-text files it reads at startup, so it stops guessing.

This folder is shared: you and your assistant both read and edit it, but the agent is the one working from it, loading what each task needs to act.

You install one coach, and it builds the rest with you, one step at a time. Works with **Cowork** and **Claude Code**; **Codex** and other agents use the same folder through `AGENTS.md`.

> Official version (Spanish): [README.md](README.md).

---

## What it ships, in two layers

1. **The coach.** A mode of the assistant that asks you questions and builds, chatting with you, your own second brain: identity, projects, shortcuts, your own skills. This is the point. It takes real work from you; the coach walks with you, it does not do it alone.
2. **The `/brain-*` toolkit.** Commands: phrases you type starting with `/` in the Claude chat that trigger a ready-made recipe (strip AI smell from a text, write in your voice, build a prompt, and more), no extra setup. This is the extra: useful from minute one, but not the point. Plain-text files: cherry-pick the one skill you like and copy it, no coach install, no need to try the rest of the repo (see the "The toolkit, ready on day one" section below).

The point behind it: the more catalog skills you replace with your own, the less you need this repo.

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

This is the extra layer of the method (see above). It runs on its own from minute one, but the coach is the point.

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
| `/brain-ship` | Ships what Claude built and hands you the link; first run connects your host and leaves it ready, then it just ships |
| `/brain-deck` | Builds a presentation in stages, rough to final |
| `/brain-audit` | Health check of your second brain |
| `/brain-doc` | Closes a session: routes everything durable to its place |
| `/brain-simple` | Lost the thread? Plain-language recap: where we are, your move, mine |
| `/brain-recap` | Visual recap of the session in a single HTML file: what happened, what got decided, what's still open |
| `/brain-newskill` | Build a new skill following the anatomy that works |
| `/brain-evalskill` | Grade a skill against its rubric and propose fixes (doesn't apply them) |

Just want one skill, not the whole toolkit? Cherry-pick it: it's MIT and plain text, copy `kit/skills/<name>/` and its command `commands/brain-<name>.md` into your own `~/.claude/skills/` and `~/.claude/commands/`, no coach install, nothing else touched.

The toolkit commands are stock and work the same for everyone. `/brain-coach` is the engine: its job is, above all, to help you **generate and maintain your second-brain architecture** (your projects, identity, and your own skills), one step at a time. A *skill* is a saved recipe a phrase triggers; using the toolkit ones is the fastest way to see what one is before you write your own.

Beyond the toolkit, `/brain-triage` (your daily brief) is the first configurable skill: the coach teaches you to set it up once you connect a source over MCP — mail, calendar, or tasks.

They run as slash commands in both Cowork and Claude Code, with no setup. In Cowork you can also trigger them by describing what you want.

## Install

Doesn't touch anything of yours: no reordering, no changing existing files. You can install it just to try the toolkit, no commitment; if you like it, ask the coach to build the rest with you. If not, uninstall it and everything's back the way it was.

### Cowork (no terminal)

1. In the app: **Customize → Plugins → Personal plugins → "+" → Add marketplace → "Add from a repository"**, paste `brunogiel/agentic-second-brain` and hit **Install** on the **`brain`** plugin. (`/setup-cowork` and `/plugin` don't work here: the first is the official registry, the second is Claude Code terminal.)
2. Open or create the folder where your brain should live. A synced folder is best: Drive, iCloud, or Dropbox.
3. Type `/brain` to start. It asks before creating anything, never builds folders behind your back, and in Cowork the plugin updates itself.

### Claude Code

```bash
curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/install.sh | bash
```

Or, if you prefer the plugin system over the curl one-liner:

```text
/plugin marketplace add brunogiel/agentic-second-brain
/plugin install brain@agentic-second-brain
```

It installs the method and commands globally and does not touch your brain folder. Then open the folder where you want to work and type `/brain` to start.

## How it works

The model under the hood (Opus, Fable, Haiku, GPT-5) writes text. The client (Cowork, Claude Code, Codex) gives it hands to read and edit files. Your folder gives it the context. The payoff: your context window stays cheap and uncluttered, because instead of loading everything, the agent fetches the one or two files a task needs.

That works because of the layout. **This repo uses the PARA method** (projects, areas, resources, archive) plus an inbox, because it orders everything by how actionable it is and gives the agent a clear map of where things live. On top sits a small **master index** (`CLAUDE.md`) that points to where everything is. Files stay small and single-purpose, so the index points and the agent fetches only what the task needs, and you can open or edit any piece by hand without anything breaking.

Two parts stay separate. **This method** lives outside your folder so it doesn't interfere with your files (a plugin in Cowork, `~/.claude/skills/` in Claude Code) and holds the coach, templates, and kit catalog. **Your context, on the other hand, lives in your folder**, and holds only your stuff. It ends up looking like this (starter names, rename to taste):

```text
CLAUDE.md        # the master index your assistant reads first
ESTADO.md        # short status + your progress + the kit catalog
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

## What it touches and how to undo it

- The Claude Code installer only installs the global method.
- The coach creates files in your brain only after you approve.
- Existing files are not overwritten.
- Updates refresh the method, not your folder.
- Uninstall removes the engine, not your data.

To uninstall in Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/uninstall.sh | SB_YES=1 bash
```

In Cowork, uninstall the plugin from the UI (**Customize → Plugins**).

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

The coach reads `ESTADO.md`, tells you where you are, and proposes one next step.

The point behind it: replace every catalog skill with one of your own. The day none are left to replace, you no longer need this repo.

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

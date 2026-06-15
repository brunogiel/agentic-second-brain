# SecondBrain

A simple, installable method to organize how you work with **Claude Code** (or **Cowork**) and grow it over time. You install one thing, a coach, and it builds and grows the rest with you, one rung at a time.

Built for anyone: total beginner or power user. You don't need to code. If you do, the code/context split is already baked in.

> 🇦🇷 Method content is in Spanish (rioplatense). This README is in English for reach. Spanish version: [README.es.md](README.es.md).

---

## Why this works

Claude is a brain that generates text. The harness (Claude Code, Cowork) gives it hands and memory. **Your folders are what turn it into _your_ assistant.** A few plain text files, read at the start of every session, stop it from guessing who you are and how you work. That is the whole trick. The rest is staying organized.

Most people never write those files. This gives you the seed and a coach that walks you through growing it.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/brunogiel/secondbrain-claude/main/install.sh | bash
```

This creates your PARA folders and starter files, sets up a hidden `.secondbrain/` for the machinery, and installs the skills. Your folder stays clean: you only see your own stuff, the process stays out of sight.

Not on the terminal (e.g. Cowork desktop)? Download the zip or `git clone`, or just open Claude in the folder and say *"set up my system"*.

Then open Claude Code or Cowork in the folder and type **`/second-brain-coach`**.

## The ladder (grow one rung at a time)

You don't build the whole system on day one. You climb. The coach teaches you the idea behind each rung, not just what to do.

| Level | What you learn + add |
|---|---|
| **0** | The 3 layers (model / harness / your folders). It knows you (`sobre-mi` + `como-trabajo`) |
| **1** | Your first project (its own brain + decision log) |
| **2** | Shortcuts (route the assistant instantly) |
| **3** | Your first skill, and what a script is: the kit's update-checker |
| **4** | Your first routine (something that runs on its own) |
| **5** | (if you code) the code/context split |

Beginner or advanced? The coach adapts: one rung at a time with full teaching for newcomers, or a fast multi-rung setup plus an advanced track for power users. Ask **`/second-brain-coach`** anytime: it tells you where you are and proposes the next step. It proposes, you decide.

## Cowork first, migrate to Code

Your whole system lives in one synced folder, so it's the same brain wherever you open it. Start in **Cowork** (no terminal needed). When you grow into code, just open the same folder in **Claude Code**: there's no migration, the brain is already there.

## What's inside

- **`CLAUDE.md`** — your root file, a thin router read at the start of every session.
- **`ESTADO.md`** — your dashboard: where you are, what's active.
- **`sobre-mi.md` / `como-trabajo.md`** — who you are and how you like to work (fill-in templates).
- **`soul.md` / `dev-prefs.md`** — what you're really about (fills in over time, in conversation) and, if you code, how you like to work the code.
- **`.secondbrain/`** (hidden) — the process: `reference.md` (the manual) and version control. Out of sight, syncs anyway.
- **Skills** (dormant until a phrase triggers them):
  - **`second-brain-coach`** — walks you up the levels and teaches as you go.
  - **`redactar`** — writes in your voice (learns it from your own sample texts).
  - **`anti-slop`** — strips the "AI smell" out of any text.

## Philosophy

- **Propose, you decide.** Nothing gets created without your OK.
- **One rung at a time.** No overwhelming to-do lists.
- **Teach as you climb.** You learn the idea, not just the task.
- **Light to run.** Reads only what it needs, so it stays cheap even on the $20 plan.
- **Everything ships dormant.** A skill does nothing until a phrase wakes it up.

## Credit

Made by [Bruno Gielczynsky](https://www.linkedin.com/in/brunogiel/). Part of a family of installable AI methods alongside [Empat.ia](https://github.com/brunogiel/Empat.ia).

## License

MIT. Use it, fork it, make it yours.

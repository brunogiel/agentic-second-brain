---
description: Structure for SKILL.md files in skill-based repos
alwaysApply: true
---

# Skill File Structure

Each skill lives in its own folder with a `SKILL.md` at the root. Scripts and references go alongside.

```
{skill-name}/
├── SKILL.md             ← contract + workflow
├── scripts/             ← optional, only if needed
└── references/          ← optional, supporting docs the skill cites
```

## SKILL.md frontmatter

```yaml
---
name: skill-name
description: |
  Rich, trigger-phrase-laden description. Should include the natural-language
  phrases a user might say that should activate this skill. Avoid generic verbs
  like "use", "do", "make"; use specifics.
when_to_use:
  - "Quote literal trigger phrases here"
  - "Multiple variants of the same intent"
inputs:
  - name: input1
    description: What it is and what format
    required: true
---
```

## SKILL.md body

Required sections in order:

1. **Context** — when this skill applies and when it doesn't. Negative scope matters.
2. **Inputs** — what the user/caller has to provide.
3. **Process** — numbered steps. Mark each step as `[DET]` (deterministic, runs the same every time) or `[LATENT]` (model judgment required).
4. **Output expected** — what the deliverable looks like, where it goes, what success means.
5. **Success metrics** — how to know the skill worked. Used by `eval-skill` as rubric.

## Rules

- No bundles (`.skill` ZIPs). Always a folder with plain `SKILL.md` + optional scripts.
- Portable: any LLM that reads the folder should be able to execute.
- Scripts are reusable code (Python, bash). Don't leave them in `/tmp/` — keep them with the skill.
- If a skill generates evaluable output, declare `## Output expected` and `## Success metrics` so `eval-skill` can use them as rubric.

## Anti-patterns

- ❌ Single mega-skill that tries to do 10 things. Split into smaller skills the orchestrator can invoke.
- ❌ Skills that assume context not declared in `Inputs`. If the skill needs it, list it.
- ❌ Vague descriptions. "Handles things related to X" doesn't trigger reliably. List trigger phrases.
- ❌ Steps that mix `[DET]` and `[LATENT]` work without marking which is which.

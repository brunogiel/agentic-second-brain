---
description: Universal rules that apply regardless of stack
alwaysApply: true
---

# Universal Engineering Rules

These apply to any repo you own, regardless of language or framework.

## File size

- Files **≤ 300 lines**. If over 200, look for an extraction (hook, sub-component, helper module).
- If a file is over 300 lines, refactor before adding more.

## Naming

- No abbreviations except very standard ones (`url`, `id`, `db`, `api`). `usrMgr` is not allowed, `userManager` is.
- Boolean variables: `is*`, `has*`, `should*`, `can*`. Not `flag`, `status` (unless really a status).
- Functions are verbs, variables are nouns.

## Imports

- Direct imports, no barrel files (`index.ts` re-exports). Reference: <https://tkdodo.eu/blog/please-stop-using-barrel-files>
- Use absolute paths with alias (`@/` or equivalent) for anything that crosses 2+ folder levels.

## Secrets and config

- **Never** commit `.env`, `credentials.json`, API keys, tokens, or any file with secrets.
- Add to `.gitignore` before the first commit, not after a leak.
- Use environment variables via `.env.local` (gitignored) and document required vars in `.env.example` (committed, no values).

## Logging and errors

- No `console.log/warn/error` in production code. Use the project's logger (Pino, structlog, etc.).
- Never swallow errors silently with `try/catch` that does nothing. If you catch, log + decide what to do.
- Error messages should help the next person debug, not just say "something failed".

## Comments

- Default: no comments. Code with good names is self-documenting.
- Write a comment **only** when the *why* is non-obvious: a workaround, a hidden constraint, an invariant a future reader would miss.
- Never write comments that repeat what the code says (`// increment counter` above `counter++`).
- Never reference tickets or PRs in comments. That context belongs in commits and PR descriptions.

## Dead code

- If a function, variable, or import is unused, delete it. Don't leave it with `// removed` notes.
- If a feature is unused, delete the code paths. Don't keep them "just in case".

## Testing

- The deliverable isn't done until you saw it work. Type-checks and unit tests verify code correctness, not feature correctness.
- For UI changes: start dev server and use the feature in a browser before claiming done.
- For backend: curl or integration test the endpoint at minimum.
- A hidden/backgrounded browser pane doesn't run `requestAnimationFrame`, so scroll and interaction events (scroll listeners, `IntersectionObserver`, animations) silently fail to fire there, a false negative, not a real bug. Verify that class of behavior with the pane visible, or against the raw served HTML (`curl`), not through a hidden tab. Before reporting "X doesn't fire" or "page doesn't scroll", check `document.hidden` and the viewport size.

## Performance

- Don't optimize before measuring. But also don't write O(n²) when O(n) is the same effort.
- Avoid N+1 queries, especially in loops. Batch or join.
- For list rendering, paginate or virtualize when items > 100.

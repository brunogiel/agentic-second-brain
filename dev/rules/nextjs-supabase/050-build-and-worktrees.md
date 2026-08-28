---
description: Turbopack rejects symlinked node_modules in git worktrees, breaking build and dev
alwaysApply: false
---

# Build & Git Worktrees (Turbopack)

Applies when running `next build` / `next dev` from a git worktree whose `node_modules` is a symlink to the main repo (`ln -s /path/to/main/node_modules`).

## The problem

Turbopack refuses to follow symlinks that point outside the project's filesystem root. In a worktree, `node_modules` is typically symlinked from the main repo, so the build (and sometimes dev) fails with:

```
Symlink [path]/node_modules is invalid, it points out of the filesystem root.
```

`typecheck` and `lint` are unaffected, only Turbopack's build/dev compiler chokes on it. Dev has been observed to work with the symlink on some runs and fail with the exact same error on others (Next 16.2.6), so don't treat a passing `next dev` as proof the symlink is safe for `next build`.

## Fix: use webpack instead of Turbopack

```bash
node_modules/.bin/next build --webpack
node_modules/.bin/next dev --webpack --port 3007   # any free port
```

Webpack resolves symlinks fine. This is the fastest, safest fix for a worktree: it never touches the main repo, so it also sidesteps the risks below. It's a webpack build, not Turbopack, but it's enough to catch boundary/import/compile errors for a DoD gate.

## If you need a real Turbopack build

Replace the symlink with a real `node_modules` via hardlink-clone (near-zero disk, ~10s instead of the 1-2min a full `cp -R` takes):

```bash
rm -f node_modules
cp -Rcl /path/to/main-repo/node_modules ./node_modules
```

This produces a real directory (not a symlink) with files hardlinked to the main repo, so Turbopack accepts it.

## Do not copy the worktree's files into the main repo to build there instead

It's tempting when the worktree build is inconvenient, but it has two failure modes:
- `rsync --delete` (or any free overwrite) can destroy **uncommitted WIP** sitting in the main repo. That's not recoverable via git: a change that was never staged has no blob, so `git fsck --lost-found` won't find it either.
- The shell's cwd can end up parked in the main repo, and a later `git add -A && git commit && git push` meant for the worktree branch lands on `main` instead, skipping review and deploying straight to prod.

If you must copy files to the main repo anyway: check `git status` there first and stash/abort if it's dirty, copy only the specific files you need (never `--delete`), and use `git -C <path>` explicitly on every git command instead of relying on cwd.

**Why:** Turbopack has a security restriction against following symlinks outside the project root, with no flag to disable it. The only ways around it are a non-symlinked `node_modules`, or the webpack builder, which does resolve symlinks.

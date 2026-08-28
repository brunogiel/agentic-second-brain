---
description: Parking de WIP: comitea lo que haya sin exigir definition of done y lo pushea para seguir desde otro lado.
---

Se para acá y el trabajo de ESTE worktree tiene que quedar en el remoto para continuarlo en otra máquina. **No es "done", es parking.** Nota opcional: $ARGUMENTS

1. **Verificá que estés en tu branch**, no en `main` ni `integration/*`. Si lo estás, pará y avisá.
2. **Comiteá lo que haya como WIP**, sin exigir que el type-check o el build pasen: puede estar a medio hacer. Mensaje corto pero que ubique después.
3. **Pusheá:** `git push -u origin HEAD`.
4. **Reportá:** branch, último commit, y que quedó listo para continuar en otro lado.

Ojo: desde la otra máquina vas a ver **solo lo pusheado**. Si tenés varios worktrees abiertos, corré esto en cada uno antes de irte. Al volver, arrancá con `/dev-sync`.

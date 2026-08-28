---
description: Limpieza de cierre del día: borra branches y worktrees ya mergeados. No toca lo que sigue abierto.
---

Cierre del día: limpiar lo ya mergeado para no acumular. Indicación opcional: $ARGUMENTS

1. `git checkout main && git pull`.
2. **Listá** los worktrees y los branches locales ya mergeados a `main`, cruzados con los remotos.
3. **Mostrá en una tabla qué se borraría y qué se conserva** (lo que sigue en progreso, y todo worktree con cambios sin commitear). **Pedí confirmación antes de borrar nada.**
4. Con el OK: sacá los worktrees mergeados, borrá sus branches y corré `git worktree prune`. Los branches remotos solo si se confirma explícitamente.

Nunca borres un worktree con cambios sin commitear ni el branch de algo en progreso. Ante la duda, conservá y preguntá.

Por qué existe este comando: acumular ramas termina en forense sobre decenas de branches de varios días para saber qué está en `main`. Ver `dev/WORKFLOW.md`.

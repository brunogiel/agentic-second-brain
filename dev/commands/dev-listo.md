---
description: Cierra la tarea del worktree actual: comitea, pushea el branch y lo deja listo para integrar después.
---

La tarea de este worktree está terminada y se deja lista para integrar más tarde. Nota opcional: $ARGUMENTS

1. **Verificá que estés en tu branch**, no en `main` ni en `integration/*`. Si lo estás, **pará y avisá**: algo salió mal, ahí no se commitea.
2. **Definition of done primero:** type-check, lint o build, según el tipo de cambio (ver `dev/WORKFLOW.md`). Si algo falla, arreglá la causa raíz antes de commitear. No está hecho hasta verlo funcionar.
3. **Comiteá** con un mensaje que explique el porqué, no el qué.
4. **Pusheá:** `git push -u origin HEAD`.
5. **Reportá en una línea:** branch, qué hace, y "listo para integrar".

**No mergees** a `main` ni a `integration/*` acá. Eso es `/dev-integrar`. Tu branch queda pusheado esperando.

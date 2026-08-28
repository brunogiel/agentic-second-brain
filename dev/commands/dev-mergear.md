---
description: Mergea a main el PR ya revisado. Es la única acción que toca producción.
---

El preview ya se revisó y esto va a producción. **Es la única acción que mergea a `main`, así que es deliberada y se chequea antes.** PR: $ARGUMENTS (si viene vacío: el PR abierto del branch actual, o el integration del día).

1. **Identificá el PR** y confirmá en una línea cuál es: número, título y base.
2. **Chequeá que esté listo:** base `main`, mergeable, checks en verde. Pasá el link del preview una vez más.
3. **Si algo no está limpio** (checks rojos, conflictos, base equivocada, archivos inesperados en el diff): **pará y avisá. No mergees.**
4. **Si está todo bien:** mergeá con squash y borrá el branch.
5. **Confirmá** que mergeó, que arrancó el deploy, y pasá la URL de producción cuando termine.
6. **Ofrecé `/dev-limpiar`** para borrar los branches y worktrees que entraron.

Si hay varios PRs, mergealos de a uno y reportá cada deploy. Nunca con checks en rojo sin confirmación explícita.

---
description: Consolida los branches terminados en un integration branch, abre UN PR y devuelve el link del preview.
---

Consolidá los branches terminados en un integration branch y subí un solo PR. **Esta sesión es la consolidadora: la única que toca el integration.** Indicación: $ARGUMENTS

Doctrina y las 5 reglas: `dev/WORKFLOW.md`.

1. **Base limpia:** `git checkout main && git pull`.
2. **Listá candidatos:** branches `feat/*` y `fix/*` pusheados que todavía no estén en `main`. Mostrá la lista y confirmá cuáles entran. Los worktrees con trabajo sin commitear **no entran y no se tocan**.
3. **Creá el integration:** `git checkout -b integration/<fecha>` desde `main`.
4. **Mergeá los confirmados uno por uno** con `git merge --no-ff`. Los conflictos se resuelven acá. Los archivos generados no se resuelven a mano: se regeneran una sola vez al final.
5. **Verificá el conjunto:** type-check, lint, build. Si rompe, arreglá antes de subir.
6. **Pusheá y abrí UN PR** contra `main`.
7. **Devolvé el link del preview desplegado.** Sin ese link no terminaste.
8. **Pará acá.** No mergees vos: el merge a `main` es un paso aparte y deliberado, y lo hace `/dev-mergear` después de revisar el preview.
9. **Si el repo es una app con usuarios finales,** ofrecé armar un aviso de novedades en criollo con lo que entra en este PR. Solo si te dicen que sí.

Regla de oro: nadie más commitea en el integration. Si otra sesión tiene algo, que pushee su branch y lo mergeás vos acá.

---
description: Sincroniza el repo local con el remoto al volver de trabajar en otra máquina. Fetch, fast-forward y reporte de divergencias.
---

Se volvió a trabajar en local y puede haber cosas pusheadas desde otro lado. **El remoto es la fuente de verdad.** Poné el repo al día sin romper nada. Indicación opcional: $ARGUMENTS

1. `git fetch origin --prune`, que además limpia las refs de branches borrados en el remoto.
2. **Main al día:** si estás parado en `main` y es fast-forward, `git pull --ff-only`. Si no estás en `main`, **no cambies de branch**: solo reportá cuánto quedó atrás.
3. **Reportá el estado en una tabla corta:**
   - Branches locales atrás de su remoto.
   - Branches ya mergeados a `origin/main`, candidatos a `/dev-limpiar`.
   - Worktrees cuya base quedó vieja porque `main` avanzó debajo.
   - Branches locales **sin pushear**: trabajo que la otra máquina todavía no ve.

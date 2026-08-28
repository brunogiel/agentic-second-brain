---
description: Arranca un worktree y un branch aislado con nombre para una tarea. Para días de varios cambios en paralelo.
---

Arrancá una tarea aislada en su propio worktree + branch. Tarea: $ARGUMENTS

Doctrina: `dev/WORKFLOW.md`, sección "Varios agentes en paralelo".

1. **Ubicate:** `git rev-parse --show-toplevel` y `git rev-parse --abbrev-ref HEAD`. ¿Ya estás en un worktree aislado, o en el checkout principal?

2. **Proponé el nombre del branch** a partir de la tarea: `feat/` (o `fix/` si es un bug claro) más un slug corto en kebab-case. Mostralo en una línea antes de aplicarlo.

3. **Creá o renombrá, según dónde estés:**
   - **Ya en un worktree aislado con branch autogenerado:** renombralo en su lugar con `git branch -m <nombre>`. No crees otro worktree.
   - **En el checkout principal sobre `main`:** `git worktree add -b <nombre> .worktrees/<slug> origin/main`, y entrá ahí. Si el proyecto tiene dependencias instaladas o un archivo de entorno local, symlinkealos desde el repo principal en vez de reinstalar.

4. **Confirmá el aislamiento:** carpeta propia, branch propio, y el entorno que el proyecto necesite para correr. No vas a tocar `main` ni ningún `integration/*`.

5. **Arrancá.** El cierre es con `/dev-listo`.

Si $ARGUMENTS viene vacío, preguntá en una línea qué se va a hacer antes de crear nada.

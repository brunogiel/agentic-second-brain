---
description: Sube UNA cosa terminada con su propio PR, sin esperar al batch del integration.
---

Algo ya está listo y es independiente, y se sube sin esperar a consolidar con el resto. Qué subir: $ARGUMENTS (si viene vacío, el branch del worktree actual).

1. **Identificá el branch.** Confirmá que esté commiteado y pusheado; si no, hacelo primero con la definition of done en verde.
2. **Chequeá que sea independiente:** que sean solo tus commits y que no dependa de otro branch sin mergear.
3. **Abrí su propio PR** contra `main`.
4. **Devolvé el link del preview desplegado**, esperando a que el deployment termine.
5. **Pará acá.** El merge a producción lo hace `/dev-mergear`.

Esto es para una cosa aislada. Para subir varias juntas, `/dev-integrar`.

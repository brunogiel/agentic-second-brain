# El flujo — cómo se trabaja con varios agentes a la vez

Los comandos de `dev/commands/` no son atajos sueltos: son los pasos de este flujo. Si leés
esto una vez, los comandos se explican solos.

## Git, lo básico

- **Commits chicos, mensaje descriptivo.** Nada de "fix" ni "wip". El mensaje explica el
  porqué; el qué ya lo muestra el diff.
- **Branch cuando el cambio es grande, destructivo, o querés ver el diff completo** antes de
  fusionar. Para fixes chicos en proyectos personales, push directo a `main` está bien.
- **Force-push solo con OK explícito.** Nunca a `main` de un repo con colaboradores o publicado.
- **Si un pre-commit hook falla, arreglá la causa y hacé otro commit.** Nunca `--no-verify`.

## Varios agentes en paralelo: el integration branch

Cuando tenés dos o más branches de agentes sin mergear, el default es **un solo integration
branch**, no merges separados.

El motivo es concreto: mergear de a uno son N deploys en fila y nadie prueba la combinación.
Un integration es un preview, un merge, un deploy y un rollback simple.

**El flujo, que lo corre una sola sesión:**

1. `git checkout main && git pull`
2. `git checkout -b integration/<fecha>`
3. Mergear ahí los branches terminados y resolver los conflictos en el integration.
4. Abrir **un solo PR** contra `main` y pasar el link del preview para revisar el conjunto.
5. Si está bien, mergear ese PR: un solo deploy a producción.

### Las cinco reglas, sin las cuales esto se vuelve un infierno

1. **Un solo dueño del integration.** Una sola sesión mergea y commitea ahí. Las demás
   trabajan en su branch y avisan "pusheado, listo para integrar". Nunca dos sesiones
   escribiendo el mismo working tree.
2. **Consolidar al final, no en vivo.** Las features se cocinan en paralelo y el merge es un
   paso único al cierre. Un integration que se mueve mientras le seguís metiendo cosas es un
   blanco móvil.
3. **Una sola ruta de envío.** O PRs por feature, o integration branch, o push directo a
   `main`. **Nunca las tres a la vez.**
4. **Branches con nombre, no autogenerados.** `feat/recordatorios-epic-12`, no el random que
   te propone la herramienta. Los autogenerados se acumulan y después nadie sabe qué tienen.
5. **Limpieza al cierre de cada día.** Borrar lo ya mergeado ese mismo día. Acumular termina
   en forense sobre decenas de ramas de varios días para saber qué está en `main`.

**Archivos generados** (tipos de una base de datos, clientes de API, lo que sea): no los
regeneres en cada branch, porque garantiza conflicto en el integration. Se regeneran **una
sola vez** después del merge final. Si conflictúan igual, `checkout --theirs` y regenerar, no
resolver a mano.

> **De dónde salen estas reglas.** De un día real que salió mal: tres modelos corriendo a la
> vez sobre **47 ramas y 15 worktrees**, el integration branch rehecho dos veces y 28 comandos
> de forense git para re-derivar en qué estado estaba cada cosa. Salió todo a producción, pero
> el camino costó entre 3 y 4 veces lo que tenía que costar. Las cinco reglas son el resumen
> de qué faltó ese día.

## Branch o worktree

Un **branch** cambia el estado de tu carpeta. Un **worktree** es una carpeta aparte con su
propio branch, así que podés tener varias tareas abiertas al mismo tiempo sin pisarte.

Para un cambio por vez, branch alcanza. Para varios agentes en paralelo, worktree: cada uno
en su carpeta, con su `node_modules` y su `.env` symlinkeados desde el repo principal.

## Debugging

- **Causa raíz primero, fix después.** Una línea de diagnóstico, después el cambio.
- Si la causa es trivial (un typo, un off-by-one), arreglá directo y mostrá el resultado.
- Si no es obvia (race condition, side effect, dependencia escondida), explicala **antes** de
  tocar nada.
- **Nada de fixes que tapan el síntoma:** un `try/catch` que se traga el error, un default
  silencioso. Si el sistema está roto, que se note hasta entender por qué.
- Reproducir el bug antes de arreglarlo, si es viable.

## Entregar un cambio

**Pasá siempre el link del preview desplegado, no el del PR.** El PR muestra el diff; el
preview muestra si funciona, que es lo que se está revisando. Si el preview todavía está
compilando, decilo y pasá el link cuando termine. No lo sustituyas por el del PR.

## Definition of done

El default es: **corre, se probó a mano, y si hay tests, pasan.** Por tipo de cambio:

- **Frontend:** probado en el browser, el camino feliz y uno o dos bordes.
- **Backend o API:** probado con `curl` o un test, status correcto, payload esperado.
- **Script:** corrido al menos una vez con datos reales, output revisado.
- **Documentación:** leída de punta a punta al menos una vez.

**No está hecho hasta que se lo vio funcionar.** El type-check y los tests verifican que el
código sea correcto, no que la feature sirva.

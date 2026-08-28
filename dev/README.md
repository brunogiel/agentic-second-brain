# Módulo dev — opcional, para el que además programa

Esto **no se instala con el método base**, y es a propósito: alguien que quiere un segundo
cerebro no tiene por qué recibir ocho comandos de git que no pidió.

Si además programás, acá está el ciclo completo: arrancar una tarea aislada, cerrarla,
consolidar varias, subir a producción y limpiar. Más las reglas de código que se commitean al
repo para que las lea todo el mundo, humanos y agentes.

## Qué trae

| | Qué es |
|---|---|
| [`WORKFLOW.md`](WORKFLOW.md) | La doctrina. Git, el integration branch y sus 5 reglas, branch vs worktree, debugging, definition of done. **Leé esto primero:** los comandos son los pasos de este flujo |
| [`commands/`](commands/) | Ocho comandos, uno por paso del ciclo |
| [`skills/construir/`](skills/construir/SKILL.md) | El orquestador: encadena todo el ciclo en una sola invocación |
| [`rules/`](rules/) | Reglas de código que se copian al repo y se commitean |

## Los ocho comandos

Están pensados para un día con **varias tareas en paralelo**, cada una en su propio worktree.

| Comando | Cuándo |
|---|---|
| `/dev-branch` | Arrancás una tarea. Crea el worktree y el branch con nombre |
| `/dev-listo` | La terminaste. Comitea, pushea y la deja esperando |
| `/dev-integrar` | Juntás las terminadas en un integration branch y sacás **un** PR |
| `/dev-mergear` | Revisaste el preview y va a producción. **La única acción que toca prod** |
| `/dev-subir` | Una sola cosa lista que no quiere esperar al batch |
| `/dev-limpiar` | Cierre del día: borra lo ya mergeado |
| `/dev-guardar` | Parás a mitad y seguís en otra máquina. Parking de trabajo a medio hacer |
| `/dev-sync` | Volvés y ponés el repo al día con lo que se pusheó desde otro lado |

El ciclo típico de un día con tres tareas:

```
/dev-branch  ×3   (una por tarea, en paralelo)
/dev-listo   ×3   (a medida que cada una termina)
/dev-integrar     (una sola vez, saca el PR y el preview)
/dev-mergear      (cuando revisaste el preview)
/dev-limpiar      (al cierre)
```

O `/dev-construir` una vez, que hace todo eso solo y te devuelve el link.

## Las reglas

Se **copian** al repo de destino, no se symlinkean, y se commitean. Cada repo pasa a ser dueño
de su copia y la evoluciona según su realidad: symlinkear causa drift que nadie pidió.

- **`rules/universal/`** — cross-stack. Tamaño de archivo, naming, manejo de secretos. Va casi
  siempre.
- **`rules/nextjs-supabase/`** — Next.js con App Router, TypeScript, ShadCN, TanStack Query,
  Supabase y arquitectura por capas. Solo en repos de ese stack.
- **`rules/markdown-skills/`** — repos cuyo contenido es markdown, skills y agents, no una app
  web. Los lee un modelo como instrucciones, no una persona como interfaz.

```bash
cd tu-repo
mkdir -p .cursor/rules          # o .claude/rules
cp ruta/al/kit/dev/rules/universal/*.md .cursor/rules/
git add .cursor/rules && git commit -m "Reglas de código base"
```

**No las copies todas por defecto.** El set de un stack en un repo de otro stack es ruido que el
modelo va a intentar aplicar igual.

## Instalación

```bash
./install.sh --dev
```

Sin el flag, el método base se instala como siempre y este módulo no aparece.

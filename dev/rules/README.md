# Reglas de código

Se **copian** al repo de destino, no se symlinkean, y se commitean ahí. A partir de ese momento
el repo es dueño de su copia y la evoluciona según su realidad.

Por qué copiar y no linkear: cada repo termina customizando sus reglas con constraints propios y
decisiones de arquitectura que no aplican al resto. Un symlink las sincronizaría hacia atrás y
metería drift que nadie pidió.

## Los tres sets

| Carpeta | Cuándo va |
|---|---|
| `universal/` | Casi siempre. Cross-stack: tamaño de archivo, naming, manejo de secretos |
| `nextjs-supabase/` | Solo repos Next.js + TypeScript + Supabase |
| `markdown-skills/` | Solo repos cuyo contenido es markdown, skills y agents |

**No los copies todos por defecto.** Las reglas de un stack en un repo de otro stack son ruido, y
el modelo va a intentar aplicarlas igual.

```bash
cd tu-repo
mkdir -p .cursor/rules          # o .claude/rules
cp ruta/al/kit/dev/rules/universal/*.md .cursor/rules/
git add .cursor/rules && git commit -m "Reglas de código base"
```

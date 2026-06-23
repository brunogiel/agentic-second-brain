<!--
  AGENTS.md — puntero para harnesses que NO son Claude (Codex, Cursor, etc.).
  No dupliques contenido acá: la fuente de verdad es CLAUDE.md. Esto solo existe
  para que un agente que busca "AGENTS.md" sepa adónde ir.
-->

# AGENTS.md

La fuente de verdad de este sistema es **`CLAUDE.md`** (en esta misma carpeta). Leelo entero: es el router.

- El cerebro (carpetas de texto, identidad, proyectos) **y los skills de uso** son portables. Los skills viven en `skills/` (carpeta a la vista) y se disparan por la **tabla "Mis skills" del `CLAUDE.md`**: leé esa tabla y, cuando el usuario diga una de esas frases, seguí el `skills/<nombre>/SKILL.md` correspondiente. Así andan igual acá que en Claude.
- Lo único atado a Claude es el método de armado (el comando `/sabe-coach` y un par de skills de mantenimiento, que viven global con el coach). Si ese motor no existe en este harness, no frenes: seguí el fallback de abajo.

## Fallback para agentes no-Claude

Si el usuario quiere armar o hacer crecer el sistema desde Codex, Cursor u otro agente:

1. Leé `CLAUDE.md`, después `ESTADO.md` y `ESCALERA.md` si existen.
2. No escanees todo el árbol: si el pedido es de un proyecto, leé solo el `CLAUDE.md` de ese proyecto.
3. Respetá la regla central: proponés, el usuario decide. No crees, borres, muevas ni pises archivos sin un "dale" explícito.
4. Para diagnosticar progreso, usá `ESCALERA.md`: ubicá el nivel actual, nombrá 1-2 cosas que ya están, y proponé un solo próximo paso.
5. Para activar un skill de uso, copiá `kit/skills/<nombre>/` a `skills/<nombre>/`, agregá su frase gatillo en la tabla "Mis skills" de `CLAUDE.md`, y tachalo en el catálogo de `ESCALERA.md`.
6. Si no existe `kit/` en esta carpeta, pedile al usuario que instale o abra el repo/plugin del método antes de activar skills del catálogo. El brain ya armado igual se puede usar sin ese kit.
7. Al cerrar una sesión de trabajo, actualizá `ESTADO.md` con "Última vez" y "Próximo paso"; si tocaste un proyecto, agregá una línea en su log de decisiones.

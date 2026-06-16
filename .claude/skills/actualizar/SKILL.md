---
name: actualizar
description: >
  Chequea si el kit SecondBrain tiene una versión nueva y, si vos querés, la instala.
  Usalo cuando digas "¿hay updates?", "actualizá el kit", "fijate si salió algo nuevo",
  "actualizá SecondBrain", "¿estoy al día?".
---

# actualizar: bajar las mejoras del kit

## Qué es
Mira si el kit (SecondBrain) tiene una versión más nueva que la tuya y, con tu OK, la baja.
Es infraestructura del kit: ya viene hecho (a diferencia de los skills que armás vos, este lo trae el motor).

## Flujo
1. **[DET]** Comparar versiones. En Claude Code corré el script `check-update.sh` de esta carpeta;
   en Cowork (sin terminal) hacé el mismo chequeo con tus herramientas: bajá el `VERSION` del repo
   (`https://raw.githubusercontent.com/brunogiel/secondbrain-claude/main/VERSION`) y compará con `~/.claude/skills/second-brain-coach/VERSION`.
2. **[LAT]** Si la publicada es más nueva: mostrá qué cambió (del `CHANGELOG` del repo) en 2-3 líneas
   y preguntá *"¿te la instalo?"*. No bajes nada sin un "dale".
3. **[DET]** Con el OK: corré el `install.sh` del repo (vuelve a bajar el motor y los archivos del
   kit; respeta lo tuyo, no pisa tus entregables). El `install.sh` ya refresca `~/.claude/skills/second-brain-coach/VERSION`
   al número nuevo, no hace falta tocarlo a mano.

Fijate que el paso 1 y el 3 son mecánicos (script) y el 2 es criterio (vos decidís). Eso es DET vs LAT en vivo.

## Qué lee y escribe
- **Lee:** `~/.claude/skills/second-brain-coach/VERSION` (local) y el `VERSION` / `CHANGELOG.md` del repo.
- **Escribe:** solo con tu OK, baja archivos del kit y actualiza `~/.claude/skills/second-brain-coach/VERSION`. Nunca toca tus
  carpetas PARA ni tus skills propios.

## Garantía: tu carpeta no se toca (solo el motor global)
Actualizar **refresca el motor global** (`~/.claude/skills/`: el coach y sus piezas) y nada más. **Ningún archivo de tu carpeta se pisa nunca:** el `install.sh` que corre por debajo, cuando un archivo ya existe en tu brain, lo deja como está (no sobreescribe, lo saltea). Así, si editaste tu `CLAUDE.md`, tu identidad, tu `arquitectura-skills.md` o cualquier cosa tuya, tu versión queda. La otra cara, honesta: si una versión nueva mejora un doc que vos ya tenés tocado, **te quedás con el tuyo** (no te lo pisa); si querés traer la versión nueva de ese doc puntual, pedímelo y la copio aparte para que compares. Lo único que el número de versión sube es el del motor global.

## Cuándo NO usar
- Para actualizar tus propios proyectos (esto es solo el kit).
- Si no hay red: avisá que no pudiste chequear y frená, no inventes una versión.

## Señales de que salió bien
- Sabés si estás al día o no, sin entrar a internet a mano.
- Si actualizó, `~/.claude/skills/second-brain-coach/VERSION` quedó en el número nuevo.
- Nada se bajó sin tu OK; tus cosas quedaron intactas.

<!--
  MIGRACIÓN — la guía que seguís VOS (el coach) cuando la persona quiere traer sus Projects de Claude.
  No es un skill aparte (no clutterea el menú): es un doc tuyo, hermano de tu SKILL.md, que leés cuando
  aparece el caso (b) del Paso 0, o cuando la persona dice "migrá mis proyectos de claude", "traé mis
  projects", "importá mis proyectos de la app", "tengo un montón de proyectos en claude para traer".
-->

# Migración: traer tus Projects de Claude al sistema

## Qué es
Los Projects de la app de Claude están cerrados: no se leen desde acá. Los traemos y convertimos cada uno en la carpeta PARA que corresponde —Proyecto si tiene objetivo y termina, Área si es una responsabilidad que sigue— con su `CLAUDE.md`. Hay dos caminos según cuántos sean.

## Antes de empezar: elegí el camino
- **Pocos (≈5 o menos), o querés revisarlos uno por uno → camino manual.** Es el bueno por defecto: más control, cero espera.
- **Muchos → camino export (bulk).** Pero ojo con los límites del export oficial, porque cambian qué esperar:
  - Es **todo o nada**: no podés exportar un solo Project.
  - **No trae los archivos de conocimiento**: vienen como *referencias*, no como bytes. Los docs los re-bajás/adjuntás a mano.
  - Las conversaciones vienen como nodos encadenados (`parent_message_uuid`), no como charlas legibles: hay que reconstruirlas.
  - Tarda de minutos a horas y el link de descarga vive 24 h.
  - Sirve para traer en bloque **la lista + las instrucciones + el historial**; los docs, no.

## Camino manual (uno por vez)
1. **[LAT]** Pedile que elija UN Project para empezar.
2. **[LAT]** ¿Esto es un **Proyecto** (objetivo + fecha, se termina) o un **Área** (no termina)? Eso decide la carpeta: `1. Proyectos/<nombre>/` o `2. Áreas/<nombre>/`. No asumas Proyecto: muchos Projects de Claude son Áreas.
3. **[DET]** Pedile lo del Project: las custom instructions, los archivos de conocimiento (que los suba o pegue), y —opcional— las conversaciones que quiera conservar.
4. **[LAT]** Armá `<carpeta>/CLAUDE.md` desde la plantilla `plantilla-proyecto.md` (vive con el coach, junto a su `SKILL.md`): el contexto sale de las instructions reescritas a tu voz, más un log de decisiones que arranca hoy.
5. **[DET]** Guardá los archivos de conocimiento en esa carpeta. Si trajo conversaciones, dejalas en `<carpeta>/historial/`.
6. **[LAT]** Mostrale cómo quedó y confirmá antes de pasar al siguiente. No los batchees todos de una.

## Camino export (bulk, para muchos)
1. **[DET]** Decile cómo bajarlo: Claude.ai → Settings → Privacy → **Export data**. Llega por mail (minutos a horas), el link vive 24 h. Que te pase la ruta local del zip.
2. **[DET]** Reconstruir el zip es laburo mecánico → **que lo haga un script chico, no el modelo a ojo.** Escribí/adaptá uno contra ESE zip que: lea `projects.json` (cada Project con su nombre + custom instructions), agrupe `conversations.json` por Project y recorra la cadena `parent_message_uuid` para rearmar cada charla. Emite una carpeta de staging por Project con instructions + historial.
3. **[LAT]** Por cada Project, decidí Proyecto vs Área (PARA). Podés rutear en lote, pero la decisión es tuya, no del script.
4. **[DET]** Por cada uno, generá `<carpeta>/CLAUDE.md` (instructions → contexto + log que arranca hoy) y `<carpeta>/historial/` con las charlas reconstruidas.
5. **[LAT]** Los **docs**: el export no los trae. Listá qué archivos tenía cada Project y avisá cuáles hay que volver a bajar/adjuntar a mano. No los des por migrados.
6. **[LAT]** Repasá 2-3 carpetas a mano (ruteo + contexto) antes de dar por migrado el lote.

## Qué lee y escribe
- **Lee:** lo que el usuario pega/sube, o el zip del export; y `plantilla-proyecto.md` (vive con el coach, junto a su `SKILL.md`).
- **Escribe:** `1. Proyectos/<nombre>/` o `2. Áreas/<nombre>/` con su `CLAUDE.md` (+ `historial/` y los docs).
- **No toca:** proyectos que ya viven en el sistema.

## Cuándo NO usar
- Para proyectos que ya viven en el sistema.
- Para "traer todo de una a `1. Proyectos/`" sin revisar: muchos Claude Projects son Áreas, no Proyectos, y el ruteo importa.

## Señales de que lo hiciste bien
- Cada Project quedó en la carpeta PARA **correcta** (Proyecto si termina, Área si no), con su `CLAUDE.md`.
- El contexto (las instructions) no se perdió en la traducción: está en el `CLAUDE.md`, en tu voz.
- Los archivos de conocimiento están **físicamente** en la carpeta, no como links muertos del export.
- Revisaste muestras de a uno, no diste por bueno un batch a ciegas.

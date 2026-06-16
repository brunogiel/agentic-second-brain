---
name: evaluar-skill
description: >
  Evalúa un skill contra su propio SKILL.md y propone mejoras concretas (no las aplica). Lee el
  SKILL.md como rúbrica, mira el output de la última corrida real, juzga criterio por criterio
  con cita textual, y deja las propuestas en un archivo de mejoras. Usalo cuando el usuario diga
  "evaluá el skill X", "este skill salió flojo", "revisá la última corrida de Y", "¿este skill
  cumple lo que promete?", "auditá mi skill".
---

# evaluar-skill — chequear que un skill cumpla lo que promete

## Qué es
Cada `SKILL.md` es una promesa ("este procedimiento cumple X, Y, Z"). Las corridas reales son la prueba. Sin un chequeo, los skills se pudren callados: lo que prometen deja de pasar y nadie se entera. Esto agarra una corrida y la mide contra la rúbrica del propio skill. Propone, no toca. Sirve sobre todo cuando ya tenés varios skills y querés mantenerlos afilados.

## Cuándo SÍ / Cuándo NO
- **SÍ:** un skill que ya corrió y querés saber si cumplió su rúbrica; uno que "viene saliendo flojo".
- **NO:** un skill que nunca corrió (no hay output que medir); querés una opinión abierta sin rúbrica (eso es otra cosa); querés APLICAR las mejoras (esto solo propone — vos aplicás, o se las pasás a `crear-skill`).

## Parámetros
| Param | Req | Qué es |
|---|---|---|
| `skill` | Sí | Nombre del skill a evaluar. Resuelve el path en `skills/<skill>/`. |
| `output` | Sí | Cómo encontrar la corrida: path a un archivo, o texto pegado (`text:...`). |
| `criterios_extra` | No | Chequeos puntuales de esta corrida que no salen del SKILL.md. |

## Qué lee y escribe
- **Lee:** `skills/<skill>/SKILL.md` (la rúbrica) + el output de la corrida.
- **Escribe:** SOLO `skills/<skill>/mejoras.md` (las propuestas, acumulativas). NUNCA toca el `SKILL.md` evaluado ni el output.

## Flujo
1. **[DET]** Encontrá el `SKILL.md` del skill. Si hay varios o ninguno, preguntá.
2. **[LAT]** Sacá la rúbrica: listá los criterios del SKILL.md por tipo — regla dura ("NUNCA/SIEMPRE"), formato de output, señales de éxito, cuándo NO usar. Si no hay NINGUNO → rúbrica vacía: una sola propuesta ("agregá Señales de éxito") y avisá. No inventes criterios.
3. **[DET]** Conseguí el output de la corrida (path o texto pegado).
4. **[LAT]** Juzgá criterio por criterio: cumple **sí / no / no aplica**, con **cita textual** del output como prueba (nunca parafrasees la evidencia).
5. **[LAT]** Por cada "no", redactá una propuesta concreta que apunte a UNA sección del SKILL.md. Buena: *"Agregá a Reglas: 'no repetir el deadline si ya está en la línea 1'"*. Mala: *"ser más prolijo"*.
6. **[DET]** Guardá en `skills/<skill>/mejoras.md`: una fila por criterio fallido. Si ya existe esa fila, sumale una muestra; a las 3 muestras marcala `⚠ reincidente`.

## Output esperado
```
## Eval de <skill>
- Criterios evaluados: N · Fallidos: M
- Propuestas: K (nuevas / repetidas) · Reincidentes ⚠: <lista o "ninguno">
Archivo actualizado: skills/<skill>/mejoras.md
```

## Reglas duras
1. Solo propone, NUNCA aplica. Prohibido tocar el SKILL.md evaluado o el output.
2. Una sola pasada por corrida (sin loops).
3. Evidencia siempre con cita textual del output.
4. Rúbrica vacía → no inventes criterios: proponé agregarlos.

## Señales de que lo hiciste bien
- Cada criterio del SKILL.md tiene un veredicto (sí/no/n.a.) con una cita que lo prueba.
- Cada propuesta apunta a UNA sección concreta, no a un "mejoralo".
- `mejoras.md` quedó con las filas nuevas o las muestras sumadas.
- No tocaste el skill ni su output.

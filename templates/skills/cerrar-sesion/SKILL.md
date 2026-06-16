---
name: cerrar-sesion
description: >
  Cierra la sesión capturando qué pasó: deja el tablero y el log al día y anota el próximo paso,
  para que la próxima sesión arranque sabiendo. Usalo cuando el usuario diga "cerremos",
  "terminamos por hoy", "cerrá la sesión", "guardá dónde quedamos", "listo por hoy", "anotá esto y seguimos".
---

# cerrar-sesion: que tu juicio se acumule

## Qué es
El cierre del ciclo de captura, y lo que hace que el sistema sea más vos con el uso: el modelo
arranca de cero cada vez, tus archivos no. Si no capturás al cerrar, la próxima sesión vuelve a
adivinar. Esto te fuerza (suave) a dejar registro en 30 segundos.

## Flujo
1. **[LAT]** Resumí en 2-3 líneas qué se hizo y qué se decidió en la sesión. Mostráselo para confirmar.
2. **[DET]** Actualizá `ESTADO.md`: "Última vez: <qué pasó> (fecha)" y, si cambió, proyectos activos.
3. **[DET]** Si hubo una decisión importante, appendeá UNA línea al log del proyecto activo
   (`1. Proyectos/<proyecto>/CLAUDE.md`, sección "Decisiones"): `AAAA-MM-DD: <qué y por qué>`.
4. **[DET]** Dejá el **próximo paso** en una línea (en `ESTADO.md` y/o en el proyecto): qué sigue y
   con qué contexto, para que `abrir-sesion` lo levante mañana. Este es el "handoff" a tu yo futuro.
5. **[LAT]** Si apareció algo que vale para todo (no para este proyecto), ofrecé guardarlo en
   `MEMORIA.md`. Con tu OK, no por las tuyas.

## Qué lee y escribe
- **Escribe:** `ESTADO.md` (siempre), el log del proyecto activo (si hubo decisión), `MEMORIA.md`
  (solo con OK). No toca nada más.

## Cuándo NO usar
- Para una tarea puntual a mitad de sesión: esto es el cierre, no un guardado constante.

## Señales de que salió bien
- `ESTADO.md` quedó con "última vez" + "próximo paso" frescos.
- La decisión del día (si la hubo) quedó en una línea del log, no en tu cabeza.
- Mañana, `abrir-sesion` te va a poder briefear sin que reconstruyas nada.

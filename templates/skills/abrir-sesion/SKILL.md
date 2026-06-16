---
name: abrir-sesion
description: >
  Arranca una sesión de trabajo leyendo el estado del sistema y briefeando al usuario antes
  de empezar, para no arrancar de cero. Usalo cuando el usuario diga "arranquemos", "abrí la
  sesión", "¿en qué estaba?", "retomemos", "buenas, ¿dónde quedé?", "¿qué tengo pendiente?".
---

# abrir-sesion: retomar sabiendo dónde quedaste

## Qué es
El comienzo del ciclo de captura. En vez de arrancar en frío, el asistente lee tu estado y te
pone al día en 3 líneas. Es la otra mitad de `cerrar-sesion`: lo que aquél guardó, este lo levanta.

## Flujo
1. **[DET]** Leé `ESTADO.md` (es chico): nivel, modo, proyectos activos, "última vez" y "próximo paso".
2. **[DET]** Si hay un proyecto activo o el usuario nombra uno, leé SOLO el log reciente de su
   `CLAUDE.md` (las últimas decisiones + el "próximo paso"), no todo el árbol.
3. **[LAT]** Briefealo corto, máximo 3 líneas: dónde quedaste, qué estaba pendiente, qué sigue.
   No vuelques todo: el resumen es para orientar, no para abrumar.
4. **[LAT]** Preguntá con qué quiere arrancar (proponé el "próximo paso" guardado como default).

## Qué lee y escribe
- **Lee:** `ESTADO.md` y, si aplica, el `CLAUDE.md` del proyecto activo. **No escribe nada.**

## Cuándo NO usar
- Si el usuario ya te pidió una tarea concreta: hacela, no lo frenes con un brief.
- Si recién instaló y no hay estado todavía: ahí va el coach, no esto.

## Señales de que salió bien
- El usuario sabe en 3 líneas dónde está, sin que hayas leído todo el sistema.
- Arrancan por algo concreto, no por "¿en qué estábamos?".

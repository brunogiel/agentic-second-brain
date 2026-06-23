---
description: Chequeo de salud de tu segundo cerebro: revisa que el mapa, los proyectos y las skills sigan alineados. Propone, no toca nada.
---

Corré un chequeo de salud del SABE de la carpeta actual (o lo que pidan en $ARGUMENTS). Seguí esto:

# auditar-sistema: la revisión de salud

## Qué es
Una pasada que mira si tu sistema sigue ordenado y te deja una lista corta de arreglos. Propone, no toca nada sin tu OK. Liviano: chequea estados, no lee todo el contenido.

## Qué lee y escribe
- **Lee:** estados, no contenido completo: existencia de archivos, si tienen `<...>` sin llenar, conteos de carpetas, fechas de última modificación de los logs, las filas de la tabla "Mis skills" y "Atajos".
- **Escribe:** NADA en la corrida. Solo después de tu OK, en otra pasada, toca lo que aprobaste ítem por ítem.

## Flujo
0. **[DET]** ¿Hay sistema todavía? Antes de auditar nada, mirá si hay un brain: un `CLAUDE.md` de proyecto, carpetas PARA (`1. Proyectos`, `2. Áreas`...), skills tuyos. Si lo único que hay es el kit read-only del método (sin proyecto, sin carpetas tuyas), todavía no hay nada que auditar. No audites ni escribas, y NUNCA toques el `kit/brain/` del método. Decílo claro: "todavía no tenés un sistema para auditar; lo armamos con `/sabe-coach` y volvemos a correr esto". Frená acá.
1. **[DET]** Chequeos baratos:
   - ¿`sobre-mi` / `como-trabajo` siguen con `<...>` o están al día?
   - Proyectos con el log de decisiones viejo (hace mucho que no se tocan).
   - Tabla de atajos: ¿apunta a carpetas que existen? ¿falta algún proyecto nuevo?
   - Tabla "Mis skills": ¿cada skill listado existe en `skills/`? ¿hay skills en `skills/` sin fila (no se disparan)?
   - Proyectos terminados que deberían ir a `4. Archivo/`.
   - ¿`ESTADO.md` refleja la realidad?
2. **[LAT]** Armá el reporte con el formato fijo de abajo (semáforo: verde sano / amarillo conviene tocar / rojo roto o viejo).
3. **[LAT]** Proponé de 3 a 5 arreglos concretos, priorizados, incrementales (1 fila, 1 sección, no reorganización masiva). Esperá el OK para cada uno.

## Output esperado (formato fijo)
```
## ✅ Sin cambios necesarios     ← obligatoria, aunque sea 1 ítem (lo sano se reporta como sano)
- {qué está bien}

## ⚠️ Cambios propuestos          (por área, con semáforo 🟡/🔴)
- 🟡 {qué + el arreglo concreto}

## ❓ Dudas                        (lo ambiguo va acá, no inventes la respuesta)
- {pregunta}

---
¿Aplico estos cambios? Decime qué sí y qué no.
```

## Reglas duras
1. NUNCA tocás nada sin un OK explícito, ítem por ítem.
2. El reporte SIEMPRE cierra con "¿Aplico estos cambios? Decime qué sí y qué no."
3. Propuestas incrementales por default; nada de reordenar todo de una.

## Cuándo NO usar
- Para crear cosas nuevas o subir de nivel: eso es el coach.
- Como excusa para reordenar todo de una: proponé de a poco.

## Señales de que lo hiciste bien
- [ ] El reporte tiene la sección "✅ Sin cambios necesarios" (lo sano se nombra, no se omite).
- [ ] Cada propuesta es concreta e incremental (1 fila / 1 sección), no genérica.
- [ ] Cerró con la pregunta de aprobación.
- [ ] No tocaste nada sin OK.

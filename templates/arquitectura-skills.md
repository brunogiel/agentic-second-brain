# arquitectura-skills.md

> Tu referencia para armar skills que funcionen: cuándo conviene uno, cómo se escribe, y los errores que casi todos cometen. Tenelo a mano cuando uses `crear-skill` o cuando quieras revisar uno viejo. Es un Recurso: no se lee de corrido, venís cuando lo necesitás.

## Qué es un skill (y qué no)
Un skill es una receta guardada: instrucciones que tu asistente sigue cuando una frase lo dispara. Mientras nadie lo llama, no hace nada. Por eso podés tener muchos sin que molesten.
No es: un lugar para guardar datos (eso son tus archivos), ni algo que corre solo (eso es una rutina).

## Cuándo crear uno: la regla de 3
¿Le pediste lo mismo 3 veces? Ahí sí. Antes es prematuro: un skill para algo que hacés una vez es laburo al pedo.

## El principio: harness fino, skill gordo
Toda la inteligencia vive en el `SKILL.md`, no en mil instrucciones sueltas que repetís cada vez. El asistente (el harness) queda fino; el skill, gordo. Así no te repetís y el skill mejora en un solo lugar.

## DET vs LAT: separá lo mecánico de lo que pide criterio
- **DET (determinístico):** mecánico, siempre igual. "Abrí este archivo", "sumá la columna C". Conviene clavarlo exacto, o que lo haga un script.
- **LAT (latente):** pide criterio. "Elegí el mejor título", "escribí en mi tono". Ahí le das contexto y libertad, no una receta rígida.

Marcá cada paso `[DET]` o `[LAT]`. El error del principiante es tratar todo como LAT ("hacelo lindo") o todo como DET ("seguí estos 40 pasos"). Cuando separás, tus skills se vuelven confiables.

## Anatomía mínima de un skill que funciona
Un `SKILL.md` en una carpeta, con:
- **Descripción con frases reales** que lo disparan (no "hace reportes", sino "cargá la factura", "subí el resumen"). Eso es lo que hace que se dispare solo. Escribila en **tercera persona** ("Arma un reporte… Usalo cuando el usuario diga…"), no en segunda ("te ayuda a…"): es lo que recomienda la doctrina oficial de skills, porque la descripción se inyecta en el system prompt y el punto de vista mezclado confunde el disparo.
- **Nombre** en minúscula-con-guiones, idealmente en gerundio (`armando-reportes`, `redactando`), sin las palabras `claude` ni `anthropic` (están reservadas).
- **Contexto en 2 líneas:** qué hace y para quién, en términos de tu trabajo.
- **Cuándo SÍ y cuándo NO** usarlo. El *cuándo NO* pesa más que el *cuándo SÍ*: es lo que evita que el skill secuestre charlas que no le tocan.
- **Pasos marcados `[DET]` o `[LAT]`.**
- **Qué archivos lee y escribe.**
- **Cómo se ve un buen resultado:** qué devuelve + 2 o 3 señales de que salió bien.

## Errores típicos (esquivalos)
- **Clonar un skill cambiando un dato:** parametrizá, que tome el dato como entrada.
- **Pedirle al modelo cuentas grandes:** contar o cruzar muchas filas es script (DET), no criterio.
- **Mega-skill:** si una parte sirve para varias cosas, sacala a su propio skill chico y reusala.
- **Sin señales de éxito:** si al terminar no sabés si salió bien, falta definirlo.
- **Hornear el tono adentro del skill:** la voz ya vive en tu identidad (`soul`/`como-trabajo`/`mi-estilo`) y dispara junto. El skill maneja el *proceso* (estructura, pasos, formato); el tono lo pone tu identidad. No los dupliques.

## Si no se dispara (el debug más rápido)
Tenés el skill pero no se activa cuando lo llamás. Preguntale al asistente: *"¿cuándo usarías el skill X?"*. Te recita la descripción tal cual la entiende, y ahí ves al toque qué está vago, qué falta o por qué matchea otra cosa. El problema de un skill que no engancha casi siempre vive en las **frases de la descripción**, no en los pasos. (Distinto de `evaluar-skill`, que mide la *calidad* de una corrida que ya pasó; esto arregla que ni arranque.)

## Skill vs rutina vs orquestador (para cuando crezcas)
- **Skill:** receta, corre con vos presente, puede preguntarte.
- **Rutina:** corre sola, en horario, sin que estés.
- **Orquestador:** no hace el trabajo, coordina a otros skills y junta los resultados.

Empezás con skills. Lo demás viene después, cuando una tarea ya no te necesita ahí.

## Cómo se arma un orquestador (Nivel 5)
Un orquestador es un skill que NO hace el trabajo: reparte y junta. El patrón:
1. **Parte el trabajo** en pedazos independientes (por archivo, por tema, por lente).
2. **Reparte:** llama a otros skills en orden (orquestador con estado, arrastra contexto entre pasos) o lanza subagentes en paralelo, cada uno con su pedazo y su contexto limpio (multi-agente).
3. **Junta:** toma los resultados y los sintetiza en una sola salida.

Reglas: el coordinador queda fino (decide qué se reparte y cómo se junta); el laburo pesado vive en los skills/subagentes que llama. Paralelo solo cuando los pedazos son de verdad independientes; si cada paso necesita el anterior, es secuencial. Se aprende igual que un skill: usás uno de ejemplo (el de PPT) para ver el patrón y después armás el tuyo. El multi-agente brilla cuando una decisión necesita varias miradas (ver `council`: 4 lentes + síntesis).

## Dónde viven (y cómo se disparan)
Los skills que usás viven en **`skills/`** de tu SB, a secas y a la vista (los ves, los abrís, aprendés cómo están). Lo que los dispara es **la tabla "Mis skills" de tu `CLAUDE.md`**: el asistente lee el `CLAUDE.md` al arrancar y, cuando decís una frase que matchea una fila (frase → skill), sigue ese `skills/<nombre>/SKILL.md`. Por eso andan **igual en Claude Code, Cowork y Codex** (los tres leen el `CLAUDE.md`; en Codex vía `AGENTS.md`), sin carpetas ocultas ni nada específico de un harness.

Regla de oro: **un skill sin su fila en la tabla no existe para el asistente.** Cuando sumás uno (de uso del kit o propio), anotalo en "Mis skills" con su frase gatillo. El frontmatter del `SKILL.md` afina cómo y cuándo dispara; la fila es lo que lo pone en el radar.

No van en `3. Recursos/`: ahí va material de referencia (como este mismo archivo), no las capacidades. Los skills son infraestructura del agente, por eso viven en `skills/`, no dentro de PARA.

Aparte queda el **motor de armado** (el coach, `actualizar`, `migrar`): vive global e invisible en `~/.claude/skills/`, se llama por nombre y no aparece en tu `skills/`. Y las **versiones-fuente** de los skills de uso (el catálogo) viven ocultas en `.secondbrain/skills-disponibles/`: el coach copia de ahí a `skills/` cuando adoptás uno.

## Checklist antes de dar por hecho un skill
- [ ] ¿Se dispara con frases reales tuyas?
- [ ] ¿Cada paso está marcado `[DET]` o `[LAT]`?
- [ ] ¿Dice qué archivos toca?
- [ ] ¿Tiene 2-3 señales de éxito?
- [ ] ¿Lo mecánico lo hace un script, no el modelo adivinando?
- [ ] ¿El `SKILL.md` es corto y enfocado? Si crece mucho, lo pesado (ejemplos largos, tablas, referencia) va a un archivo aparte en la misma carpeta que el skill lee solo cuando hace falta (divulgación progresiva, un nivel de profundidad — no archivos que apuntan a archivos que apuntan a archivos).

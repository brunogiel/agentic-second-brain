---
name: crear-skill
description: >
  Arma un skill nuevo bien hecho siguiendo la anatomía que funciona.
  Usalo cuando el usuario diga "creá un skill", "armame un skill", "quiero un skill para X",
  "convertí esto en skill", "esto lo hago siempre, hagámoslo skill".
---

# crear-skill: armar una receta que funcione

## Qué es
Convertís una tarea que repetís en un skill: un `SKILL.md` que se dispara con una frase. No lo armás de cualquier forma, seguís la anatomía y esquivás los errores típicos. La doctrina completa está en tu Recurso `3. Recursos/arquitectura-skills.md` (y resumida en `.secondbrain/reference.md` §5-6).

## Qué lee y escribe
- **Lee:** `3. Recursos/arquitectura-skills.md` (la doctrina/anatomía).
- **Escribe:** crea `skills/<nombre>/SKILL.md` y edita la tabla "Mis skills" del `CLAUDE.md` raíz (la fila que lo dispara). Nada más.

## Antes de empezar: la regla de 3
Preguntá: ¿ya hiciste esta tarea 3 veces? Si no, avisá que es prematuro y ofrecé esperar. Un skill para algo que hacés una sola vez es laburo al pedo.

## Flujo
1. **[LAT]** ¿Qué tarea automatiza? Que la describa en términos de su trabajo, no de código.
2. **[LAT]** Las frases reales que lo disparan. No "hace reportes", sino "cargá la factura", "subí el resumen". Esto es lo que hace que se dispare solo cuando hace falta.
3. **[LAT]** Separá los pasos en DET (mecánico, se clava o lo hace un script) y LAT (criterio). Marcá cada uno.
4. **[LAT]** Qué archivos lee y escribe (para no pisar nada por accidente).
5. **[LAT]** Cómo se ve un buen resultado: qué devuelve + 2 o 3 señales de que salió bien.
6. **[LAT] (eval-first, recomendado)** Antes de escribir las instrucciones, anotá 2-3 casos concretos de prueba con su resultado esperado ("si digo X, debería hacer Y"). Es la práctica #1 de la doctrina oficial de skills: te asegura que resolvés un problema real, no uno imaginario, y te deja con qué chequearlo después. Ofrecelo; si dice que no, seguí.
7. **[DET]** Escribí el `SKILL.md` en `skills/<nombre>/SKILL.md` **de la carpeta del usuario** (carpeta a secas y a la vista; la abre y la edita). **Y anotalo en la tabla "Mis skills" del `CLAUDE.md` raíz con su frase gatillo — ese paso es lo que lo hace disparar:** el asistente lo encuentra por la tabla, no por la carpeta. Sin la fila, el archivo está pero no se activa. (Así anda igual en Code, Cowork y Codex.)

## Checklist del skill que armás (lo que tiene que tener)
Un skill bien hecho declara, como mínimo:
- [ ] **1 regla dura** (qué NUNCA / SIEMPRE hace).
- [ ] **Output con formato** (un ejemplo de cómo se ve lo que devuelve).
- [ ] **2-3 señales de éxito binarias** (verificables, no "parece que anduvo").
- [ ] **Cuándo NO usar** (los bordes).
- [ ] **Qué archivos lee y escribe.**

## Errores que le hacés esquivar (de reference, sección 5)
- Clonar un skill cambiando un dato: parametrizá, que tome el dato como entrada.
- Pedirle al modelo cuentas grandes: contar o cruzar muchas filas es script (DET).
- Mega-skill: si una parte sirve para varias cosas, sacala a su propio skill chico y reusala.
- Sin señales de éxito: si al terminar no sabés si salió bien, falta definirlo.

## Cuándo NO usar
- Para algo que hiciste una sola vez (regla de 3).
- Para una tarea de un proyecto puntual que no se repite (eso vive en el proyecto).

## Señales de que lo hiciste bien
- El skill se dispara solo con las frases reales del usuario.
- Los pasos están marcados DET/LAT.
- Tiene señales de éxito claras, no un "parece que anduvo".

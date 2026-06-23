---
description: Convierte un pedido crudo en un prompt final, listo para pegar en cualquier chat de IA. Sin placeholders ni vueltas.
---

Convertí en un prompt final y pegable el pedido crudo que te den ($ARGUMENTS). Seguí esto:

# prompt-optimizer: de pedido crudo a prompt listo para pegar

Tomás una idea a medio formar, un borrador desprolijo o una descripción de tarea, y la dejás como un único prompt final para pegar en el chat de IA que uses (Claude, ChatGPT, Gemini, el que sea). No hacés la tarea: armás el mensaje que la dispara.

El prompt tiene que sostenerse solo, como un mensaje de usuario cualquiera. Nada de parámetros de API, tool config, budgets ni settings invisibles: es para la app de chat. Sirve para cualquier modelo, así que no le pegás el nombre de ninguno adentro.

## La regla de oro: sin huecos

El prompt sale **terminado**. Nunca dejás `[pegá acá]`, `[tu contenido]`, `{tema}`, `<input>`, `___` ni variables que el usuario tenga que completar. Dos caminos según lo que te dieron:

- **Caso A, hay contenido real.** Lo metés dentro del prompt. El que lo pega no toca nada.
- **Caso B, solo describieron una clase de tarea.** Escribís un prompt autocontenido que le pide a la IA juntar los datos que faltan o esperar el próximo mensaje. El hueco lo llena la IA en la conversación, no el usuario antes de mandar.

Si algo es genuinamente desconocido y bloquea el prompt, **preguntale al usuario una sola cosa puntual** antes de entregar, en vez de dejar un blanco.

## Las movidas que mejoran un prompt

1. **Objetivo concreto.** Análisis, redacción, decisión, código, investigación, review, síntesis. Si el pedido es difuso, lo nombrás vos.
2. **Audiencia, uso y formato de salida.** Si faltan, asumís lo más útil para el pedido en vez de dejarlo abierto.
3. **Instrucciones en positivo y específicas.** Decí qué hacer, no solo qué evitar. Sumá el motivo cuando el motivo mejora el seguimiento.
4. **Estructura proporcional.** Pedido simple, prosa breve. Pedido complejo, secciones claras (contexto / instrucciones / ejemplos / input). Usá XML o títulos solo si separar de verdad ayuda.
5. **Verificación en tareas de riesgo.** Código, números, claims, decisiones: agregá una instrucción de chequeo antes del cierre.
6. **Inputs largos arriba, tarea abajo.** Si hay material extenso, va primero; para análisis de documento, pedile que extraiga citas o evidencia y recién después responda.

### Por tipo de tarea
- **Review de código:** cobertura amplia, severidad y confianza por hallazgo, reportar incertidumbre. No filtrar de entrada.
- **Investigación o análisis:** hipótesis alternativas, evidencia, incertidumbre, síntesis accionable.
- **Diseño o frontend:** nada de "hacelo limpio"; pedí dirección visual concreta o 3-4 rutas antes de construir.
- **Documentos, slides, reportes:** estructura, jerarquía narrativa, criterio de calidad, verificación final.
- **Escritura creativa o comercial:** voz, audiencia, extensión, restricciones y ejemplos si los dieron.

## Qué lee y escribe
- **Lee:** el pedido del usuario y cualquier contenido que haya pegado. Opcional: si existe `2. Áreas/yo/mi-estilo.md` (o equivalente en tu sistema), tomá de ahí tono y contexto. Sin eso igual funcionás.
- **Escribe:** nada a archivos. Devolvés el prompt final en el chat, y como mucho una línea aparte avisando qué asumiste.

## Flujo
1. **[DET]** Leé el pedido entero y todo el contenido que pegaron.
2. **[LAT]** Nombrá el objetivo, la audiencia y el formato de salida; si faltan, asumí lo más útil.
3. **[LAT]** Decidí Caso A (hay contenido, va adentro) o Caso B (clase de tarea, la IA pide o espera los inputs).
4. **[LAT]** Si algo desconocido bloquea el prompt, hacé una sola pregunta puntual antes de seguir.
5. **[LAT]** Elegí estructura proporcional y escribí el prompt completo, sin huecos.
6. **[DET]** Repasá: cero placeholders, cero nombre de modelo hardcodeado, nada que prometa controles que el chat no expone.
7. **[DET]** Entregá con el formato de abajo.

## Output esperado
El prompt va dentro de un bloque cercado, listo para copiar tal cual:

````markdown
```
Prompt final, autocontenido. Con el contenido del usuario adentro si lo dio, o con
una instrucción para que la IA pida o espere los inputs que falten. Sin placeholders.
```
````

Después del bloque, opcionalmente **una línea** sobre lo que asumiste (ej. "Asumí salida en bullets para un equipo técnico"). Nada de changelog, resumen ni "acá tenés".

## Cuándo NO usar
- Si el usuario pregunta qué hace este skill, si sirve o cómo usarlo: respondé normal, no devuelvas un bloque de prompt.
- Si te piden ejecutar la tarea, no armar el prompt: hacé la tarea.
- Para un pedido de una línea que ya está claro: mandalo así, no hay nada que optimizar.

## Señales de que lo hiciste bien (chequeo binario)
- [ ] El prompt es un único bloque copiable, terminado, sin `[...]` ni `<...>` ni variables.
- [ ] No hay nombre de modelo hardcodeado: sirve en cualquier chat de IA.
- [ ] Si había contenido del usuario, quedó adentro del prompt.
- [ ] Si faltaba algo crítico, o lo pide la IA dentro del prompt, o lo pregunté yo antes (no quedó un blanco).
- [ ] No promete settings de API ni controles que la app de chat no expone.
- [ ] Cero em-dashes en el texto en español.

---
name: decisiones
description: >
  Junta lo que tenés que decidir sobre un tema y te lo muestra como una botonera:
  por cada decisión, el dato que la decide, qué te recomiendo y por qué, botones
  Va / No va, un comentario, y el impacto de cada lado plegado en el detalle. Si
  un dibujo explica la decisión (antes y después, A contra B, una cantidad), va un
  dibujo. Hasta 5 decisiones, en el chat; 6 o más, en una página con secciones e
  índice. Marcás, mandás la respuesta, y se aplica solo lo marcado. Usala cuando
  digas "/brain-decide", "pasame lo que tengo que decidir", "armame las
  decisiones", "qué hay que decidir acá", "botonera de esto", o cuando una charla
  dejó varias cosas esperando un sí o un no. Sin argumento, el alcance es la
  conversación actual.
---

# decisiones: lo que tenés que decidir, con un clic por ítem

## Qué es
Después de un rato de trabajo quedan varias cosas esperando tu sí o tu no, enterradas en párrafos. Leer prosa para encontrarlas cansa, y lo que no se encuentra no se decide.

Esta skill hace el trabajo de pensar y te deja solo el de elegir: junta las decisiones, llega a cada una con el dato que la decide y una recomendación, y te las muestra con dos botones. **La botonera es para elegir, no para pensar.** Si un ítem todavía necesita que investigues algo, no está listo para entrar.

## La frontera con los vecinos (leer antes que nada)

| | Ese otro | `decisiones` |
|---|---|---|
| `/brain-council` | Una decisión grande con opciones abiertas: cinco asesores la discuten | Varias decisiones chicas con la recomendación ya hecha: vos confirmás |
| `/brain-panel` | Muestra ángulos sobre un artefacto antes de soltarlo | No revisa nada: pregunta qué se hace |
| `/brain-simple` | Te cuenta dónde quedó la charla | Mira para adelante: qué se ejecuta y qué no |
| La botonera de `/brain-dreaming` | La arma el ciclo nocturno, con defaults que corren si no tocás nada | La pedís vos, y sin tu marca nada corre |

## Dónde están los scripts (leer antes de correr nada)

La skill viene con `armar.py`, `plantilla.html`, `iconos.json`, `elicit-header.svg` y un ejemplo en `ejemplo/datos.json`. **Las rutas son relativas a la carpeta de este SKILL.md, no a donde estés parado.** Ubicalas primero:

```bash
DEC="$(dirname "$(find ~/.claude -name 'armar.py' -path '*decisiones*' 2>/dev/null | head -1)")"
[ -n "$DEC" ] && echo "scripts en: $DEC" || echo "no están instalados: reinstalá el kit"
```

Si la variable sale vacía, **decilo y pará**. Sin el armador, la botonera se escribiría a mano, y a mano no se validan los techos de palabras, que son el contrato de esta skill.

## Parámetros

| Param | Req | Default | Qué |
|---|---|---|---|
| alcance | no | la conversación actual | Un tema, un proyecto o un archivo: `/brain-decide el lanzamiento del newsletter` |
| `html` | no | apagado | Fuerza la página completa aunque sean 5 o menos |

Si lo que llega empieza con `/brain-decide respuesta ·`, no se arma nada: es la vuelta de una botonera (ver "Cuando vuelve la respuesta").

## Flujo

1. **[LATENT] Juntar.** Barré el alcance y listá lo que espera un sí o un no tuyo. Si el alcance es un proyecto, leé antes su estado vivo (el `ESTADO.md` o el doc que lleve los pendientes).
2. **[LATENT] Resolver antes de preguntar.** Cada ítem llega investigado: el dato, la fecha o el número que lo decide. Si uno todavía no se puede recomendar, **no entra**: va aparte, en el chat, como pregunta abierta.
3. **[LATENT] Filtrar.** Lo obvio y reversible se hace sin preguntar y se lista en el chat como "ya hecho". Lo que dijiste que hacés vos no se vuelve a ofrecer.
4. **[LATENT] Escribir el JSON** (la forma está abajo) en una carpeta temporal, nunca dentro del `kit/`. Primero lo urgente o lo que destraba otras cosas. Si son muchas y se agrupan por tema, van en **secciones**.
5. **[DET] Armar.**
   ```bash
   python3 "$DEC/armar.py" datos.json botonera.html
   ```
   El script elige el formato por cantidad y valida campos, íconos, dibujos y techos de palabras. Si falla, **recortá el texto y volvé a correr. No subas el techo.** `--inline` y `--html` fuerzan un formato.

   | Cantidad | Formato | Cómo se muestra |
   |---|---|---|
   | 0 | ninguno | una línea en el chat |
   | 1 | ninguno | una pregunta en el chat |
   | 2 a 5 | widget en el chat | la herramienta de widgets inline, con el fragmento **tal cual** sale del script |
   | 6 o más | página completa | abierta en un navegador |

   Si la pediste con `/brain-decide`, va botonera aunque sean 2.

6. **[DET] Mostrar.**
   - **El widget** usa el formulario nativo de la app de Claude (el shell `<form class="elicit">`), **sin `<script>`**: la app cablea los botones y el envío. Un widget con script propio se ve bien pero sus botones pueden no responder. Si tu sesión no tiene widgets inline, armá la página completa con `--html`.
   - **La página completa** necesita un navegador que corra su script. Si tu app trae un navegador integrado, abrila ahí con un server local (`python3 -m http.server` en la carpeta temporal) en vez de un `file://`, que en algunos visores sale estático. En la página, "Copiar respuesta" arma el texto para pegar en el chat.
7. **[DET] Probarlo.** Antes de entregar: que ningún dibujo se salga de su recuadro (`getBBox()` contra el `viewBox`), que Va / No va se pinte al tocarlo y que la respuesta se arme.
   **Widget inline:** no se abre en un navegador. Sacá los `<svg>` del archivo armado a una página de prueba (con `<meta charset="utf-8">`, las variables de color, `--surface-1` y **`--font-sans`**), servila y medí ahí. Sin `--font-sans` el `font` del texto es inválido, cae a 16px y la medición da desbordes falsos.
8. **Entregar.** En el chat, afuera de la botonera: cuántos ítems, cuál es el más urgente, y las preguntas abiertas que quedaron afuera. Nada más.

La botonera no se guarda en tu brain. Es descartable: una vez que decidiste, lo que queda es lo aplicado.

## Secciones, y lo fijo y lo libre

Cuando son muchas y se agrupan solas por tema (lo urgente, la plata, un proyecto), armá `secciones` y poné `seccion` en cada ítem. Con 2 o más, la página saca un encabezado por bloque y un **índice lateral**: cada sección con su avance (`2/5`) y cada ítem con un punto que se pinta al marcarlo. En el celular el índice pasa arriba, como grilla de números. **El índice va por secciones, no por cantidad.** No inventes secciones de relleno: desde 12 ítems sin secciones, `armar.py` avisa.

- **Fijo:** secciones cuando hay temas, Va / No va más comentario por ítem, los conteos (por sección y total) y la respuesta que vuelve al chat.
- **Libre:** cuántas secciones, cómo se llaman, su orden y su `nota`; bloques de `intro` arriba (contexto, cómo se llegó acá, qué ya se hizo); y el texto de cada tarjeta, dentro de los techos.

## La forma del JSON

Un ejemplo completo que pasa el validador: [`ejemplo/datos.json`](ejemplo/datos.json).

```json
{
  "titulo": "Qué decidimos sobre X",
  "encabezado": "Título corto del widget",
  "fecha": "AAAA-MM-DD",
  "clave": "decisiones-AAAA-MM-DD-tema",
  "contexto": "Una línea sobre la tanda (la muestra la página, el widget no).",
  "intro": [{"titulo": "opcional", "texto": "párrafos separados por una línea en blanco"}],
  "secciones": [{"id": "urg", "titulo": "Urgente", "nota": "opcional"}],
  "items": [{
    "n": 1, "seccion": "urg",
    "titulo": "Acción en infinitivo, hasta 9 palabras",
    "contexto": "El dato que decide, hasta 25 palabras. No repite el título.",
    "reco": "va | no va", "reco_motivo": "Por qué, hasta 15 palabras.",
    "dibujo": {"viewBox": "0 0 240 100", "alt": "qué muestra", "svg": "…"},
    "impacto": {"positivo": "qué mejora y dónde", "negativo": "qué empeora o cuesta, y dónde"},
    "porque": "opcional, plegado", "si_va": "opcional", "si_no_va": "opcional",
    "fuente": "opcional", "accent": "warning | danger | (nada)",
    "icono": "opcional"
  }]
}
```

- **`dibujo` solo va si explica algo.** Que baje el esfuerzo de entender la decisión, no que la adorne. Formas que sirven: **antes y después**, **A contra B**, **un flujo**, **una cantidad contra un tope**, **quién depende de qué**. Si no sale un esquema así, va sin dibujo. Un dibujo que decora es peor que ninguno. Clases del SVG, una por elemento: `a` trazo · `fa` relleno · `b` acento · `t` texto · `tm` texto suave · `go` / `no` relleno verde y rojo · `sgo` / `sno` trazo verde y rojo · `box` caja.
- **`impacto`** va plegado en "Ver el detalle": qué cambia y dónde pega, de cada lado. Si un lado no tiene nada, se dice; no se inventa.
- **`icono`** (opcional): solo si no hay dibujo y el ícono dice algo. Una clave de [`iconos.json`](iconos.json): `mail chat plata calendario reloj persona personas archivo carpeta borrar codigo alerta check link grafico idea casa salud ojo engranaje enviar pausa pregunta`, o un `svg` propio en `viewBox 0 0 64 64`.
- **`accent`**, solo con semántica: `danger` = borra, mueve plata, toca credenciales o sale a un tercero sin vuelta atrás. `warning` = un tema sensible (salud, plata de otros, terceros).
- **`clave`**: única por tanda. Encabeza la respuesta, para saber a qué tanda contesta.

## Reglas de contenido (la carga visual baja es el contrato)

- **Lo visible de una tarjeta son 50 palabras como mucho, más el dibujo**: título, contexto y motivo. El resto va plegado: impacto, por qué, si va, si no va, fuente.
- **El contexto trae el dato, no repite el título.** Mal: "Hay que ver el mail". Bien: "El mail del martes solo tiene el link; faltan las tres tareas que prometiste".
- **La recomendación se ve en el borde del botón, no en una marca.** Nada viene marcado: una propuesta prellenada no es una respuesta. Al tocarlo, el botón se pinta entero: Va en verde, No va en rojo. "Marcar todo como te recomiendo" existe solo en la página, y sigue siendo un clic tuyo.
- **Números reales o ningún número.** Si un número no se verificó, no va.
- **Sin emojis de adorno.** Un término, un significado: si en un ítem algo está "agendado", en los otros también es "agendado".

## Cuando vuelve la respuesta

- **Del widget** llega una línea: `{encabezado} — Decision 1: Va · Comentario 1: … · Notas: …`. Un `Decision N` que falta es sin marcar. Si dice `Skipped the form`, no se aplica nada.
- **De la página** llega un bloque que arranca con `/brain-decide respuesta · {clave}`, con una línea por ítem.

Antes de ejecutar:

1. **Leé los comentarios primero.** Un "va" o un "no va" con comentario suele querer decir "sí, pero así". Si el comentario cambia la acción, aplicá esa versión y decilo.
2. **Nombrá lo que quedó sin marcar.** No se hace, ni "de paso".
3. **Si algo marcado choca con algo sin marcar**, preguntá antes de aplicar.
4. Aplicá lo marcado y cerrá con una línea por ítem: hecho, no hecho, y por qué.
5. Si la tanda es de un proyecto, lo decidido va a su registro de decisiones o a su estado vivo. La botonera no.

## Output esperado
- Hasta 5: un widget en el chat con un grupo por ítem (título, dibujo si explica, contexto, recomendación en el borde del botón, Va / No va, comentario, detalle plegado), más notas y "Enviar respuesta".
- 6 o más: lo mismo en una página, con conteo en vivo, "Copiar respuesta", y secciones con índice si hay temas.
- En el chat: cuántos ítems, el más urgente, y las preguntas abiertas aparte.

## Cuándo NO usar
- **Una sola decisión:** se pregunta en el chat. Una botonera de una tarjeta es más lenta que una pregunta.
- **Una decisión grande, con opciones todavía abiertas:** eso es `/brain-council`.
- **Para pensar en voz alta:** si no hay recomendación para cada ítem, todavía no es una botonera.

## Señales de que lo hiciste bien (chequeo binario)
- [ ] Ningún ítem te pide investigar algo para poder decidirlo.
- [ ] Cada contexto trae un dato concreto, no una paráfrasis del título.
- [ ] Cada dibujo explica algo de su decisión, y ninguno se sale de su recuadro.
- [ ] `armar.py` pasó sin subir ningún techo.
- [ ] Nada vino marcado de entrada.
- [ ] El widget se mostró tal cual salió del script, sin `<script>` agregado a mano.
- [ ] Las preguntas que no se podían recomendar quedaron en el chat, afuera de la botonera.
- [ ] Al volver la respuesta, lo sin marcar no se ejecutó.

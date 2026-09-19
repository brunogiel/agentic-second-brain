---
name: leccion
description: >
  Convierte cualquier disparador (un tuit, un link, un artículo, una pregunta,
  un tema suelto) en una LECCIÓN: un único archivo HTML autocontenido, pensado
  para aprender ese tema, con una estética que dicta la temática. Tiene DOS
  MODOS y se preguntan siempre: "a fondo" (la lección completa, con referencias
  reales) y "nivel cero" (mega corta, dibujos grandes, ~150 palabras en toda la
  pieza). Usalo cuando digas "/brain-lesson", "hacé una lección sobre esto",
  "quiero aprender esto", "armame una lección de este tuit o este artículo",
  "explicámelo como si tuviera 5 años", "hacémelo bien simple con dibujos", o
  cuando pases un material y quieras entenderlo. El resultado es SIEMPRE un solo
  .html: no produce cursos, ni series, ni archivos múltiples.
---

# leccion — un tema que no sabés, en un solo HTML

## Qué es
Le pasás un disparador (un tuit, un link, un texto pegado, una pregunta suelta) y te devuelve **una pieza para aprender ese tema**: un archivo HTML que se abre con doble click, sin internet, y te lo explica hasta que lo entendés.

Sirve para dos momentos distintos: cuando querés **entender un tema a fondo** para poder discutirlo, y cuando querés **entender la idea de algo en dos minutos** para saber de qué están hablando.

El principio: **una lección enseña, no informa.** Un resumen te cuenta qué dice el material. Una lección te deja pudiendo explicárselo a otro.

## La frontera con `/brain-recap` (leer antes que nada)
Los dos devuelven un HTML autocontenido y ahí se terminan los parecidos:

| | `/brain-recap` (repaso-visual) | `/brain-lesson` (este) |
|---|---|---|
| De dónde sale | Lo que pasó en tu sesión o tu proyecto | Un tema del mundo que todavía no sabés |
| Qué te deja | Saber dónde quedaste parado | Poder explicar el tema |
| Cuándo | Después de trabajar | Antes de entender |

Si lo que querés es ubicarte en una charla que se enredó, eso es `/brain-simple`, y no arma ningún archivo.

## Los dos modos
La profundidad define dos piezas distintas. **Se pregunta siempre (paso 2) y se elige una. No existe el punto medio.**

| | **A fondo** | **Nivel cero** |
|---|---|---|
| Para qué | entender el mecanismo y poder discutirlo | que alguien que no sabe nada entienda la idea |
| Techo de texto | el que el tema pida | **~150 palabras en TODA la pieza** |
| Unidad | bloques con subtítulos que afirman algo | pantallas: un dibujo grande, una frase |
| Referencias | obligatorias y reales | ninguna |

### El contrato del modo nivel cero
- **El techo de palabras es la regla, no una sugerencia.** ~150 palabras en la pieza entera, títulos incluidos. Si no entra, se saca contenido; no se achica la tipografía. Sin ese techo el modo se degrada a una lección corta, que es la peor de las dos piezas.
- **Una idea por pantalla, un dibujo protagonista.** El SVG ocupa el centro y la frase lo acompaña. A lo sumo una línea chica de apoyo.
- **Se suspenden**, y no es un descuido: el mapa macro, la tensión, el vocabulario técnico, el destilado, el autochequeo y las referencias. Este modo explica el mecanismo en criollo, no sitúa el tema en un campo.
- **Siguen valiendo**: números reales o ninguno, archivo autocontenido, imprimible, el lugar donde se guarda y el paso 6.
- Si el tema no se entiende sin una precisión que no entra en el techo, decilo y ofrecé el modo a fondo. **No entregues un híbrido.**

## Flujo

### Paso 0: ¿Hay dónde guardarlo? [DET]
Antes de armar nada, mirá si hay un sistema escribible: carpetas PARA (`1. Proyectos`, `2. Áreas`), algún lugar donde el archivo tenga sentido mañana. Si lo único que hay es el kit recién instalado, la lección se arma igual pero va a quedar suelta: decilo y preguntá dónde la dejás. **Nunca escribas dentro del `kit/` del método:** eso es la app, no tu carpeta.

### Paso 1: Leé el material entero [DET]
El título de un artículo no es el artículo, y el tuit que linkea un paper no es el paper. Si el disparador es un link y no podés acceder, pedí que te peguen el contenido: eso cuenta como una de tus preguntas. **No armes una lección sobre lo que suponés que dice el material.**

### Paso 2: Preguntá, una sola tanda, máximo 5 [DET]
Todas juntas, no de a una, con la opción por defecto primera para que se conteste rápido. Una es **fija, se hace siempre**, aunque el resto se deduzca del pedido:

- **¿A fondo o nivel cero?** *A fondo:* la lección completa, con referencias, para poder discutir el tema. *Nivel cero:* mega corta, dibujos grandes, ~150 palabras, para que lo entienda cualquiera.

El orden de esas dos opciones lo dicta el pedido: si el disparador pide simpleza o rapidez ("explicámelo fácil", "como si tuviera 5 años"), *nivel cero* va primera. Si no dice nada, va primera *a fondo*.

Las demás salen de este banco, y solo si no se deducen del pedido:
- ¿Qué querés sacar de la lección? (entender el mecanismo, poder opinar, aplicarlo a algo concreto)
- ¿Cuánto sabés ya del tema? (para calibrar por dónde entrar)
- [Si el material es ambiguo] ¿La lección es sobre X o sobre Y?

### Paso 3: Confirmá el encuadre con UNA pregunta [DET]
Con las respuestas en mano, enunciá en una línea la temática y el ángulo que vas a usar: *"La lección va a ser sobre X, entrando por Y, a profundidad Z. ¿Dale?"* Esperá el sí antes de escribir. Una lección mal encuadrada se tira entera, y darse cuenta al final cuesta la pieza completa.

### Paso 4: Escribí la lección [LAT]
Seguí las reglas de contenido y de HTML de abajo, según el modo elegido.

### Paso 5: Guardala donde va [DET]
Nombre `leccion-<tema>.html`, o `leccion-<tema>-nivel-cero.html` si es el modo corto. **Los dos modos sobre el mismo tema conviven y no se pisan.**

| El tema es de… | Va a… |
|---|---|
| Un proyecto tuyo | `1. Proyectos/<ese proyecto>/` |
| Un área tuya (lo que estés estudiando) | `2. Áreas/<esa área>/` |
| Nadie claro | Proponé un lugar y preguntá. No lo fuerces a una carpeta cualquiera |

Nunca la dejes en la carpeta de descargas ni en un temporal: un archivo que no sabés dónde quedó es un archivo perdido.

### Paso 6: Probala antes de entregarla [DET]
Abrí el archivo y miralo. Tres chequeos, con la pieza delante:

1. Buscá en el HTML `http`, `src=` y `@import`. Toda referencia a algo de afuera (un CDN, una fuente, una imagen remota) se saca o se incrusta. Los únicos links que sobreviven son los de "Para seguir", que están para hacer click, no para que la página se dibuje.
2. **Renderizá los SVG y miralos.** Que el código parezca correcto no alcanza: un `viewBox` más chico que el dibujo lo desborda sobre el texto, y un ícono encima de una cifra la vuelve ilegible. En nivel cero, donde el dibujo es la pieza, este chequeo es el más importante de los tres.
3. Ninguna sección vacía, ningún placeholder tuyo, ningún número que no salga del material.

Si no la abriste, no la entregues.

### Paso 7: Entregá [DET]
Devolvé el path, mostrala, y decí en una línea qué cubre **y qué quedó afuera**. Lo segundo importa tanto como lo primero: quien lee una lección necesita saber dónde termina.

## Reglas de contenido

> Estas reglas son **del modo a fondo**. En nivel cero rige el contrato de arriba, con la excepción de "números reales o ninguno", que vale siempre.

- **Primero el mapa, después la tensión.** La lección abre SIEMPRE por lo macro: 2 a 4 oraciones de contexto, dónde vive este tema, de qué campo es, por qué importa ahora. De ahí, directo a la tensión, la paradoja o la pregunta abierta que lo hace interesante. Lo macro no es la definición básica: si hay una capa básica imprescindible, despachala en una línea.
- **Asumí un lector inteligente.** Ya conoce la primera capa de casi todo. Nada de validación ni elogio ("¡buena pregunta!"), nada de analogías introductorias como plato principal. Si te dijeron cuánto saben del tema, ese nivel es el piso, no el techo.
- **Vocabulario técnico y referencias reales.** Autores, papers, frameworks, debates vivos, con nombre y apellido. Cada afirmación fuerte tiene de dónde salió. **Si no estás seguro de una referencia, omitila.** Una lección con una cita inventada vale menos que una lección con tres citas menos.
- **Subtítulos que afirman algo.** Los títulos de los bloques son afirmaciones, no etiquetas: "El promedio ponderado es todo el truco", no "El mecanismo". Leyendo solo los subtítulos se reconstruye la lección.
- **Números reales o ningún número.** Si el material no trae cifras, no fabriques métricas ni porcentajes de adorno.
- **Cerrá repasando.** El final vuelve a lo macro (dónde quedó parado el lector en el mapa del principio) y resume la lección en conceptos, 3 a 5 líneas, sin introducir nada nuevo.

## La estructura de la pieza (adaptá, no rellenes)
1. **Apertura:** título, lo macro (el contexto de 2 a 4 oraciones) y la tensión que abre el tema. En la cabecera, declarar modo y tiempo de lectura ("Lección a fondo · ~12 min").
2. **Cuerpo:** 3 a 6 bloques con subtítulos que afirman, del núcleo hacia los bordes. Diagramas SVG cuando un dibujo explica mejor que un párrafo.
3. **Cierre:** lo macro de vuelta, la lección resumida en conceptos, y **una sola frase** que condensa lo esencial con la línea del porqué que la sostiene, visualmente destacadas.
4. **Para seguir:** las fuentes del material y 2 a 4 referencias reales, con link cuando exista y **una línea de por qué leer cada una** (qué agrega que la lección no cubrió).
5. Opcional, solo si suma: 2 o 3 preguntas de autochequeo con la respuesta escondida en `<details>`.

Toda sección vacía se elimina: la estructura refleja lo que hay, nunca al revés.

## Reglas del HTML
- **Un solo archivo, autocontenido.** CSS y JS inline, cero CDNs, cero fuentes externas (stack del sistema con fallback), cero imágenes remotas. Los diagramas van en SVG inline o CSS puro. Se abre con doble click, sin internet, dentro de diez años.
- **Legible ante todo.** Ancho de lectura acotado (`max-width` de unos 70 caracteres en el cuerpo). Este es el eje de la pieza: una lección se lee sostenido, no se escanea. Si hay que elegir, gana la lectura.
- **La estética la dicta el tema.** Una lección de historia puede ser cálida y tipográfica; una de criptografía, técnica y monoespaciada. Elegí paleta, tipografía y layout vos, sin preguntar, y una sola estética por pieza.
- **Los diagramas son SVG inline** y aparecen cuando un dibujo explica mejor que un párrafo. En nivel cero el SVG es el protagonista, no el adorno.
- **Imprimible.** Un bloque `@media print` que la deje digna en A4: `@page { size: A4; margin: 15mm }`, `break-inside: avoid` en cada bloque, y fondo claro si la pieza es oscura.
- **Que funcione en el teléfono.** Es donde se lee la mitad de lo que uno estudia.
- **Cero em-dashes en el texto en español.** Ni en títulos ni en el cuerpo: coma, dos puntos o punto.
- **Footer:** título, modo y fecha `YYYY-MM-DD`. Sin firmas ni créditos: el HTML no menciona ni a la IA ni a este skill.

## Output esperado
Un solo archivo `.html` guardado en su lugar, más tu respuesta en tres líneas: el path, qué cubre la lección y qué quedó afuera.

## Cuándo NO usar
- **Para repasar lo que ya hiciste:** eso es `/brain-recap`, que sale de tu sesión y no de un tema del mundo.
- **Para ubicarte en una charla enredada:** eso es `/brain-simple`, y es texto corto, sin archivo.
- **Para convencer a alguien:** una pieza que argumenta por etapas es `/brain-deck`. Esta enseña, no persuade.
- **Para un curso o una serie:** un pedido, un archivo. Si el tema no entra en una pieza, es más de un tema: decilo y proponé cuál va primero.

## Señales de que lo hiciste bien (chequeo binario)
- [ ] Hiciste la pregunta fija (a fondo o nivel cero) antes de escribir una línea de HTML.
- [ ] Leíste el material entero, no el título ni el primer párrafo.
- [ ] Confirmaste el encuadre en una línea y esperaste el sí.
- [ ] Si fue nivel cero, la pieza entera entra en ~150 palabras contadas, títulos incluidos.
- [ ] Si fue a fondo, cada referencia existe de verdad y ninguna está inventada.
- [ ] Leyendo solo los subtítulos se reconstruye la lección.
- [ ] Abriste el archivo, y renderizaste los SVG y los miraste.
- [ ] Abre sin internet: cero CDNs, cero fuentes remotas, cero imágenes externas.
- [ ] Se imprime digno en A4, sin bloques cortados a la mitad.
- [ ] Cero em-dashes en el texto en español.
- [ ] Quedó guardada en su carpeta, con su nombre, sin pisar una lección anterior sobre el mismo tema, y dijiste dónde.
- [ ] Dijiste qué quedó afuera, no solo qué cubre.

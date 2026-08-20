---
description: Repaso visual de esta sesión (o de un tema) en un solo HTML: qué pasó, qué se decidió, los números y qué queda abierto. Se escanea en 30 segundos.
---

Armá el repaso visual de esta sesión (o del tema que venga en $ARGUMENTS). Seguí esto:

# repaso-visual — lo que pasó, en un solo HTML

## Qué es
Una pasada que mira todo lo que pasó (esta sesión, o un tema que nombres) y lo devuelve como **una pieza visual para mirar**: un archivo HTML que se abre con doble click, sin internet, y te cuenta el recorrido, las decisiones con su porqué, los números y lo que quedó colgando.

Sirve para dos cosas: **repasar** vos mismo algo largo sin releer la conversación, y **mostrárselo a alguien** que no estuvo, sin mandarle un chat de 300 mensajes.

El principio: **es un repaso, no un acta.** Un acta registra todo con el mismo peso. Un repaso jerarquiza: lo que cambió el rumbo va grande, lo accesorio va chico o directamente no va.

## La frontera con `/brain-doc` (leer antes que nada)
Los dos barren la misma conversación. Hacen cosas distintas y **no se reemplazan**:

| | `/brain-doc` (documenta) | `/brain-recap` (este) |
|---|---|---|
| Qué hace | Rutea y **escribe** en tu sistema | **Muestra**, no escribe en tu sistema |
| Sale hacia | El log del proyecto, tu estado, tu memoria, el inbox | Un `.html` para mirar o compartir |
| Para qué | Que la sesión no se pierda | Repasarla de un vistazo o mostrarla |

**Regla dura.** Si la sesión tuvo decisiones, números o pendientes durables, el repaso **no cierra el tema**: es lindo, pero tu sistema quedó igual que antes. Al entregar el archivo, cerrá con una línea ofreciendo `/brain-doc`, sin correrlo por tu cuenta. Nunca des una sesión por cerrada porque saliste con un repaso: el riesgo real es quedarte con la sensación de haber guardado, con el estado sin tocar.

## Los dos modos
- **Sesión:** el material es la conversación actual. Repasás lo que se hizo, se decidió y quedó pendiente en ESTA sesión, en orden.
- **Tema:** te nombran un tema. El material es lo que haya en contexto más lo que te peguen o te señalen. No inventes historia que no tenés: si el material no alcanza, pedirlo cuenta como una de tus preguntas.

## Flujo

### Paso 0: ¿Hay dónde guardarlo? [DET]
Antes de armar nada, mirá si hay un sistema escribible: carpetas PARA (`1. Proyectos`, `2. Áreas`), un `CLAUDE.md` de proyecto, algún lugar donde el archivo tenga sentido mañana. Si lo único que hay es el kit del método recién instalado, sin carpetas tuyas, el repaso se puede armar igual pero va a quedar suelto: decilo y preguntá dónde lo dejás, no lo tires en cualquier lado. **Nunca escribas dentro del `kit/` del método:** eso es la app, no tu carpeta.

### Paso 1: Fijá el alcance [DET]
¿Sesión o tema? ¿Desde cuándo hasta cuándo? Si el pedido ya lo dice, no preguntes nada de esto.

### Paso 2: Preguntá, una sola tanda, máximo 5 [DET]
Todas juntas, no de a una, y con la opción por defecto marcada para que se conteste rápido. Una es **fija, se hace siempre**:

- **¿Busco referencias externas en la web para enriquecer el repaso, o uso solo lo que hay en la sesión y el contexto actual?**

Las demás salen de este banco, y solo si no se deducen del pedido:
- ¿Para quién es? (para vos como repaso, o para alguien que no estuvo)
- ¿Qué querés en primer plano? (decisiones, números, cronología, hallazgos)
- ¿Hay material que deba incluir y no tengo? (pegámelo)
- ¿Algo que quede afuera sí o sí?

### Paso 3: Destilá el material [LAT]
Releé el material **entero**, no solo lo último. Ordenalo en estos ejes, y quedate solo con los que existan de verdad:

- **Qué pasó:** la secuencia, si el material es narrativo.
- **Qué se decidió:** cada decisión con su porqué en una línea.
- **Números:** las cifras que salieron, con su etiqueta.
- **Hallazgos:** lo que se aprendió o se descubrió a mitad de camino.
- **Qué queda abierto:** pendientes y próximos pasos.

Máximo 7 bloques en la pieza final. Si hay más material, fusioná o cortá: un repaso de 15 bloques ya no se escanea, se lee, y entonces perdió el punto.

**Freno.** Si al terminar de destilar no queda ni un bloque con contenido real, frená acá: decilo en una línea y ofrecé la respuesta en dos renglones, en vez de armar un HTML con seis secciones vacías. Una charla de tres mensajes no necesita un repaso visual.

### Paso 4: Armá el HTML [LAT]
Seguí las reglas de contenido y de HTML de acá abajo.

### Paso 5: Guardalo donde va [DET]
Nombre `repaso-<tema>-<YYYY-MM-DD>.html`, y el lugar según de quién sea el tema:

| El tema es de… | Va a… |
|---|---|
| Un proyecto | `1. Proyectos/<ese proyecto>/repasos/` (creá la carpeta si no está) |
| Un área | `2. Áreas/<esa área>/repasos/` |
| Nadie claro | Proponé un lugar y preguntá, igual que hace `documenta`. No lo fuerces a una carpeta cualquiera |

**Si ya existe un archivo con ese nombre, no lo pises.** Es el repaso de otra corrida sobre el mismo tema: sumale un sufijo (`-2`) o preguntá cuál queda. Correr el comando dos veces nunca tiene que borrar el trabajo de la primera.

Nunca lo dejes en la carpeta de descargas ni en un temporal: un archivo que no sabés dónde quedó es un archivo perdido. La excepción es que te digan explícitamente que es descartable.

### Paso 6: Probalo antes de entregarlo [DET]
Abrí el archivo y miralo. Tres chequeos concretos, con la pieza delante:

1. Buscá en el HTML `http`, `src=` y `@import`. Toda referencia a algo de afuera (un CDN, una fuente, una imagen remota) se saca o se incrusta. Los únicos links que sobreviven son los de la sección Referencias, que están para hacer click, no para que la página se dibuje.
2. Ninguna sección vacía, ningún placeholder tuyo, ningún número que no salga del material.
3. El bloque `@media print` existe.

Si no lo abriste, no lo entregues: un repaso que no miraste es un intento, no un entregable.

### Paso 7: Entregá [DET]
Devolvé el path, mostralo, y decí en UNA línea qué cubre. Cerrá ofreciendo `/brain-doc` según la regla dura de arriba.

## Reglas de contenido
- **Un destacado por bloque, máximo.** Cada bloque tiene a lo sumo UN protagonista: una cifra grande, una frase destacada o un hito. Si todo grita, no se escucha nada.
- **Repaso, no venta.** Frases fuertes y conceptos destacados, sí: son lo que hace que un repaso se recuerde. Pero el objetivo es repasar, no vender. Sin superlativos gratuitos, sin autobombo, sin tono de landing. Una frase se destaca porque condensa algo cierto, no porque suene épica.
- **Números reales o ningún número.** Si el material no trae cifras, no fabriques métricas ni porcentajes de adorno. Un repaso con números inventados es peor que uno sin números.
- **Cada dato con su peso visual.** Decisiones como tarjetas con su porqué en una línea. Números como cifras grandes con etiqueta. Secuencias como línea de tiempo. Pendientes como lista clara al final.
- **Procedencia marcada.** Si buscaste en la web, lo externo se distingue de lo propio de la sesión con una marca sutil y consistente, y la pieza cierra con una mini sección de referencias con sus links.
- **Toda sección vacía se elimina.** La pieza refleja lo que hay, nunca una grilla a medio llenar.
- **Cero em-dashes en el texto en español.** Ni en los títulos ni en el cuerpo: coma, dos puntos o punto.
- **Nada sensible adentro.** Ni claves, ni datos personales de terceros, ni nada que hayas marcado como privado en tu sistema. Si el repaso es para compartir, pasale el mismo filtro que le pasarías a algo que sale de tu carpeta.

## La estructura de la pieza (adaptá, no rellenes)
1. **Cabecera:** título del repaso, alcance (qué período o qué tema) y una línea con el saldo, la que responde "¿y, cómo salió?".
2. **El recorrido:** la línea de tiempo de lo que pasó, si el material es narrativo.
3. **Decisiones:** qué se decidió y por qué, si las hubo.
4. **Números:** las cifras que importan, grandes, si las hay.
5. **Hallazgos:** lo que se aprendió, si lo hay.
6. **Queda abierto:** pendientes y próximos pasos, si los hay.
7. **Referencias:** solo si hubo búsqueda web.

## Reglas del HTML
- **Un solo archivo, autocontenido.** CSS y JS inline, cero CDNs, cero fuentes externas (stack del sistema con fallback), cero imágenes remotas. Gráficos y líneas de tiempo en SVG o CSS puro. Se abre con doble click, sin internet, dentro de diez años.
- **La estética la dicta el tema.** Un repaso de finanzas puede ser sobrio y numérico; uno de un viaje, cálido; uno de infraestructura, técnico y monoespaciado. Elegí paleta, tipografía y layout vos, sin preguntar, y una sola estética por pieza.
- **Escaneable primero.** De un vistazo se entienden título, saldo y bloques; el detalle vive en el segundo nivel de lectura. Que funcione en el teléfono.
- **Imprimible.** Un bloque `@media print` que la deje digna en A4: `@page { size: A4; margin: 15mm }`, `break-inside: avoid` en cada bloque y cada tarjeta para que no se corten a la mitad, y fondo claro si la pieza es oscura. Eso es lo que la vuelve compartible como PDF sin trabajo extra.
- **Footer:** título, alcance y fecha `YYYY-MM-DD`. Sin firmas ni créditos: el HTML no menciona ni a la IA ni a este skill.

## Output esperado
Un solo archivo `.html` guardado en su lugar, más tu respuesta en tres líneas: el path, qué cubre la pieza, y el ofrecimiento de `/brain-doc` si quedó algo durable sin guardar.

## Cuándo NO usar
- **Para guardar lo que pasó:** eso es `/brain-doc`. Este muestra, no guarda.
- **Para convencer a alguien:** una pieza que argumenta y persuade por etapas es `/brain-deck`. Este repasa lo que hubo, no arma un caso.
- **Para ubicarte en una charla que se te enredó:** eso es `/brain-simple`, que te lo baja en texto corto sin armar ningún archivo.
- **Cuando no hay material:** una sesión de tres mensajes no necesita un repaso visual, necesita una respuesta.

## Señales de que lo hiciste bien (chequeo binario)
- [ ] Hiciste la pregunta fija (web sí o web no) antes de escribir una línea de HTML.
- [ ] Barriste el material entero, no solo lo último que pasó.
- [ ] Cada número que aparece salió del material; no hay ni una cifra decorativa.
- [ ] Ningún bloque tiene dos protagonistas peleando por la atención.
- [ ] No quedó ninguna sección vacía ni con un "sin datos" adentro.
- [ ] Lo abriste y lo miraste antes de entregarlo.
- [ ] El archivo abre sin internet: cero CDNs, cero fuentes remotas, cero imágenes externas.
- [ ] Se imprime digno en A4, sin bloques cortados a la mitad.
- [ ] Cero em-dashes en el texto en español.
- [ ] Quedó guardado en su carpeta, con su nombre y su fecha, sin pisar un repaso anterior, y dijiste dónde.
- [ ] Si había algo durable sin guardar, ofreciste `/brain-doc` en vez de dar el tema por cerrado.

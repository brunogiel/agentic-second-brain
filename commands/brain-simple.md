---
description: Te ubica en una charla larga. Sin nada, te baja el estado en simple y corto. Con "html", el repaso visual de la sesión en un archivo. Con "html inline", ese repaso mostrado acá mismo.
---

Ubicá a la persona en esta conversación. Lo que escribió después del comando: $ARGUMENTS

**Ruteo, esto primero:** sin argumento (o `corto` / `texto` / `simple` / `chat`) va el **modo corto**; `inline` / `flash` / `widget`, solos o pegados a `html`, van al **modo inline**; `html` / `resumen` / `visual` / `repaso` sin ninguna de esas palabras va al **modo html**. Cualquier otra cosa cae al corto y el argumento se toma como el tema. El texto que sobra después del modo es el alcance.

No preguntes cuál de los tres: el argumento ya lo dijo.

---

# simple: ubicarte en una charla larga

Un tiro claro. Cuando una conversación se hizo larga o te perdiste el hilo, te bajo dónde estamos y qué sigue. **Es una sola vez, no un modo: te lo dejo claro y la charla sigue normal.**

No bajo el nivel ni te trato como si no entendieras. Es lo mismo que explicarle a alguien que sabe pero perdió el hilo: corto, ordenado, sin jerga de más.

## Los tres modos

El argumento elige el modo. **El default es el corto: sin argumento no se pregunta nada.**

| | **corto** (default) | **html** | **html inline** |
|---|---|---|---|
| Se pide con | `/brain-simple`, o una frase gatillo | `/brain-simple html` | `/brain-simple html inline` |
| Devuelve | 5 líneas en el chat | un `.html` guardado | la pieza mostrada en el chat |
| Cuánto tarda | segundos | minutos | ~1 minuto |
| Preguntas | ninguna | una (¿busco en la web?) | **ninguna** |
| Queda archivo | no | sí, en tu sistema | no, vive en la conversación |
| Quién lo hace | este skill | `repaso-visual` completo | `repaso-visual` inline |

Sinónimos que rutean al **corto**: `corto`, `texto`, `simple`, `chat`. Al **html**: `html`, `resumen`, `visual`, `repaso`. Al **inline**: cualquiera de los de html más `inline`, y también `inline`, `flash` o `widget` solos. Cualquier otra cosa cae al corto, y el argumento se toma como el tema sobre el que quiere la bajada.

**Desempate:** si aparece `inline` (o `flash` / `widget`), gana el inline, esté o no la palabra `html` al lado.

**Nunca preguntes cuál de los tres.** Si el argumento no matchea, corto y listo: este skill existe para que no tengas que decidir cuando ya estás perdido.

**El texto que sobra después del modo es el ALCANCE.** `/brain-simple html el rediseño del onboarding` arma el repaso de ese tema, no de la sesión. Sin nada al lado, el alcance es ESTA conversación.

### Los modos visuales en detalle

Los dos corren [`repaso-visual`](../repaso-visual/SKILL.md), que es el motor de la pieza. **El formato ya viene elegido por el comando: la pregunta de completo vs inline no se hace.**

- **`html` → formato completo.** Un `.html` guardado en su lugar, imprimible y compartible. La única pregunta es la fija de ese formato: ¿busco referencias en la web o uso solo lo que hay acá?
- **`html inline` → formato inline.** La pieza mostrada en la conversación, sin archivo. **Cero preguntas.** Necesita un cliente que sepa mostrar HTML inline; si el tuyo no puede, decilo y ofrecé el completo en vez de escupir un bloque de código.

Si el material no da para ni un bloque real, frená en los dos: una charla de tres mensajes no necesita un repaso visual, necesita una respuesta.

## Qué hace el modo corto

Repasa ESTA conversación (lo que se decidió, lo que quedó a medias, el próximo paso) y te lo devuelve en un bloque chico que separa tu parte de la mía. No re-explica todo de cero: te da lo justo para reengancharte.

## El formato de salida del modo corto

```
📍 Dónde estamos: <una línea, sin vueltas>
🫵 Qué hacés vos: <tu próximo paso, concreto>
🤖 Qué sigo yo: <qué hago apenas me des el OK>
```

Si hay UNA cosa trabada que bloquea todo, sumá una línea `🚧 Lo trabado: ...`.

Reglas del bloque:
- Tope 5 líneas. Si no entra, la charla mezcla varios temas: no la fuerces, preguntá "¿por dónde querés arrancar?" y cortá ahí.
- Jerga técnica solo si hace falta, y traducida al toque.
- Nada de guiones largos: coma, punto, dos puntos o paréntesis.

## Flujo del modo corto

1. **[LAT]** Leé la conversación: qué se decidió, qué quedó a medias, cuál es el próximo movimiento. Separá lo tuyo de lo mío.
2. **[LAT]** Bajalo con el formato de arriba, en lenguaje simple y corto.
3. **[DET]** Entregá el bloque y seguí la charla en tu tono normal. No quedás pegado en ningún modo.

*Los modos visuales no usan estos pasos: siguen el flujo de `repaso-visual`, con el formato y el alcance ya fijados.*

## La frontera con `/brain-doc`

Los tres modos barren la misma conversación y **ninguno guarda nada en tu sistema**. Si la sesión tuvo decisiones, números o pendientes durables, cerrá ofreciendo `/brain-doc`, sin correrlo por tu cuenta. Salir con un repaso lindo y el sistema sin tocar es la trampa que este skill no puede resolver solo.

## Cuándo NO usar

- Charlas cortas o recién arrancadas: no hace falta ubicar a nadie.
- Cuando lo que se pide es avanzar el trabajo, no resumirlo: ahí seguí con la tarea.
- Para bajar la calidad o el detalle técnico: esto cambia CÓMO se cuenta el estado, no qué tan bien se hace el trabajo.
- Para guardar lo que pasó: eso es `/brain-doc`.
- Para convencer a alguien con una pieza que argumenta por etapas: eso es `/brain-deck`.

## Señales de que lo hiciste bien (chequeo binario)

- [ ] El modo salió del argumento solo, sin preguntar cuál de los tres.
- [ ] Corto: el bloque entra en ≤5 líneas y separa explícitamente qué hace la persona y qué hacés vos.
- [ ] Corto: lenguaje simple, sin jerga sin traducir, cero em-dashes.
- [ ] Corto: un solo tiro, la charla siguió normal sin quedar en ningún modo.
- [ ] Visuales: no volviste a preguntar el formato, y el inline no hizo ni una pregunta.
- [ ] Visuales: si el cliente no sabe mostrar HTML inline, lo dijiste en vez de simularlo.
- [ ] La persona se reengancha sin pedir un segundo resumen.
- [ ] Si quedó algo durable sin guardar, ofreciste `/brain-doc` en vez de dar el tema por cerrado.

---

# repaso-visual — lo que pasó, en un solo HTML

## Qué es
Una pasada que mira todo lo que pasó (esta sesión, o un tema que nombres) y lo devuelve como **una pieza visual para mirar**: un archivo HTML que se abre con doble click, sin internet, y te cuenta el recorrido, las decisiones con su porqué, los números y lo que quedó colgando.

Sirve para dos cosas: **repasar** vos mismo algo largo sin releer la conversación, y **mostrárselo a alguien** que no estuvo, sin mandarle un chat de 300 mensajes.

**Este skill no tiene comando propio: se entra por [`simple`](../simple/SKILL.md).** `/brain-simple html` lo corre en formato completo y `/brain-simple html inline` en formato inline. El `/brain-recap` que existió hasta la v2.40.0 se dio de baja: hacía exactamente lo mismo que `/brain-simple html`, y dos comandos para una sola pieza es una decisión de más cada vez que la querés.

El principio: **es un repaso, no un acta.** Un acta registra todo con el mismo peso. Un repaso jerarquiza: lo que cambió el rumbo va grande, lo accesorio va chico o directamente no va.

## La frontera con `/brain-doc` (leer antes que nada)
Los dos barren la misma conversación. Hacen cosas distintas y **no se reemplazan**:

| | `/brain-doc` (documenta) | `/brain-simple html` (este) |
|---|---|---|
| Qué hace | Rutea y **escribe** en tu sistema | **Muestra**, no escribe en tu sistema |
| Sale hacia | El log del proyecto, tu estado, tu memoria, el inbox | Un `.html` para mirar o compartir |
| Para qué | Que la sesión no se pierda | Repasarla de un vistazo o mostrarla |

**Regla dura.** Si la sesión tuvo decisiones, números o pendientes durables, el repaso **no cierra el tema**: es lindo, pero tu sistema quedó igual que antes. Al entregar el archivo, cerrá con una línea ofreciendo `/brain-doc`, sin correrlo por tu cuenta. Nunca des una sesión por cerrada porque saliste con un repaso: el riesgo real es quedarte con la sensación de haber guardado, con el estado sin tocar.

## Los dos alcances
*El alcance dice de qué material salís. El formato (abajo) dice qué entregás. Son dos ejes independientes: cualquier alcance sale en cualquier formato.*

- **Sesión:** el material es la conversación actual. Repasás lo que se hizo, se decidió y quedó pendiente en ESTA sesión, en orden.
- **Tema:** te nombran un tema. El material es lo que haya en contexto más lo que te peguen o te señalen. No inventes historia que no tenés: si el material no alcanza, pedirlo cuenta como una de tus preguntas.

## Los dos formatos: completo e inline

El formato no es un matiz: son dos piezas distintas, con costos distintos. **Lo elige el comando, no vos:** `/brain-simple html` es completo, `/brain-simple html inline` es inline. Si el pedido llegó por una frase suelta ("armame el repaso de esto"), sin comando, ahí sí preguntás cuál de los dos.

| | **Completo** | **Inline** |
|---|---|---|
| Sale como | un archivo `.html` guardado | la pieza mostrada en el chat |
| Preguntas | una (¿busco en la web?) | **ninguna** |
| Busca en la web | según la respuesta | **nunca** |
| Permanencia | vive en tu sistema | vive en la conversación |
| Imprimible / compartible | sí | no |
| Techo | el que el material pida (~7 bloques) | ~5 bloques, entra de un vistazo |
| Cuándo | para volver, para mandar, para imprimir | repasar YA, para vos |

### El contrato del formato inline

- **Cero preguntas.** Ni siquiera la de la web: buscar afuera es justo lo lento, y este formato existe para salir rápido. Si el material no alcanza, aplicá el freno del paso 3, no una pregunta.
- **Necesita un cliente que sepa mostrar HTML en la conversación** (un panel de artefactos, un visor de widgets, una vista previa inline). **Si el tuyo no puede, no lo simules con un bloque de código:** decilo en una línea y ofrecé el completo. Un repaso que no se ve no es un repaso.
- **Efímero a propósito.** No se guarda archivo, no lleva footer, no lleva `@media print`.
- **Se ve solo, pero igual se mira.** No hay paso de abrir el archivo, pero revisá la pieza renderizada antes de darla por terminada: un SVG desbordado se ve igual de mal inline.
- **Siguen valiendo enteras:** números reales o ninguno, un destacado por bloque, toda sección vacía se elimina, nada sensible adentro, y que la pieza no mencione a la IA ni a este skill.
- **Ojo con lo sensible.** Una pieza inline parece descartable y no lo es: queda en la conversación, que se comparte, se exporta y se lee después. Pasale el mismo filtro que al completo.
- **Cerrá ofreciendo guardarlo.** Una línea: si le sirve, "guardámelo" lo convierte en la pieza completa, con destino y todo. **No lo guardes por tu cuenta.**

### Cuándo empujar al completo

Si el material tiene más de ~5 bloques con contenido real, o números que piden lectura detenida, o te dijeron que es para mostrarle a alguien, decilo en una línea antes de escribir y ofrecé el completo. **No entregues un inline que ya sabés que se queda corto.**

## Flujo

### Paso 0: ¿Hay dónde guardarlo? [DET]
Antes de armar nada, mirá si hay un sistema escribible: carpetas PARA (`1. Proyectos`, `2. Áreas`), un `CLAUDE.md` de proyecto, algún lugar donde el archivo tenga sentido mañana. Si lo único que hay es el kit del método recién instalado, sin carpetas tuyas, el repaso se puede armar igual pero va a quedar suelto: decilo y preguntá dónde lo dejás, no lo tires en cualquier lado. **Nunca escribas dentro del `kit/` del método:** eso es la app, no tu carpeta.

### Paso 1: Fijá el alcance [DET]
¿Sesión o tema? ¿Desde cuándo hasta cuándo? Si el pedido ya lo dice, no preguntes nada de esto.

### Paso 2: Preguntá, una sola tanda, máximo 5 [DET]
**Si el formato es inline, no preguntes nada: andá al paso 3.** Es el contrato de ese formato.

**Si el pedido llegó sin comando** (una frase suelta), la primera pregunta es cuál de los dos formatos quiere, y va sola.

En completo, todas juntas, no de a una, y con la opción por defecto marcada para que se conteste rápido. Una es **fija, se hace siempre**:

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

*Acá el proceso se bifurca. Si es inline, seguí el paso 4 y saltá directo al 7. Si es completo, seguí los pasos 4 a 7.*

### Paso 4: Armá la pieza [LAT]
Seguí las reglas de contenido y de HTML de acá abajo. En inline se suspenden cuatro de las reglas del HTML (archivo único, imprimible, footer y destino); las demás valen enteras, sobre todo la estética dictada por el tema y lo de no meter nada sensible.

### Paso 5: Guardalo donde va [DET] *(solo completo)*
Nombre `repaso-<tema>-<YYYY-MM-DD>.html`, y el lugar según de quién sea el tema:

| El tema es de… | Va a… |
|---|---|
| Un proyecto | `1. Proyectos/<ese proyecto>/repasos/` (creá la carpeta si no está) |
| Un área | `2. Áreas/<esa área>/repasos/` |
| Nadie claro | Proponé un lugar y preguntá, igual que hace `documenta`. No lo fuerces a una carpeta cualquiera |

**Si ya existe un archivo con ese nombre, no lo pises.** Es el repaso de otra corrida sobre el mismo tema: sumale un sufijo (`-2`) o preguntá cuál queda. Correr el comando dos veces nunca tiene que borrar el trabajo de la primera.

Nunca lo dejes en la carpeta de descargas ni en un temporal: un archivo que no sabés dónde quedó es un archivo perdido. La excepción es que te digan explícitamente que es descartable.

### Paso 6: Probalo antes de entregarlo [DET] *(solo completo)*
Abrí el archivo y miralo. Tres chequeos concretos, con la pieza delante:

1. Buscá en el HTML `http`, `src=` y `@import`. Toda referencia a algo de afuera (un CDN, una fuente, una imagen remota) se saca o se incrusta. Los únicos links que sobreviven son los de la sección Referencias, que están para hacer click, no para que la página se dibuje.
2. Ninguna sección vacía, ningún placeholder tuyo, ningún número que no salga del material.
3. El bloque `@media print` existe.

Si no lo abriste, no lo entregues: un repaso que no miraste es un intento, no un entregable.

### Paso 7: Entregá [DET]
**Completo:** devolvé el path, mostralo, y decí en UNA línea qué cubre.

**Inline:** mostrá la pieza, decí en UNA línea qué cubre, y sumá otra ofreciendo guardarla. Miralo renderizado antes: que el código parezca correcto no alcanza.

En los dos casos, cerrá ofreciendo `/brain-doc` según la regla dura de arriba.

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
- **Para ubicarte en una charla que se te enredó:** eso es `/brain-simple` a secas, que te lo baja en texto corto sin armar ninguna pieza.
- **Cuando no hay material:** una sesión de tres mensajes no necesita un repaso visual, necesita una respuesta.

## Señales de que lo hiciste bien (chequeo binario)
- [ ] El formato salió del comando; no lo preguntaste de nuevo.
- [ ] En completo: hiciste la pregunta fija (web sí o web no) antes de escribir una línea de HTML. En inline: no hiciste ninguna.
- [ ] Barriste el material entero, no solo lo último que pasó.
- [ ] Cada número que aparece salió del material; no hay ni una cifra decorativa.
- [ ] Ningún bloque tiene dos protagonistas peleando por la atención.
- [ ] No quedó ninguna sección vacía ni con un "sin datos" adentro.
- [ ] Lo abriste y lo miraste antes de entregarlo.
- [ ] El archivo abre sin internet: cero CDNs, cero fuentes remotas, cero imágenes externas.
- [ ] Se imprime digno en A4, sin bloques cortados a la mitad.
- [ ] Cero em-dashes en el texto en español.
- [ ] Completo: quedó guardado en su carpeta, con su nombre y su fecha, sin pisar un repaso anterior, y dijiste dónde.
- [ ] Inline: lo viste renderizado, no guardaste nada por tu cuenta, y ofreciste convertirlo en completo.
- [ ] Si había algo durable sin guardar, ofreciste `/brain-doc` en vez de dar el tema por cerrado.

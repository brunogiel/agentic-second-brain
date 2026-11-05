---
description: Arma una presentación por etapas, de bruto a final (brief, historia, estructura, copy, .pptx), o un video animado con voz. No te tira la pieza de una: la construís vos, una etapa a la vez con tu OK.
---

Armá la pieza de comunicación que te pidan ($ARGUMENTS), por etapas. Seguí esto:

# ppt-builder: armar un deck (y otras piezas) por etapas

> **Ejemplo de orquestador.** Este skill no escribe el copy ni genera los slides él mismo: coordina un proceso de 5 etapas y, en cada una, **llama a los skills que ya hacen ese trabajo** (`redactar` para la voz, `anti-slop` para limpiar, el skill de pptx para el asset). Es el patrón del Nivel 5: repartir y juntar, no rehacer.

Se arma por bloques, de la base para arriba: no empezás por el copy si todavía no está la historia. El laburo va por **5 etapas funcionales**. Orientado sobre todo a **deck/ppt**; el mismo flujo sirve para post, video, carrusel o landing cambiando el molde en las últimas etapas. Todo vive en **un solo doc que crece** (`pieza.md`), una etapa a la vez, con OK antes de pasar a la siguiente.

## Cómo corre
- **Una etapa a la vez.** Construís la etapa, la mostrás, esperás un "dale", recién ahí seguís. Nunca las 5 de una.
- **Bloqueo duro entre etapas.** Aunque haya contexto suficiente para imaginar Historia, Estructura o Copy, NO avances ni scaffoldees la etapa siguiente hasta tener OK explícito sobre la actual. Si el usuario trae material que pertenece a una etapa futura, capturalo como insumo o `[PENDIENTE PARA ETAPA N]`, pero no lo resuelvas todavía.
- **El usuario lidera lo creativo.** El skill ejecuta, propone y arma; el ángulo, la historia, el copy y el tono los cierra el usuario. Frasealo "armé esto, ¿te cierra?", no decidas solo.
- **UN solo doc que crece.** Cada etapa appendea una sección H2 al mismo markdown (`{BASE}/{SLUG}/pieza.md`), no un archivo por etapa. Arriba el brief, abajo lo último.
- **Profundidad por etapa.** Cada etapa corre en **skip / liviano / full**. Al arrancar proponés un perfil según medio + tamaño; el usuario lo ajusta antes de construir.
- **Reuso, no reinvento.** La etapa Copy pasa por `redactar` (voz del usuario) + `anti-slop` (limpieza). La etapa Asset usa el skill de pptx (si lo tiene) o un generador tipo Gamma; en video, las herramientas de `video/`. No reescribís un revisor de estilo, un generador de slides ni el motor de video.
- **Si `MEDIO` es `video`, leé `reference-video.md` antes de la Etapa 1.** Trae los gates, los formatos y la receta técnica del Asset. Vive al lado de este archivo, con las herramientas en `video/`. Las rutas son relativas a la carpeta de este SKILL.md, no a donde estés parado. Ubicala primero:

  ```bash
  PPT="$(dirname "$(find ~/.claude -name 'reference-video.md' -path '*ppt-builder*' 2>/dev/null | head -1)")"
  ```

## Parámetros (kickoff)
Cerrar con el usuario lo que falte (no inventar):

| Param | Qué es | Ej. |
|---|---|---|
| `PIEZA` | de qué va, en una línea | "lanzamiento del producto X" |
| `MEDIO` | **ppt** (default) / post / video / carrusel / landing. Puede ser más de uno | ppt |
| `SLUG` | nombre corto kebab-case para la carpeta | `lanzamiento-x` |
| `BASE` | carpeta del proyecto donde vive. Default: `1. Proyectos/<proyecto>/` | `1. Proyectos/Lanzamiento/` |
| `OBJETIVO` | qué querés que pase | "que prueben el producto" |
| `AUDIENCIA` | a quién le habla | founders / clientes / equipo |

**Convención de archivos:** doc único en `{BASE}/{SLUG}/pieza.md`; assets generados (pptx, imágenes, prompts, el mp4) en `{BASE}/{SLUG}/assets/`.

**Research / contexto (escape hatch):** el default es un solo `pieza.md`, sin subcarpetas. Si una pieza necesita research, **proponéselo al usuario antes de crear nada**; recién con OK se arma `{BASE}/{SLUG}/contexto/`.

## Perfil de profundidad (lo primero que se propone)
Tres niveles por etapa: **skip** (no aplica o ya está; 1 línea y seguís), **liviano** (lo mínimo para que la próxima etapa salga bien), **full** (a fondo). **[LAT]** Proponé un default según medio + tamaño; el usuario lo ajusta:

| Medio | Brief | Historia | Estructura | Copy | Asset |
|---|---|---|---|---|---|
| **Deck / ppt** | liviano | liviano | full | full | full |
| **Post LinkedIn** | liviano | liviano | liviano | full | liviano |
| **Carrusel** | liviano | liviano→full | full | full | full |
| **Video** | full | full | full | full | full |
| **Landing** | liviano→full | full | full | full | full |

Video va full en todo porque cada error que pasa de etapa se paga caro en el Asset: un cambio de texto con la voz ya generada es otra toma, y otro render.

Guardá el perfil aprobado en el frontmatter del doc (`profundidad:` por etapa).

## Las 5 etapas
**Etapa 0: Kickoff + scaffold** `[DET]`
Reunir parámetros, proponer el perfil de profundidad, esperar OK. Crear `{BASE}/{SLUG}/` + `assets/` + `pieza.md` con frontmatter (`pieza`, `medio`, `objetivo`, `audiencia`, `profundidad` por etapa, `creado`).

**Etapa 1 · Brief** `[LAT]` → appendea `## 1. Brief`
- **Contexto:** dónde aterriza la pieza, realidades del canal (LinkedIn premia el hook en las 2 primeras líneas; un deck se proyecta y se lee a 3 metros).
- **Objetivo + audiencia:** para qué es, a quién, qué querés que sienta/haga.
- **Límites:** no-negociables (marca, legal, tono, qué NO decir).
- **Formato (solo deck/ppt):** ¿es una presentación con alguien que la cuenta, o un documento que se lee solo? Con presenter, la slide lleva lo mínimo y el presenter dice el resto: la slide no es un karaoke. Si es documento, cada slide se tiene que entender sin nadie al lado.
- **Solo video, los 3 gates** (`reference-video.md` §Antes de arrancar): (1) ¿quién lo publica y lo quiere? Si sale con una marca que no es tuya (un socio, una agencia, un cliente), su dueño ve una muestra chica antes de producir; sin su OK no se pasa de la Etapa 1. (2) Formato, del más humano al más IA: tu voz y pantallas reales, o animación con voz sintética. Elegilo según cuánto juzga oficio la audiencia. (3) Qué hace quien lo ve al terminar (abrir un link, escanear un QR, agendar).
- **Piense / Sienta / Haga:** al terminar, ¿qué querés que la audiencia piense, sienta y haga? Una respuesta por cada uno. Es el filtro para decidir qué queda y qué sobra.
- *liviano* = bullets. *full* = + research del canal si hace falta (proponer antes). Checkpoint.

Regla de salida: la Etapa 1 termina con un checkpoint y una pregunta de confirmación. NO metas todavía índice de slides, copy, prompts de asset ni estructura tentativa, salvo como `Notas para etapa futura`.

**Etapa 2 · Historia** `[LAT]` → appendea `## 2. Historia`
Un mini-storyboard: el input de Estructura, no una narrativa literaria. Cada bloque es una línea, no un párrafo.
- **Mensaje central** en UNA frase. Si no entra en una frase, son dos mensajes; elegí uno.
- **Por qué importa** a esta audiencia (el stake, la tensión). Sin esto la pieza informa pero no mueve.
- **Bloques en orden:** la lista de temas/momentos en secuencia, cada uno con (a) qué querés que la audiencia sienta o entienda y (b) qué decís para lograrlo. Sin desarrollar el copy todavía, solo la intención. Esta lista es la que después se expande en slides/beats/tarjetas.
- Lo que falte (un dato, un caso real) va como `[ABIERTO: ...]`, nunca inventado. Checkpoint.

**Patrón héroe/guía (decks de venta, propuestas, pitches):** la audiencia es el héroe; vos (tu empresa, producto o servicio) sos el guía, no el protagonista. El arco: el héroe tiene un problema → en el peor momento aparece el guía → le da un plan → lo llama a actuar → esa acción evita el fracaso → y termina en un éxito. Si la pieza busca vender o convencer, proponé este patrón como opción para los Bloques.

**Solo video:** al cerrar la Historia, pasá el storyboard por `panel` con 4 lentes (el destinatario, alguien de afuera, un editor, un fundador exigente con el producto). Ahí un "es un cronograma sin una idea que empuje" cuesta una línea; sobre el video ya renderizado cuesta una vuelta entera.

*liviano* = mensaje central + por qué importa + bloques en bullets cortos. *full* = + el hilo conductor (la forma que hilvana todo: antes/después, problema→giro→solución, una anécdota que ancla) y 2 alternativas de orden para elegir cuál fluye mejor.

**Etapa 3 · Estructura** `[LAT]` → appendea `## 3. Estructura`
- **ppt/deck:** lista de slides por título, 1 idea por slide, arco apertura → tensión → resolución → cierre/CTA. **La cantidad de slides emerge del storyboard de Historia:** expandí cada bloque en tantas slides como ideas tenga, sin comprimir ni inflar. Proponé el número que sale y ajustalo con el usuario si no se siente bien. Referencia de ritmo: ~2 min por slide.
  **Composición:** poco texto y letra grande (≥32 pt de referencia). La audiencia lee el título, después el subtítulo, y el resto probablemente se lo saltea si no está resaltado: jerarquizá en consecuencia. **El título es la conclusión, no el tema** ("Septiembre fue el mes con más ventas", no "Ventas de septiembre"); en un gráfico, el título dice qué muestra. Revelá de a poco, no adelantes todo en una slide. Ilustrá siempre que puedas (foto, ícono, mockup antes que texto puro). Evitá tablas si se puede simplificar de otra forma.
- **post:** hook / cuerpo / CTA (marcar dónde corta el "ver más").
- **video:** una tabla de escenas: `| n | narración | en pantalla | acción visual | fuente |`. La narración es tentativa; en pantalla van ≤4 palabras; cada acción visual se ancla a la palabra de la voz que la nombra; la fuente dice de dónde sale cada dato. Reglas: un elemento persiste entre escenas para que el video no sea una serie de diapositivas; cada escena cierra quieta; los ejemplos se anuncian como ejemplos ("Un ejemplo:"); un término, un significado en todo el video (dos palabras para lo mismo se leen como dos cosas). El cierre lleva el llamado a hacer (link o QR) y la voz lo dice. Ritmo: ~2,2 palabras por segundo de voz.
- **carrusel:** tarjetas numeradas.
- **landing:** hero (promesa + CTA) → problema → solución → prueba → cierre/CTA.
- Respeta los límites del brief. *liviano* = el molde en bullets. *full* = + 1 frase de qué entra en cada slide/beat/tarjeta. Checkpoint.

**Etapa 4 · Copy** `[LAT]` → appendea `## 4. Copy`
El texto real, llenando la estructura. Corre en tres sub-pasos, los tres obligatorios (cuatro en video):

**4a. Draft:** llená el molde con el texto. ppt = por slide, título + bullets/idea + nota de presenter; post = el texto completo; video = la narración de cada escena en la tabla; carrusel = texto por tarjeta; landing = headline + subhead + body + CTAs por sección. Datos/casos que no existan → `[ABIERTO: ...]`, no inventar. *full* = + 2-3 variantes de apertura/hook.

**4b. Voz** `[DET]`: pasá el draft por `redactar` para que suene a la voz del usuario. Bajá la informalidad si la pieza va a terceros (cliente, audiencia externa). No anuncies que "estás aplicando el estilo", solo hacelo y mostrá el resultado.

**4c. Anti-slop** `[DET]`: pasá una vez por `anti-slop` (sacar reframes "no es X es Y", verbos metafóricos, puffery, vocab muerto, **0 em-dashes**). Cada palabra paga renta. Mostrá el resultado final, no el diff.

**4d. Narración congelada (solo video):** la narración de cada escena es el texto exacto que va a decir la voz. Con el OK de este checkpoint queda congelada, y recién ahí se genera la voz. Cada cambio posterior paga otra toma.

Checkpoint al cerrar 4c (y 4d en video): el usuario valida que suene a él antes del asset. Antes de cerrar, consolidá todos los `[imagen: ...]` del copy en `assets/imagenes-pendientes.md` (una fila por imagen: slide/contexto + descripción + estado). El usuario sourcea las imágenes aparte con esa lista.

**Etapa 5 · Asset final** `[LAT]`/`[DET]` → appendea `## 5. Asset final` + punteros a `assets/`
El entregable listo, 0 placeholders:
- **ppt/deck:** ofrecé los caminos y que el usuario elija. Si tiene un skill de pptx conectado → `assets/{SLUG}.pptx`. Para **Gamma**, ojo: Gamma no importa `.md` ni archivos de texto, solo acepta paste directo o `.docx`. Así que o (a) le pasás el copy pulido para pegar en Gamma → New → Generate, o (b) generás `assets/{SLUG}.docx` (H1 = título de slide, párrafo = cuerpo) y lo subís por Gamma → Import. (a) es el default por velocidad.
- **post:** texto final listo para pegar, con saltos de línea reales.
- **video:** el mp4, armado con `reference-video.md` §Cómo se hace y las herramientas de `video/`, en este orden: (1) una escena de muestra renderizada → OK del usuario (y del dueño de la marca si no es suya); (2) el resto por tandas, mostrando cada cambio como antes/después (`decisiones` sirve para eso); (3) la voz, por escena, recién con la narración congelada; (4) tiempos con Whisper y cortes en los silencios reales; (5) mezcla; (6) chequeos: cuadro final de cada escena mirado, voz contra acción medida con Whisper, conteos y QR decodificado. Los cuadros los mirás vos aunque un subagente diga que están bien. Si es un guion para que otro lo produzca: `assets/guion-video.md` + `assets/shotlist.md`.
- **carrusel:** texto + prompt de imagen por tarjeta. **landing:** prompt para el builder o el HTML, según dónde va a vivir.
- Varios medios → repetir Asset por medio (misma Historia, distinto asset). Checkpoint final → pieza terminada.

## Guía de estado (en cada checkpoint)
> **📍 Dónde estamos:** Etapa {N}/5: {nombre} ({profundidad})
> **✅ Qué cerramos:** {1-2 bullets + quedó en `pieza.md` §{etapa}}
> **⏭️ Qué sigue:** {próxima etapa + su profundidad propuesta}
> **🙋 Qué necesito de vos:** {la decisión que destraba, o "nada, decime dale y sigo"}

## Qué lee y escribe
- **Lee:** lo que el usuario te pasa de la pieza; `2. Áreas/yo/mi-estilo.md` (vía `redactar`). En video, `reference-video.md`.
- **Escribe:** `{BASE}/{SLUG}/pieza.md` (crea + appendea, una H2 por etapa) y `{BASE}/{SLUG}/assets/` (los assets). `contexto/` solo con OK.
- **Invoca (no reescribe):** `redactar` + `anti-slop` (Copy); `panel` (Historia de un video); el skill de pptx (Asset de deck); las herramientas de `video/` y un servicio de voz sintética (Asset de video).

## Cuándo NO usar
- Un texto corto de una sola pasada (responder un mail, un párrafo) → `redactar` directo, sin las 5 etapas.
- Validar un negocio nuevo con paid media (research → landings → campañas) → eso es otro proceso, no esto. Una landing **suelta** (evento, coming-soon, portfolio) sí es acá.

## Señales de que lo hiciste bien
- [ ] Cada etapa se cerró con un OK explícito antes de la siguiente (0 etapas blasteadas de una).
- [ ] Todo vive en UN doc que crece (`pieza.md`), no un archivo por etapa.
- [ ] El perfil de profundidad se propuso y el usuario lo ajustó antes de construir.
- [ ] Reuso real: Copy pasó por `redactar` + `anti-slop`; el asset de deck salió del skill de pptx o de Gamma.
- [ ] 0 em-dashes; 0 datos/testimonios inventados (faltantes como `[ABIERTO]`).
- [ ] **Video:** el dueño de la marca vio la muestra antes de producir (si no es tuya); la voz se generó una sola vez por narración congelada; cada acción cae a menos de 0,1 s de su palabra (Whisper); el cuadro final de cada escena fue mirado.

## Si algo sale raro
- **"Hacelo todo de una":** igual presentá checkpoints por etapa; ofrecé correr seguido pero sin saltear Historia ni Estructura (ahí se define si la pieza para de pie).
- **Tentación de un archivo por etapa:** NO. Un solo `pieza.md` que crece. Si quedó largo, podá prosa vieja, no partas el doc.
- **Falta `MEDIO`:** bloquea Estructura/Copy/Asset (cambian de forma por medio). Default ppt, pero confirmalo al arrancar.
- **Querer subcarpetas de contexto:** proponéselo al usuario antes; no crees `contexto/` por las dudas.
- **Video, el servicio de voz gratis dice que está ocupado:** no reintentes en la misma vuelta. Seguí con lo visual y probá en la siguiente; si hay apuro, un plan pago o la voz del usuario grabada.
- **Video, una frase cambia con la voz ya hecha:** generá solo esa escena y empalmala en los silencios con `video/empalmar.py`. Nunca cortes a mitad de palabra.
- **Video, un subagente dice "listo":** abrí los cuadros igual. Un subagente puede reportar cinco etiquetas visibles donde el cuadro muestra tres.

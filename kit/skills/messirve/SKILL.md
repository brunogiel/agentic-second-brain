---
name: messirve
description: >
  El filtro de entrada de lo que ves afuera. Le pasás un tuit, un video de YouTube,
  un post, un repo, un artículo o el skill de un amigo, y lo cruza contra lo que ya
  tenés armado en tu brain: te dice si ya lo tenés, qué le podés robar si lo tenés,
  y si no lo tenés, si te sirve de verdad y lo agrega. Usala cuando digas "mirá esto
  a ver si me sirve", "¿esto lo tengo?", "¿me sirve?", "fijate si esto suma", "te paso
  un tuit", "mirá este video", "qué le puedo robar a esto", "compará esto con lo mío",
  o cuando quieras intercambiar skills con otra persona (modo figuritas). Lee la fuente
  de verdad antes de opinar y no agrega nada sin mostrarte qué entra.
---

# messirve: pasar lo de afuera por el filtro de lo tuyo

## Qué es
Lo que ves afuera llega suelto: un tuit con un truco, un video de 40 minutos, el repo de alguien, el skill que te pasó un amigo. Casi todo se pierde, y lo poco que guardás queda como link muerto en una nota. Esta skill le pone una puerta a ese flujo: **una sola entrada, y un veredicto por cada cosa que la fuente promete.**

El principio: **antes de decidir si algo sirve, hay que saber qué ya tenés.** El error caro no es dejar pasar algo bueno, es agregar la cuarta versión de algo que ya tenías, o decir "no lo tengo" sobre algo que sí. Por eso el inventario va primero y el veredicto después.

Lo que se acumula así **compone**: cada pasada mejora una pieza existente o suma una que te faltaba, y el brain trabaja mejor la próxima vez.

## Qué lee y escribe
- **Lee:** la fuente real (el hilo completo, la transcripción del video, el README del repo, el `SKILL.md` que te pasaron), y tu brain (el `CLAUDE.md` raíz, tu carpeta `skills/`, tus proyectos, tu `como-trabajo.md`).
- **Escribe (con tu OK):** un skill nuevo en `skills/`, un parche sobre un skill que ya tenías, una regla en `como-trabajo.md`, o una entrada en el inbox si todavía no está claro dónde va.
- **Nunca escribe sin mostrarte antes** qué archivo toca y con qué contenido.

## Los tres veredictos
Por cada capacidad que la fuente promete, uno de estos tres:

| Veredicto | Qué significa | Qué devuelve |
|---|---|---|
| **Ya lo tengo** | Tu brain ya cubre eso | Dónde lo tenés, y en una línea por qué lo tuyo alcanza |
| **Lo tengo, pero** | Lo tenés, y el de afuera hace una parte mejor | El diff concreto: qué línea, paso o regla le robás, y a cuál de tus archivos entra |
| **No lo tengo** | Es capacidad nueva | Pasa por el gate de abajo. Si pasa, se arma. Si no, se descarta con el motivo escrito |

El veredicto del medio es el que más rinde y el que más se saltea. "Ya lo tengo" es la respuesta cómoda que corta el análisis antes de tiempo: si la fuente cubre lo mismo que vos, todavía falta preguntar **cómo** lo cubre.

## El gate de "me sirve"
Sin criterio, todo sirve, y un brain con cien skills que no usás es peor que uno con diez que sí. Para entrar, tiene que cumplir **las dos**:

1. **Un caso tuyo, con nombre.** Podés decir la última vez que hiciste eso a mano, o el próximo momento concreto en que lo vas a usar. "Está bueno" y "algún día me va a servir" no son casos.
2. **Nadie más lo cubre.** No hay ya un skill tuyo al que esto sea un parche. Si lo hay, no es un skill nuevo: es el veredicto del medio.

Si falla la 1, va al inbox como idea, no al brain como capacidad. Si falla la 2, se convierte en parche.

## Flujo

### Paso 0: ¿Hay brain contra qué comparar? [DET]
Mirá si existe un brain escribible: un `CLAUDE.md` raíz, carpetas tuyas, una `skills/`. Si lo único que hay es el kit del método (sin nada tuyo todavía), no hay contra qué cruzar: decílo y ofrecé armarlo con `/brain-coach`. Nunca escribas adentro del `kit/` del método. Frená acá.

### Paso 1: Leer la fuente de verdad [DET]
Abrir lo que te pasaron **entero**, no el título ni el primer párrafo:
- Link o hilo: traerlo y leerlo completo, incluidas las respuestas si ahí está la carne.
- Video: la transcripción. Si no hay, decilo y pedí otra vía; no resumas un video por su título.
- Repo: el README y los archivos que nombra, no la descripción de GitHub.
- Skill que te pasaron: el `SKILL.md` completo, sobre todo el flujo y los gates.
- Captura o screenshot: leer lo que se ve, y marcar explícitamente lo que quedó cortado.

Si la fuente no se puede abrir, decilo y frená. **Un veredicto sobre algo que no leíste no vale**, y es la forma más rápida de meterle basura al brain.

### Paso 2: Listar lo que la fuente promete [LAT]
Sacar las capacidades concretas, una por línea. Capacidad es algo que **se hace**, no un tema. "Habla de memoria" no entra; "guarda un hecho durable y lo relee al arrancar" sí.

Descartar acá lo que sea puro marketing, opinión o hype sin mecanismo atrás. Si de una fuente entera sale una sola capacidad, está bien: ese es el caso normal.

### Paso 3: Inventariar lo tuyo [DET]
Antes de comparar nada, leer qué tenés: el `CLAUDE.md` raíz (el mapa), la carpeta `skills/`, los proyectos activos, `como-trabajo.md`. Buscar por **lo que hace cada cosa**, no por cómo se llama: dos skills con nombres distintos pueden hacer lo mismo, y uno que se llama parecido puede hacer otra cosa.

Sin este paso los veredictos salen mal para los dos lados: "no lo tengo" sobre algo que tenías, y "ya lo tengo" sobre algo que se le parece de nombre.

### Paso 4: Un veredicto por capacidad [LAT]
Cruzar cada capacidad del Paso 2 contra el inventario del Paso 3 y asignar uno de los tres veredictos. Para las que caen en **No lo tengo**, correr el gate de "me sirve" y dejar escrito el resultado, incluso cuando el resultado es que no pasa.

Para las que caen en **Lo tengo, pero**, el diff tiene que ser accionable: qué texto entra, en qué archivo, en qué sección. "Podría mejorarse" no es un diff.

### Paso 5: Mostrar y escribir [DET]
Mostrar la tabla de veredictos y, abajo, exactamente qué se va a escribir y dónde. Esperar tu OK.

Con el OK: escribir, y verificar releyendo lo que quedó. Un skill nuevo se arma con la anatomía de `crear-skill`, no a mano suelta. Un parche entra en la sección que corresponde del archivo que ya existía, sin duplicar la pieza entera.

Lo que no pasó el gate va al inbox con una línea de por qué, o se descarta. Que quede escrito el descarte sirve: la próxima vez que alguien te pase lo mismo, ya lo tenés resuelto.

## Modo figuritas (intercambio con otra persona)
Cuando en vez de un link tenés la carpeta de skills de alguien, corré el mismo flujo en **las dos direcciones**:

- **Lo que le robás:** sus skills contra tu inventario, con los tres veredictos de siempre.
- **Lo que le das:** tu carpeta contra la de esa persona, y cuáles de los tuyos le cubren un hueco. Sirve para la vuelta del intercambio, y además te muestra qué tenés que ella no.

Antes de pasar algo tuyo, la pasada de privacidad es obligatoria: sacar nombres de clientes, montos, paths personales, credenciales y cualquier dato de terceros. **Un skill tuyo suele tener adentro tu contexto**; lo que se intercambia es el mecanismo, no tus datos.

## Output esperado
Primero la tabla, y recién después lo que se escribe:

| Capacidad de la fuente | Veredicto | Dónde / qué entra |
|---|---|---|
| {lo que la fuente hace, en una línea} | Ya lo tengo / Lo tengo, pero / No lo tengo | {tu archivo, el diff concreto, o el motivo del descarte} |

Abajo: el contenido exacto a escribir, por archivo, esperando OK. Y una línea de cierre con lo que quedó en el inbox y lo que se descartó.

## Cuándo NO usar
- Para guardar un link que querés leer después: eso es el inbox, y no hace falta cruzarlo con nada.
- Para el paneo de salud de tu brain, sin fuente externa: eso es `auditar-sistema`.
- Para mejorar un skill tuyo contra su propia rúbrica: eso es `evaluar-skill`.
- Para armar un skill desde cero cuando ya sabés qué querés: eso es `crear-skill` directo.

## Señales de que lo hiciste bien (chequeo binario)
- [ ] Leíste la fuente completa antes de opinar, y si no se podía abrir, frenaste en vez de adivinar.
- [ ] Inventariaste lo tuyo **antes** de asignar veredictos, buscando por lo que hace cada cosa y no por el nombre.
- [ ] Cada capacidad de la fuente tiene su veredicto, incluidas las que terminaron descartadas.
- [ ] Los "Lo tengo, pero" traen un diff accionable: qué texto, qué archivo, qué sección.
- [ ] Lo que entró como nuevo pasó las dos condiciones del gate, y podés nombrar el caso de uso concreto.
- [ ] Nada se escribió sin que vieras antes el archivo y el contenido.
- [ ] Lo descartado quedó con el motivo escrito, no desaparecido.
- [ ] En modo figuritas, lo que sale para afuera pasó la pasada de privacidad.

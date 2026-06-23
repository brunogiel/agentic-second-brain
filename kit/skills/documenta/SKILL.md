---
name: documenta
description: >
  Forcing function de cierre: barre TODA la conversación activa y guarda lo durable
  donde corresponde (el log del proyecto, su estado vivo, el inbox, tu memoria, cómo
  trabajás), sin perder lo que pasó. Usala cuando digas "documentá", "documentá esto",
  "guardá lo que hicimos", "registrá los cambios", "no perdamos esto", "dejá esto
  asentado", "cerrá y documentá", o al cerrar una sesión con decisiones, cambios
  hechos o hallazgos. Detecta el proyecto activo, rutea cada item a su lugar canónico,
  y escribe (lo interno directo; lo externo o compartido con confirmación). NO es un
  resumen: es ruteo + escritura.
---

# documenta: guardar lo de la conversación donde corresponde

## Qué es
Una pasada de cierre para **no perder** lo que se decidió, cambió o aprendió en la conversación. No es un resumen para vos: es **ruteo + escritura** a los lugares durables de tu sistema, para que la próxima sesión (o vos dentro de un mes) lo encuentre solo. La conversación es volátil, esto la fija.

El principio: **documentar es ruteo, no volcado.** Cada item va a UN lugar canónico, no se duplica entre el log del proyecto, el inbox y tu memoria. Lo interno (archivos de tu brain) se escribe directo; lo externo o compartido se muestra y se confirma antes.

## Qué lee y escribe
- **Lee:** la conversación entera (no solo lo último) y el `CLAUDE.md` del proyecto activo (más su `STATUS.md`/`ESTADO.md` si tiene) para conocer sus convenciones.
- **Escribe directo (interno):** el `Log de decisiones` del proyecto, su estado vivo, el inbox, tu memoria, cómo trabajás. Cada escritura se verifica releyendo la entrada afectada.
- **Confirma antes (externo/compartido):** cualquier destino fuera de tu brain (un doc que comparte un equipo, un tracker conectado, un repo). Se muestra qué y dónde, y se espera tu OK, salvo que ya lo hayas pedido explícito en la charla.

## El mapa de ruteo
Cada item de la conversación va a su destino canónico según qué tipo de cosa sea:

| Tipo de item | Destino canónico |
|---|---|
| Decisión o avance de un proyecto (con su porqué) | el `Log de decisiones` del `CLAUDE.md` del proyecto activo (o su `STATUS.md`/`ESTADO.md` si es estado vivo) |
| Idea suelta, cosa a decidir después, hilo que quedó abierto | el inbox del brain (`0. Inbox/INBOX.md`) |
| Hecho durable sobre vos (que no debe re-litigarse) | `2. Áreas/yo/MEMORIA.md` |
| Cómo querés que trabaje (corrección o approach confirmado) | `2. Áreas/yo/como-trabajo.md` |
| Cambio de tu voz o tu forma de escribir | `2. Áreas/yo/mi-estilo.md` (si existe) |
| Doc compartido con un destino externo conectado | proponer dónde y confirmar antes de escribir |
| Lo que no tiene dueño claro | proponer dónde y preguntar antes de escribir |

Si tu sistema tiene un destino externo conectado (un Notion compartido, una hoja de cálculo, un repo), proponelo y confirmá antes de escribir. Nunca se empuja algo afuera sin que lo veas.

## Flujo

### Paso 0: ¿Hay sistema todavía? [DET]
Antes de rutear nada, mirá si hay un brain escribible: un `CLAUDE.md` de proyecto, carpetas PARA (`0. Inbox`, `1. Proyectos`, `2. Áreas`...), un destino donde guardar. Si lo único que hay es el kit read-only del método (sin proyecto, sin carpetas tuyas), todavía no tenés sistema. No rutees ni escribas, y NUNCA escribas dentro del `kit/brain/` del método. Decílo claro: "todavía no tenés un sistema para documentar; lo armamos con `/sabe-coach` y volvemos a correr esto". Frená acá.

### Paso 1: Ubicar el contexto [DET]
- Detectar el o los proyectos activos de la conversación (por la carpeta donde estás + de qué se habló).
- Leer su `CLAUDE.md` (y su `STATUS.md`/`ESTADO.md` si tiene) para conocer **sus** convenciones: ¿tiene `Log de decisiones`? ¿un estado vivo aparte? ¿algún destino externo conectado?
- Eso define el mapa de destinos posibles para esta conversación.

### Paso 2: Barrer TODA la conversación [LAT]
Releer la charla **entera**, no solo lo último. Extraer candidatos, clasificados por tipo:
- **Decisión:** se eligió un camino, con su porqué.
- **Cambio hecho:** se tocó algo real (un archivo, una config, un doc, un borrador).
- **Hallazgo o diagnóstico:** cambió el entendimiento de algo; corrige un doc o una memoria previa.
- **Cómo querés que trabaje:** una corrección o la confirmación de un approach.
- **Contradicción:** algo que choca con lo que dice un doc o tu memoria.
- **Idea suelta:** sirve más allá de este proyecto, o queda para después.
- **Hilo abierto:** quedó pendiente (va al inbox).

### Paso 3: Rutear cada item [DET]
Mandar cada candidato a su destino canónico según el mapa de arriba. Antes de escribir cada item: **chequear que no exista ya**. Si existe, **actualizar** esa entrada en vez de crear una nueva (vale para la memoria, los logs y todo lo que sea append).

### Paso 4: Escribir [DET]
- **Interno** (log del proyecto, estado vivo, memoria, como-trabajo, inbox): escribir directo.
- **Externo o compartido** (cualquier destino conectado fuera de tu brain): mostrar exactamente **qué** se va a escribir y **dónde**, y confirmar antes. Excepción: si ya lo pediste explícito en la conversación.
- **Verificar** cada escritura releyendo la entrada afectada.

### Paso 5: El manifiesto [DET]
Cerrar con una tabla `item | destino | status`. Dejar marcado con claridad lo que quedó como **propuesta esperando tu OK**.

## Output esperado (el manifiesto)
Una tabla de qué se documentó y dónde, con el estado de cada item:

| Item | Destino | Status |
|---|---|---|
| {la decisión / el cambio / el hallazgo} | {el archivo o lugar canónico} | escrito / actualizado / ya existía / **propuesto (espera OK)** |

Lo interno ya escrito y verificado; lo externo confirmado o presentado como propuesta. Cero duplicados.

## Cuándo NO usar
- Charla trivial o puramente factual, sin nada durable que guardar.
- Para el paneo periódico de salud de tu sistema: eso es `auditar-sistema`.
- Como reemplazo de pensar dónde va algo: si el dueño no está claro, se pregunta, no se inventa.

## Señales de que lo hiciste bien (chequeo binario)
- [ ] Barriste la conversación **entera**, no solo la última acción.
- [ ] Cada item quedó en **un** solo lugar canónico (sin duplicar entre log, inbox y memoria).
- [ ] Antes de escribir cada item, chequeaste si ya existía; si existía, actualizaste en vez de duplicar.
- [ ] Lo interno se escribió directo y se verificó releyendo.
- [ ] Lo externo o compartido nunca se escribió sin que lo vieras y dieras OK.
- [ ] Lo que no tenía dueño claro se preguntó, no se forzó a un destino cualquiera.
- [ ] Cerraste con el manifiesto `item | destino | status`, marcando lo que quedó esperando OK.

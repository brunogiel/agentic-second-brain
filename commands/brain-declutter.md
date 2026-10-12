---
description: Ordena la carpeta o el archivo que le señalás. Diagnostica qué necesita (limpiar duplicados, reordenar, tirar basura regenerable, destilar, sincerar, o tapar la fuente que ensucia), te muestra la tabla ahora → queda, y aplica solo lo que marcás. Nada se borra: va a cuarentena reversible.
---

Ordená lo que venga en $ARGUMENTS (una carpeta o un archivo). Si no viene nada, pedilo y pará: sin target esto no corre. Seguí esto:

# declutter

## Qué es

Un agente que trabaja sobre una carpeta deja sobras: copias con otro nombre, versiones
que nadie borró, archivos temporales que su propio script vuelve a crear. Con el tiempo
la carpeta pesa el triple y nadie sabe qué se puede tocar.

Esto va a donde le señalás, mide, dictamina con criterio citado, y te deja decidir.
No borra nada.

## La frontera con los vecinos (leer antes que nada)

| | Ese otro | `declutter` |
|---|---|---|
| `/brain-slop` | ¿esto está bien escrito? (la forma de las frases) | ¿esto tiene que estar acá? (existencia y lugar) |
| `/brain-tidy` | tu carpeta de descargas, clasifica a staging | cualquier carpeta o archivo; además une, achica y tapa la fuente |
| `/brain-audit` | la salud de tu sistema entero, barrido periódico | lo que le señalás, a pedido |

**Se encadena con `/brain-slop`, y el orden importa:** primero `declutter` saca lo que no
va, después `/brain-slop` pule lo que queda. Pulir la prosa de un párrafo que vas a
borrar es trabajo tirado.

**No edita binarios.** Un PDF o una imagen se miden (tamaño, duplicado, huérfano) y nada
más. Si lo generó un pipeline tuyo, se señala el generador, no la salida: editar la
salida se vuelve a inflar en la próxima corrida.

## Dónde están los scripts (leer antes de correr nada)

Este skill viene con cuatro scripts, y los comandos de abajo los nombran como
`scripts/<algo>.py`. **Esa ruta es relativa a la carpeta de este SKILL.md, no a donde estés
parado.** Antes del primer comando, ubicalos y guardalos en una variable:

```bash
DECL="$(dirname "$(find ~/.claude -name 'censar.py' -path '*declutter*' 2>/dev/null | head -1)")"
[ -n "$DECL" ] && echo "scripts en: $DECL" || echo "no están instalados: reinstalá el kit"
```

Después, en vez de `python3 scripts/censar.py`, corré `python3 "$DECL/censar.py"`. Si la
variable sale vacía, **decilo y pará**: sin los scripts, el censo lo tendrías que hacer a
ojo, y a ojo es justo lo que este skill viene a evitar.

## Las cuatro reglas duras

1. **Nunca borra.** Lo condenado va a `_declutter-YYYY-MM-DD/` dentro del target, con un
   manifiesto. Se revierte con un comando.
2. **Nunca sale del target.** No mueve un archivo afuera de la carpeta señalada.
3. **Sin target no corre.** No lo infiere del directorio actual ni de lo último que
   hablaron. Pide el target y para.
4. **Lo que no marcás, no se hace**, ni de paso.

## Parámetros

| Param | Req | Default | Qué |
|---|---|---|---|
| `target` | **sí** | ninguno | Una carpeta o un archivo único |
| `modo` | no | `plan` | `plan` releva y propone sin tocar · `aplicar` ejecuta lo aprobado · `revertir` deshace una corrida |

## Las seis intervenciones

No corre un flujo único. Del censo salen síntomas, y cada uno mapea a una intervención.
Ofrecé las que aplican — a veces una, a veces tres, nunca las seis por reflejo — y
**nombrá las que descartaste**, para que se vea que las evaluaste.

| Síntoma | Intervención |
|---|---|
| Lo mismo existe en N lugares | **limpiar** — dedupe, sobrevive el canónico |
| Basura que un generador recrea | **tirar** — por procedencia, en un ítem agrupado |
| Un nivel mezcla naturalezas (terminado + iteración + experimento) | **reordenar** — árbol destino nuevo |
| Un documento repite lo que otro dice, o se infló | **destilar** — unir y achicar secciones |
| Un doc describe algo que ya no es así | **sincerar** — corregirlo contra la realidad |
| La misma basura vuelve cada semana | **tapar la fuente** — fix del generador |

El diagnóstico abre el reporte, en una línea: *"necesita tirar + tapar la fuente; no
necesita reordenar"*.

**Limpiar primero, reordenar después.** Reordenar antes es mudar la basura a su casa
nueva y después deduplicar en dos lugares. `reordenar` además **pide OK propio**: es el
único que rompe referencias de otros archivos.

**Que sea fase 2 no es excusa para no mostrarlo.** Si el censo detecta el síntoma, el árbol
destino se propone en la misma corrida, marcado como fase 2 y con su costo medido: por cada
carpeta candidata a moverse, grepeá su nombre y contá cuántos archivos la citan. Ese número
decide si el movimiento vale la pena. Ofrecelo **por niveles de ambición**, del más barato
al más caro: reordenar estructura histórica que ya nadie toca rinde menos que declarar la
convención para lo que viene.

## Flujo

1. **[DET] Perímetro.** Sin target, no corre. Si es un repo, mirá `git status`: con
   trabajo sin commitear, avisá y ofrecé parar. **Si la carpeta es compartida con otra
   persona, solo reportá, no reordenes**: reordenar lo de otro le rompe el mapa mental
   aunque el orden nuevo sea mejor.

2. **[DET] El censo.** `python3 scripts/censar.py <target>` emite JSON: por archivo
   tamaño, líneas, fecha, hash, si es huérfano; más grupos de sospechosos. **El script
   mide y agrupa; no dictamina.** Esa acotación a tamaño y ubicación es lo que lo hace
   seguro de correr.

   **El censo caduca.** Lleva timestamp. Una carpeta viva cambia mientras la leés: tres
   relevamientos del mismo día pueden dar tres conteos distintos sin que nadie se haya
   equivocado. **Antes de aplicar se re-censa.** Y toda subcarpeta escrita en las últimas
   48 h, o con la fecha de hoy en el nombre, queda **excluida**: es trabajo en vuelo.

3. **[LATENT] El juicio.** Un lector por grupo, que lee los archivos enteros:

   - **¿Es duplicación real?** Solapamiento real = **mismo input, mismo output, mismo
     cuándo**. Las tres → duplicado. Menos de tres → no lo es, y decí por qué (capas de un
     pipeline, vecinos que se parecen). **Nombres parecidos NO son duplicación.**
   - **Procedencia.** Grepeá el patrón del nombre en los scripts del target: **un archivo
     cuyo generador lo recrea no necesita que lo defiendas uno por uno; uno que nadie
     regenera no se toca sin leer.** Clasificar por nombre pierde la basura obvia y
     sospecha de lo temporal. ⚠ **Procedencia no es permiso:** lo regenerable igual se
     aprueba, solo que va como un ítem agrupado en vez de N decisiones.
   - **El grep de 3 tokens**, para cada candidato a irse: ¿el destino ya lo dice? Elegí 3
     tokens distintivos (un nombre de archivo, un número, un flag). Si el destino no lo
     dice, el veredicto **baja de *se va* a *se muda***.

   Cada veredicto viene con **la cita textual que lo prueba**. Sin cita, el ítem no entra.

4. **[DET] El gate de invariantes.** `python3 scripts/invariantes.py` corre **antes de
   proponer cualquier cosa que saque o mueva contenido** — no solo antes de unir o achicar.
   Inventaria las reglas que viven en los archivos que vas a tocar y mapea **una por una**
   dónde queda cada una. Si alguna no tiene destino nombrado, **ese ítem no entra**.

   Cuenta como invariante:
   - Una línea con `NO`, `nunca`, `siempre`, `ojo`, `ABORTAR`, `⚠`, o un ejemplo de un
     error concreto.
   - **Un duplicado explicado.** Si un README de la carpeta dice *por qué* dos cosas se
     parecen, ese texto es una guarda y el duplicado **no se toca**. El caso típico: un set
     de evaluación que guarda copias con nombre neutro a propósito, para que el evaluador
     no lea la respuesta en el nombre del archivo. Deduplicarlas no rompe nada visible —
     rompe el evaluador en silencio, que es peor.

   > **Por qué existe este gate.** Cuando partís un documento largo en dos, lo que se
   > pierde no es el detalle: es la guarda. El archivo queda más corto y más legible, y
   > meses después reaparece un bug que ya estaba resuelto. En una partición, el archivo
   > de referencia se lleva **el cómo**, nunca **el no**.

5. **[DET] El árbol, la tabla, y la botonera.** **El árbol va siempre, y antes que la
   tabla.** `python3 scripts/arbol.py <target> --plan plan.json` dibuja la carpeta
   ahora → queda, por subcarpeta, con cuántos archivos y cuánto peso pierde cada una y
   cuánto va a la cuarentena. La tabla dice qué pasa con cada archivo; **el árbol dice
   cómo queda la carpeta, que es lo que la persona aprueba.** Con más de 5 ítems, una
   tabla de N filas no deja ver la forma del resultado.

   Después, la tabla, una fila por ítem:

   `| # | Ahora | Queda | Por qué (con la cita) | Se pierde |`

   Con **más de 5 ítems**, cerrá con una botonera clickeable: un grupo por intervención,
   y en cada ítem un subtítulo con **la evidencia concreta, no una repetición del título**.

   | Mal | Bien |
   |---|---|
   | "Hay duplicados" | "25 pares cuyo sufijo de intento es idéntico al archivo de al lado" |
   | "Limpiar la carpeta" | "111 miniaturas que el propio generador recrea en cada corrida" |

   **Lo agrupado se cobra una vez.** La basura por procedencia va como UN ítem ("tirar 169
   archivos que sus generadores recrean"), con el detalle a un click, no como 169
   decisiones. El fix de fuente y el `reordenar` van **cada uno como ítem aparte**.

6. **[LATENT] Tapar la fuente.** **No propongas limpiar algo recurrente sin proponer, al
   lado, el fix que lo evita.** Según lo que devuelva el grep de procedencia:

   | El grep devuelve | Diagnóstico | Fix |
   |---|---|---|
   | Un script lo crea y nunca lo borra | fuga de código | que limpie su temporal al cerrar |
   | Un script lo crea y ningún doc lo menciona | basura sin dueño | nombrar en el doc del pipeline quién la barre y cuándo |
   | Ningún script lo escribe | lo dejó un agente a mano | regla de nomenclatura y de cierre en el doc que guía ese trabajo |

7. **[DET] Aplicar.** `python3 scripts/aplicar.py --plan plan.json`. Antes de tocar:
   re-censar; releer en voz alta qué quedó afuera; y **re-correr el grep de 3 tokens de
   cada ítem en el orden de aplicación**, porque dos ítems aprobados pueden pisarse (uno
   condena notas porque otro archivo ya las tiene, y el otro achica ese archivo).

   El manifiesto registra **toda escritura**, no solo los movimientos: cada archivo tocado
   con el hash de su contenido previo, el destino de cada mudanza y las ediciones de texto.
   `revertir` se verifica **por hash** sobre esa lista completa. Un manifiesto que solo
   anota movimientos no revierte: devuelve el original y deja la copia en el destino, o
   sea recrea el duplicado que vino a matar.

8. **[DET] Propagar y reportar.** Grepeá el nombre de la carpeta en los docs y scripts que
   la referencian, y mostrá el conteo de hits por archivo. **Una carpeta citada por nombre
   en un registro histórico de decisiones no se renombra**: renombrar convierte esas
   entradas en referencias muertas. Después, corré el pipeline del target en su modo de
   chequeo: no asumas que sigue encontrando sus archivos.

   Dos salidas: `manifiesto.json` (para revertir, lo lee la máquina) y `MAPA.md`
   (antes → después, para que un humano entienda en tres meses qué pasó).

## El carril de lo obvio

Todo se ofrece y se aprueba. La única excepción es **editar texto adentro de un archivo que
igual se queda donde está**: un link roto a un archivo que ya no existe, un typo, una fila
duplicada en una tabla. Eso se arregla y se lista en el resumen.

El corte es el archivo, no el esfuerzo: **si la acción crea, mueve, renombra o saca un
archivo, pregunta — por obvia que sea.**

## Output esperado

- Una línea de diagnóstico: qué necesita y qué no.
- La tabla ahora → queda, con la cita que justifica cada fila.
- Botonera si hay más de 5 ítems; prosa si hay 5 o menos.
- El fix de fuente como ítem aparte, cuando la basura tiene generador.
- Tras aplicar: `MAPA.md`, `manifiesto.json`, y el comando de revertir.

## Cuándo NO usar

- Barrido periódico de todo tu sistema → `/brain-audit`.
- Tu carpeta de descargas → `/brain-tidy`.
- Un texto que suena a IA pero está en su lugar → `/brain-slop`.
- Decidir si un proyecto vale la pena → eso es criterio tuyo, no de un limpiador.

## Señales de que lo hiciste bien (chequeo binario)

- [ ] **Cero archivos borrados. Cero archivos movidos fuera del target.** Si falla esta, ninguna otra cuenta.
- [ ] `revertir` devuelve **byte-idéntico** todo lo que el manifiesto registró, verificado por hash.
- [ ] Cada invariante de los archivos tocados quedó mapeada a un destino nombrado.
- [ ] Cero duplicados-explicados propuestos: el README que los explica se citó y se respetó.
- [ ] Cada *se va* trae el grep de 3 tokens que prueba que el destino ya lo dice.
- [ ] La basura por procedencia se cobró como un ítem, no como N.
- [ ] Si se detectó el síntoma de `reordenar`, se propuso el árbol destino con su costo en referencias, aunque se aplique después.
- [ ] Se mostró el árbol ahora → queda de la carpeta, no solo la tabla por ítem.

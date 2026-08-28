---
description: Convierte un pedido en criollo en el contrato de lo que se va a hacer: requisitos numerados y una verificación chequeable por cada uno. Antes de construir.
---

Armá el spec de lo que te pidan ($ARGUMENTS): requisitos numerados y cómo se verifica cada uno. No construyas nada. Seguí esto:

# spec — el contrato, antes de hacer

## Qué es

Un plan te dice qué se va a tocar. Un spec te dice **contra qué se va a chequear**. Son cosas
distintas y la segunda es la que casi nunca se escribe.

Sin spec pasan dos cosas, las dos silenciosas. La primera: los huecos de producto los cierra el
modelo por su cuenta, sin avisar, porque leyó el código y "dedujo". La segunda: quien revisa el
resultado deriva los criterios del mismo pedido que produjo el resultado, así que el que hizo el
trabajo termina fijando la vara con la que se lo juzga.

**Las dos cosas que este skill agrega**, y si no hace estas dos es un plan con pasos de más:

1. **Pregunta lo que la fuente no sabe.** Los huecos se nombran y se preguntan, no se deducen.
2. **No cierra sin una verificación chequeable.** Medido sobre 56 planes reales: 51 tenían sección
   de verificación, pero solo **15 fijaban un valor esperado concreto** y **13 nombraban un edge
   case**. El gate del paso 6 fuerza esas dos.

## Parámetros

- `objetivo` (requerido): la tarea en criollo.
- `dominio`: `codigo` (default si estás parado en un repo) | `entregable`. Cambia el
  reconocimiento, dónde se escribe y la rúbrica del gate. El resto del flujo es idéntico.
- `profundidad`: `full` (default) | `express` (tope 2 preguntas). Si toca un archivo y no abre
  decisiones, usá `express` sin preguntar.
- `interactivo`: `true` (default) | `false`. En `false` no se pregunta nada: cada hueco se escribe
  como una línea `SUPUESTO:` visible, **nunca se resuelve en silencio**.

## Cuándo NO correrlo

- **Trabajo exploratorio**, donde el descubrimiento es el trabajo. Un spec adelante te encierra en
  lo que ya pensabas.
- **Un fix de una línea.** El spec sale más caro que el cambio.
- **Si el repo ya tiene su propio sistema de specs.** Dos specs compitiendo es peor que ninguno:
  abstenete y devolvé el control.

## Flujo

1. **Abstención** [DET]: ¿ya hay un sistema de specs en este repo, o la pieza cae en un flujo que
   tiene el suyo? Si sí, decilo y terminá.

2. **Reconocimiento** [LATENT]: informate **antes de abrir la boca**. Cero preguntas en este paso.
   - `codigo`: qué archivos toca, qué convenciones sigue el repo, cómo se verifica hoy algo
     parecido, qué hay corriendo en producción.
   - `entregable`: **quién lo recibe y qué sabe ya**, de qué fuente sale cada dato, qué se le mandó
     antes sobre lo mismo, y qué reglas duras aplican.

3. **Lista de huecos** [LATENT]: escribí qué **no** se puede resolver leyendo la fuente. Entran
   solo: decisiones de producto, umbrales de negocio, comportamiento ante el caso raro, qué se dice
   y qué no, y el borde del alcance. **Descartá todo hueco que la fuente ya responde:** una pregunta
   cuyo dato estaba en el repo es un bug de este skill, no una pregunta.

4. **Entrevista acotada** [LATENT]: máximo **5 preguntas en `full`, 2 en `express`**, de a una,
   y **la primera opción siempre es lo que asumís**, para que se confirme con un click. Cortá antes
   si no queda hueco: **cero preguntas es un resultado válido y bueno.**

5. **Escritura** [DET]: escribí el spec con el template de abajo. Slug corto en kebab-case.

6. **Gate** [DET]: corré los 6 checks de tu dominio sobre el spec recién escrito. **Si alguno falla,
   no cerrás:** completás y volvés a chequear. Un spec que no pasa el gate no se entrega.

7. **Handoff** [DET]: devolvé el path, los requisitos en una línea cada uno, y los supuestos
   abiertos. Si hay un skill que va a verificar después, pasale este spec: ahí deja de derivar
   criterios propios y chequea contra tus `Rn`.

## Template

```markdown
# <título del cambio>

## Objetivo
Una o dos líneas: qué problema resuelve, para quién.

## Contexto (leído de la fuente)
Qué encontré que condiciona la solución. En entregable: quién lo recibe y qué sabe ya.

## Requisitos
- **R1.** <requisito verificable, uno por línea>
- **R2.** ...

## Fuera de alcance
Qué NO se hace acá, y adónde va si va a algún lado.

## Edge cases
<caso> → <comportamiento esperado>
En entregable: <cómo lo puede leer mal quien lo recibe> → <qué en la pieza lo previene>
(o la línea explícita: "Sin edge cases relevantes: <por qué>")

## Verificación
- **R1** → <qué correr, dónde mirar, contra qué fuente> → **debe dar** <valor o estado concreto>
- **R2** → ...

## Guardrails
Qué NO se toca durante la verificación. En entregable: qué no puede salir en la pieza.

## Supuestos abiertos
- SUPUESTO: <lo que asumí sin confirmar>
```

**Por qué los requisitos van numerados.** Los planes suelen listar *cambios* ("1. la query, 2. el
service, 3. la tabla"), no *requisitos*. Contra una lista de cambios, quien revisa no puede decir
"falla R3" sin interpretar. Con `Rn`, el review es mecánico: recorre la lista y marca cuál falla.

## El gate: 6 checks

Los tres primeros formalizan lo que se suele hacer bien igual. **G4 y G5 son los que fallan más de
dos tercios de las veces**, y son la razón de ser del gate.

| # | `codigo` | `entregable` |
|---|---|---|
| **G1** | Cada `Rn` tiene su línea en Verificación. Falla si hay un requisito sin cómo chequearlo | igual |
| **G2** | El camino feliz se verifica en el **artefacto real**. Falla si solo hay type-check, lint o build | **Cada dato tiene su fuente citada.** Falla si hay un número que sale de memoria o "de la conversación" |
| **G3** | Guardrail declarado si la verificación toca producción o datos vivos | **Qué no puede salir** de la pieza. Falla si va a un tercero y no lo declara |
| **G4** | Al menos **un valor esperado concreto** si toca datos, cálculo o conteo. Falla con "chequear que funcione" | **Qué dato tiene que aparecer y de dónde sale.** Falla con "que los números estén bien" |
| **G5** | Al menos **un edge case nombrado**, o por qué no hay | **Cómo cae si lo leen mal:** el malentendido probable y qué lo previene |
| **G6** | "Fuera de alcance" declarado. Falla si el build queda libre de inventar scope | igual: qué no se promete en esta pieza |

Los checks son textuales sobre el propio `.md`. Se corren leyéndolo, no hace falta script.

**G2 y G3 en `entregable` no son adorno.** Salen de dos incidentes reales: inflar la evidencia
cuando no había fuente, y mandar a un tercero material que no le correspondía. Un spec de
entregable que no los declara no está terminado.

## Output esperado

- El spec escrito y pasando los 6 checks.
- En el chat, un cierre corto: el path, los `Rn` en una línea cada uno, y los supuestos si quedaron.
  Nada de repetir el spec entero.
- **Cero código escrito y cero entregable escrito.** Ni una línea del mail, ni un commit, ni un
  branch. Este skill define contra qué se va a chequear; escribirlo es de otro.

## Success metrics

- 100% de los specs entregados pasan los 6 checks. El que no pasa, no se entrega.
- ≤5 preguntas en `full`, ≤2 en `express`, y **cero preguntas cuyo dato estuviera en la fuente**.
- Quien revise después puede decir "falla R3" sin interpretar ni derivar criterios propios.
- En modo no interactivo, todo hueco queda visible como `SUPUESTO:`. Cero decisiones en silencio.
- El spec no menciona branch, PR, integrar ni mergear: eso es de la entrega, no del contrato.
- En `entregable`: ningún dato sin fuente nombrada.

## Troubleshooting

- **"Hacé lo que te parezca."** No es carta blanca: escribí el `SUPUESTO:` con lo que elegiste y
  seguí. El supuesto visible es el punto.
- **Una verificación no se puede correr** porque falta un acceso o datos que todavía no existen.
  Declarala igual y marcala `[bloqueada: falta X]`. No se borra del spec.
- **Tentación de meter la ruta de entrega adentro.** No. Si el spec dice "mergear a main", está mal
  escrito.

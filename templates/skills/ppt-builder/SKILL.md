---
name: ppt-builder
description: >-
  Arma una pieza de comunicación por etapas, de bruto a final, en UN solo doc que crece. Pensado
  sobre todo para deck/ppt, sirve igual para post de LinkedIn, video, carrusel o una landing.
  Usalo cuando el usuario diga "armame el ppt/deck de X", "armemos el post de Y", "hagamos el
  carrusel de Z", "el guion del video de W", "armá la landing de X", "construilo por etapas",
  "vamos paso a paso", "vamos por bloques". Cinco etapas: Brief → Historia → Estructura → Copy →
  Asset final. Una etapa a la vez, propone-vos-decidís, profundidad regulable. Es un ORQUESTADOR:
  no hace todo solo, coordina las etapas e invoca otros skills (redactar + anti-slop en Copy, el
  skill de pptx en el Asset). NO es para un texto corto de una sola pasada (eso es redactar directo).
---

# ppt-builder — armar un deck (y otras piezas) por etapas

> **Ejemplo de orquestador.** Este skill no escribe el copy ni genera los slides él mismo: coordina un proceso de 5 etapas y, en cada una, **llama a los skills que ya hacen ese trabajo** (`redactar` para la voz, `anti-slop` para limpiar, el skill de pptx para el asset). Es el patrón del Nivel 5: repartir y juntar, no rehacer.

Se arma por bloques, de la base para arriba: no empezás por el copy si todavía no está la historia. El laburo va por **5 etapas funcionales**. Orientado sobre todo a **deck/ppt**; el mismo flujo sirve para post, video, carrusel o landing cambiando el molde en las últimas etapas. Todo vive en **un solo doc que crece** (`pieza.md`), una etapa a la vez, con OK antes de pasar a la siguiente.

## Cómo corre
- **Una etapa a la vez.** Construís la etapa, la mostrás, esperás un "dale", recién ahí seguís. Nunca las 5 de una.
- **El usuario lidera lo creativo.** El skill ejecuta, propone y arma; el ángulo, la historia, el copy y el tono los cierra el usuario. Frasealo "armé esto, ¿te cierra?", no decidas solo.
- **UN solo doc que crece.** Cada etapa appendea una sección H2 al mismo markdown (`{BASE}/{SLUG}/pieza.md`), no un archivo por etapa. Arriba el brief, abajo lo último.
- **Profundidad por etapa.** Cada etapa corre en **skip / liviano / full**. Al arrancar proponés un perfil según medio + tamaño; el usuario lo ajusta antes de construir.
- **Reuso, no reinvento.** La etapa Copy pasa por `redactar` (voz del usuario) + `anti-slop` (limpieza). La etapa Asset usa el skill de pptx (si lo tiene) o un generador tipo Gamma. No reescribís un revisor de estilo ni un generador de slides.

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

**Convención de archivos:** doc único en `{BASE}/{SLUG}/pieza.md`; assets generados (pptx, imágenes, prompts) en `{BASE}/{SLUG}/assets/`.

**Research / contexto (escape hatch):** el default es un solo `pieza.md`, sin subcarpetas. Si una pieza necesita research, **proponéselo al usuario antes de crear nada**; recién con OK se arma `{BASE}/{SLUG}/contexto/`.

## Perfil de profundidad (lo primero que se propone)
Tres niveles por etapa: **skip** (no aplica o ya está; 1 línea y seguís), **liviano** (lo mínimo para que la próxima etapa salga bien), **full** (a fondo). **[LAT]** Proponé un default según medio + tamaño; el usuario lo ajusta:

| Medio | Brief | Historia | Estructura | Copy | Asset |
|---|---|---|---|---|---|
| **Deck / ppt** | liviano | full | full | full | full |
| **Post LinkedIn** | liviano | liviano→full | liviano | full | liviano |
| **Carrusel / video** | liviano | full | full | full | full |
| **Landing** | liviano→full | full | full | full | full |

Guardá el perfil aprobado en el frontmatter del doc (`profundidad:` por etapa).

## Las 5 etapas
**Etapa 0 — Kickoff + scaffold** `[DET]`
Reunir parámetros, proponer el perfil de profundidad, esperar OK. Crear `{BASE}/{SLUG}/` + `assets/` + `pieza.md` con frontmatter (`pieza`, `medio`, `objetivo`, `audiencia`, `profundidad` por etapa, `creado`).

**Etapa 1 · Brief** `[LAT]` → appendea `## 1. Brief`
- **Contexto:** dónde aterriza la pieza, realidades del canal (LinkedIn premia el hook en las 2 primeras líneas; un deck se proyecta y se lee a 3 metros).
- **Objetivo + audiencia:** para qué es, a quién, qué querés que sienta/haga.
- **Límites:** no-negociables (marca, legal, tono, qué NO decir).
- *liviano* = bullets. *full* = + research del canal si hace falta (proponer antes). Checkpoint.

**Etapa 2 · Historia** `[LAT]` → appendea `## 2. Historia`
- **Mensaje central** en UNA frase. Si no entra en una frase, son dos mensajes; elegí uno.
- **Por qué importa** a esta audiencia (el stake, la tensión). Sin esto la pieza informa pero no mueve.
- **Hilo conductor:** la forma que hilvana el mensaje (antes/después, problema→giro→solución, una anécdota que ancla). *full* = + mapeo del hilo contra la estructura.
- Lo que falte (un dato, un caso real) va como `[ABIERTO: ...]`, nunca inventado. Checkpoint.

**Etapa 3 · Estructura** `[LAT]` → appendea `## 3. Estructura`
- **ppt/deck:** lista de slides por título, 1 idea por slide, arco apertura → tensión → resolución → cierre/CTA. **Definir la cantidad de slides.**
- **post:** hook / cuerpo / CTA (marcar dónde corta el "ver más"). **video:** beats con duración tentativa. **carrusel:** tarjetas numeradas. **landing:** hero (promesa + CTA) → problema → solución → prueba → cierre/CTA.
- Respeta los límites del brief. *liviano* = el molde en bullets. *full* = + 1 frase de qué entra en cada slide/beat/tarjeta. Checkpoint.

**Etapa 4 · Copy** `[LAT]` → appendea `## 4. Copy`
- **Llenar el molde:** ppt = por slide, título + bullets/idea + nota de presenter; post = el texto completo; video = guion por beat; carrusel = texto por tarjeta; landing = headline + subhead + body + CTAs por sección.
- **Pulir:** pasá por `redactar` (la voz del usuario) + `anti-slop` (una pasada: sacar reframes "no es X es Y", puffery, verbos metafóricos, vocab muerto). **0 em-dashes.** Cada palabra paga renta.
- Datos/casos que no existan → `[ABIERTO: ...]`, no inventar. *liviano* = draft directo pulido. *full* = + 2-3 variantes de apertura/hook. Checkpoint (el usuario valida que suene a él).

**Etapa 5 · Asset final** `[LAT]`/`[DET]` → appendea `## 5. Asset final` + punteros a `assets/`
El entregable listo, 0 placeholders:
- **ppt/deck:** ofrecé ambos caminos y que el usuario elija — un prompt para **Gamma** (`assets/gamma-prompt.md`) O el `.pptx` vía el **skill de pptx** que tenga conectado (`assets/{SLUG}.pptx`).
- **post:** texto final listo para pegar, con saltos de línea reales. **video:** guion + shotlist + prompt(s). **carrusel:** texto + prompt de imagen por tarjeta. **landing:** prompt para el builder o el HTML, según dónde va a vivir.
- Varios medios → repetir Asset por medio (misma Historia, distinto asset). Checkpoint final → pieza terminada.

## Guía de estado (en cada checkpoint)
> **📍 Dónde estamos:** Etapa {N}/5 — {nombre} ({profundidad})
> **✅ Qué cerramos:** {1-2 bullets + quedó en `pieza.md` §{etapa}}
> **⏭️ Qué sigue:** {próxima etapa + su profundidad propuesta}
> **🙋 Qué necesito de vos:** {la decisión que destraba, o "nada, decime dale y sigo"}

## Qué lee y escribe
- **Lee:** lo que el usuario te pasa de la pieza; `2. Áreas/yo/mi-estilo.md` (vía `redactar`).
- **Escribe:** `{BASE}/{SLUG}/pieza.md` (crea + appendea, una H2 por etapa) y `{BASE}/{SLUG}/assets/` (los assets). `contexto/` solo con OK.
- **Invoca (no reescribe):** `redactar` + `anti-slop` (Copy); el skill de pptx (Asset de deck).

## Cuándo NO usar
- Un texto corto de una sola pasada (responder un mail, un párrafo) → `redactar` directo, sin las 5 etapas.
- Validar un negocio nuevo con paid media (research → landings → campañas) → eso es otro proceso, no esto. Una landing **suelta** (evento, coming-soon, portfolio) sí es acá.

## Señales de que lo hiciste bien
- [ ] Cada etapa se cerró con un OK explícito antes de la siguiente (0 etapas blasteadas de una).
- [ ] Todo vive en UN doc que crece (`pieza.md`), no un archivo por etapa.
- [ ] El perfil de profundidad se propuso y el usuario lo ajustó antes de construir.
- [ ] Reuso real: Copy pasó por `redactar` + `anti-slop`; el asset de deck salió del skill de pptx o de Gamma.
- [ ] 0 em-dashes; 0 datos/testimonios inventados (faltantes como `[ABIERTO]`).

## Si algo sale raro
- **"Hacelo todo de una":** igual presentá checkpoints por etapa; ofrecé correr seguido pero sin saltear Historia ni Estructura (ahí se define si la pieza para de pie).
- **Tentación de un archivo por etapa:** NO. Un solo `pieza.md` que crece. Si quedó largo, podá prosa vieja, no partas el doc.
- **Falta `MEDIO`:** bloquea Estructura/Copy/Asset (cambian de forma por medio). Default ppt, pero confirmalo al arrancar.

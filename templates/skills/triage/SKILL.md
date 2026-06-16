---
name: triage
description: >
  Te arma el brief del día y los accionables, cruzando tus fuentes: mail,
  calendario (reporte de citas) y tu chat/tareas de trabajo (Slack, Jira,
  Linear, Trello, Notion comments, lo que uses). Usalo cuando digas
  "armame el brief del día", "triage", "qué tengo hoy", "briefeame",
  "leeme los mails", "qué llegó al inbox", "revisá mi correo". Cada fuente
  necesita su MCP conectado; con el mail solo ya arranca.
---

# triage: el brief del día

## Qué es
Lee tus fuentes y te las devuelve masticadas: arriba un **brief** (cómo viene el día en 2-4 líneas), abajo los **accionables generales** cruzando todo. No manda, no archiva, no cierra nada solo: propone.

El **mail** es el corazón. El **calendario** (reporte de citas) y tu **chat/tareas** (Slack, Jira, Linear, Trello, Notion comments, o lo que uses) son extras que se ofrecen y se suman si los tenés conectados. No asume tu stack: trabaja con lo que haya.

## Qué lee y escribe
- **Lee:** mail / calendario / chat / tareas por MCP (las fuentes que tengas conectadas).
- **Escribe:** NADA. No manda, no archiva, no cierra tickets, no responde. Solo lee y propone — actuar es siempre con tu OK (y lo hace otro skill, ej. `redactar`).
- **Modo degradado:** si una fuente conectada falla a mitad, marcá `⚠ no pude leer X` arriba del brief; no la omitas en silencio.

## Precondición: las fuentes por MCP
Cada fuente entra por su MCP (mirá `.secondbrain/reference.md`, sección 17):
- **Mail** (Gmail u otro) — el piso. Si no está, frená y guiá a conectarlo.
- **Calendario** — para el reporte de citas. Opcional.
- **Chat / tareas de trabajo** — Slack, Jira, Linear, Trello, Notion comments, lo que sea. Opcional, lo que tengas.

La primera vez (o si solo tenés el mail), **ofrecé** sumar calendario y chat/tareas: "¿querés que además te lea el calendario y el Slack/Jira/Linear/Trello para el brief completo?". No frenes todo por una fuente que falta: con el mail alcanza para arrancar.

## Flujo
1. **[DET]** Mirá qué fuentes hay conectadas por MCP (mail, calendario, chat/tareas). Para las que falten y servirían, ofrecé conectarlas, pero seguí con lo que haya.
2. **[DET]** Leé cada fuente conectada en el rango: mail y chat/tareas de las últimas 24h (o lo que pidas); calendario, el día de hoy (o el rango que digas).
3. **[LAT]** Armá el **BRIEF** (arriba, primero): 2-4 líneas con el titular del día. Cuántas citas tenés y la que importa, qué se movió en mail/chat, qué está prendido fuego. Es el titular, no la lista.
4. **[LAT]** Debajo, los **accionables generales**: los 3-5 que importan de verdad, cruzando TODAS las fuentes (no una lista por fuente). Cada uno: qué hay que hacer + de dónde salió (mail / cita / Slack / ticket).
5. **[LAT]** Detalle de apoyo, abajo:
   - **Reporte de citas** (si hay calendario): las reuniones de hoy en orden, con hora, con quién, y marcá las que necesitan prep.
   - **El resto** (mail/chat): FYI y ruido, agrupado, una línea cada uno.
6. **[LAT]** Si algo pide respuesta, ofrecé redactarla (con el skill `redactar` si está). NO mandes, archivés ni cierres tickets sin OK.

## Cuándo NO usar
- Sin ninguna fuente conectada: conectá al menos el mail primero.
- Para actuar solo (mandar mails, archivar, cerrar tickets, responder en Slack): esto lee y propone, no ejecuta.

## Señales de que lo hiciste bien
- El brief de arriba se lee en 10 segundos y ya sabés cómo viene el día.
- Los accionables son cross-fuente y de verdad importan (no una lista inflada por canal).
- Si hay calendario, el reporte de citas está completo y marcaste lo que necesita prep.
- No tocaste nada (ni mandar, ni archivar, ni cerrar) sin OK.

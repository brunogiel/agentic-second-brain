# Changelog

## 1.3.0 · 2026-11-26

**La botonera completa, con cualquier agente.** Vive ahora como carpeta `botonera/` del kit `agentic-second-brain`.

- **Tres pestañas, una vista por vez:** Sesiones · Decisiones · Bloqueos. Sesiones muestra «Trabajando ahora» (con lo que cada sesión anota con `vuelo.py`), «Hechas hoy» y el archivo. Bloqueos junta «Te esperan a vos» y lo que murió con error.
- **Tarjetas nuevas:** de revisión (un solo botón, Revisado), campo `textarea` para texto largo, `detalle` plegado, imagen a pantalla completa, «Ya no aplica» cuando una tarjeta se reemplaza (`armar.py --reemplaza <clave>#<n>[:<m>]`).
- **+info con 5 opciones** (más contexto, dibujo corto, dibujo largo, escribilo distinto, otro ejemplo) y `skill/rot.md`, la guía autocontenida para reescribir la tarjeta. **«Esto es regla»** y **«Después»** (antes «Al inbox»). Rótulos: «El agente recomienda» y «Si no decidís».
- **Obstáculos:** `obstaculo.py` publica lo que solo la persona puede hacer; `pendientes.py` lista los resueltos.
- **Un solo aviso por tanda de entradas** (ráfaga) en lugar de uno por tarjeta.
- **Bloqueo del PIN temporal y creciente:** 10 fallos seguidos bloquean 15 minutos; cada tanda nueva de 10 duplica la espera (15, 30, 60… hasta 24 h) y un ingreso correcto la pone en cero. `pin.py desbloquear` la levanta; `pin.py estado` muestra hasta cuándo. Antes quedaba bloqueada hasta desbloquear.
- **Instalador:** `--agente claude|cursor|codex|otro` (codex instala en `~/.agents/skills/botonera`), reescribe la ruta del skill en `SKILL.md` y `rot.md`, `--solo-skill` (para un bot en un servidor, sin secreto), prueba de conexión (`--sin-probar` la saltea), exige `https://` salvo localhost, avisa si faltan los CLI de Supabase o Vercel, e imprime la ruta absoluta de `instalar.sql` y el comando para copiarlo.
- **Scripts:** `maestro.py` lee, en orden, las tres variables de entorno, `BM_ENV_FILE`, `~/.config/botonera/env` y `~/.config/botonera/env-bot`, y rechaza una URL `http://` que no sea localhost. `esperar.py --una-vez` consulta una vez (sale 3 si sigue abierta). `armar.py --publicar` sale con error si el servidor rechaza. `pin.py poner` ya no acepta el PIN por argumento (solo teclado oculto). `secret-bot.py` dice dónde poner el archivo en el servidor.
- **Docs:** README con sección Seguridad (qué ve cada llave, qué sale a terceros, cómo rotar), tabla por agente y «Qué no trae»; `SKILL.md` con «Si tu agente no tiene segundo plano».
- **Queda afuera de esta versión:** crear una tarea desde el celu, dictado, inbox y lecturas. La fila «Con error» se conserva.
- Migraciones nuevas (`20261121…`); `install.sh` las suma a `instalar.sql` y se pueden repetir. Actualizar desde la 1.2.x es volver a correr el instalador y pegar el SQL.

## 1.2.1 · 2026-11-07

- **El aviso de una botonera nueva lleva su título.** Con una sola, el título del aviso es el de la botonera («Volvió: <título>» si despertó de un snooze) y abajo van la categoría y «N cards por decidir». Con varias, el aviso dice «N botoneras nuevas» (o «N botoneras volvieron» si todas despertaron) y abajo van hasta 2 títulos separados por coma, con «+N» por el resto. Los títulos se recortan a 40 letras.
- **Las categorías `privada` siguen sin nombrarse.** Una botonera de una categoría marcada `privada` en `categorias.json` no muestra su título en el aviso: cuenta en el número y el aviso dice «1 botonera nueva».
- Una migración nueva (`20261107010000_bm_avisos_titulo.sql`): la función `bm_avisos_titulos` y `bm_avisos_tick` actualizada. `install.sh` la suma a `instalar.sql`; las migraciones se pueden repetir, así que actualizar desde la 1.2.0 es volver a correr el instalador y pegar el SQL.

## 1.2.0 · 2026-11-07

- **Snooze.** En la portada de cada botonera, a la izquierda (gesto, flecha ← o el botón «Snooze»), elegís cuándo vuelve: «Hoy más tarde» (antes de las 17:00), «Mañana», «El finde» o «Próximo lunes», hasta 8 días. La botonera duerme en una fila «Snoozeadas» del home con «Despertar ahora», no se envía ni se avisa por push mientras duerme, y al despertar vuelve arriba con tus marcas. Un aviso de 5 segundos con «Deshacer» cierra el gesto. Una opción marca «vence antes» si una card vence antes de que vuelva. Todas las horas se calculan en la zona horaria de tu dispositivo.
- **Portada en forma de carpeta.** La card de contexto es una carpeta del color de su categoría, con una pestaña que dice la categoría y cuántas cards trae, y una pila de cartas que asoman por arriba (una por card, hasta 4).
- **La sesión sabe del snooze.** `esperar.py` avisa una vez por snooze (`maestro: <clave> snoozeada hasta <dd-mmm HH:MM>`, en hora local de la máquina) y la sesión lo relanza sin tocar la botonera. El tope de espera pasa a 8 días.
- Una migración nueva (`20261107…`): `snooze_hasta`, `bm_snoozear` y `bm_despertar`, y `bm_lista`, `bm_recibir`, `bm_sin_cerrar`, `bm_decidir_pin` y los dos avisos aprenden de las botoneras dormidas. `install.sh` la suma a `instalar.sql`; las migraciones se pueden repetir, así que actualizar desde la 1.1.x es volver a correr el instalador y pegar el SQL.

## 1.1.1 · 2026-11-06

- **Con cualquier agente.** El README explica cómo usar la botonera con Codex, Grok, Cursor o cualquier agente que corra Python: `--skill-dir`, el `SKILL.md` como instrucciones y `BM_SESSION_ID` para agrupar las tandas.
- La web arma el link «Abrir la conversación» solo para sesiones de la app de Claude Code; las de otros agentes se muestran sin link.
- GIF de la botonera en el celu al principio del README.

## 1.1.0 · 2026-11-06

- **Editar.** La barra de la card es «No va · Editar · Va», y la fila chica suma «+info» para comentar sin decidir. Una card sí/no puede traer `campos` (hasta 5, de tipo texto, número, fecha u opción): salen cargados con lo que propuso Claude, el que cambiás queda marcado con «Antes: X» y «Volver al original», y la respuesta vuelve como `va con cambios · título → acción · campos: id=nuevo (antes viejo)`. Si cambiás un valor, salís con ‹ Volver y decidís Va, el cambio viaja igual y la card muestra «N cambios pendientes». En las cards de una opción o varias, «Editar» permite elegir y escribir qué cambia. Cmd/Ctrl+Enter equivale a «Listo» en cualquier hoja.
- **Retomar sin la sesión viva.** Cada card puede traer `aplicar`, el plan de cada respuesta posible (≤40 palabras); `armar.py` avisa cuando falta. `retomar.py <clave>` lee la respuesta y esos planes con `bm_retomar` y arma un brief que cualquier sesión nueva puede aplicar. `colgadas.py` suma «plan aplicar N/M» a cada tanda decidida y el flag `--archivar`.
- **Fila «Con error».** Arriba del home aparece lo que murió sin avisar (una tarea programada que falló, una tanda archivada con una respuesta sin aplicar) hasta que tocás «Visto». Se publica con `errores.py` (`publicar`, `desde-runs`, `--seco`).
- **Contador en el home.** Cada fila de categoría dice cuántos mazos y cuántas cards tiene («2 mazos · 5 cards»).
- **Rol de bot.** `secret-bot.py` genera un secreto aparte para agentes que no son tu sesión de Claude Code. Solo sirve con claves y `session_id` que empiezan con `bot-`: no ve las demás tandas, ni el PIN, ni publica errores. `maestro.py` también lee la config de las variables de entorno `SUPABASE_URL`, `SUPABASE_ANON_KEY` y `BM_SECRET`.
- Dos migraciones nuevas (`20261106…`); `install.sh` las suma a `instalar.sql`. Las migraciones se pueden repetir, así que actualizar desde la 1.0.x es volver a correr el instalador y pegar el SQL.
- `tests/e2e-editar.js`: 23 casos de la web con Playwright, sin Supabase. `tests/prueba_local.py` suma los chequeos de campos, retomar, errores y rol de bot.

## 1.0.0 · 2026-11-05

Primera versión pública.

- `/botonera` para Claude Code: junta las decisiones pendientes, las arma como cards con recomendación, contexto e impacto, y las publica en tu botonera.
- Web para decidir en swipe desde el celu: entra con PIN de 4 dígitos, se instala como app, tres tipos de card (sí/no, una opción, varias), comentario por card y comentario final del envío.
- La respuesta vuelve sola a la sesión que preguntó (`esperar.py`), y `marcar.py` cierra el loop: la web muestra qué se aplicó.
- Avisos push en el celu cuando llega una botonera nueva y cuando una card vence hoy o mañana, con silencio de 22 a 8 en tu zona horaria. Los avisos llevan solo conteos y nombres de categoría.
- Categorías del home editables en `categorias.json`; las marcadas `privada` no se nombran en los avisos.
- Una sola migración SQL para tu propio proyecto Supabase, con todo detrás de funciones: la clave pública sola no lee nada.
- `install.sh`: copia el skill, guarda tu config local y te deja el SQL listo para pegar. `tests/prueba_local.py` prueba el loop entero contra un Supabase local.

---
name: publicar
description: >
  Decís /brain-ship y te sube lo último que te hizo Claude (una página, una app) y te
  devuelve el link. La primera vez, si no tenés dónde hostear, te hace crear la cuenta
  (Netlify o Vercel para páginas, Supabase si necesita base de datos), guarda la conexión
  y te la deja lista. De la segunda vez en adelante sube solo, sin preguntar. Usalo cuando
  digas "subí esto", "poné esto online", "publicá esto", "deployá", "quiero el link",
  "/brain-ship". Directo: sube y da el link, no te hace preguntas de más.
---

# publicar — decís /brain-ship y te lo sube

## Qué es
Le pedís algo a Claude, te lo hace, y en vez de quedar en un archivo suelto, `/brain-ship` lo **sube y te da el link**. Directo. La primera vez, si todavía no tenés dónde hostearlo, te manda a crear la cuenta del servicio que corresponda, **guarda esa conexión** y te la deja lista. De ahí en más, `/brain-ship` sube solo: mira lo que ya conectaste y va derecho al link.

La idea entera: **conectás una vez, subís para siempre con un comando.**

## Cuándo SÍ / Cuándo NO
- **SÍ:** tenés algo que Claude te armó (página, app, prototipo) y lo querés online ya, o querés pasarle un link a alguien. O querés conectar tu host por primera vez y dejarlo listo.
- **NO:** es un documento común (Word, PDF, planilla) que no se "sube", se abre y ya; querés que te construya algo de cero (eso se lo pedís normal); querés decidir entre servicios de hosting con un análisis largo (esto elige el obvio y avanza).

## Las 3 movidas
1. **Directo si ya hay conexión.** Si el host ya está conectado, no preguntes nada: subí y devolvé el link. Ese es el caso normal, el de todos los días.
2. **La primera vez, conectá y dejá listo.** Sin host conectado, guiás la creación de la cuenta (la hace la persona, vos no podés crear cuentas ni cargar sus datos), capturás la conexión y la persistís. Que sea la última vez que se pregunta.
3. **El secreto nunca en la carpeta sincronizada.** El brain se sincroniza (Drive, iCloud). El token o la clave va a la MCP o a un archivo local fuera de la carpeta; en el brain queda solo el puntero: qué está conectado, qué proyecto, qué URL, cómo reconectar.

## Qué lee y escribe
- **Lee:** lo que hay que subir (path, o "lo último que me hiciste") + el registro de conexiones del brain y las MCP de hosting disponibles.
- **Escribe:** deploya; registra la conexión (puntero en el brain, secreto en local o MCP); devuelve la URL en vivo.

## Flujo
1. **[DET]** ¿Qué hay que subir y de qué tipo es? Routing rápido, no hand-holding: ¿estático (HTML/CSS/JS, se sube y anda) o app que necesita servidor o base de datos? Eso decide el host, nada más.
2. **[DET]** ¿Hay host conectado para ese tipo? Mirá el registro del brain (`dev-prefs` / conexiones) y las MCP disponibles. Si hay → salteá directo a subir (paso 6).
3. **[LAT]** Si no hay host, elegí el más simple para lo que es: página estática → Netlify o Vercel; con base de datos o login → Supabase. Un solo camino, el obvio, no un menú largo.
4. **[LAT]** Mandá a crear la cuenta. Dale el link directo del servicio y esperá a que la persona se registre. No podés crear la cuenta ni tipear sus credenciales vos: se la hace ella, vos guiás en 2 líneas.
5. **[LAT]** Capturá la conexión por el camino más fácil: si hay MCP oficial del host (Vercel, Netlify, Supabase), conectá por ahí, que la MCP maneja la credencial. Si no hay MCP, pedí el token o deploy hook que la persona copia de su panel, y guardalo en un lugar **local, fuera de la carpeta sincronizada**. Enseñale en 2 líneas de dónde se saca ese token. Después registrá en el brain solo el **puntero** (host, proyecto, URL, cómo reconectar), nunca el secreto.
6. **[DET]** Subí y devolvé el link.
7. **[DET]** Confirmá que el deploy es real: que la URL abra de verdad. No des "ya lo subí" por hecho.

De la próxima corrida en adelante: `/brain-ship` encuentra el host en el registro, sube y da el link. Cero preguntas.

## Output esperado
```
## 🚀 Subido
Link: <URL en vivo>
Qué subí: <archivo o proyecto> → <host>
Conexión: <ya estaba lista / la dejé conectada para la próxima>
```

Primera vez (cuando hubo que conectar):
```
## 🔌 Te dejé el host conectado
Creaste tu cuenta en: <servicio>
Conexión guardada: <MCP / token local> — el secreto NO quedó en tu carpeta sincronizada
En tu brain anoté: <host + proyecto + URL, el puntero para reconectar>

## 🚀 Subido
Link: <URL en vivo>
La próxima: solo /brain-ship y sube solo.
```

## Reglas duras
1. Directo si ya hay conexión: `/brain-ship` = subir + link, sin preguntas.
2. No creás cuentas ni cargás credenciales por la persona. La cuenta se la hace ella; vos guiás.
3. El secreto nunca en la carpeta sincronizada del brain. Va a MCP o a config local; en el brain solo el puntero.
4. Conectás una vez. La primera vez se configura; de ahí en más es instantáneo.
5. Confirmá el deploy real (la URL abre), no lo des por hecho.
6. Cero em-dashes en el texto en español.

## Señales de que lo hiciste bien
- La segunda vez que corrés `/brain-ship` no preguntó nada y te dio el link.
- El token no quedó en la carpeta sincronizada: está en la MCP o en config local.
- La persona se creó su propia cuenta y la conexión quedó registrada para reusar.
- La URL abre de verdad, la verificaste.
- Cero em-dashes.

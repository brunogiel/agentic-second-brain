---
description: Decís /brain-ship y sube lo último que te hizo Claude, verifica que abra y te da el link. La primera vez conecta tu host y lo deja listo; después sube solo.
---

Subí lo que te pasen ($ARGUMENTS, o lo último que hiciste en la sesión), verificá que abra y devolvé el link. Seguí esto:

# publicar — decís /brain-ship y te lo sube

## Qué es
Le pedís algo a Claude, te lo hace, y en vez de quedar en un archivo suelto, `/brain-ship` lo **sube, verifica que abra y te da el link**. Directo. La primera vez, si todavía no tenés dónde hostearlo, te manda a crear la cuenta del servicio que corresponda, **guarda esa conexión** y te la deja lista. De ahí en más, `/brain-ship` sube solo: mira lo que ya conectaste y va derecho al link.

La idea entera: **conectás una vez, subís para siempre con un comando.**

## Cuándo SÍ / Cuándo NO
- **SÍ:** tenés algo que Claude te armó (página, app, prototipo) y lo querés online ya, o querés pasarle un link a alguien. O querés conectar tu host por primera vez y dejarlo listo.
- **NO:** es un documento común (Word, PDF, planilla) que no se "sube", se abre y ya; querés que te construya algo de cero (eso se lo pedís normal); querés decidir entre servicios de hosting con un análisis largo (esto elige el obvio y avanza).

## Las 3 movidas
1. **Directo si ya hay conexión.** Si el host ya está conectado, no preguntes nada: subí, verificá y devolvé el link. Ese es el caso normal, el de todos los días.
2. **La primera vez, conectá y dejá listo.** Sin host conectado, guiás la creación de la cuenta (la hace la persona, vos no podés crear cuentas ni cargar sus datos), capturás la conexión y la persistís. Que sea la última vez que se pregunta.
3. **El secreto nunca en la carpeta sincronizada.** El brain se sincroniza (Drive, iCloud). El token o la clave va a la MCP o a un archivo local fuera de la carpeta; en el brain queda solo el puntero: qué está conectado, qué proyecto, qué URL, cómo reconectar.

## Elegir host
- **Estático** (HTML/CSS/JS, o una SPA con build como Next export o Vite: sigue siendo estático, solo le sumás el build command) → **Netlify o Vercel**.
- **App de verdad** (necesita servidor vivo o base de datos o login en runtime) → **Supabase** para los datos/auth, más el front por el host estático.
- **Si ya declaraste un host preferido** en tu registro del brain, ese gana, aunque haya otro más a mano. Solo lo cambiás si pedís "usá el que esté conectado".

## Detectar si hay host conectado
Chequealo de verdad, no lo asumas, en este orden:
1. **Tu registro de hosting en el brain** (ej. `2. Áreas/yo/dev-prefs.md`, sección Hosting, o un `conexiones.md`): ¿hay host preferido o ya conectado, con su puntero?
2. **El CLI o token del host:** Netlify → `~/.config/netlify/config.json` (login del CLI) o `$NETLIFY_AUTH_TOKEN`. Vercel → `vercel whoami` o su MCP. Supabase → su MCP o `$SUPABASE_ACCESS_TOKEN`.
3. **MCP oficial del host** disponible en la sesión.

Si hay conexión para el tipo que necesitás, saltá directo a deployar.

## Guardar la conexión (primera vez)
- **El secreto va afuera del brain.** Preferí el login nativo del CLI o el MCP oficial, que manejan el secreto ellos (`netlify login` lo guarda en `~/.config/netlify/`). Si es un token manual, guardalo en `~/.config/brain-ship/<host>.token` (local, fuera de la carpeta sincronizada). Nunca en el brain.
- **En el brain va solo el puntero:** una fila con `host | tipo | proyecto | url | dónde vive el secreto | cómo reconectar`.

## Comando de deploy (apuntá a la CARPETA, no al archivo suelto)
| Caso | Comando |
|---|---|
| Netlify, estático | `netlify deploy --dir=<carpeta> --prod` |
| Vercel, estático | `vercel deploy --prod --yes` (desde la carpeta) |
| SPA con build | primero el build (`npm run build`), después deploy de la carpeta de salida |
| App con DB/login | Supabase para datos/auth + el front por el host estático |

Netlify y Vercel sirven un **directorio**, no un `index.html` suelto: si le pasás el archivo, no anda. Apuntá siempre a la carpeta que lo contiene.

## Qué lee y escribe
- **Lee:** lo que hay que subir (path, o "lo último que me hiciste") + el registro de conexiones del brain y las MCP de hosting disponibles.
- **Escribe:** deploya; registra la conexión (puntero en el brain, secreto en local o MCP); devuelve la URL en vivo verificada.

## Flujo
1. **[DET]** Routing. Mirá qué hay que subir y decidí estático vs app (ver "Elegir host"). Eso fija el host.
2. **[DET]** ¿Hay host conectado para ese tipo? Corré los chequeos de "Detectar si hay host conectado". Si hay, saltá al paso 6.
3. **[LAT]** Elegí host respetando tu preferencia declarada por sobre el que esté a mano.
4. **[LAT]** Primera vez sin host: mandá a crear la cuenta (link directo de signup) y **frená ahí**. La cuenta la crea la persona; no creás cuentas ni tipeás credenciales. Mostrá el template "primera vez, falta conectar" y esperá el "listo".
5. **[LAT]** Capturá la conexión con el secreto afuera del brain (ver "Guardar la conexión") y registrá solo el puntero.
6. **[DET]** Deployá con el comando del host, apuntando a la carpeta (ver la tabla).
7. **[DET]** **Verificá antes de cantar victoria.** La URL responde 200 (no 404 ni página de error) y renderiza lo tuyo, no la landing del host ni una página en blanco. Si podés, abrila y confirmá el contenido. Si falla, no digas "subido": reportá el error y arreglá (carpeta equivocada, build faltante, deploy a preview en vez de prod).
8. **[DET]** Cerrá devolviendo el **link en vivo como última línea**, más el puntero que guardaste. De la próxima corrida en adelante: `/brain-ship` encuentra el host y sube directo, cero preguntas.

## Output esperado
Caso normal (host ya conectado):
```
## 🚀 Subido y verificado
Qué subí: <archivo o proyecto> → <host>
Verificado: la URL abre (200) y renderiza <lo esperado>
Conexión: ya estaba lista

Link: <URL en vivo>
```

Primera vez, frenado en el gate (falta que crees la cuenta):
```
## 🔌 Primera vez: falta conectar <host>
Esto es <estático / app> y todavía no tenés <host> conectado (chequeé CLI, token y tu registro: nada).
Hacé 2 pasos y volvés:
1) Creá tu cuenta gratis: <link de signup>. La creás vos, yo no puedo registrarte.
2) Conectá por CLI (`<comando de login>`, el token queda en <path local, fuera de tu Drive>) o pegame un token (lo guardo en ~/.config/brain-ship/, nunca en la carpeta sincronizada).
Decime "listo" y en la misma corrida subo, verifico y te paso el link.
```

Primera vez, resuelto (conectó y deployó en la misma corrida):
```
## 🔌 Host conectado
Cuenta: <host> · Conexión guardada en <MCP / CLI / token local> — el secreto NO quedó en tu carpeta sincronizada
Anoté en tu brain: <host + proyecto + url> (el puntero para reconectar)

## 🚀 Subido y verificado
Verificado: la URL abre y renderiza lo tuyo

Link: <URL en vivo>
La próxima: solo /brain-ship y sube solo.
```

## Reglas duras
1. Directo si ya hay conexión: `/brain-ship` = subir + verificar + link, sin preguntas.
2. No creás cuentas ni cargás credenciales por la persona. La cuenta se la hace ella; vos guiás.
3. El secreto nunca en la carpeta sincronizada del brain. Va a MCP o a `~/.config/...` local; en el brain solo el puntero.
4. La preferencia de host declarada gana sobre el host que esté a mano.
5. Deployá la carpeta, no el archivo suelto.
6. Verificá que la URL abra y renderice lo tuyo antes de decir "subido". Si no verifica, no es un deploy, es un intento: reportalo como tal.
7. El link va como última línea, siempre.
8. Cero em-dashes en el texto en español.

## Señales de que lo hiciste bien
- La segunda vez que corrés `/brain-ship` no preguntó nada y te dio el link.
- Verificaste que la URL abre y muestra tu contenido, no una landing del host ni un 404.
- El token no quedó en la carpeta sincronizada: está en la MCP o en config local.
- Quedó el puntero en el brain para reconectar la próxima.
- El link fue lo último que devolviste.
- Cero em-dashes.

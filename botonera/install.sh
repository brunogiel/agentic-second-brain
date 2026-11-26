#!/usr/bin/env bash
# Instalador de Botonera: copia el skill, escribe la config local y deja listo el SQL para Supabase.
# macOS y Linux. Se puede correr más de una vez: reusa el BM_SECRET que ya exista.
#
# Uso:
#   ./install.sh --url https://xxxx.supabase.co --key <publishable/anon key>
#   ./install.sh --agente codex --url ... --key ...
#   ./install.sh --solo-skill --agente claude     # solo copia el skill (para otra máquina o un bot)
#   ./install.sh --hook                           # solo imprime el bloque de hooks de Claude Code
#
# Opciones:
#   --url <SUPABASE_URL>      URL del proyecto de Supabase, con https:// (si falta, la pide)
#   --key <key>               clave pública (publishable/anon) del proyecto (si falta, la pide)
#   --agente <a>              claude (default) | cursor | codex | otro. Elige dónde instalar el skill:
#                             claude y cursor -> ~/.claude/skills/botonera, codex -> ~/.agents/skills/botonera.
#                             otro exige --skill-dir.
#   --skill-dir <dir>         dónde instalar el skill (gana sobre --agente)
#   --solo-skill              copia el skill y listo: no genera secreto, ni config.js, ni SQL
#   --sin-probar              no prueba la conexión con la URL y la clave (para trabajar sin red)
#   --zona <zona IANA>        zona horaria del aviso push (default: la del sistema, o UTC)
#   --avisar-url <url>        función de push (default <SUPABASE_URL>/functions/v1/bm-avisar)
#   --contacto <url|mailto:>  contacto de la firma VAPID de los avisos (default <SUPABASE_URL>)
#   --yes                     sin preguntas: pisa el directorio del skill si ya existe
#   --hook                    imprime el hook de entregar.py y sale (no toca settings.json)
#   -h, --help                esta ayuda
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
shopt -s nullglob
MIGRACIONES=("$AQUI"/supabase/migrations/*.sql)   # en orden de fecha: la base entera y sus agregados
shopt -u nullglob

URL=""
KEY=""
SKILL_DIR=""
AGENTE=""
SOLO_SKILL=0
SIN_PROBAR=0
RUTA_CLAUDE="~/.claude/skills/botonera"   # como aparece escrita en SKILL.md y rot.md
ZONA=""
AVISAR_URL=""
CONTACTO=""
SI=0
SOLO_HOOK=0

die() { echo "error: $*" >&2; exit 1; }
info() { echo "· $*"; }

ayuda() { awk 'NR>1 && /^#/ {print; next} NR>1 {exit}' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }
aviso() { echo "aviso: $*" >&2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --url)        [ $# -ge 2 ] || die "--url necesita un valor"; URL="$2"; shift 2 ;;
    --key)        [ $# -ge 2 ] || die "--key necesita un valor"; KEY="$2"; shift 2 ;;
    --agente)     [ $# -ge 2 ] || die "--agente necesita un valor"; AGENTE="$2"; shift 2 ;;
    --solo-skill) SOLO_SKILL=1; shift ;;
    --sin-probar) SIN_PROBAR=1; shift ;;
    --skill-dir)  [ $# -ge 2 ] || die "--skill-dir necesita un valor"; SKILL_DIR="$2"; shift 2 ;;
    --zona)       [ $# -ge 2 ] || die "--zona necesita un valor"; ZONA="$2"; shift 2 ;;
    --avisar-url) [ $# -ge 2 ] || die "--avisar-url necesita un valor"; AVISAR_URL="$2"; shift 2 ;;
    --contacto)   [ $# -ge 2 ] || die "--contacto necesita un valor"; CONTACTO="$2"; shift 2 ;;
    --yes|-y)     SI=1; shift ;;
    --hook)       SOLO_HOOK=1; shift ;;
    -h|--help)    ayuda; exit 0 ;;
    *)            die "opción desconocida: $1 (probá --help)" ;;
  esac
done

case "$AGENTE" in
  ""|claude|cursor|codex|otro) ;;
  *) die "--agente '$AGENTE' no existe (opciones: claude, cursor, codex, otro)" ;;
esac
[ "$SOLO_SKILL" -eq 0 ] || [ -n "$AGENTE" ] || [ -n "$SKILL_DIR" ] \
  || die "--solo-skill necesita --agente o --skill-dir (así sé dónde copiarlo)"
if [ -z "$SKILL_DIR" ]; then
  case "$AGENTE" in
    ""|claude|cursor) SKILL_DIR="$HOME/.claude/skills/botonera" ;;
    codex)            SKILL_DIR="$HOME/.agents/skills/botonera" ;;
    otro)             die "con --agente otro tenés que decir dónde va el skill: --skill-dir <carpeta donde tu agente lea sus instrucciones>" ;;
  esac
fi

# ~ al principio de --skill-dir (si llegó sin expandir)
case "$SKILL_DIR" in
  "~")   SKILL_DIR="$HOME" ;;
  "~/"*) SKILL_DIR="$HOME/${SKILL_DIR#\~/}" ;;
esac
SKILL_DIR="${SKILL_DIR%/}"
[ -n "$SKILL_DIR" ] || die "--skill-dir no puede ser la raíz"

# --- --hook: solo el bloque, sin tocar nada ---------------------------------------------------
if [ "$SOLO_HOOK" -eq 1 ]; then
  cat <<HOOK
Sumá esto al archivo de ajustes de Claude Code, ~/.claude/settings.json (si ya tenés "hooks", mezclalo con lo que hay; este instalador no edita ese archivo):

{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "python3 $SKILL_DIR/entregar.py" } ] }
    ],
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "python3 $SKILL_DIR/entregar.py" } ] }
    ]
  }
}

El hook es opcional: si el proceso que espera la respuesta (esperar.py) muere, vuelve a entregarla a la sesión.
HOOK
  exit 0
fi

# --- python3 >= 3.9 ---------------------------------------------------------------------------
command -v python3 >/dev/null 2>&1 || die "no encuentro python3 (hace falta la versión 3.9 o más nueva)"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' \
  || die "hace falta python3 3.9 o más nuevo (tenés $(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])'))"

[ -f "$AQUI/skill/armar.py" ] || die "no encuentro $AQUI/skill/armar.py: corré el instalador desde el repo clonado"

# ruta como se muestra: ~/... si está bajo $HOME y no tiene espacios
mostrar_ruta() {
  case "$1" in
    "$HOME"/*) local r="~/${1#"$HOME"/}"; case "$r" in *" "*) printf '%s' "$1" ;; *) printf '%s' "$r" ;; esac ;;
    *) printf '%s' "$1" ;;
  esac
}
SKILL_MOSTRAR="$(mostrar_ruta "$SKILL_DIR")"

# --- copiar el skill (y reescribir la ruta del skill en SKILL.md y rot.md) -------------------------
instalar_skill() {
  local copiar=1 r=""
  if [ -e "$SKILL_DIR" ]; then
    if [ "$SI" -eq 1 ]; then
      info "ya existe $SKILL_DIR: lo piso (--yes)"
    elif [ -t 0 ]; then
      read -r -p "Ya existe $SKILL_DIR. ¿Lo piso? [s/N]: " r
      case "$r" in s|S|si|SI|sí|Sí|y|Y|yes) ;; *) copiar=0 ;; esac
    else
      die "ya existe $SKILL_DIR y no hay terminal para preguntar (usá --yes para pisarlo)"
    fi
  fi
  if [ "$copiar" -eq 1 ]; then
    mkdir -p "$SKILL_DIR"
    cp -R "$AQUI/skill/." "$SKILL_DIR/"
    find "$SKILL_DIR" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
    if [ "$SKILL_MOSTRAR" != "$RUTA_CLAUDE" ]; then
      python3 - "$SKILL_DIR" "$RUTA_CLAUDE" "$SKILL_MOSTRAR" <<'PY'
import pathlib, sys
carpeta, viejo, nuevo = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
for nombre in ("SKILL.md", "rot.md"):
    f = carpeta / nombre
    if f.is_file():
        f.write_text(f.read_text(encoding="utf-8").replace(viejo, nuevo), encoding="utf-8")
PY
    fi
    info "skill instalado en $SKILL_DIR"
  else
    info "dejo el skill como está en $SKILL_DIR"
  fi
}

# --- --solo-skill: copiar y salir, sin secreto ni config ni SQL -------------------------------
if [ "$SOLO_SKILL" -eq 1 ]; then
  instalar_skill
  cat <<RECETA

No generé secreto, ni config.js, ni SQL. Para que un bot en un servidor publique y reciba respuestas:
  1. En tu máquina, con la instalación completa hecha: python3 $SKILL_MOSTRAR/secret-bot.py (escribe env-bot e imprime un SQL con su hash; corré ese SQL en Supabase).
  2. Llevá env-bot al servidor, a un archivo con permisos 600 que lea solo el usuario del bot, y fuera de cualquier repo.
  3. En el bot: export BM_ENV_FILE=<ruta de ese archivo> (o las tres variables SUPABASE_URL, SUPABASE_ANON_KEY y BM_SECRET).
  4. Cada sesión del bot: export BM_SESSION_ID=bot-<nombre>. Sus claves empiezan con bot-.
  5. Opcional, para achicar imágenes: pip install pillow.
  6. Que el bot siga $SKILL_MOSTRAR/SKILL.md: publica con armar.py --publicar y lee la respuesta con esperar.py <clave> --una-vez.
RECETA
  exit 0
fi

# --- python3 >= 3.9 ---------------------------------------------------------------------------
command -v python3 >/dev/null 2>&1 || die "no encuentro python3 (hace falta la versión 3.9 o más nueva)"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' \
  || die "hace falta python3 3.9 o más nuevo (tenés $(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])'))"

[ "${#MIGRACIONES[@]}" -gt 0 ] || die "faltan las migraciones en $AQUI/supabase/migrations (el repo está incompleto)"

# Herramientas de los pasos siguientes: solo avisan, no cortan.
command -v supabase >/dev/null 2>&1 \
  || aviso "no encuentro el CLI de Supabase (lo necesitás para desplegar los avisos). Instalación: brew install supabase/tap/supabase, o https://supabase.com/docs/guides/cli"
command -v vercel >/dev/null 2>&1 \
  || aviso "no encuentro el CLI de Vercel (lo necesitás para subir la web con Vercel). Instalación: npm i -g vercel. Cualquier hosting estático también sirve."

# --- datos de Supabase ------------------------------------------------------------------------
preguntar() {  # preguntar <variable> <texto>
  local var="$1" texto="$2" valor=""
  if [ "$SI" -eq 1 ] || [ ! -t 0 ]; then
    die "falta $texto (pasalo con --url / --key)"
  fi
  read -r -p "$texto: " valor
  eval "$var=\$valor"
}

[ -n "$URL" ] || preguntar URL "URL de Supabase (https://<ref>.supabase.co)"
[ -n "$KEY" ] || preguntar KEY "Clave pública (publishable/anon) de Supabase"
URL="${URL%/}"
case "$URL" in
  https://*) ;;
  http://localhost|http://localhost:*|http://localhost/*|http://127.0.0.1|http://127.0.0.1:*|http://127.0.0.1/*) ;;
  http://*)  die "la URL tiene que empezar con https:// (http:// solo vale para localhost; recibí: $URL)" ;;
  *)         die "la URL tiene que empezar con https:// (recibí: $URL)" ;;
esac
case "$URL$KEY" in *[[:space:]]*|*\"*|*\'*|*\\*) die "la URL y la clave no pueden tener espacios, comillas ni barras" ;; esac
[ -n "$KEY" ] || die "la clave está vacía"

# --- prueba de conexión -----------------------------------------------------------------------
probar_conexion() {
  command -v curl >/dev/null 2>&1 || { aviso "no tengo curl: me salteo la prueba de conexión"; return 0; }
  local codigo ruta
  for ruta in /rest/v1/ /auth/v1/settings; do
    if [ "${KEY#sb_}" != "$KEY" ]; then
      codigo="$(curl -sS -m 8 -o /dev/null -w '%{http_code}' -H "apikey: $KEY" "$URL$ruta" 2>/dev/null || true)"
    else
      codigo="$(curl -sS -m 8 -o /dev/null -w '%{http_code}' -H "apikey: $KEY" -H "Authorization: Bearer $KEY" "$URL$ruta" 2>/dev/null || true)"
    fi
    case "$codigo" in 2??) return 0 ;; esac
  done
  die "Esa URL o clave no responden: copialas de Project Settings → API en Supabase (o corré con --sin-probar si no tenés red ahora)"
}
if [ "$SIN_PROBAR" -eq 1 ]; then
  info "no pruebo la conexión (--sin-probar)"
else
  probar_conexion
  info "la URL y la clave responden"
fi

# --- zona horaria -----------------------------------------------------------------------------
zona_valida() { printf '%s' "$1" | grep -Eq '^[A-Za-z][A-Za-z0-9_+-]*(/[A-Za-z0-9_+-]+)*$'; }

detectar_zona() {
  local z=""
  if [ -n "${TZ:-}" ]; then z="${TZ#:}"; fi
  if ! zona_valida "$z" 2>/dev/null; then
    z=""
    if [ -L /etc/localtime ]; then
      z="$(readlink /etc/localtime 2>/dev/null | sed -n 's#.*/zoneinfo/##p')"
    fi
  fi
  if ! zona_valida "$z" 2>/dev/null && [ -r /etc/timezone ]; then
    z="$(head -n1 /etc/timezone 2>/dev/null | tr -d '[:space:]')"
  fi
  if ! zona_valida "$z" 2>/dev/null && command -v timedatectl >/dev/null 2>&1; then
    z="$(timedatectl show -p Timezone --value 2>/dev/null || true)"
  fi
  if zona_valida "$z" 2>/dev/null; then echo "$z"; else echo "UTC"; fi
}

[ -n "$ZONA" ] || ZONA="$(detectar_zona)"
zona_valida "$ZONA" || die "la zona '$ZONA' no parece una zona IANA (ej. Europe/Madrid)"
[ -n "$AVISAR_URL" ] || AVISAR_URL="$URL/functions/v1/bm-avisar"
case "$AVISAR_URL" in *[[:space:]]*|*\'*) die "--avisar-url no puede tener espacios ni comillas simples" ;; esac

# --- skill ------------------------------------------------------------------------------------
instalar_skill

# --- config local (~/.config/botonera/env) ----------------------------------------------------
CONF_DIR="$HOME/.config/botonera"
ENV_FILE="$CONF_DIR/env"
mkdir -p "$CONF_DIR"
chmod 700 "$CONF_DIR"

SECRETO=""
if [ -f "$ENV_FILE" ]; then
  SECRETO="$(sed -n 's/^BM_SECRET=//p' "$ENV_FILE" | head -n1 | tr -d "\"' \t\r")"
fi
if [ -n "$SECRETO" ]; then
  info "reuso el BM_SECRET que ya había en $ENV_FILE"
else
  SECRETO="$(python3 -c 'import secrets;print(secrets.token_hex(32))')"
  info "generé un BM_SECRET nuevo"
fi

( umask 077
  {
    echo "SUPABASE_URL=$URL"
    echo "SUPABASE_ANON_KEY=$KEY"
    echo "BM_SECRET=$SECRETO"
  } > "$ENV_FILE" )
chmod 600 "$ENV_FILE"
info "config escrita en $ENV_FILE (permisos 600)"

# --- web/config.js (la clave pública puede viajar al navegador) --------------------------------
if [ -d "$AQUI/web" ]; then
  python3 - "$URL" "$KEY" > "$AQUI/web/config.js" <<'PY'
import json, sys
print("window.BOTONERA_CONFIG = { supabaseUrl: %s, supabaseKey: %s };" % (json.dumps(sys.argv[1]), json.dumps(sys.argv[2])))
PY
  info "web/config.js escrito"
else
  aviso "no existe $AQUI/web, no escribí config.js"
fi

# --- SQL: instalar.sql (migración + bm_instalar) y bootstrap.sql (solo bm_instalar) -----------
LINEA="$(BM_SECRET="$SECRETO" python3 - "$AVISAR_URL" "$ZONA" "${CONTACTO:-$URL}" <<'PY'
import hashlib, os, sys
huella = hashlib.sha256(os.environ["BM_SECRET"].encode("utf-8")).hexdigest()
q = lambda x: "'" + x.replace("'", "''") + "'"
avisar, zona, contacto = sys.argv[1:4]
print("select public.bm_instalar(%s, %s, %s, %s);" % (q(huella), q(avisar), q(zona), q(contacto)))
PY
)"
[ -n "$LINEA" ] || die "no pude armar la llamada a bm_instalar"

( umask 077
  { for m in "${MIGRACIONES[@]}"; do cat "$m"; printf '\n'; done; printf '%s\n' "$LINEA"; } > "$CONF_DIR/instalar.sql"
  printf '%s\n' "$LINEA" > "$CONF_DIR/bootstrap.sql" )
chmod 600 "$CONF_DIR/instalar.sql" "$CONF_DIR/bootstrap.sql"
info "SQL escrito en $CONF_DIR/instalar.sql y $CONF_DIR/bootstrap.sql (permisos 600)"

# --- próximos pasos ---------------------------------------------------------------------------
REF=""
case "$URL" in
  https://*.supabase.co) REF="${URL#https://}"; REF="${REF%%.*}" ;;
esac
[ -n "$REF" ] || REF="<project-ref>"

if command -v pbcopy >/dev/null 2>&1; then COPIAR="pbcopy < \"$CONF_DIR/instalar.sql\""
elif command -v wl-copy >/dev/null 2>&1; then COPIAR="wl-copy < \"$CONF_DIR/instalar.sql\""
elif command -v xclip >/dev/null 2>&1; then COPIAR="xclip -selection clipboard < \"$CONF_DIR/instalar.sql\""
else COPIAR="cat \"$CONF_DIR/instalar.sql\""; fi

case "$AGENTE" in
  codex) INVOCAR='En Codex, escribí $botonera.' ;;
  otro)  INVOCAR="Con tu agente, pedile que siga $SKILL_MOSTRAR/SKILL.md." ;;
  *)     INVOCAR='En Claude Code o Cursor, escribí /botonera.' ;;
esac

cat <<PASOS

Listo. Faltan estos pasos, en este orden:

  1. Pegá el SQL en el SQL editor de Supabase y ejecutalo. El archivo está en:
       $CONF_DIR/instalar.sql
     Para copiarlo al portapapeles:
       $COPIAR
     (Si las migraciones ya están aplicadas, por ejemplo con "supabase start", pegá solo
     $CONF_DIR/bootstrap.sql. Si venís de una versión anterior, volvé a correr este
     instalador y pegá el instalar.sql nuevo: las migraciones se pueden repetir.)

  2. Desplegá la función de avisos push, desde la carpeta del repo:
       supabase functions deploy bm-avisar --project-ref $REF --no-verify-jwt

  3. Desplegá la web:
       cd web && vercel deploy --prod

  4. Poné el PIN de 4 dígitos (te lo pide con el teclado oculto):
       python3 $SKILL_MOSTRAR/pin.py poner

  5. Abrí la web en el celular, instalala como app y prendé los avisos.

  6. $INVOCAR

Opcional: para que las respuestas lleguen aunque se cierre la sesión de Claude Code, corré
  ./install.sh --hook
y sumá lo que imprime a ~/.claude/settings.json.

Opcional: para que un bot publique sin tu secreto completo, corré
  python3 $SKILL_MOSTRAR/secret-bot.py
y ejecutá el SQL que imprime.
PASOS

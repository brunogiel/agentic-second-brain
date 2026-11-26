#!/usr/bin/env bash
# Prueba del instalador y de los scripts de config. No toca tu HOME real, no usa la red ni ningún servicio:
# copia el instalador, el skill y las migraciones a una carpeta temporal y corre todo con un HOME temporal.
#
# Uso:  bash tests/prueba_instalador.sh
set -u

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

REPO="$TMP/repo"
mkdir -p "$REPO/web" "$REPO/supabase"
cp "$AQUI/install.sh" "$REPO/"
cp -R "$AQUI/skill" "$REPO/skill"
cp -R "$AQUI/supabase/migrations" "$REPO/supabase/migrations"
find "$REPO" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true

PASAN=0; FALLAN=0
ok()   { PASAN=$((PASAN + 1)); echo "  PASA   $1"; }
mal()  { FALLAN=$((FALLAN + 1)); echo "  FALLA  $1${2:+ ($2)}"; }
chequear() { if [ "$2" -eq 0 ]; then ok "$1"; else mal "$1" "${3:-}"; fi; }   # chequear <nombre> <codigo> [detalle]

URL_OK="https://abcdefgh.supabase.co"
CLAVE="sb_clave_de_prueba_123"
instalar() {  # instalar <HOME> [args...]  -> stdout+stderr en $SALIDA, código en $COD
  local h="$1"; shift
  mkdir -p "$h"
  SALIDA="$(HOME="$h" bash "$REPO/install.sh" "$@" 2>&1)"; COD=$?
}
permisos() { stat -c %a "$1" 2>/dev/null || stat -f %Lp "$1"; }

echo "Instalador"
bash -n "$AQUI/install.sh"; chequear "bash -n install.sh" $?

# 1. --agente codex
H1="$TMP/h-codex"
instalar "$H1" --agente codex --url "$URL_OK" --key "$CLAVE" --sin-probar --yes --zona UTC
chequear "--agente codex termina bien" $COD "$SALIDA"
[ -f "$H1/.agents/skills/botonera/SKILL.md" ]; chequear "codex instala en ~/.agents/skills/botonera" $?
[ -f "$H1/.agents/skills/botonera/rot.md" ]; chequear "codex trae rot.md" $?
if grep -q '~/\.claude' "$H1/.agents/skills/botonera/SKILL.md" "$H1/.agents/skills/botonera/rot.md"; then mal "el SKILL.md y rot.md instalados para codex no nombran ~/.claude"; else ok "el SKILL.md y rot.md instalados para codex no nombran ~/.claude"; fi
grep -q '~/\.agents/skills/botonera/armar\.py' "$H1/.agents/skills/botonera/SKILL.md"; chequear "el SKILL.md de codex usa la ruta real" $?
printf '%s' "$SALIDA" | grep -q '\$botonera'; chequear "el cierre de codex nombra \$botonera" $?
printf '%s' "$SALIDA" | grep -q "$H1/.config/botonera/instalar.sql"; chequear "imprime la ruta absoluta de instalar.sql" $?
printf '%s' "$SALIDA" | grep -Eq 'pbcopy|wl-copy|xclip|cat '; chequear "imprime el comando para copiar instalar.sql" $?

# 2. claude por defecto
H2="$TMP/h-claude"
instalar "$H2" --url "$URL_OK" --key "$CLAVE" --sin-probar --yes --zona UTC
[ -f "$H2/.claude/skills/botonera/SKILL.md" ]; chequear "sin --agente instala en ~/.claude/skills/botonera" $?
printf '%s' "$SALIDA" | grep -q '/botonera'; chequear "el cierre de claude nombra /botonera" $?

# 3. --agente otro exige --skill-dir; --skill-dir gana
instalar "$TMP/h-otro" --agente otro --url "$URL_OK" --key "$CLAVE" --sin-probar --yes
[ "$COD" -ne 0 ] && printf '%s' "$SALIDA" | grep -q -- '--skill-dir'; chequear "--agente otro sin --skill-dir falla con mensaje" $?
instalar "$TMP/h-otro" --agente codex --skill-dir "$TMP/mi-agente/skill" --url "$URL_OK" --key "$CLAVE" --sin-probar --yes
[ -f "$TMP/mi-agente/skill/SKILL.md" ]; chequear "--skill-dir gana sobre --agente" $?

# 4. --solo-skill
H4="$TMP/h-solo"
rm -f "$REPO/web/config.js"
instalar "$H4" --solo-skill --agente claude --yes
chequear "--solo-skill termina bien" $COD "$SALIDA"
[ -f "$H4/.claude/skills/botonera/SKILL.md" ]; chequear "--solo-skill copia el skill" $?
[ ! -e "$H4/.config/botonera/env" ] && [ ! -e "$H4/.config/botonera/instalar.sql" ]; chequear "--solo-skill no crea env ni SQL" $?
[ ! -e "$REPO/web/config.js" ]; chequear "--solo-skill no crea web/config.js" $?
printf '%s' "$SALIDA" | grep -q 'BM_ENV_FILE' && printf '%s' "$SALIDA" | grep -q 'BM_SESSION_ID=bot-'; chequear "--solo-skill imprime la receta del bot" $?
instalar "$H4" --solo-skill --yes
[ "$COD" -ne 0 ]; chequear "--solo-skill sin --agente ni --skill-dir falla" $?

# 5. URL: https obligatorio salvo localhost
instalar "$TMP/h-http" --url "http://ejemplo.com" --key "$CLAVE" --sin-probar --yes
[ "$COD" -ne 0 ] && printf '%s' "$SALIDA" | grep -q 'https://'; chequear "http://ejemplo.com se rechaza" $?
instalar "$TMP/h-local" --url "http://localhost:55321" --key "$CLAVE" --sin-probar --yes
chequear "http://localhost:55321 se acepta" $COD "$SALIDA"
instalar "$TMP/h-sonda" --url "http://127.0.0.1:9" --key "$CLAVE" --yes
[ "$COD" -ne 0 ] && printf '%s' "$SALIDA" | grep -q 'no responden'; chequear "sin --sin-probar, una URL que no responde falla con el mensaje" $?

# 6. secreto: se reusa, permisos 600, no sale por stdout
ENV2="$H2/.config/botonera/env"
SEC1="$(sed -n 's/^BM_SECRET=//p' "$ENV2")"
[ -n "$SEC1" ]; chequear "el env tiene BM_SECRET" $?
printf '%s' "$SALIDA$(HOME="$H2" bash "$REPO/install.sh" --url "$URL_OK" --key "$CLAVE" --sin-probar --yes --zona UTC 2>&1)" | grep -qF "$SEC1"; R=$?
[ "$R" -ne 0 ]; chequear "el secreto no aparece en stdout" $?
SEC2="$(sed -n 's/^BM_SECRET=//p' "$ENV2")"
[ "$SEC1" = "$SEC2" ]; chequear "la segunda corrida reusa el secreto" $?
[ "$(permisos "$ENV2")" = "600" ]; chequear "env queda con permisos 600" $?
[ "$(permisos "$H2/.config/botonera/instalar.sql")" = "600" ]; chequear "instalar.sql queda con permisos 600" $?
grep -qF "$SEC1" "$H2/.config/botonera/instalar.sql"; R=$?
[ "$R" -ne 0 ]; chequear "instalar.sql lleva el hash y no el secreto" $?

# 7. maestro.py
echo "Scripts"
SK="$H2/.claude/skills/botonera"
cat > "$TMP/env-bot" <<ENVB
SUPABASE_URL=https://bot.supabase.co
SUPABASE_ANON_KEY=sb_clave_bot
BM_SECRET=secreto-de-bot
ENVB
HV="$TMP/h-vacio"; mkdir -p "$HV"
R="$(cd "$SK" && HOME="$HV" BM_ENV_FILE="$TMP/env-bot" python3 -B -c 'import maestro; print(maestro.config()["SUPABASE_URL"])' 2>&1)"
[ "$R" = "https://bot.supabase.co" ]; chequear "maestro.py toma BM_ENV_FILE" $? "$R"
R="$(cd "$SK" && HOME="$H2" BM_ENV_FILE="$TMP/env-bot" python3 -B -c 'import maestro; print(maestro.config()["SUPABASE_URL"])' 2>&1)"
[ "$R" = "https://bot.supabase.co" ]; chequear "BM_ENV_FILE gana sobre ~/.config/botonera/env" $? "$R"
mkdir -p "$HV/.config/botonera"; cp "$TMP/env-bot" "$HV/.config/botonera/env-bot"
R="$(cd "$SK" && HOME="$HV" python3 -B -c 'import maestro; print(maestro.config()["BM_SECRET"])' 2>&1)"
[ "$R" = "secreto-de-bot" ]; chequear "maestro.py cae a ~/.config/botonera/env-bot" $? "$R"
sed 's#https://bot.supabase.co#http://ejemplo.com#' "$TMP/env-bot" > "$TMP/env-http"
R="$(cd "$SK" && HOME="$HV" BM_ENV_FILE="$TMP/env-http" python3 -B -c 'import maestro; print(maestro.config())' 2>/dev/null)"
[ "$R" = "None" ]; chequear "maestro.py rechaza SUPABASE_URL http:// que no es localhost" $? "$R"

# 8. pin.py
R="$(cd "$SK" && HOME="$H2" python3 -B pin.py poner 1234 2>&1)"; COD=$?
[ "$COD" -ne 0 ] && printf '%s' "$R" | grep -q 'no se pasa por argumento'; chequear "pin.py poner 1234 falla con mensaje" $? "$R"

# 9. esperar.py
R="$(cd "$SK" && python3 -B esperar.py --help 2>&1)"
printf '%s' "$R" | grep -q -- '--una-vez'; chequear "esperar.py --help nombra --una-vez" $?
sed 's#https://bot.supabase.co#http://127.0.0.1:9#' "$TMP/env-bot" > "$TMP/env-local"
R="$(cd "$SK" && HOME="$HV" BM_ENV_FILE="$TMP/env-local" python3 -B esperar.py una-clave --una-vez 2>&1)"; COD=$?
[ "$COD" -ne 0 ]; chequear "esperar.py --una-vez sale sin colgarse cuando no llega al servidor" $? "$COD"

echo
echo "$PASAN pasan, $FALLAN fallan"
[ "$FALLAN" -eq 0 ]

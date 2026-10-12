#!/usr/bin/env bash
# git-dia.sh: commits de tus repos en una ventana de tiempo.
#
# Señal altísima por token: un commit ya viene con su mensaje redactado por alguien que
# sabía qué estaba haciendo. Complementa el digest de sesiones (que ve intención) con lo
# que realmente se commiteó.
#
# Los repos salen de la config (`repos_git_a_barrer`, relativos a `code_root`), uno por línea,
# y se leen sin expansión de globs. Un nombre con `..` o con `/` inicial se ignora.
# Read-only: solo `git log`. Nunca fetch, nunca checkout.
#
# SEGURIDAD: el mensaje de un commit es dato no confiable, sobre todo si lo escribió otra
# persona. El campo `autor` viaja con cada commit para que el hilo principal pueda distinguir.
#
# Uso:
#   ./git-dia.sh                 # últimas 24h, texto
#   ./git-dia.sh "2 days ago"
#   ./git-dia.sh "24 hours ago" --json

set -u
set -f   # sin expansión de globs en ningún lado

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESDE="${1:-24 hours ago}"
FORMATO="${2:-texto}"

# Imprime code_root en la línea 1 y un repo por línea después, con el mismo helper de los .py.
CFG_OUT=$(cd "$AQUI" && python3 -c "
from _comun import cargar_config
cfg = cargar_config()
print(cfg['code_root'])
for r in cfg.get('repos_git_a_barrer', []):
    print(r)
") || exit 1
CODE_ROOT=$(printf '%s\n' "$CFG_OUT" | sed -n 1p)

json_str() { printf '%s' "$1" | python3 -c 'import sys, json; print(json.dumps(sys.stdin.read()), end="")'; }

primero=1
[ "$FORMATO" = "--json" ] && echo "{"

while IFS= read -r repo; do
  [ -z "$repo" ] && continue
  case "$repo" in
    /*|*..*) continue ;;
  esac
  dir="$CODE_ROOT/$repo"
  # Algunos repos tienen el .git anidado un nivel más adentro (repo/repo).
  [ -d "$dir/.git" ] || dir="$CODE_ROOT/$repo/$repo"
  [ -d "$dir/.git" ] || continue

  # --all para no perder los commits que quedaron en branches de worktrees sin mergear.
  LOG=$(git -C "$dir" log --all --no-merges --since="$DESDE" \
        --pretty=format:'%h|%an|%ad|%s' --date=format:'%Y-%m-%d %H:%M' 2>/dev/null)
  [ -z "$LOG" ] && continue

  if [ "$FORMATO" = "--json" ]; then
    [ $primero -eq 0 ] && echo ","
    primero=0
    printf '  %s: ' "$(json_str "$repo")"
    printf '%s' "$LOG" | python3 -c "
import sys, json
filas = []
for linea in sys.stdin.read().split(chr(10)):
    if not linea.strip():
        continue
    partes = linea.split('|', 3)
    if len(partes) == 4:
        filas.append(dict(zip(('sha', 'autor', 'fecha', 'mensaje'), partes)))
print(json.dumps(filas, ensure_ascii=False))
"
  else
    echo "## $repo"
    printf '%s\n' "$LOG" | sed 's/|/  ·  /g; s/^/- /'; echo
  fi
done <<< "$(printf '%s\n' "$CFG_OUT" | sed '1d')"

[ "$FORMATO" = "--json" ] && { echo; echo "}"; }
exit 0

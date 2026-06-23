#!/usr/bin/env bash
#
# check-update.sh — compara tu versión del kit con la publicada.
# El paso DET del skill `actualizar`. No instala nada: solo te dice si estás al día.
# Uso:  bash check-update.sh
set -euo pipefail

REPO="brunogiel/sabe"
RAW="https://raw.githubusercontent.com/${REPO}/main"
LOCAL_FILE="${HOME}/.claude/skills/sabe-coach/VERSION"

if [ ! -f "$LOCAL_FILE" ]; then
  echo "No encuentro $LOCAL_FILE. ¿Está instalado el método (corriste install.sh)?"
  exit 1
fi

LOCAL="$(tr -d '[:space:]' < "$LOCAL_FILE")"
REMOTE="$(curl -fsSL "${RAW}/VERSION" 2>/dev/null | tr -d '[:space:]' || true)"

if [ -z "$REMOTE" ]; then
  echo "No pude consultar la versión publicada (¿sin internet?). Probá de nuevo más tarde."
  exit 2
fi

echo "tuya:      $LOCAL"
echo "publicada: $REMOTE"

# Comparación por orden de versión (la mayor gana). Si difieren, hay update.
if [ "$LOCAL" = "$REMOTE" ]; then
  echo "estado: al-dia"
elif [ "$(printf '%s\n%s\n' "$LOCAL" "$REMOTE" | sort -V | tail -1)" = "$REMOTE" ]; then
  echo "estado: hay-update"
else
  echo "estado: adelantada"   # tu local es más nueva que main (raro, ej. dev)
fi

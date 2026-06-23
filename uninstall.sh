#!/usr/bin/env bash
#
# Agentic Second Brain uninstaller
# https://github.com/brunogiel/agentic-second-brain
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/uninstall.sh | SB_YES=1 bash
#   (o, si clonaste el repo:  bash uninstall.sh)
#
# Saca SOLO el motor global del método (~/.claude/skills/: el coach + actualizar + migrar).
# NUNCA toca tu carpeta/brain: tu CLAUDE.md, tu identidad, tus proyectos, tu 0. Inbox,
# tus Recursos y tus skills de uso quedan intactos. El método se instala como una app;
# esto desinstala la app, no borra tus datos.
set -euo pipefail

SKILLS_DIR="${HOME}/.claude/skills"
COMMANDS_DIR="${HOME}/.claude/commands"
METHOD_SKILLS=("agentic-second-brain-coach" "actualizar")   # migrar ya no es skill (es doc del coach); actualizar es Code-only
METHOD_COMMANDS=("asb" "asb-coach" "asb-slop" "asb-write" "asb-panel" "asb-council" "asb-prompt" "asb-deck" "asb-audit" "asb-doc" "asb-simple")   # el toolkit /asb-* (Code: ~/.claude/commands/)

echo ""
echo "🧠  Agentic Second Brain: desinstalar el motor global"
echo ""

# --- qué hay para sacar ---
present=0
echo "Esto saca SOLO el método (instalado como app):"
for s in "${METHOD_SKILLS[@]}"; do
  if [ -d "${SKILLS_DIR}/${s}" ]; then
    echo "  • ${SKILLS_DIR}/${s}"
    present=$((present + 1))
  fi
done

if [ "$present" -eq 0 ]; then
  echo "  (no encontré el motor global en ${SKILLS_DIR}; quizás ya lo sacaste,"
  echo "   o está bundled dentro de tu carpeta para Cowork. En ese caso borrás la carpeta vos.)"
  echo ""
  echo "Tu carpeta/brain no se toca en ningún caso."
  exit 0
fi

echo ""
echo "❗ Lo que NO se toca (tu contenido, queda intacto):"
echo "  • tu carpeta del brain entera: CLAUDE.md, ESTADO.md, ESCALERA.md, AGENTS.md"
echo "  • tu identidad (2. Áreas/yo/), tus proyectos, tu 0. Inbox/, tus Recursos"
echo "  • tus skills de uso (la carpeta visible skills/ de tu brain)"
echo ""

# --- confirmación (segura tanto en pipe como interactivo) ---
if [ "${1:-}" = "-y" ] || [ "${SB_YES:-}" = "1" ]; then
  reply="s"
elif [ -t 0 ]; then
  printf "¿Saco el motor global? [s/N] "
  read -r reply
else
  echo "En modo pipe necesito confirmación explícita. Volvé a correr con SB_YES=1:"
  echo "  curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/uninstall.sh | SB_YES=1 bash"
  exit 0
fi

case "$reply" in
  s | S | si | Si | SI | y | Y) ;;
  *) echo "Cancelado. No toqué nada."; exit 0 ;;
esac

# --- sacar solo el motor ---
for s in "${METHOD_SKILLS[@]}"; do
  if [ -d "${SKILLS_DIR}/${s}" ]; then
    rm -rf "${SKILLS_DIR}/${s}"
    echo "  ✓ saqué ${s}"
  fi
done
# --- sacar los comandos slash del toolkit (Code: ~/.claude/commands/) ---
for c in "${METHOD_COMMANDS[@]}"; do
  if [ -f "${COMMANDS_DIR}/${c}.md" ]; then
    rm -f "${COMMANDS_DIR}/${c}.md"
    echo "  ✓ saqué /${c}"
  fi
done

echo ""
echo "✅ Listo. El motor global salió. Tu carpeta/brain quedó intacta."
echo "   Si además querés borrar tu contenido, borrá la carpeta a mano: es tuya, vos decidís."
echo ""

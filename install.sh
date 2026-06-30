#!/usr/bin/env bash
#
# Agentic Second Brain installer — vía Claude Code (terminal).
# https://github.com/brunogiel/agentic-second-brain
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/brunogiel/agentic-second-brain/main/install.sh | bash
#
# ¿En Cowork (sin terminal)? NO uses esto: instalá el plugin desde la app:
#   Customize → Plugins → Add marketplace → pegá  brunogiel/agentic-second-brain  → instalá el plugin "brain"
#
# Dos baldes, claros:
#   1. EL MÉTODO (global, ~/.claude/skills/): se instala como una app. El motor (el coach, +
#      el updater actualizar que es Code-only) más el kit que el coach usa (kit/brain + kit/skills)
#      bundled adentro del coach. Invisible; se usa vía /brain-coach.
#   2. TU BRAIN (esta carpeta): SOLO lo tuyo — CLAUDE.md (índice maestro) + ESTADO.md + ESCALERA.md +
#      AGENTS.md, las carpetas PARA + 0. Inbox, tu identidad en "2. Áreas/yo/", y skills/ (los
#      skills que usás, que el coach te va sumando). Nada del método ensucia tu carpeta.
# Descarga atómica: si algo falla, no te deja a medias. Después: abrí Claude acá y escribí /brain-coach
set -euo pipefail

REPO="brunogiel/agentic-second-brain"
BRANCH="main"
RAW="https://raw.githubusercontent.com/${REPO}/${BRANCH}"

# El mismo árbol del repo sirve al plugin (Cowork) y a este script (Code): una sola fuente.
#   skills/     = el motor ACTIVO (solo el coach; lo escanea el plugin)
#   motor-code/ = actualizar (Code-only: el plugin se autoactualiza, no va como skill del plugin)
#   kit/        = lo que el coach instala en tu brain (kit/brain = templates, kit/skills = catálogo)

# --- el método (global) ---
SKILLS_DIR="${HOME}/.claude/skills"
COACH_DIR="${SKILLS_DIR}/coach"          # el coach + sus piezas + el kit, bundled (global, mismo nombre que el plugin)
MOTOR_SRC="coach"                        # el skill motor en el repo (skills/coach); en el plugin se ve brain:coach
SKILLS_USO=("redactar" "anti-slop" "crear-skill" "evaluar-skill" "auditar-sistema" "triage" "ppt-builder" "panel" "council" "prompt-optimizer" "documenta" "simple" "verificar")  # kit/skills

# --- el brain que se scaffoldea (desde kit/brain/) ---
ROOT_FILES=("CLAUDE.md" "ESTADO.md" "ESCALERA.md" "AGENTS.md")
YO_FILES=("sobre-mi.md" "como-trabajo.md" "mi-estilo.md" "MEMORIA.md")
YO_EXTRA=("soul.md" "dev-prefs.md")   # NO se scaffoldean; el coach los suma después (van bundled en el kit)
RECURSOS=("arquitectura-skills.md" "anti-slop-writing.md")

echo ""
echo "🧠  Agentic Second Brain — instalando el método..."
echo ""

# --- 0. precheck de red ---
if ! curl -fsSL "${RAW}/VERSION" -o /dev/null 2>/dev/null; then
  echo "  ✗ No pude conectar con GitHub. Revisá tu internet y volvé a correr el comando."
  echo "    (No toqué nada todavía.)"
  exit 1
fi

# --- descarga atómica a tempdir ---
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fetch() {  # fetch <ruta-en-repo> <destino-en-tmp>
  mkdir -p "$(dirname "${TMP}/$2")"
  if ! curl -fsSL "${RAW}/$1" -o "${TMP}/$2"; then
    echo "  ✗ Falló la descarga de $1. Instalación cancelada (no quedó nada a medias)."
    exit 1
  fi
}

echo "  ↓ bajando archivos..."
# kit/brain (templates): se scaffoldea Y se bundlea con el coach
for f in "${ROOT_FILES[@]}"; do fetch "kit/brain/${f}" "kit/brain/${f}"; done
for f in "${YO_FILES[@]}";  do fetch "kit/brain/identidad/${f}" "kit/brain/identidad/${f}"; done
for f in "${YO_EXTRA[@]}";  do fetch "kit/brain/identidad/${f}" "kit/brain/identidad/${f}"; done
for f in "${RECURSOS[@]}";  do fetch "kit/brain/recursos/${f}"  "kit/brain/recursos/${f}";  done
fetch "kit/brain/inbox/INBOX.md" "kit/brain/inbox/INBOX.md"
# kit/skills (catálogo de skills de uso): se bundlea con el coach
for s in "${SKILLS_USO[@]}"; do fetch "kit/skills/${s}/SKILL.md" "kit/skills/${s}/SKILL.md"; done
# el motor (skills/coach en el repo)
fetch "skills/${MOTOR_SRC}/SKILL.md" "motor/${MOTOR_SRC}/SKILL.md"
# actualizar (Code-only): vive en motor-code/, lo bajamos para instalarlo global en Code
fetch "motor-code/actualizar/SKILL.md" "motor/actualizar/SKILL.md"
mkdir -p "${TMP}/motor/actualizar"
curl -fsSL "${RAW}/motor-code/actualizar/check-update.sh" -o "${TMP}/motor/actualizar/check-update.sh" 2>/dev/null || true
# las piezas del coach (hermanas de su SKILL.md), incluida la guía de migración
fetch "skills/${MOTOR_SRC}/reference.md"          "coach/reference.md"
fetch "skills/${MOTOR_SRC}/plantilla-proyecto.md" "coach/plantilla-proyecto.md"
fetch "skills/${MOTOR_SRC}/ejemplos.md"           "coach/ejemplos.md"
fetch "skills/${MOTOR_SRC}/migracion.md"          "coach/migracion.md"
fetch "VERSION"      "coach/VERSION"
fetch "CHANGELOG.md" "coach/CHANGELOG.md"

# comandos slash (Code): se instalan en ~/.claude/commands/ con prefijo brain- para no chocar
# con comandos genéricos. En el plugin (Cowork) se ven como brain:coach (sin prefijo redundante).
CONSERJE="brain"                                                                                              # commands/brain.md → /brain
TOOLKIT=("coach" "slop" "write" "panel" "council" "prompt" "deck" "audit" "doc" "simple" "triage" "verify" "newskill" "evalskill")   # commands/<x>.md → /brain-<x>
fetch "commands/${CONSERJE}.md" "commands/${CONSERJE}.md"
for c in "${TOOLKIT[@]}"; do fetch "commands/${c}.md" "commands/${c}.md"; done

# NOTA: este script NO arma tu carpeta del brain. Eso lo hace el coach, charlando y
# preguntándote (igual que en Cowork): así nada se crea sin tu OK. Acá solo instalamos
# el método (motor + kit) global. El brain lo armás vos con /brain-coach.

# ============ EL MÉTODO (global, ~/.claude/skills/) ============
mkdir -p "$SKILLS_DIR"
# el motor (coach) → instalado como ~/.claude/skills/coach/
mkdir -p "$COACH_DIR"
cp "${TMP}/motor/${MOTOR_SRC}/SKILL.md" "${COACH_DIR}/SKILL.md"
# actualizar (Code-only) global, con su script
mkdir -p "${SKILLS_DIR}/actualizar"
cp "${TMP}/motor/actualizar/SKILL.md" "${SKILLS_DIR}/actualizar/SKILL.md"
[ -f "${TMP}/motor/actualizar/check-update.sh" ] && cp "${TMP}/motor/actualizar/check-update.sh" "${SKILLS_DIR}/actualizar/check-update.sh"
# las piezas del coach, adentro de su carpeta (incluida la guía de migración)
cp "${TMP}/coach/reference.md"          "${COACH_DIR}/reference.md"
cp "${TMP}/coach/plantilla-proyecto.md" "${COACH_DIR}/plantilla-proyecto.md"
cp "${TMP}/coach/ejemplos.md"           "${COACH_DIR}/ejemplos.md"
cp "${TMP}/coach/migracion.md"          "${COACH_DIR}/migracion.md"
cp "${TMP}/coach/VERSION"               "${COACH_DIR}/VERSION"
cp "${TMP}/coach/CHANGELOG.md"          "${COACH_DIR}/CHANGELOG.md"
# el kit completo (brain + skills), bundled con el coach para que lo use después.
# Es contenido del MÉTODO (no de tu brain): refrescarlo en cada install/update es lo correcto;
# tu carpeta del brain es aparte y no se toca acá. Reemplazo atómico: copio primero, swap después,
# así nunca queda una ventana sin kit si algo falla a mitad de camino.
rm -rf "${COACH_DIR}/kit.new"
cp -R "${TMP}/kit" "${COACH_DIR}/kit.new"
rm -rf "${COACH_DIR}/kit"
mv "${COACH_DIR}/kit.new" "${COACH_DIR}/kit"
# comandos slash (Code-only): ~/.claude/commands/ con prefijo brain-
COMMANDS_DIR="${HOME}/.claude/commands"
mkdir -p "$COMMANDS_DIR"
cp "${TMP}/commands/${CONSERJE}.md" "${COMMANDS_DIR}/${CONSERJE}.md"                          # /brain (el conserje)
for c in "${TOOLKIT[@]}"; do cp "${TMP}/commands/${c}.md" "${COMMANDS_DIR}/brain-${c}.md"; done   # /brain-<x>
echo "  ✓ método instalado global (motor + kit de ${#SKILLS_USO[@]} skills) en ~/.claude/skills/"
echo "  ✓ comandos instalados en ~/.claude/commands/ (toolkit /brain-* completo)"

cat <<EOF

✅  Listo. El MÉTODO quedó instalado (motor + kit), global e invisible, en ~/.claude/skills/.
    Tu carpeta del brain NO se tocó: la armás vos con el coach, que te pregunta antes de crear nada
    (igual que en Cowork). El método es la app; el cerebro es tuyo.

Próximo paso: abrí Claude Code (o Cowork) en la carpeta donde quieras tu sistema y escribí:

   /brain                 ← el conserje: tu toolkit + dónde vas parado (empezá por acá)
   /brain-coach           ← el coach: arma/resetea tu sistema, te ubica y propone el próximo paso

EOF

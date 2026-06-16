#!/usr/bin/env bash
#
# SecondBrain installer
# https://github.com/brunogiel/secondbrain-claude
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/brunogiel/secondbrain-claude/main/install.sh | bash
#
# Dos baldes, claros:
#   1. EL MÉTODO (global, ~/.claude/skills/): se instala como una app. El coach lleva sus
#      piezas adentro de su propia carpeta (reference.md, plantillas, ejemplos, el catálogo de
#      skills de uso, la versión). Más actualizar y migrar. Invisible; se usa vía /second-brain-coach.
#   2. TU BRAIN (esta carpeta): SOLO lo tuyo — CLAUDE.md (router) + ESTADO.md + ESCALERA.md +
#      AGENTS.md, las carpetas PARA + 0. Inbox, tu identidad en "2. Áreas/yo/", y skills/ (los
#      skills que usás, que el coach te va sumando). Nada del método ensucia tu carpeta.
# El coach copia los skills de uso de su catálogo (global) a tu skills/ (visible) cuando los adoptás.
# Descarga atómica: si algo falla, no te deja a medias. Después: abrí Claude acá y escribí /second-brain-coach
set -euo pipefail

REPO="brunogiel/secondbrain-claude"
BRANCH="main"
RAW="https://raw.githubusercontent.com/${REPO}/${BRANCH}"

# --- tu brain (esta carpeta): solo tu contenido ---
ROOT_FILES=("CLAUDE.md" "ESTADO.md" "ESCALERA.md" "AGENTS.md")
YO_DIR="2. Áreas/yo"
YO_FILES=("sobre-mi.md" "como-trabajo.md" "mi-estilo.md" "MEMORIA.md")

# --- el método (global): el motor + las piezas que el coach lleva adentro ---
SKILLS_DIR="${HOME}/.claude/skills"
COACH_DIR="${SKILLS_DIR}/second-brain-coach"          # el coach + sus piezas bundled
SKILLS_MOTOR=("second-brain-coach" "actualizar" "migrar-de-claude-projects")
SKILLS_USO=("redactar" "anti-slop" "crear-skill" "evaluar-skill" "auditar-sistema" "triage" "ppt-builder")  # catálogo

echo ""
echo "🧠  SecondBrain — armando tu sistema..."
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
# tu brain
for f in "${ROOT_FILES[@]}"; do fetch "templates/${f}" "root/${f}"; done
for f in "${YO_FILES[@]}";   do fetch "templates/${f}" "yo/${f}";   done
fetch "templates/arquitectura-skills.md" "recursos/arquitectura-skills.md"
fetch "templates/INBOX.md"               "inbox/INBOX.md"
# el método: motor
for s in "${SKILLS_MOTOR[@]}"; do fetch ".claude/skills/${s}/SKILL.md" "motor/${s}/SKILL.md"; done
mkdir -p "${TMP}/motor/actualizar"
curl -fsSL "${RAW}/.claude/skills/actualizar/check-update.sh" -o "${TMP}/motor/actualizar/check-update.sh" 2>/dev/null || true
# el método: piezas que el coach lleva adentro
fetch "process/reference.md"          "bundle/reference.md"
fetch "templates/proyecto-CLAUDE.md"  "bundle/plantilla-proyecto.md"
fetch "templates/ejemplos.md"         "bundle/ejemplos.md"
fetch "VERSION"                       "bundle/VERSION"
fetch "CHANGELOG.md"                  "bundle/CHANGELOG.md"
# el método: catálogo de skills de uso
for s in "${SKILLS_USO[@]}"; do fetch "templates/skills/${s}/SKILL.md" "uso/${s}/SKILL.md"; done

# ============ TU BRAIN (esta carpeta) ============
for d in "0. Inbox" "1. Proyectos" "2. Áreas" "3. Recursos" "4. Archivo"; do mkdir -p "$d"; done
echo "  ✓ carpetas PARA + 0. Inbox"

place() {  # place <archivo-en-tmp> <destino>  — no pisa si ya existe
  if [ -e "$2" ]; then echo "  • $2 ya existe, lo dejo como está"
  else mkdir -p "$(dirname "$2")"; cp "${TMP}/$1" "$2"; echo "  ✓ $2"; fi
}
for f in "${ROOT_FILES[@]}"; do place "root/${f}" "$f"; done
for f in "${YO_FILES[@]}";   do place "yo/${f}" "${YO_DIR}/${f}"; done
place "recursos/arquitectura-skills.md" "3. Recursos/arquitectura-skills.md"
place "inbox/INBOX.md"                  "0. Inbox/INBOX.md"
mkdir -p "skills"   # tus skills de uso, a la vista (vacía; el coach la llena)
echo "  ✓ carpeta visible skills/ (vacía; el coach te suma skills, ruteados por tu CLAUDE.md)"

# ============ EL MÉTODO (global, ~/.claude/skills/) ============
mkdir -p "$SKILLS_DIR"
for s in "${SKILLS_MOTOR[@]}"; do
  mkdir -p "${SKILLS_DIR}/${s}"
  cp "${TMP}/motor/${s}/SKILL.md" "${SKILLS_DIR}/${s}/SKILL.md"
done
[ -f "${TMP}/motor/actualizar/check-update.sh" ] && cp "${TMP}/motor/actualizar/check-update.sh" "${SKILLS_DIR}/actualizar/check-update.sh"
# las piezas del coach, adentro de su carpeta
cp "${TMP}/bundle/reference.md"          "${COACH_DIR}/reference.md"
cp "${TMP}/bundle/plantilla-proyecto.md" "${COACH_DIR}/plantilla-proyecto.md"
cp "${TMP}/bundle/ejemplos.md"           "${COACH_DIR}/ejemplos.md"
cp "${TMP}/bundle/VERSION"               "${COACH_DIR}/VERSION"
cp "${TMP}/bundle/CHANGELOG.md"          "${COACH_DIR}/CHANGELOG.md"
# el catálogo de skills de uso, adentro del coach
mkdir -p "${COACH_DIR}/skills-disponibles"
for s in "${SKILLS_USO[@]}"; do
  mkdir -p "${COACH_DIR}/skills-disponibles/${s}"
  cp "${TMP}/uso/${s}/SKILL.md" "${COACH_DIR}/skills-disponibles/${s}/SKILL.md"
done
echo "  ✓ método instalado global (${#SKILLS_MOTOR[@]} skills + reference + catálogo de ${#SKILLS_USO[@]}) en ~/.claude/skills/"

cat <<EOF

✅  Listo. Dos baldes:
   👁  TU BRAIN (esta carpeta): CLAUDE.md + ESTADO.md + ESCALERA.md + AGENTS.md, carpetas PARA + 0. Inbox,
       tu identidad, y skills/ (vacía; el coach la llena). Solo lo tuyo.
   🔒 EL MÉTODO (global, invisible): el coach y sus piezas en ~/.claude/skills/. Se usa por nombre.

Próximo paso: abrí Claude Code (o Cowork) en esta carpeta y escribí:

   /second-brain-coach

Te hace un par de preguntas y arranca, de a un escalón.

EOF

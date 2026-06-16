#!/usr/bin/env bash
#
# SecondBrain installer
# https://github.com/brunogiel/secondbrain-claude
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/brunogiel/secondbrain-claude/main/install.sh | bash
#
# Topología (la regla, en 3 baldes):
#   1. VISIBLE en tu SB: tu contexto (PARA, identidad, CLAUDE.md, ESTADO, Inbox) y
#      los SKILLS QUE USÁS (en skills/, carpeta a secas). Estos NO se instalan todos de
#      una: el coach te los va sumando a medida que avanzás (redactar, anti-slop, triage,
#      auditar, crear-skill, abrir/cerrar-sesion). Los ves, los abrís, aprendés cómo están.
#      Se disparan desde la tabla "Mis skills" de tu CLAUDE.md (por eso andan en Claude
#      Code, Cowork y Codex por igual: los tres leen el CLAUDE.md, sin carpetas ocultas).
#   2. OCULTO en tu SB (.secondbrain/): el proceso — la doctrina (reference.md), la
#      plantilla de proyecto, y el CATÁLOGO de skills de uso (las versiones-fuente que
#      el coach copia a skills/ cuando adoptás una). Más el control de versión.
#   3. GLOBAL e invisible (~/.claude/skills/): SOLO el motor de armado — el coach,
#      más actualizar y migrar (mantenimiento). Se llaman por nombre (/second-brain-coach);
#      no ensucian tu carpeta.
# Descarga atómica: si algo falla, no te deja el sistema a medio armar.
# Después: abrí Claude Code (o Cowork) acá y escribí  /second-brain-coach
set -euo pipefail

REPO="brunogiel/secondbrain-claude"
BRANCH="main"
RAW="https://raw.githubusercontent.com/${REPO}/${BRANCH}"

# --- qué se baja ---
ROOT_FILES=("CLAUDE.md" "ESTADO.md" "AGENTS.md")          # raíz, visibles
YO_DIR="2. Áreas/yo"
YO_FILES=("sobre-mi.md" "como-trabajo.md" "mi-estilo.md" "MEMORIA.md")
# El MOTOR de armado: global e invisible. Solo el coach + mantenimiento.
SKILLS_MOTOR=("second-brain-coach" "actualizar" "migrar-de-claude-projects")
# Skills de USO: el usuario los ve y los usa. NO se instalan acá; se dejan en el
# catálogo oculto (.secondbrain/skills-disponibles/) y el coach los copia a skills/
# (visible) a medida que el usuario avanza.
SKILLS_USO=("abrir-sesion" "cerrar-sesion" "redactar" "anti-slop" "crear-skill" "evaluar-skill" "auditar-sistema" "triage")
SKILLS_DIR="${HOME}/.claude/skills"
SB_DIR=".secondbrain"
CAT_DIR="${SB_DIR}/skills-disponibles"

echo ""
echo "🧠  SecondBrain — armando tu sistema..."
echo ""

# --- 0. precheck de red: si no hay conexión, frenamos ANTES de crear nada ---
if ! curl -fsSL "${RAW}/VERSION" -o /dev/null 2>/dev/null; then
  echo "  ✗ No pude conectar con GitHub. Revisá tu internet y volvé a correr el comando."
  echo "    (No toqué nada todavía.)"
  exit 1
fi

# --- descarga atómica: bajamos todo a un tempdir y recién al final movemos ---
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
for f in "${ROOT_FILES[@]}";  do fetch "templates/${f}" "root/${f}"; done
for f in "${YO_FILES[@]}";    do fetch "templates/${f}" "yo/${f}";   done
fetch "templates/arquitectura-skills.md" "recursos/arquitectura-skills.md"
fetch "templates/INBOX.md"               "inbox/INBOX.md"
fetch "templates/proyecto-CLAUDE.md"     "sb/plantilla-proyecto.md"
fetch "templates/ejemplos.md"            "sb/ejemplos.md"
fetch "process/reference.md"             "sb/reference.md"
fetch "VERSION"                          "sb/VERSION"
fetch "CHANGELOG.md"                     "sb/CHANGELOG.md"
for s in "${SKILLS_MOTOR[@]}"; do fetch ".claude/skills/${s}/SKILL.md" "motor/${s}/SKILL.md"; done
for s in "${SKILLS_USO[@]}";   do fetch "templates/skills/${s}/SKILL.md" "uso/${s}/SKILL.md"; done
# script opcional del skill actualizar (no aborta si no está)
mkdir -p "${TMP}/motor/actualizar"
curl -fsSL "${RAW}/.claude/skills/actualizar/check-update.sh" -o "${TMP}/motor/actualizar/check-update.sh" 2>/dev/null || true

# --- a partir de acá ya tenemos todo: movemos a destino ---

# 1. Carpetas PARA + bandeja de captura
for d in "0. Inbox" "1. Proyectos" "2. Áreas" "3. Recursos" "4. Archivo"; do
  mkdir -p "$d"
done
echo "  ✓ carpetas PARA + 0. Inbox"

place() {  # place <archivo-en-tmp> <destino>  — no pisa si ya existe
  if [ -e "$2" ]; then
    echo "  • $2 ya existe, lo dejo como está"
  else
    mkdir -p "$(dirname "$2")"
    cp "${TMP}/$1" "$2"
    echo "  ✓ $2"
  fi
}

# 2. Raíz (router + tablero + puntero AGENTS)
for f in "${ROOT_FILES[@]}"; do place "root/${f}" "$f"; done

# 3. Identidad en PARA
for f in "${YO_FILES[@]}"; do place "yo/${f}" "${YO_DIR}/${f}"; done

# 3b. Recursos que vienen llenos + protocolo de inbox
place "recursos/arquitectura-skills.md" "3. Recursos/arquitectura-skills.md"
place "inbox/INBOX.md"                  "0. Inbox/INBOX.md"

# 4. Proceso oculto (.secondbrain/): doctrina + plantilla + catálogo de skills de uso.
#    reference.md NO se pisa (lo puede editar el coach); VERSION/CHANGELOG se refrescan.
mkdir -p "$SB_DIR"
place "sb/reference.md"          "${SB_DIR}/reference.md"
place "sb/plantilla-proyecto.md" "${SB_DIR}/plantilla-proyecto.md"
place "sb/ejemplos.md"           "${SB_DIR}/ejemplos.md"
cp "${TMP}/sb/VERSION"      "${SB_DIR}/VERSION"
cp "${TMP}/sb/CHANGELOG.md" "${SB_DIR}/CHANGELOG.md"
# El catálogo: las versiones-fuente de los skills de uso, ocultas. El coach copia de acá a skills/.
mkdir -p "$CAT_DIR"
for s in "${SKILLS_USO[@]}"; do
  mkdir -p "${CAT_DIR}/${s}"
  cp "${TMP}/uso/${s}/SKILL.md" "${CAT_DIR}/${s}/SKILL.md"
done
echo "  ✓ proceso oculto en ${SB_DIR}/ (doctrina + catálogo de ${#SKILLS_USO[@]} skills de uso)"

# 5. El MOTOR de armado: global e invisible. Solo coach + mantenimiento. Se refresca siempre.
mkdir -p "$SKILLS_DIR"
for s in "${SKILLS_MOTOR[@]}"; do
  mkdir -p "${SKILLS_DIR}/${s}"
  cp "${TMP}/motor/${s}/SKILL.md" "${SKILLS_DIR}/${s}/SKILL.md"
done
[ -f "${TMP}/motor/actualizar/check-update.sh" ] && cp "${TMP}/motor/actualizar/check-update.sh" "${SKILLS_DIR}/actualizar/check-update.sh"
echo "  ✓ motor instalado (${#SKILLS_MOTOR[@]} skills global/invisible en ~/.claude/skills/)"

# 6. Tus skills VISIBLES: carpeta skills/ a secas (real, a la vista). Arranca vacía; el coach
#    la va llenando. Se disparan desde la tabla "Mis skills" de tu CLAUDE.md — por eso andan
#    igual en Claude Code, Cowork y Codex (los tres leen el CLAUDE.md), sin carpetas ocultas.
mkdir -p "skills"
echo "  ✓ carpeta visible skills/ (vacía; el coach te va sumando skills, ruteados por tu CLAUDE.md)"

cat <<EOF

✅  Listo. Se armó tu SecondBrain:
   • 5 carpetas (0. Inbox + PARA)  • CLAUDE.md + ESTADO.md + AGENTS.md  • tu identidad
   • el motor (${#SKILLS_MOTOR[@]} skills) global e invisible  • skills/ vacía, lista para que el coach la llene

Cómo queda, en una línea:
   👁  ves: tu contexto + skills/ (tus skills, que el coach va sumando)
   🔒 no ves: .secondbrain/ (proceso) y el motor (~/.claude/skills/, se llama por nombre)

Próximo paso: abrí Claude Code (o Cowork) en esta carpeta y escribí:

   /second-brain-coach

Te hace un par de preguntas y arranca, de a un escalón.

EOF

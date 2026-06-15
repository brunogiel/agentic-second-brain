#!/usr/bin/env bash
#
# SecondBrain installer
# https://github.com/brunogiel/secondbrain-claude
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/brunogiel/secondbrain-claude/main/install.sh | bash
#
# What it does:
#   1. Creates your PARA folders (visible) in the current directory.
#   2. Drops your starter files (visible): thin root CLAUDE.md + identity + ESTADO. Never overwrites.
#   3. Sets up the hidden .secondbrain/ folder (the process: doctrine + version).
#   4. Installs the skills globally in ~/.claude/skills/ so they work in every project.
# After install, open Claude Code (or Cowork) here and type:  /second-brain-coach
set -euo pipefail

REPO="brunogiel/secondbrain-claude"   # confirm the final repo slug here
BRANCH="main"
RAW="https://raw.githubusercontent.com/${REPO}/${BRANCH}"

# Visible at root (your stuff). Never overwritten.
ROOT_FILES=("CLAUDE.md" "sobre-mi.md" "como-trabajo.md" "mi-estilo.md" "MEMORIA.md" "ESTADO.md")
# Skills (the coach is the entry point).
SKILLS=("second-brain-coach" "redactar" "anti-slop")
SKILLS_DIR="${HOME}/.claude/skills"
SB_DIR=".secondbrain"

echo ""
echo "🧠  SecondBrain — armando tu sistema..."
echo ""

# 1. PARA folders (visible)
for d in "1. Proyectos" "2. Áreas" "3. Recursos" "4. Archivo"; do
  mkdir -p "$d"
done
echo "  ✓ carpetas PARA creadas"

# 2. Root files (visible, skip if present, never overwrite your content)
for f in "${ROOT_FILES[@]}"; do
  if [ -e "$f" ]; then
    echo "  • $f ya existe, lo dejo como está"
  else
    curl -fsSL "${RAW}/templates/${f}" -o "$f"
    echo "  ✓ $f"
  fi
done

# 3. Hidden process folder (.secondbrain/): doctrine + version. No se ve en Finder, sincroniza igual.
mkdir -p "$SB_DIR"
curl -fsSL "${RAW}/templates/reference.md" -o "${SB_DIR}/reference.md"
curl -fsSL "${RAW}/VERSION"                -o "${SB_DIR}/VERSION"
curl -fsSL "${RAW}/CHANGELOG.md"           -o "${SB_DIR}/CHANGELOG.md"
echo "  ✓ proceso oculto en ${SB_DIR}/"

# 4. Skills (global)
mkdir -p "$SKILLS_DIR"
for s in "${SKILLS[@]}"; do
  mkdir -p "${SKILLS_DIR}/${s}"
  curl -fsSL "${RAW}/skills/${s}/SKILL.md" -o "${SKILLS_DIR}/${s}/SKILL.md"
  echo "  ✓ skill instalado: ${s}"
done

echo ""
echo "Listo. Abrí Claude Code (o Cowork) en esta carpeta y escribí:  /second-brain-coach"
echo ""

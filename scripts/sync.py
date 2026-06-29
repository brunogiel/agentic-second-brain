#!/usr/bin/env python3
"""Sincroniza los comandos /brain-* del toolkit con su kit-skill.

Fuente única de verdad = la kit-skill (`kit/skills/<skill>/SKILL.md`).
El comando (`commands/<cmd>.md`) se arma como:
    su propia cabecera  (frontmatter + linea-puente con $ARGUMENTS, todo lo anterior al primer "# ")
  + el body de la kit-skill  (del primer "# " en adelante)

Asi el body vive en UN solo lugar (la kit-skill) y el comando solo aporta su
frontmatter `description` + la linea de intro. Esto mata el riesgo de que las dos
copias se desincronicen a mano.

Uso:
    python3 scripts/sync.py          regenera los comandos desde las kit-skills
    python3 scripts/sync.py --check  no escribe; sale con codigo 1 si alguno difiere

No corre en runtime (el plugin sirve archivos estaticos). Es una herramienta de repo:
corrrunla despues de editar una kit-skill, y/o como check en pre-commit / CI.
"""
import os
import sys

# comando -> kit-skill (los 13 del toolkit; brain y brain-coach NO mapean a una kit-skill).
# Los comandos viven con nombre pelado en el repo (commands/slop.md) para verse brain:slop en el plugin.
PAIRS = {
    "slop": "anti-slop",
    "write": "redactar",
    "prompt": "prompt-optimizer",
    "panel": "panel",
    "council": "council",
    "deck": "ppt-builder",
    "audit": "auditar-sistema",
    "doc": "documenta",
    "simple": "simple",
    "triage": "triage",
    "verify": "verificar",
    "newskill": "crear-skill",
    "evalskill": "evaluar-skill",
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def split_at_title(text):
    """Devuelve (cabecera, body). El body arranca en la primera linea que empieza con '# '."""
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("# "):
            return "".join(lines[:i]), "".join(lines[i:])
    return text, ""


def main():
    check = "--check" in sys.argv
    drift = []
    for cmd, skill in PAIRS.items():
        cmd_path = os.path.join(ROOT, "commands", cmd + ".md")
        kit_path = os.path.join(ROOT, "kit", "skills", skill, "SKILL.md")
        if not os.path.exists(cmd_path) or not os.path.exists(kit_path):
            print(f"  FALTA: {cmd} <-> {skill} (revisar paths)")
            drift.append(cmd)
            continue
        with open(cmd_path) as f:
            current = f.read()
        header, _ = split_at_title(current)
        with open(kit_path) as f:
            _, body = split_at_title(f.read())
        regenerated = header + body
        if check:
            if current != regenerated:
                drift.append(cmd)
        elif current != regenerated:
            with open(cmd_path, "w") as f:
                f.write(regenerated)
            print(f"  sync  commands/{cmd}.md  <-  kit/skills/{skill}")
        else:
            print(f"  ok    commands/{cmd}.md")

    if check:
        if drift:
            print("DESINCRONIZADO: " + ", ".join(drift))
            print("Corré: python3 scripts/sync.py")
            sys.exit(1)
        print(f"OK: los {len(PAIRS)} comandos del toolkit están en sync con sus kit-skills.")
    else:
        print(f"OK: {len(PAIRS)} comandos regenerados desde las kit-skills.")


if __name__ == "__main__":
    main()

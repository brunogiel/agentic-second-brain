#!/usr/bin/env python3
"""Sincroniza los comandos /brain-* del toolkit con su kit-skill.

Fuente única de verdad = la kit-skill (`kit/skills/<skill>/SKILL.md`).
El comando (`commands/<cmd>.md`) se arma como:
    su propia cabecera  (frontmatter + linea-puente con $ARGUMENTS, todo lo anterior al primer "# ")
  + el body de la kit-skill  (del primer "# " en adelante)

Un comando puede mapear a VARIAS kit-skills (una lista en PAIRS). Ahi los bodies se
concatenan en orden, separados por una regla `---`. Es el caso de `brain-simple`, que
tiene modos: el modo corto lo resuelve `simple` y los visuales los resuelve
`repaso-visual`, y el comando tiene que viajar con los dos adentro para ser autocontenido.

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

# comando -> kit-skill, o lista de kit-skills (brain y brain-coach NO mapean a ninguna).
# Los comandos viven con prefijo brain- en el repo (commands/brain-slop.md) porque Cowork muestra
# el comando por su nombre de archivo (/brain-slop), no por el namespace del plugin.
PAIRS = {
    "brain-slop": "anti-slop",
    "brain-write": "redactar",
    "brain-prompt": "prompt-optimizer",
    "brain-panel": "panel",
    "brain-council": "council",
    "brain-deck": "ppt-builder",
    "brain-audit": "auditar-sistema",
    "brain-doc": "documenta",
    # brain-simple tiene 3 modos: el corto sale de `simple`, los visuales de `repaso-visual`.
    # `brain-recap` se dio de baja en la 3.0.0: era el mismo comando que `/brain-simple html`.
    "brain-simple": ["simple", "repaso-visual"],
    "brain-lesson": "leccion",
    "brain-messirve": "messirve",
    "brain-triage": "triage",
    "brain-verify": "verificar",
    "brain-ship": "publicar",
    "brain-newskill": "crear-skill",
    "brain-evalskill": "evaluar-skill",
    "brain-spec": "spec",
    "brain-transcribe": "transcribir",
    "brain-tidy": "ordenar",
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
    for cmd, skills in PAIRS.items():
        if isinstance(skills, str):
            skills = [skills]
        cmd_path = os.path.join(ROOT, "commands", cmd + ".md")
        kit_paths = [os.path.join(ROOT, "kit", "skills", sk, "SKILL.md") for sk in skills]
        faltan = [p for p in kit_paths if not os.path.exists(p)]
        if not os.path.exists(cmd_path) or faltan:
            print(f"  FALTA: {cmd} <-> {', '.join(skills)} (revisar paths)")
            drift.append(cmd)
            continue
        with open(cmd_path) as f:
            current = f.read()
        header, _ = split_at_title(current)
        bodies = []
        for kit_path in kit_paths:
            with open(kit_path) as f:
                _, body = split_at_title(f.read())
            bodies.append(body.rstrip() + "\n")
        regenerated = header + "\n---\n\n".join(bodies)
        if check:
            if current != regenerated:
                drift.append(cmd)
        elif current != regenerated:
            with open(cmd_path, "w") as f:
                f.write(regenerated)
            print(f"  sync  commands/{cmd}.md  <-  " + ", ".join("kit/skills/" + sk for sk in skills))
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

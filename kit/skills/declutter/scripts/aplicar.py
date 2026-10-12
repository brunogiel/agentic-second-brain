#!/usr/bin/env python3
"""Aplica lo aprobado y revierte. NUNCA borra.

    python3 aplicar.py --plan plan.json
    python3 aplicar.py --revertir <target>/_declutter-YYYY-MM-DD

El manifiesto registra TODA escritura, no solo los movimientos: cada archivo tocado
con el hash de su contenido previo, el destino de cada mudanza, los links reapuntados
y las ediciones de texto. Un manifiesto que solo anota movimientos no revierte:
devuelve el original y deja la copia en el destino, o sea recrea el duplicado.

plan.json = [{"accion":"mover"|"reubicar"|"editar", "path":..., "destino":...?,
              "contenido_nuevo":...?, "veredicto":..., "cita":...}]
"""
import argparse, hashlib, json, os, shutil, sys
from datetime import date, datetime


# El gate vive acá tambien, no solo en el censo: aplicar.py recibe un plan que pudo
# armar cualquiera. Un ejecutor ciego convierte las invariantes del SKILL.md en adorno.
# Sumá acá los archivos de identidad de tu sistema: los que definen cómo trabajás.
VEDADOS_NOMBRE = {"package-lock.json", "uv.lock", "poetry.lock", "yarn.lock",
                  "bun.lockb", "Cargo.lock", "Gemfile.lock", "composer.lock",
                  "pnpm-lock.yaml"}
VEDADOS_RUTA = ("/backups/", "/.git/", "/.obsidian/", "/.env", "/archive/",
                "/ARCHIVE/", "/_declutter-")


# El indice maestro de tu sistema: se propone el diff, no se edita. Ajusta la ruta.
MAESTRO = "__ponne_aca_tu_indice_maestro__"


def vedado(path):
    import os as _o
    if path.endswith(MAESTRO):
        return "es el CLAUDE.md maestro: se propone el diff, no se edita"
    if _o.path.basename(path) in VEDADOS_NOMBRE:
        return f"es intocable por nombre ({_o.path.basename(path)})"
    for frag in VEDADOS_RUTA:
        if frag in path:
            return f"vive bajo un path intocable ({frag.strip('/')})"
    return None


def h(path):
    if not os.path.isfile(path):
        return None
    m = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            m.update(b)
    return m.hexdigest()


def aplicar(plan_path):
    plan = json.load(open(plan_path, encoding="utf-8"))
    if not plan:
        sys.exit("plan vacío")
    target = os.path.abspath(plan[0].get("target") or os.path.dirname(plan[0]["path"]))
    base = target if os.path.isdir(target) else os.path.dirname(target)
    cuarentena = os.path.join(base, f"_declutter-{date.today()}")
    # Una segunda corrida el mismo dia NO pisa la anterior: su manifiesto dejaria de
    # describir la realidad y revertir mentiria diciendo "byte-identico".
    if os.path.exists(os.path.join(cuarentena, "manifiesto.json")):
        n = 2
        while os.path.exists(os.path.join(base, f"_declutter-{date.today()}-{n}")):
            n += 1
        cuarentena = os.path.join(base, f"_declutter-{date.today()}-{n}")
    os.makedirs(cuarentena, exist_ok=True)

    entradas, saltados = [], []
    for item in plan:
        p = os.path.abspath(item["path"])
        if not os.path.exists(p):
            saltados.append({"path": p, "motivo": "ya no existe (se movió entre el censo y ahora)"})
            continue
        motivo = vedado(p)
        if motivo:
            saltados.append({"path": p, "motivo": f"VEDADO: {motivo}"})
            continue
        if not p.startswith(base + os.sep):
            saltados.append({"path": p, "motivo": "VEDADO: esta fuera del target"})
            continue
        prev = h(p)
        if item["accion"] == "mover":
            rel = os.path.relpath(p, base)
            dest = os.path.join(cuarentena, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(p, dest)
            entradas.append({"accion": "mover", "origen": p, "destino": dest,
                             "hash_previo": prev, "veredicto": item.get("veredicto"),
                             "cita": item.get("cita")})
        elif item["accion"] == "reubicar":
            dest = os.path.abspath(item["destino"])
            if not dest.startswith(base + os.sep):
                saltados.append({"path": p, "motivo": "VEDADO: el destino sale del target"})
                continue
            if os.path.exists(dest):
                saltados.append({"path": p, "motivo": f"el destino ya existe, no se pisa: {dest}"})
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(p, dest)
            entradas.append({"accion": "reubicar", "origen": p, "destino": dest,
                             "hash_previo": prev, "veredicto": item.get("veredicto"),
                             "cita": item.get("cita")})
        elif item["accion"] == "editar":
            rel = os.path.relpath(p, base)
            backup = os.path.join(cuarentena, "_previas", rel)
            os.makedirs(os.path.dirname(backup), exist_ok=True)
            shutil.copy2(p, backup)          # la version previa COMPLETA, siempre
            open(p, "w", encoding="utf-8").write(item["contenido_nuevo"])
            entradas.append({"accion": "editar", "origen": p, "backup": backup,
                             "hash_previo": prev, "hash_nuevo": h(p),
                             "veredicto": item.get("veredicto"), "cita": item.get("cita")})
        else:
            saltados.append({"path": p, "motivo": f"accion desconocida: {item['accion']}"})

    manifiesto = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "target": target,
        "cuarentena": cuarentena,
        "escrituras": entradas,
        "saltados": saltados,
        "revertir_con": f'python3 aplicar.py --revertir "{cuarentena}"',
    }
    json.dump(manifiesto, open(os.path.join(cuarentena, "manifiesto.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    liberado = sum(os.path.getsize(e["destino"]) for e in entradas
                   if e["accion"] == "mover" and os.path.exists(e["destino"]))
    print(f"{len(entradas)} escrituras registradas · {round(liberado/1024/1024,1)} MB a cuarentena")
    if saltados:
        print(f"{len(saltados)} saltados (no se falló la corrida por eso)")
    print(f"revertir: {manifiesto['revertir_con']}")


def revertir(cuarentena):
    man_path = os.path.join(cuarentena, "manifiesto.json")
    if not os.path.isfile(man_path):
        sys.exit(f"sin manifiesto en {cuarentena}")
    man = json.load(open(man_path, encoding="utf-8"))
    ok, fallos = 0, []
    for e in reversed(man["escrituras"]):        # orden inverso: deshace pisadas entre items
        if e["accion"] in ("mover", "reubicar"):
            if not os.path.exists(e["destino"]):
                fallos.append((e["origen"], "falta en cuarentena")); continue
            os.makedirs(os.path.dirname(e["origen"]), exist_ok=True)
            shutil.move(e["destino"], e["origen"])
            dest = e["origen"]
        else:
            if not os.path.exists(e["backup"]):
                fallos.append((e["origen"], "falta el backup")); continue
            shutil.copy2(e["backup"], e["origen"])
            dest = e["origen"]
        if h(dest) == e["hash_previo"]:
            ok += 1
        else:
            fallos.append((dest, "hash distinto al original"))

    print(f"revertidos y verificados por hash: {ok}/{len(man['escrituras'])}")
    for p, m in fallos:
        print(f"  FALLO {m}: {p}", file=sys.stderr)
    if fallos:
        sys.exit(1)
    print(f"Todo byte-idéntico. La cuarentena quedó en {cuarentena}; borrala vos si querés.")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan")
    g.add_argument("--revertir")
    a = ap.parse_args()
    aplicar(a.plan) if a.plan else revertir(a.revertir)


if __name__ == "__main__":
    main()

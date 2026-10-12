#!/usr/bin/env python3
"""Barrido de mtime de tu brain, sin tope de resultados.

Por qué existe: el extractor de sesiones solo ve lo que se escribe con Write/Edit. Lo que se
hace por bash (mv, sed, scripts, refactors de estructura) es invisible para él. El mtime del
disco no miente.

Uso: python3 barrido-mtime.py --horas 24 [--json]

Agrupa por proyecto (las primeras dos carpetas). Excluye por NOMBRE de carpeta suelto (la
regla de privacidad del skill) y ruido conocido. NO recortar la salida con `head`: el
orden del filesystem es arbitrario y un bloque de archivos de ruido puede tapar el resto
de la ventana.
"""
import argparse
import collections
import json
import os
import time

from _comun import cargar_config

RUIDO_DIRS = {".git", "node_modules", "__pycache__", "backups"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horas", type=float, default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    cfg = cargar_config()
    raiz = cfg["brain_root"]
    horas = a.horas if a.horas is not None else cfg.get("ventana", {}).get("horas", 24)
    excl_dirs = RUIDO_DIRS | set(cfg.get("excluir_paths", []))
    state_dir = os.path.abspath(cfg["state_dir"])
    corte = time.time() - horas * 3600

    grupos = collections.defaultdict(list)
    total = 0
    for dp, dn, fn in os.walk(raiz):
        dn[:] = [x for x in dn if x not in excl_dirs]
        if os.path.abspath(dp).startswith(state_dir):
            dn[:] = []
            continue
        for f in fn:
            if f == ".DS_Store":
                continue
            fp = os.path.join(dp, f)
            try:
                m = os.path.getmtime(fp)
            except OSError:
                continue
            if m >= corte:
                r = os.path.relpath(fp, raiz)
                g = "/".join(r.split(os.sep)[:2]) if os.sep in r else "(raiz)"
                grupos[g].append((m, r))
                total += 1

    if a.json:
        print(json.dumps({"total": total,
                          "grupos": {g: [r for _, r in sorted(v)] for g, v in grupos.items()}},
                         ensure_ascii=False, indent=1))
        return

    print(f"TOTAL {total} archivos en {horas:g}h, {len(grupos)} grupos")
    for g, v in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
        v.sort()
        ini = time.strftime('%m-%d %H:%M', time.localtime(v[0][0]))
        fin = time.strftime('%m-%d %H:%M', time.localtime(v[-1][0]))
        print(f"\n## {g} ({len(v)})  {ini} a {fin}")
        for _, r in v[:15]:
            print("  ", r)
        if len(v) > 15:
            print(f"   ... y {len(v) - 15} más")


if __name__ == "__main__":
    main()

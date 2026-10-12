#!/usr/bin/env python3
"""Dibuja el arbol del target ANTES y DESPUES de aplicar el plan. No toca nada.

    python3 arbol.py <target> --plan plan.json [--niveles 2]

Corre SIEMPRE en el Paso 5, al lado de la tabla por item. La tabla dice que pasa con
cada archivo; el arbol dice como queda la carpeta. Con mas de 5 items la tabla sola
no deja ver la forma del resultado, que es lo que se aprueba.
"""
import argparse, json, os, sys
from collections import defaultdict

def peso(d):
    t = 0
    for r, ds, fs in os.walk(d):
        ds[:] = [x for x in ds if x not in {".git", "__pycache__", "node_modules"}]
        for f in fs:
            p = os.path.join(r, f)
            if os.path.isfile(p) and not os.path.islink(p):
                try: t += os.path.getsize(p)
                except OSError: pass
    return t

def cuenta(d):
    n = 0
    for r, ds, fs in os.walk(d):
        ds[:] = [x for x in ds if x not in {".git", "__pycache__", "node_modules"}]
        n += len([f for f in fs if f != ".DS_Store"])
    return n

def mb(b): return b / 1024 / 1024

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target"); ap.add_argument("--plan", required=True)
    ap.add_argument("--niveles", type=int, default=2)
    a = ap.parse_args()
    T = os.path.abspath(a.target)
    plan = json.load(open(a.plan, encoding="utf-8"))

    # delta por carpeta de primer nivel
    quitado = defaultdict(lambda: [0, 0])     # carpeta -> [archivos, bytes]
    llegado = defaultdict(lambda: [0, 0])
    editado = defaultdict(int)
    for it in plan:
        p = os.path.abspath(it["path"])
        rel = os.path.relpath(p, T)
        top = rel.split(os.sep)[0]
        if it["accion"] == "reubicar":
            try: b = os.path.getsize(p)
            except OSError: b = 0
            dtop = os.path.relpath(os.path.abspath(it["destino"]), T).split(os.sep)[0]
            quitado[top][0] += 1; quitado[top][1] += b
            llegado[dtop][0] += 1; llegado[dtop][1] += b
        elif it["accion"] == "mover":
            try: b = os.path.getsize(p)
            except OSError: b = 0
            quitado[top][0] += 1; quitado[top][1] += b
        else:
            editado[top] += 1

    if os.path.isfile(T):
        print(f"### {os.path.basename(T)} — archivo único\n")
        print(f"Se edita en el lugar. La versión previa completa va a la cuarentena, "
              f"al lado del archivo.")
        return
    tops = sorted(set([d for d in os.listdir(T) if os.path.isdir(os.path.join(T, d))
                   and not d.startswith("_declutter-")] + list(llegado.keys())))
    sueltos = [f for f in os.listdir(T) if os.path.isfile(os.path.join(T, f)) and f != ".DS_Store"]

    filas, tb, tq, tn, tnq = [], 0, 0, 0, 0
    for d in tops:
        full = os.path.join(T, d)
        b, n = peso(full), cuenta(full)
        qn, qb = quitado[d]; ln, lb = llegado[d]
        nb, nn = b - qb + lb, n - qn + ln
        tb += b; tq += nb; tn += n; tnq += nn
        if ln and not qn:     cambio = f"**+{ln} archivos · +{mb(lb):.0f} MB** (llegan de otra carpeta)"
        elif qn and ln:       cambio = f"**-{qn} / +{ln} archivos**"
        elif qn and editado[d]: cambio = f"**-{qn} archivos · -{mb(qb):.0f} MB** · {editado[d]} editados"
        elif qn:              cambio = f"**-{qn} archivos · -{mb(qb):.0f} MB**"
        elif editado[d]:      cambio = f"{editado[d]} editado{'s' if editado[d]>1 else ''}"
        else:                 cambio = "sin cambios"
        filas.append((f"`{d}/`", f"{n} arch · {mb(b):.0f} MB", f"{nn} arch · {mb(nb):.0f} MB", cambio))
    if sueltos:
        filas.append(("(sueltos en la raíz)", f"{len(sueltos)} arch", f"{len(sueltos)} arch", "sin cambios"))
    qn_tot = sum(v[0] for v in quitado.values()); qb_tot = sum(v[1] for v in quitado.values())
    if qn_tot:
        filas.append((f"`_declutter-<fecha>/`", "—", f"{qn_tot} arch · {mb(qb_tot):.0f} MB",
                      "**nuevo** · reversible"))

    print(f"### {os.path.basename(T)}/ — ahora → queda\n")
    print("| Carpeta | Ahora | Queda | Cambio |")
    print("|---|---|---|---|")
    for f in filas:
        print(f"| {f[0]} | {f[1]} | {f[2]} | {f[3]} |")
    print(f"| **Total** | **{tn} arch · {mb(tb):.0f} MB** | **{tnq} arch · {mb(tq):.0f} MB** | "
          f"**-{tn-tnq} archivos** |")
    ed = sum(editado.values())
    if ed:
        print(f"\n{ed} archivos se editan en el lugar; la versión previa completa va a la "
              f"cuarentena. La cuarentena ocupa {mb(qb_tot):.0f} MB hasta que la borres.")


if __name__ == "__main__":
    main()

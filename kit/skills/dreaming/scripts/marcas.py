#!/usr/bin/env python3
"""Lista las marcas abiertas que dejó el dreaming. Solo lee.

Dos lugares:
  - Sección `## 🚩 Marcas para revisar` del estado vivo (STATUS.md) de cada proyecto
    (líneas `- [ ] AAAA-MM-DD · etiqueta · qué pasa · fuente: ...`).
  - Ítems del inbox cuyo `resumen:` empieza con "🚩 dreaming" y siguen `estado: pendiente`.

Uso:
  python3 marcas.py                  # todas, texto
  python3 marcas.py --json           # todas, JSON
  python3 marcas.py --dias 7         # solo las de 7 días o más
  python3 marcas.py --proyecto "1. Proyectos/Mi app"
"""
import argparse
import datetime
import json
import os
import re
import sys

from _comun import cargar_config, contiene_alguno

HEADER = "## 🚩 Marcas para revisar"
LINEA = re.compile(r"^- \[ \] (\d{4}-\d{2}-\d{2}) · (.+)$")
SIEMPRE_EXCLUIDAS = ("/backups/", "/node_modules/", "/.git/")


def marcas_estado(cfg):
    raiz = cfg["brain_root"]
    archivo_estado = cfg.get("archivo_estado", "STATUS.md")
    excluir = tuple(cfg.get("excluir_paths", [])) + (cfg["carpetas"]["archivo"],) + SIEMPRE_EXCLUIDAS
    out = []
    for dir_actual, dirs, files in os.walk(raiz):
        # Se compara contra el path relativo al brain, normalizado (NFC + minúsculas).
        rel_dir = "/" + os.path.relpath(dir_actual, raiz).replace(os.sep, "/") + "/"
        if contiene_alguno(rel_dir, excluir):
            dirs[:] = []
            continue
        if archivo_estado not in files:
            continue
        path = os.path.join(dir_actual, archivo_estado)
        dentro = False
        with open(path, encoding="utf-8") as f:
            for linea in f:
                if linea.startswith("## "):
                    dentro = linea.strip() == HEADER
                    continue
                m = LINEA.match(linea.strip()) if dentro else None
                if m:
                    out.append({"donde": os.path.relpath(path, raiz), "fecha": m.group(1),
                                "texto": m.group(2), "tipo": "estado"})
    return out


def marcas_inbox(cfg):
    out = []
    nombre = cfg["carpetas"]["inbox"]
    inbox = os.path.join(cfg["brain_root"], nombre)
    if not os.path.isdir(inbox):
        return out
    for f in sorted(os.listdir(inbox)):
        if not f.endswith(".md"):
            continue
        with open(os.path.join(inbox, f), encoding="utf-8") as fh:
            head = fh.read(1500)
        if "🚩 dreaming" not in head or "estado: pendiente" not in head:
            continue
        fecha = re.search(r"creado:\s*(\d{4}-\d{2}-\d{2})", head)
        resumen = re.search(r'resumen:\s*"?(.+?)"?\s*$', head, re.M)
        out.append({"donde": f"{nombre}/{f}", "fecha": fecha.group(1) if fecha else f[:10],
                    "texto": resumen.group(1) if resumen else f, "tipo": "inbox"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dias", type=int, default=0)
    ap.add_argument("--proyecto", default="")
    a = ap.parse_args()
    cfg = cargar_config()
    hoy = datetime.date.today()
    todas = marcas_estado(cfg) + marcas_inbox(cfg)
    for m in todas:
        try:
            m["dias"] = (hoy - datetime.date.fromisoformat(m["fecha"])).days
        except ValueError:
            m["dias"] = 0
    todas = [m for m in todas if m["dias"] >= a.dias and m["donde"].startswith(a.proyecto)]
    todas.sort(key=lambda m: m["fecha"])
    if a.json:
        json.dump(todas, sys.stdout, ensure_ascii=False, indent=1)
        return
    if not todas:
        print("Sin marcas abiertas.")
    for m in todas:
        print(f"{m['fecha']} ({m['dias']}d) · {m['donde']} · {m['texto']}")


if __name__ == "__main__":
    main()

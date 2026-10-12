#!/usr/bin/env python3
"""Gate de veracidad de last_run.json (el último paso de cada corrida).

Falla (exit 1) si falta un paso obligatorio o si un paso con ok:true no trae `evidencia`
(cantidad leída, path o query). `ok:false` con `detalle` es válido: "no corrí este paso" es
un resultado permitido. Mentir con ok:true no.

Formato esperado de last_run.json:
  {"fecha": "AAAA-MM-DD",
   "pasos": [{"nombre": "sesiones", "ok": true, "evidencia": "4 proyectos, 2 subagentes"},
             {"nombre": "mails", "ok": false, "detalle": "el conector de mail no respondió"}]}

Los pasos obligatorios salen de `pasos_obligatorios` en la config.

Uso: python3 verificar-corrida.py [path/a/last_run.json]   (default: state_dir/last_run.json)
"""
import datetime
import json
import pathlib
import sys

from _comun import cargar_config

cfg = cargar_config()
OBLIGATORIOS = cfg.get("pasos_obligatorios", [])
p = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(cfg["state_dir"]) / "last_run.json"
if not p.is_file():
    print(f"GATE FALLA: no existe {p}")
    sys.exit(1)
d = json.loads(p.read_text(encoding="utf-8"))

errores = []
if d.get("fecha") != str(datetime.date.today()):
    errores.append(f"fecha {d.get('fecha')} no es de hoy")
pasos = {x.get("nombre"): x for x in d.get("pasos", [])}
for n in OBLIGATORIOS:
    x = pasos.get(n)
    if x is None:
        errores.append(f"falta el paso '{n}'")
    elif x.get("ok") is True and not str(x.get("evidencia", "")).strip():
        errores.append(f"paso '{n}' con ok:true sin evidencia")
    elif x.get("ok") is False and not str(x.get("detalle", "")).strip():
        errores.append(f"paso '{n}' con ok:false sin detalle")
    elif x.get("ok") not in (True, False):
        errores.append(f"paso '{n}' sin campo ok (true o false)")

if errores:
    print("GATE FALLA:\n- " + "\n- ".join(errores))
    sys.exit(1)
print("GATE OK:", len(OBLIGATORIOS), "pasos con evidencia")

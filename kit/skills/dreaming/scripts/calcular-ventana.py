#!/usr/bin/env python3
"""Calcula la ventana de la corrida: cuántas horas hacia atrás tiene que leer.

Regla: arranca en `ventana.horas`. Si la corrida anterior (`last_run.json`, campo `fecha`) fue
hace más tiempo que eso, se estira para cubrir el hueco, con tope en
`ventana.techo_horas_si_hubo_hueco`. Un hueco mayor al tope no se recupera.

Imprime una sola línea: `<horas> <dias>` (días = horas redondeadas hacia arriba, para la
query de mail con `newer_than:<dias>d`).

Uso:
  set -- $(python3 calcular-ventana.py); HORAS=$1; DIAS=$2
"""
import json
import math
import os
from datetime import datetime

from _comun import TZ_LOCAL, cargar_config

cfg = cargar_config()
v = cfg.get("ventana", {})
base = float(v.get("horas", 24))
techo = float(v.get("techo_horas_si_hubo_hueco", 72))
horas = base

ruta = os.path.join(cfg["state_dir"], "last_run.json")
if os.path.isfile(ruta):
    try:
        with open(ruta, encoding="utf-8") as f:
            fecha = json.load(f).get("fecha")
        ultima = datetime.strptime(fecha, "%Y-%m-%d").replace(tzinfo=TZ_LOCAL)
        desde_ultima = (datetime.now(TZ_LOCAL) - ultima).total_seconds() / 3600
        horas = max(base, desde_ultima)
    except (ValueError, TypeError, OSError, json.JSONDecodeError):
        horas = base          # last_run.json ilegible: se usa la ventana base

horas = min(horas, max(techo, base))
horas = math.ceil(horas)
print(horas, math.ceil(horas / 24))

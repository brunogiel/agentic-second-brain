#!/usr/bin/env python3
"""Gate de veracidad de la corrida (el último paso de cada corrida).

Dos chequeos:

1. `last_run.json`: falla (exit 1) si falta un paso obligatorio o si un paso con ok:true no
   trae `evidencia` (cantidad leída, path o query). `ok:false` con `detalle` es válido:
   "no corrí este paso" es un resultado permitido. Mentir con ok:true no.

2. `pending-dream.json` (en state_dir, si existe): falla si algún ítem con `default` "Va"
   tiene una `accion` o `etiqueta` que contenga (substring, minúsculas) alguna entrada de
   `botonera.nunca_default_va` (por ejemplo "mandar" o "invitar": un evento con invitados
   es mandar algo en tu nombre). Es el cumplimiento por código de esa lista: el modelo no
   decide si un ítem peligroso puede correr solo.

Formato esperado de last_run.json:
  {"fecha": "AAAA-MM-DD",
   "pasos": [{"nombre": "sesiones", "ok": true, "evidencia": "4 proyectos, 2 subagentes"},
             {"nombre": "mails", "ok": false, "detalle": "el conector de mail no respondió"}]}

Formato esperado de pending-dream.json (también se acepta una lista pelada de ítems):
  {"creado": "AAAA-MM-DD", "status": "abierto",
   "items": [{"n": 1, "etiqueta": "mail", "proyecto": "1. Proyectos/Mi app",
              "accion": "archivar el mail de X ya capturado", "default": "Va",
              "creado": "AAAA-MM-DD", "marca": "1. Proyectos/Mi app/STATUS.md",
              "respuesta": null, "ejecutado": null}]}

Los pasos obligatorios salen de `pasos_obligatorios` en la config.

Uso: python3 verificar-corrida.py [path/a/last_run.json]   (default: state_dir/last_run.json)
     python3 verificar-corrida.py --solo-botonera   (solo el chequeo 2; lo usa el paso 0)
"""
import datetime
import json
import pathlib
import sys

from _comun import cargar_config, contiene_alguno, norm

cfg = cargar_config()
OBLIGATORIOS = cfg.get("pasos_obligatorios", [])
PROHIBIDOS = cfg.get("botonera", {}).get("nunca_default_va", [])
state = pathlib.Path(cfg["state_dir"])
SOLO_BOTONERA = "--solo-botonera" in sys.argv[1:]
args = [a for a in sys.argv[1:] if not a.startswith("--")]
p = pathlib.Path(args[0]) if args else state / "last_run.json"
errores = []
d = {}
if not SOLO_BOTONERA:
    if not p.is_file():
        print(f"GATE FALLA: no existe {p}")
        sys.exit(1)
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"GATE FALLA: {p} no es JSON válido ({e})")
        sys.exit(1)
    if d.get("fecha") != str(datetime.date.today()):
        errores.append(f"fecha {d.get('fecha')} no es de hoy")
pasos = {x.get("nombre"): x for x in d.get("pasos", [])}
for n in ([] if SOLO_BOTONERA else OBLIGATORIOS):
    x = pasos.get(n)
    if x is None:
        errores.append(f"falta el paso '{n}'")
    elif x.get("ok") is True and not str(x.get("evidencia", "")).strip():
        errores.append(f"paso '{n}' con ok:true sin evidencia")
    elif x.get("ok") is False and not str(x.get("detalle", "")).strip():
        errores.append(f"paso '{n}' con ok:false sin detalle")
    elif x.get("ok") not in (True, False):
        errores.append(f"paso '{n}' sin campo ok (true o false)")

# Botonera: ningún ítem con default "Va" puede tocar algo de nunca_default_va.
pend = state / "pending-dream.json"
n_items = 0
if pend.is_file():
    try:
        pd = json.loads(pend.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        pd = None
        errores.append(f"pending-dream.json no es JSON válido ({e})")
    if pd is not None:
        items = pd.get("items", []) if isinstance(pd, dict) else pd
        for it in items if isinstance(items, list) else []:
            n_items += 1
            if norm(str(it.get("default", ""))).strip() != "va":
                continue
            texto = f"{it.get('accion', '')} {it.get('etiqueta', '')}"
            for palabra in PROHIBIDOS:
                if contiene_alguno(texto, [palabra]):
                    errores.append(f"botonera ítem {it.get('n', '?')}: default Va con "
                                   f"'{palabra}' en su acción o etiqueta (nunca_default_va)")

if errores:
    print("GATE FALLA:\n- " + "\n- ".join(errores))
    sys.exit(1)
print("GATE OK:", len(OBLIGATORIOS), "pasos con evidencia,", n_items, "ítems de botonera revisados")

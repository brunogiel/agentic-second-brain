#!/usr/bin/env python3
"""Helper compartido por los scripts del skill dreaming: carga la config y resuelve paths.

Orden de búsqueda de la config:
  1. la variable de entorno DREAMING_CONFIG
  2. ~/.config/dreaming/config.json
  3. config.json junto al SKILL.md (una carpeta arriba de scripts/)
Si no hay ninguna, el script corta con un mensaje claro: copiá config.example.json.
"""
import json
import os
import sys
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(AQUI)

# Hora local de la máquina. Los timestamps sin zona se asumen locales.
TZ_LOCAL = datetime.now().astimezone().tzinfo


def _candidatos():
    env = os.environ.get("DREAMING_CONFIG")
    if env:
        yield os.path.expanduser(env)
    yield os.path.expanduser("~/.config/dreaming/config.json")
    yield os.path.join(SKILL_DIR, "config.json")


def cargar_config():
    for ruta in _candidatos():
        if os.path.isfile(ruta):
            with open(ruta, encoding="utf-8") as f:
                cfg = json.load(f)
            for clave in ("brain_root", "transcripts_root", "code_root", "state_dir"):
                if clave in cfg:
                    cfg[clave] = os.path.expanduser(cfg[clave])
            cfg["_ruta_config"] = ruta
            return cfg
    sys.exit("No encontré la config de dreaming. Copiá config.example.json a "
             "~/.config/dreaming/config.json y ajustala (o definí DREAMING_CONFIG).")


def ruta_estado(cfg, nombre):
    """Path dentro de state_dir. Crea la carpeta si no existe."""
    os.makedirs(cfg["state_dir"], exist_ok=True)
    return os.path.join(cfg["state_dir"], nombre)

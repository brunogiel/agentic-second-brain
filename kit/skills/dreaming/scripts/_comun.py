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
import unicodedata
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


# Claves sin las cuales los scripts no pueden trabajar. Si falta una, se corta con un mensaje
# claro. `excluir_paths` es obligatoria a propósito: sin perímetro de privacidad no se corre.
REQUERIDAS = ("brain_root", "transcripts_root", "code_root", "state_dir", "carpetas",
              "excluir_paths", "paths_no_durables", "topes")


def cargar_config():
    for ruta in _candidatos():
        if os.path.isfile(ruta):
            with open(ruta, encoding="utf-8") as f:
                cfg = json.load(f)
            faltan = [c for c in REQUERIDAS if c not in cfg]
            if faltan:
                sys.exit(f"A la config {ruta} le faltan claves obligatorias: {', '.join(faltan)}. "
                         "Mirá config.example.json.")
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


def norm(texto):
    """Normaliza para comparar: Unicode NFC + minúsculas. Se aplica a AMBOS lados."""
    return unicodedata.normalize("NFC", texto or "").lower()


def contiene_alguno(texto, fragmentos):
    """True si `texto` contiene alguno de los `fragmentos` (substring, normalizado)."""
    t = norm(texto)
    return any(norm(f) in t for f in fragmentos if f)


def es_privado(texto, cfg):
    """Perímetro de privacidad: substring de excluir_paths en `texto`, normalizado NFC + lower."""
    return contiene_alguno(texto, cfg.get("excluir_paths", []))


def resolver_salida(cfg, ruta, permitidos=("brain_root", "state_dir")):
    """Resuelve `ruta` con realpath y aborta si no cuelga de alguna raíz permitida.

    Los symlinks y los `..` se resuelven ANTES de comparar, así que no se puede escapar
    del brain ni de state_dir escribiendo por un enlace.
    """
    real = os.path.realpath(os.path.expanduser(ruta))
    for clave in permitidos:
        raiz = os.path.realpath(cfg[clave])
        if real == raiz or real.startswith(raiz + os.sep):
            return real
    sys.exit(f"Salida rechazada: {ruta} no cuelga de {' ni de '.join(permitidos)}.")

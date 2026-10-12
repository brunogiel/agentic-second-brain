#!/usr/bin/env python3
"""Pasa la transcripción de una reunión a un .txt legible por tramos.

Algunos conectores de reuniones (Granola, Fireflies, Otter...) devuelven la transcripción
entera en UNA sola línea de decenas de miles de tokens, y la herramienta Read corta por
líneas: un subagente no la puede leer. Este script lo corre el hilo principal, nunca el
subagente. Pone un salto por cada turno de hablante y por cada oración, y escribe el .txt.

Dónde escribe: primero en `state_dir/reuniones/`. Recién después del gate de contenido
(regla 2 del SKILL.md) se mueve o copia a la carpeta del proyecto. El destino se resuelve con
realpath y tiene que colgar de `brain_root` o de `state_dir`; si no, el script aborta. El
nombre del archivo es un slug: solo `a-z`, `0-9` y `-`, más la extensión `.txt`. Los
nombres de adjuntos de mails y mensajes se sanitizan con la misma regla.

Uso: python3 transcript-a-txt.py <archivo-con-el-resultado-del-conector> <destino.txt>
"""
import os
import re
import sys

from _comun import cargar_config, resolver_salida

SLUG_TXT = re.compile(r"^[a-z0-9][a-z0-9-]*\.txt$")

if len(sys.argv) != 3:
    sys.exit("Uso: transcript-a-txt.py <archivo-de-entrada> <destino.txt>")

src, dst = sys.argv[1], sys.argv[2]
cfg = cargar_config()
if not SLUG_TXT.match(os.path.basename(dst)):
    sys.exit("Nombre de destino rechazado: usá solo a-z, 0-9 y guiones, terminado en .txt "
             "(ejemplo: 2026-10-12-reunion-cliente-transcript.txt).")
dst = resolver_salida(cfg, dst)
os.makedirs(os.path.dirname(dst), exist_ok=True)

with open(src, encoding="utf-8") as f:
    crudo = f.read()
cuerpo = max(crudo.split("\n"), key=len)          # la línea larga es la transcripción
txt = cuerpo.replace("\\n", "\n")
txt = re.sub(r"(?<=[.?!])\s+(?=[A-ZÁÉÍÓÚ¿¡])", "\n", txt)
with open(dst, "w", encoding="utf-8") as f:
    f.write(txt)
lineas = txt.count("\n")
print(f"{len(txt)} caracteres, {lineas} líneas -> {dst}")
if lineas < 20:
    sys.exit("la transcripción no se partió: revisar el formato antes de pasarla al subagente")

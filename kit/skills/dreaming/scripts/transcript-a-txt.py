#!/usr/bin/env python3
"""Pasa la transcripción de una reunión a un .txt legible por tramos.

Algunos conectores de reuniones (Granola, Fireflies, Otter...) devuelven la transcripción
entera en UNA sola línea de decenas de miles de tokens, y la herramienta Read corta por
líneas: un subagente no la puede leer. Este script lo corre el hilo principal, nunca el
subagente. Pone un salto por cada turno de hablante y por cada oración, y lo escribe al
lado de la nota de la reunión. El subagente lee ese .txt por tramos de ~250 líneas.

Uso: python3 transcript-a-txt.py <archivo-con-el-resultado-del-conector> <destino.txt>
"""
import re
import sys

if len(sys.argv) != 3:
    sys.exit("Uso: transcript-a-txt.py <archivo-de-entrada> <destino.txt>")

src, dst = sys.argv[1], sys.argv[2]
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

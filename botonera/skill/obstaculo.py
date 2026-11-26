#!/usr/bin/env python3
"""Publica un obstáculo en Bloqueos: algo que SOLO la persona puede hacer y que frena al agente.

Aparece en la pestaña Bloqueos, bajo «Te esperan a vos», con qué hacer, dónde y qué trabajo frena. Ella toca «Listo»
(o «No puedo», o deja un comentario) y el agente lo recoge después con pendientes.py.

Uso:
  python3 obstaculo.py --titulo "Iniciá sesión en el panel de analítica" --link https://ejemplo.com/panel \\
      --frena "el reporte semanal" [--por-que "pide un login tuyo"] [--retoma "cuando lo hagas, corro el reporte"] \\
      [--de "reportes"] [--seco]
  python3 obstaculo.py --llevado <id>      # ya recogí ese obstáculo resuelto (lo marca para que no vuelva a avisar)

  --titulo    qué hay que hacer, en una línea. Obligatorio.
  --link      https obligatorio si no hay --comando (un http o javascript: se rechaza).
  --comando   lo que la persona copia y pega (en vez de un link, o además).
  --frena     qué trabajo se frena. Sin esto el obstáculo va abajo de los que frenan.
  --por-que   una línea: por qué traba.
  --retoma    qué sigue cuando lo haga: lo lee la sesión que lo recoge. Es una pista, no una orden.
  --de        de qué proyecto o tema viene.
  --seco      imprime lo que mandaría y no llama a la red.

Si ya hay un obstáculo abierto con el mismo título no publica otro (sale 0). Sale 1 y no publica nada si falta el título,
si falta tanto el link https como el comando, o si el servidor lo rechaza. Los obstáculos son del dueño de la botonera:
el secret de bot no puede publicarlos.
"""
import argparse
import json
import re
import sys

import maestro


def validar(a):
    """Devuelve el texto del error, o None si el pedido vale."""
    link = (a.link or "").strip()
    cmd = (a.comando or "").strip()
    if not " ".join(a.titulo.split()):
        return "falta --titulo"
    if link and not re.fullmatch(r"https://\S+", link):
        return "el link tiene que ser https y sin espacios"
    if not link and not cmd:
        return "falta el dónde: pasá --link https://… o --comando '…'"
    return None


def cuerpo(a):
    una = lambda t: " ".join(str(t or "").split())
    return {"p_titulo": una(a.titulo), "p_por_que": una(a.por_que), "p_de": una(a.de), "p_frena": una(a.frena),
            "p_link": (a.link or "").strip(), "p_comando": (a.comando or "").strip(), "p_retoma": una(a.retoma)}


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Publica un obstáculo en Bloqueos")
    ap.add_argument("--titulo", default="")
    ap.add_argument("--link", default="")
    ap.add_argument("--comando", default="")
    ap.add_argument("--frena", default="")
    ap.add_argument("--por-que", dest="por_que", default="")
    ap.add_argument("--retoma", default="")
    ap.add_argument("--de", default="")
    ap.add_argument("--seco", action="store_true")
    ap.add_argument("--llevado", type=int, metavar="ID")
    a = ap.parse_args(argv)

    if a.llevado is not None:
        cfg = maestro.config()
        if not cfg:
            print("maestro: sin config (~/.config/botonera/env)", file=sys.stderr)
            return 1
        try:
            res = maestro.rpc("bm_obstaculo_llevado", {"p_secret": cfg["BM_SECRET"], "p_id": a.llevado})
        except maestro.ErrorMaestro as ex:
            print(f"obstaculo: falló ({ex})", file=sys.stderr)
            return 1
        print(f"obstaculo: #{a.llevado} " + ("recogido" if isinstance(res, dict) and res.get("llevado") else "ya estaba recogido o no existe"))
        return 0

    error = validar(a)
    if error:
        print(f"obstaculo: {error}", file=sys.stderr)
        return 1
    body = cuerpo(a)
    if a.seco:
        print("obstaculo (seco): bm_obstaculo_publicar " + json.dumps(body, ensure_ascii=False))
        return 0
    cfg = maestro.config()
    if not cfg:
        print("maestro: sin config (~/.config/botonera/env), no publicado", file=sys.stderr)
        return 1
    try:
        res = maestro.rpc("bm_obstaculo_publicar", {"p_secret": cfg["BM_SECRET"], **body})
    except maestro.ErrorMaestro as ex:
        print(f"obstaculo: el servidor lo rechazó o la red falló ({ex})", file=sys.stderr)
        return 1
    if not isinstance(res, dict) or "id" not in res:
        print(f"obstaculo: respuesta inesperada del servidor ({res!r}), no sé si se publicó", file=sys.stderr)
        return 1
    if res.get("nuevo"):
        print(f"obstaculo: publicado · #{res['id']} · {body['p_titulo']}")
    else:
        print(f"obstaculo: ya había uno abierto con ese título · #{res['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

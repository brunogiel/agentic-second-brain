#!/usr/bin/env python3
"""Vuelo: cada sesión anota qué hace y su próximo paso; la pestaña Sesiones lo muestra en el grupo «En vuelo».

Uso:
  python3 vuelo.py anotar "<qué hace>" "<próximo paso>" [--titulo T] [--estado trabajando|esperando] [--seco]
  python3 vuelo.py cerrar [--seco]

`anotar` hace upsert de la fila de esta sesión (`bm_vuelo_anotar`): al arrancar y cada vez que cambia el rumbo. Una sesión que
queda esperando una respuesta del usuario usa `--estado esperando`. `cerrar` la saca de En vuelo (`bm_vuelo_cerrar`): al terminar.
Una fila que nadie toca en 48 h deja de mostrarse sola.

El session_id sale como en armar.py: CLAUDE_CODE_HOST_SESSION_ID o, si no, BM_SESSION_ID. Sin session_id avisa por stderr y sale 0
sin escribir nada (una sesión sin id no tiene fila que anotar). Lo mismo sin config de la botonera. El título por defecto sale de la
carpeta y el branch de git donde corre; `--titulo` lo pisa. Cada campo se recorta a 140 caracteres con «…».
`--seco` imprime lo que mandaría (sin el secret) y no llama a la red.

Sale 0 siempre que no sea un error de uso: anotar el vuelo nunca tiene que trabar el laburo de la sesión.
"""
import argparse
import json
import os
import subprocess
import sys

import maestro

MAX = 140
ESTADOS = ("trabajando", "esperando")


def id_sesion():
    """Igual que armar.id_sesion: el de la sesión de Claude Code o, si no hay, BM_SESSION_ID. Sin ninguno, None.
    (No se importa armar.py: es un script grande que no tiene que cargarse para anotar una línea.)"""
    return (os.environ.get("CLAUDE_CODE_HOST_SESSION_ID") or os.environ.get("BM_SESSION_ID") or "").strip() or None


def recortar(texto, tope=MAX):
    """Una sola línea, sin espacios de más; si pasa el tope, corta y cierra con «…» (el total queda en `tope`)."""
    t = " ".join(str(texto if texto is not None else "").split())
    return t if len(t) <= tope else t[:tope - 1].rstrip() + "…"


def titulo_por_defecto(cwd=None):
    """«carpeta · branch» del lugar donde corre (el branch se omite en main/master/HEAD o fuera de git)."""
    cwd = cwd or os.getcwd()
    carpeta = os.path.basename(os.path.normpath(cwd)) or cwd
    try:
        rama = subprocess.run(["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True,
                              timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        rama = ""
    if rama and rama not in ("main", "master", "HEAD") and rama.split("/")[-1] != carpeta:
        return f"{carpeta} · {rama}"
    return carpeta


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="vuelo.py", description="Anota o cierra la fila «En vuelo» de esta sesión.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("anotar", help="qué hace y próximo paso")
    a.add_argument("que_hace")
    a.add_argument("proximo")
    a.add_argument("--titulo")
    a.add_argument("--estado", choices=ESTADOS, default="trabajando")
    a.add_argument("--seco", action="store_true")
    c = sub.add_parser("cerrar", help="saca esta sesión de En vuelo")
    c.add_argument("--seco", action="store_true")
    args = ap.parse_args(argv)

    sid = id_sesion()
    if not sid:
        print("vuelo: sin session_id (ni CLAUDE_CODE_HOST_SESSION_ID ni BM_SESSION_ID): no anoté nada", file=sys.stderr)
        return 0

    if args.cmd == "anotar":
        nombre = "bm_vuelo_anotar"
        body = {"p_session_id": sid,
                "p_titulo": recortar(args.titulo or titulo_por_defecto()),
                "p_que_hace": recortar(args.que_hace),
                "p_proximo": recortar(args.proximo),
                "p_estado": args.estado}
    else:
        nombre = "bm_vuelo_cerrar"
        body = {"p_session_id": sid}

    if args.seco:
        print(f"vuelo (seco): {nombre} " + json.dumps(body, ensure_ascii=False))
        return 0
    cfg = maestro.config()
    if not cfg:
        print("vuelo: sin config (~/.config/botonera/env): no anoté nada", file=sys.stderr)
        return 0
    try:
        maestro.rpc(nombre, {"p_secret": cfg["BM_SECRET"], **body})
    except maestro.ErrorMaestro as ex:
        print(f"vuelo: no llegó a la base ({ex})", file=sys.stderr)
        return 0
    print(f"vuelo: {'anotado' if args.cmd == 'anotar' else 'cerrado'} · {sid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

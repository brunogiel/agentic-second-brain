#!/usr/bin/env python3
"""Hook de Claude Code: entrega a la sesión las respuestas de la botonera que quedaron sin aplicar.

Corre como hook SessionStart y UserPromptSubmit. Red de seguridad de esperar.py: si el proceso que
esperaba la respuesta murió (se cerró la app, se reinició la sesión), la respuesta sigue en Supabase.
Este hook la busca por session_id y la inyecta como additionalContext.

Uso:
  python3 entregar.py                      # como hook: JSON por stdout solo si hay algo para entregar
  python3 entregar.py --probar <session_id> # texto legible, sin tocar el estado local

La sesión propia sale de CLAUDE_CODE_HOST_SESSION_ID (formato local_<uuid>), el mismo valor que
armar.py guardó como session_id de cada botonera. El session_id del stdin del hook es otro espacio de ids.
Estado local: ~/.cache/botonera/entregadas.json ({clave: epoch de la última entrega}). Una clave
se vuelve a entregar recién pasadas 2 horas.
Solo va a la red si la sesión tiene la marca ~/.cache/botonera/sesiones/<session_id>, que
armar.py deja al publicar: así el resto de las sesiones no suma ~2,5 s a cada mensaje.
Cualquier error (sin config, red, HTTP, JSON, disco) sale 0 sin stdout: un hook nunca bloquea la sesión.
Presupuesto total ~5 s, repartido entre todas las llamadas.
"""
import json
import os
import sys
import time
from pathlib import Path

import maestro

ESPERA_REENTREGA = 2 * 3600  # segundos antes de repetir una clave ya entregada
OLVIDAR_TRAS = 7 * 24 * 3600  # claves más viejas que esto se sacan del estado
PRESUPUESTO = 5.0  # segundos para toda la corrida
TIMEOUT_LLAMADA = 4
ENCABEZADO = (
    "Botonera: llegaron respuestas que esta sesión todavía no aplicó (esperar.py no las entregó). "
    "Aplicalas según el SKILL.md de la botonera (§Cuando vuelve la respuesta) y cerrá cada una "
    "con marcar.py <clave> aplicada."
)


def ruta_estado():
    return Path(os.path.expanduser("~/.cache/botonera/entregadas.json"))


def leer_estado():
    try:
        datos = json.loads(ruta_estado().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(datos, dict):
        return {}
    return {k: v for k, v in datos.items() if isinstance(v, (int, float))}


def guardar_estado(estado):
    ruta = ruta_estado()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_name(f"{ruta.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, ruta)


def llamar(nombre, body, limite):
    """rpc con timeout = lo que quede del presupuesto (tope TIMEOUT_LLAMADA); None si ya no queda."""
    resto = limite - time.time()
    if resto < 0.3:
        return None
    maestro.TIMEOUT = min(TIMEOUT_LLAMADA, resto)
    return maestro.rpc(nombre, body)


def respuestas(session_id, claves_ok, limite):
    """[(clave, respuesta_texto)] de las botoneras de esta sesión; claves_ok filtra cuáles entregar."""
    cfg = maestro.config()
    if not cfg:
        return []
    res = llamar("bm_pendientes", {"p_secret": cfg["BM_SECRET"], "p_horas": 0}, limite)
    filas = [res] if isinstance(res, dict) else (res or [])
    claves = []
    for f in filas:
        clave = f.get("clave") if isinstance(f, dict) else None
        if clave and f.get("session_id") == session_id and claves_ok(clave) and clave not in claves:
            claves.append(clave)
    salida = []
    for clave in claves:
        r = llamar("bm_recibir", {"p_secret": cfg["BM_SECRET"], "p_clave": clave}, limite)
        if r is None:  # se acabó el presupuesto
            break
        texto = r.get("respuesta_texto") if isinstance(r, dict) else None
        if texto is not None:
            salida.append((clave, texto))
    return salida


def main():
    args = sys.argv[1:]
    probar = None
    if "--probar" in args:
        i = args.index("--probar")
        try:
            probar = args[i + 1]
        except IndexError:
            sys.exit("uso: python3 entregar.py [--probar <session_id>]")
    limite = time.time() + PRESUPUESTO

    evento = "UserPromptSubmit"
    if not sys.stdin.isatty():
        try:
            datos = json.loads(sys.stdin.read() or "{}")
            if isinstance(datos, dict) and datos.get("hook_event_name"):
                evento = str(datos["hook_event_name"])
        except (OSError, ValueError):
            pass

    session_id = probar or os.environ.get("CLAUDE_CODE_HOST_SESSION_ID")
    if not session_id:
        return
    # armar.py deja esta marca al publicar: una sesión que nunca publicó no paga la llamada a la red.
    if not probar and not (Path(os.path.expanduser("~/.cache/botonera/sesiones")) / session_id).exists():
        return

    ahora = time.time()
    if probar:
        estado = {}
    else:
        estado = leer_estado()
    encontradas = respuestas(
        session_id,
        lambda c: bool(probar) or ahora - estado.get(c, 0) > ESPERA_REENTREGA,
        limite,
    )
    if not encontradas:
        if probar:
            print(f"entregar: nada para entregar a {session_id}")
        return

    texto = ENCABEZADO + "\n\n" + "\n\n".join(t for _, t in encontradas)
    if probar:
        print(texto)
        return

    estado = {k: v for k, v in estado.items() if ahora - v < OLVIDAR_TRAS}
    for clave, _ in encontradas:
        estado[clave] = ahora
    guardar_estado(estado)  # antes de imprimir: si el disco falla, mejor callar que repetir en cada mensaje
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": evento, "additionalContext": texto}}))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as ex:  # el hook nunca bloquea la sesión
        print(f"entregar: {type(ex).__name__}: {ex}", file=sys.stderr)
    sys.exit(0)

#!/usr/bin/env python3
"""Marca el estado de una botonera de la botonera una vez que Claude actuó sobre ella.

Uso:
  python3 marcar.py <clave> aplicada|respondida_en_chat ["resumen"]
  python3 marcar.py <clave> esperando "qué necesitás del usuario"
  python3 marcar.py <clave> trabajando
  python3 marcar.py <clave> archivada "por qué se cierra"
  echo "resumen" | python3 marcar.py <clave> aplicada -

El resumen es una línea por ítem, separadas por \\n (o por stdin con `-`). Es opcional.
`esperando`: terminaste el turno y la pelota la tiene el usuario en la conversación (el texto es el motivo,
lo ve en la web). `trabajando`: el usuario contestó y volvés a trabajar (vuelve a recibida).
`archivada`: una limpieza cierra una tanda colgada (su sesión ya no está); sale de la web.
"""
import sys

import maestro

ESTADOS = ("aplicada", "respondida_en_chat", "esperando", "trabajando", "archivada")


def reintento(estado, anterior):
    """Si respondida_en_chat no valía porque la tanda ya estaba recibida/esperando, el reintento es aplicada.
    Devuelve el estado a reintentar, o None si no corresponde."""
    if estado == "respondida_en_chat" and anterior in ("recibida", "esperando"):
        return "aplicada"
    return None


def main():
    args = sys.argv[1:]
    if len(args) not in (2, 3) or args[1] not in ESTADOS:
        sys.exit("uso: python3 marcar.py <clave> aplicada|respondida_en_chat|esperando|trabajando|archivada [resumen | -]")
    clave, estado = args[0], args[1]
    resumen = None
    if len(args) == 3:
        resumen = sys.stdin.read() if args[2] == "-" else args[2].replace("\\n", "\n")
        resumen = resumen.strip() or None
    cfg = maestro.config()
    if not cfg:
        print("maestro: sin config (~/.config/botonera/env), no marcado")
        sys.exit(1)
    try:
        res = maestro.rpc("bm_marcar", {"p_secret": cfg["BM_SECRET"], "p_clave": clave,
                                        "p_estado": estado, "p_resumen": resumen})
    except maestro.ErrorMaestro as ex:
        print(f"maestro: falló ({ex})", file=sys.stderr)
        sys.exit(1)
    antes = res.get("anterior") if isinstance(res, dict) else res
    if isinstance(res, dict) and res.get("cambiado") is False and reintento(estado, antes):
        nuevo = reintento(estado, antes)
        resumen = "respondida en el chat · " + resumen if resumen else "respondida en el chat"
        try:
            res = maestro.rpc("bm_marcar", {"p_secret": cfg["BM_SECRET"], "p_clave": clave,
                                            "p_estado": nuevo, "p_resumen": resumen})
        except maestro.ErrorMaestro as ex:
            print(f"maestro: falló ({ex})", file=sys.stderr)
            sys.exit(1)
        print(f"maestro: {clave} estaba {antes}, respondida_en_chat no vale ahí: la marqué aplicada con «respondida en el chat · …»")
        estado = nuevo
        antes = res.get("anterior") if isinstance(res, dict) else res
    if isinstance(res, dict) and res.get("cambiado") is False:
        # La transición no valía (ej. aplicada sin haber recibido, o dos veces): el servidor no tocó nada.
        print(f"maestro: {clave} NO se marcó {estado}: estaba {antes}")
        sys.exit(1)
    print(f"maestro: {clave} → {estado} (antes: {antes})")


if __name__ == "__main__":
    main()

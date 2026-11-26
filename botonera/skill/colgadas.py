#!/usr/bin/env python3
"""Lista las botoneras que no llegaron a un estado cerrado (para una limpieza periódica) y las archiva.

Uso:
  python3 colgadas.py
  python3 colgadas.py --archivar <clave> "<por qué>"

Sin argumentos: una botonera está colgada si sigue `abierta`, `decidida`, `recibida` o `esperando`. Imprime una línea por fila:
  clave · estado · sesión · hace cuánto se creó · session_id [· plan aplicar N/M]
En las filas `decidida` o `recibida` suma `plan aplicar N/M`: cuántas cards traen `aplicar` (el plan de cada respuesta,
ver retomar.py). Con plan, una sesión nueva las retoma en vez de archivarlas a ciegas. Sale siempre 0.

`--archivar <clave> "<por qué>"`: archiva la tanda (como `marcar.py … archivada`). Si estaba `decidida` o `recibida`, el usuario
había contestado y nadie aplicó la respuesta: además publica un error de tipo `sesion` en la fila «Con error» de la web
(errores.py), para que no se pierda sin aviso. Una tanda `abierta` o `esperando` se archiva sin error.

Las claves `bot-…` NO se listan: son de bots, no tienen una sesión de Claude Code que pueda «no estar más» y las
cierra quien administra el bot. Si se listaran, la limpieza las archivaría por error (su session_id `bot-<nombre>`
nunca existe en la app). Se dice cuántas se salteó.
"""
import sys

import errores
import maestro
import retomar
from pendientes import hace


def plan_aplicar(cfg, clave):
    """'plan aplicar N/M' de una tanda decidida/recibida, o '' si no se pudo leer (bm_retomar todavía no existe, red…)."""
    try:
        res = maestro.rpc("bm_retomar", {"p_secret": cfg["BM_SECRET"], "p_clave": clave})
    except maestro.ErrorMaestro:
        return ""
    if not isinstance(res, dict) or res.get("estado") == "no_existe":
        return ""
    con, total = retomar.cuantos_con_plan(res)
    return f" · plan aplicar {con}/{total}"


def listar():
    cfg = maestro.config()
    if not cfg:
        print("maestro: sin config (~/.config/botonera/env), no puedo mirar colgadas")
        return
    try:
        res = maestro.rpc("bm_sin_cerrar", {"p_secret": cfg["BM_SECRET"]})
    except maestro.ErrorMaestro as ex:
        print(f"maestro: falló ({ex})")
        return
    filas = [res] if isinstance(res, dict) else (res or [])
    de_bots = [f for f in filas if str(f.get("clave") or "").startswith("bot-")]
    filas = [f for f in filas if f not in de_bots]
    if not filas:
        print("maestro: nada colgado" + (f" ({len(de_bots)} bot- salteadas, son de bots)" if de_bots else ""))
        return
    print(f"maestro: {len(filas)} sin cerrar" + (f" ({len(de_bots)} bot- salteadas, son de bots)" if de_bots else ""))
    for f in filas:
        plan = plan_aplicar(cfg, f["clave"]) if f.get("estado") in ("decidida", "recibida") else ""
        print(f"{f.get('clave')} · {f.get('estado')} · {f.get('sesion_titulo') or '(sin título)'} · "
              f"hace {hace(f.get('created_at'))} · {f.get('session_id') or 'sin session_id'}{plan}")


def archivar(clave, motivo):
    """Archiva la tanda. Si tenía una respuesta del usuario sin aplicar, publica un error `sesion`. Sale 1 si no pudo archivar."""
    cfg = maestro.config()
    if not cfg:
        print("maestro: sin config (~/.config/botonera/env), no archivado")
        sys.exit(1)
    if clave.startswith("bot-"):
        print(f"maestro: {clave} es de un bot, no se archiva desde acá")
        sys.exit(1)
    try:
        res = maestro.rpc("bm_marcar", {"p_secret": cfg["BM_SECRET"], "p_clave": clave,
                                        "p_estado": "archivada", "p_resumen": motivo})
    except maestro.ErrorMaestro as ex:
        print(f"maestro: falló ({ex})", file=sys.stderr)
        sys.exit(1)
    antes = res.get("anterior") if isinstance(res, dict) else res
    if isinstance(res, dict) and res.get("cambiado") is False:
        print(f"maestro: {clave} NO se archivó: estaba {antes}")
        sys.exit(1)
    print(f"maestro: {clave} → archivada (antes: {antes})")
    if antes in ("decidida", "recibida"):
        r = errores.publicar_uno({
            "tipo": "sesion", "origen_id": clave,
            "titulo": f"Tanda archivada con tu respuesta sin aplicar: {clave}",
            "motivo": motivo,
        })
        print(f"errores: {r}" + ("" if not r.startswith("error") else " (la tanda quedó archivada igual)"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if args and args[0] == "--archivar":
        if len(args) != 3:
            sys.exit('uso: python3 colgadas.py --archivar <clave> "<por qué>"')
        archivar(args[1], args[2])
        return
    if args:
        sys.exit('uso: python3 colgadas.py  |  python3 colgadas.py --archivar <clave> "<por qué>"')
    listar()


if __name__ == "__main__":
    main()

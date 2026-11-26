#!/usr/bin/env python3
"""Publica en la fila «Con error» de la web lo que murió sin avisar.

Una tarea programada puede morir (por ejemplo, por el límite de uso) sin que nadie se entere, porque la web solo
muestra tandas abiertas y decididas. Esta fila lo cuenta hasta que el usuario toca «Visto».

Uso:
  python3 errores.py publicar <json | archivo.json> [--seco]
      Un error {tipo, origen_id, titulo, motivo?, ocurrio_at?} o una lista. tipo = 'tarea' | 'sesion'.
      origen_id: el taskId de la tarea, o la clave de la tanda. ocurrio_at (ISO) cae a «ahora» si falta.
  python3 errores.py desde-runs <runs.json> [--horas 24] [--seco]
      <runs.json> = la salida del MCP scheduled-tasks `list_task_runs` ({taskId, runs: [...]}), o una lista
      de esas salidas (una por tarea). Publica un error por cada run con
      status 'failed' que empezó en las últimas N horas (default 24), con el motivo del campo `error`.
      Repetir la lectura no duplica: la base ignora (tipo, origen_id, ocurrio_at) repetidos.
  --seco: imprime lo que publicaría y no escribe nada (ni toca la red).

Publica con el secret normal (`bm_error_publicar`); el secret de bots no puede. Sale 0 aunque la red falle:
un aviso que no se pudo publicar no tiene que tumbar la corrida de la tarea que lo publica; lo dice por stderr.
"""
import datetime
import json
import sys
from pathlib import Path

import maestro

TIPOS = ("tarea", "sesion")


def ahora_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def parsear_iso(texto):
    try:
        return datetime.datetime.fromisoformat(str(texto).replace("Z", "+00:00"))
    except ValueError:
        return None


def errores_de_runs(datos, horas=24, ahora=None):
    """list_task_runs (una salida o una lista) -> [error] de los runs fallidos de las últimas `horas`."""
    ahora = ahora or datetime.datetime.now(datetime.timezone.utc)
    corte = ahora - datetime.timedelta(hours=horas)
    salidas = datos if isinstance(datos, list) else [datos]
    out = []
    for s in salidas:
        if not isinstance(s, dict):
            continue
        tarea = s.get("taskId") or "(tarea sin id)"
        for r in s.get("runs") or []:
            if r.get("status") != "failed":
                continue
            t = parsear_iso(r.get("started_at"))
            if t is None or t < corte:
                continue
            out.append({
                "tipo": "tarea",
                "origen_id": tarea,
                "titulo": (r.get("title") or tarea),
                "motivo": r.get("error") or r.get("summary") or "falló sin motivo registrado",
                "ocurrio_at": t.isoformat(),
            })
    return out


def validar(e):
    if e.get("tipo") not in TIPOS:
        return f"tipo tiene que ser {' | '.join(TIPOS)}"
    for k in ("origen_id", "titulo"):
        if not str(e.get(k) or "").strip():
            return f"falta '{k}'"
    return None


def publicar_uno(e, seco=False):
    """Publica un error. Devuelve 'creado' | 'repetido' | 'seco' | 'error: …'. Nunca levanta."""
    falla = validar(e)
    if falla:
        return f"error: {falla}"
    e = dict(e)
    e.setdefault("ocurrio_at", ahora_iso())
    if seco:
        return "seco"
    cfg = maestro.config()
    if not cfg:
        return "error: sin config (~/.config/botonera/env)"
    try:
        res = maestro.rpc("bm_error_publicar", {
            "p_secret": cfg["BM_SECRET"], "p_tipo": e["tipo"], "p_origen_id": str(e["origen_id"]),
            "p_titulo": str(e["titulo"]), "p_motivo": e.get("motivo"), "p_ocurrio_at": e["ocurrio_at"],
        })
    except maestro.ErrorMaestro as ex:
        return f"error: {ex}"
    return str(res or "").strip().lower() or "error: respuesta vacía"


def publicar_lote(errores, seco=False):
    cuenta = {}
    for e in errores:
        r = publicar_uno(e, seco)
        clave = r.split(":")[0]
        cuenta[clave] = cuenta.get(clave, 0) + 1
        marca = "WOULD publish" if seco else r
        print(f"{marca} · {e.get('tipo')} · {e.get('origen_id')} · {e.get('titulo')} · {e.get('ocurrio_at', 'ahora')} · "
              f"{str(e.get('motivo') or '')[:120]}")
        if r.startswith("error"):
            print(f"errores: no se pudo publicar ({r})", file=sys.stderr)
    print(("seco: " if seco else "errores: ") + (", ".join(f"{v} {k}" for k, v in cuenta.items()) if cuenta else "ningún error para publicar"))


def cargar(arg):
    """Un JSON pegado en la línea de comandos o la ruta de un archivo."""
    p = Path(arg)
    texto = p.read_text(encoding="utf-8") if p.exists() else arg
    return json.loads(texto)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    seco = "--seco" in args
    horas = 24
    if "--horas" in args:
        i = args.index("--horas")
        try:
            horas = max(1, int(args[i + 1]))
        except (IndexError, ValueError):
            sys.exit("uso: python3 errores.py desde-runs <runs.json> [--horas 24] [--seco]")
        del args[i:i + 2]
    args = [a for a in args if a != "--seco"]
    if len(args) != 2 or args[0] not in ("publicar", "desde-runs"):
        sys.exit("uso: python3 errores.py publicar <json|archivo> [--seco]  |  python3 errores.py desde-runs <runs.json> [--horas 24] [--seco]")
    try:
        datos = cargar(args[1])
    except (OSError, ValueError) as ex:
        sys.exit(f"errores: no pude leer {args[1]!r}: {ex}")
    if args[0] == "desde-runs":
        errores = errores_de_runs(datos, horas)
    else:
        errores = datos if isinstance(datos, list) else [datos]
    publicar_lote(errores, seco)


if __name__ == "__main__":
    main()

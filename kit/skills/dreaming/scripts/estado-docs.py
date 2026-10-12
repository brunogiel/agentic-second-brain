#!/usr/bin/env python3
"""
estado-docs.py: mide la deriva de los estados vivos y los logs de decisiones.

Los STATUS.md y los Log de decisiones se actualizan a mano, así que se pudren en silencio:
nadie se entera de que un estado quedó tres semanas atrás hasta que lo abre.

Este script mide esa deriva. Read-only, cero criterio propio: mide y ordena.
Qué hacer con cada caso lo decide el agente, cruzando contra la actividad real del día.

Uso:
    python3 estado-docs.py                  # todos los proyectos
    python3 estado-docs.py --md
    python3 estado-docs.py --umbral-dias 14
    python3 estado-docs.py --solo "1. Proyectos/Mi app"
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timedelta

from _comun import TZ_LOCAL, cargar_config, ruta_estado

RE_FECHA = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")
RE_CHECK_ABIERTO = re.compile(r"^\s*[-*]\s*\[ \]\s*(.+)$", re.MULTILINE)
RE_CHECK_CERRADO = re.compile(r"^\s*[-*]\s*\[[xX]\]\s*(.+)$", re.MULTILINE)


def fecha_mas_reciente(texto, limite_lineas=None):
    """Fecha ISO más nueva mencionada en el texto. Los logs fechan cada entrada."""
    if limite_lineas:
        texto = "\n".join(texto.split("\n")[:limite_lineas])
    mejor = None
    for m in RE_FECHA.finditer(texto):
        try:
            f = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=TZ_LOCAL)
        except ValueError:
            continue
        if f > datetime.now(TZ_LOCAL) + timedelta(days=1):
            continue  # fechas futuras: deadlines, no registros
        if mejor is None or f > mejor:
            mejor = f
    return mejor


def leer(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def seccion_log(texto):
    """Extrae la sección 'Log de decisiones' hasta el próximo encabezado del mismo nivel."""
    m = re.search(r"^##+\s*Log de decisiones.*$", texto, re.MULTILINE | re.IGNORECASE)
    if not m:
        return None
    resto = texto[m.end():]
    fin = re.search(r"^##\s+", resto, re.MULTILINE)
    return resto[:fin.start()] if fin else resto


def auditar_proyecto(dir_proyecto, raiz, archivo_estado, ahora):
    rel = os.path.relpath(dir_proyecto, raiz)
    claude_md = os.path.join(dir_proyecto, "CLAUDE.md")
    status_md = os.path.join(dir_proyecto, archivo_estado)

    info = {
        "proyecto": rel,
        "tiene_claude_md": os.path.isfile(claude_md),
        "tiene_status": os.path.isfile(status_md),
        "log_ultima_fecha": None,
        "log_dias": None,
        "status_ultima_fecha": None,
        "status_dias": None,
        "checks_abiertos": [],
        "checks_cerrados": 0,
        "senales": [],
    }

    if info["tiene_claude_md"]:
        log = seccion_log(leer(claude_md))
        if log is None:
            info["senales"].append("sin sección 'Log de decisiones'")
        else:
            # Los logs van con lo más nuevo arriba: mirar solo el arranque de la sección.
            f = fecha_mas_reciente(log, limite_lineas=60)
            if f:
                info["log_ultima_fecha"] = f.date().isoformat()
                info["log_dias"] = (ahora - f).days

    if info["tiene_status"]:
        texto = leer(status_md)
        f = fecha_mas_reciente(texto, limite_lineas=25)
        if f:
            info["status_ultima_fecha"] = f.date().isoformat()
            info["status_dias"] = (ahora - f).days
        info["checks_abiertos"] = [c.strip()[:140] for c in RE_CHECK_ABIERTO.findall(texto)][:25]
        info["checks_cerrados"] = len(RE_CHECK_CERRADO.findall(texto))

    return info


def main():
    ap = argparse.ArgumentParser(description="Deriva de los estados vivos y logs de decisiones.")
    ap.add_argument("--umbral-dias", type=int, default=21,
                    help="A partir de cuántos días un doc se marca como derivado (default 21).")
    ap.add_argument("--solo", help="Path relativo de un solo proyecto.")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--out", help="Escribe el JSON a este path (relativo a state_dir).")
    args = ap.parse_args()

    cfg = cargar_config()
    raiz = cfg["brain_root"]
    archivo_estado = cfg.get("archivo_estado", "STATUS.md")
    ahora = datetime.now(TZ_LOCAL)

    dirs = []
    if args.solo:
        dirs = [os.path.join(raiz, args.solo)]
    else:
        base = os.path.join(raiz, cfg["carpetas"]["proyectos"])
        if os.path.isdir(base):
            for profundidad in ("*", "*/*", "*/*/*"):
                for cm in glob.glob(os.path.join(base, profundidad, "CLAUDE.md")):
                    dirs.append(os.path.dirname(cm))

    proyectos = [auditar_proyecto(d, raiz, archivo_estado, ahora) for d in sorted(set(dirs))]

    for p in proyectos:
        if p["tiene_claude_md"] and p["log_dias"] is None and "sin sección 'Log de decisiones'" not in p["senales"]:
            p["senales"].append("Log sin fechas parseables")
        if p["log_dias"] is not None and p["log_dias"] >= args.umbral_dias:
            p["senales"].append(f"Log sin entradas hace {p['log_dias']}d")
        if p["tiene_status"] and p["status_dias"] is None:
            p["senales"].append("estado sin fecha de actualización")
        if p["status_dias"] is not None and p["status_dias"] >= args.umbral_dias:
            p["senales"].append(f"estado derivado hace {p['status_dias']}d")

    payload = {
        "generado": ahora.isoformat(timespec="seconds"),
        "umbral_dias": args.umbral_dias,
        "resumen": {
            "proyectos": len(proyectos),
            "con_senales": sum(1 for p in proyectos if p["senales"]),
            "checks_abiertos": sum(len(p["checks_abiertos"]) for p in proyectos),
        },
        "proyectos": sorted(proyectos, key=lambda p: -(p["status_dias"] or p["log_dias"] or 0)),
    }

    if args.out:
        destino = args.out if os.path.isabs(args.out) else ruta_estado(cfg, args.out)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    if args.md:
        print(f"# Estado de los docs, umbral {args.umbral_dias}d")
        print(f"\n{payload['resumen']['con_senales']} de {payload['resumen']['proyectos']} "
              f"proyectos con señales, {payload['resumen']['checks_abiertos']} checks abiertos\n")
        for p in payload["proyectos"]:
            if not p["senales"] and not p["checks_abiertos"]:
                continue
            print(f"## {p['proyecto']}")
            print(f"- Log: {p['log_ultima_fecha'] or '-'} · Estado: {p['status_ultima_fecha'] or '-'}")
            for s in p["senales"]:
                print(f"- señal: {s}")
            for c in p["checks_abiertos"][:8]:
                print(f"- [ ] {c}")
            print()
    else:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        print()


if __name__ == "__main__":
    main()

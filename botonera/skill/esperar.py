#!/usr/bin/env python3
"""Espera la respuesta de una botonera publicada en la botonera.

Uso:
  python3 esperar.py <clave> [--cada 15]
  python3 esperar.py <clave> --una-vez     # una sola consulta y sale (para agentes sin segundo plano)

Si tu agente puede dejar un proceso corriendo en segundo plano, lanzalo así; cuando el proceso termina, el agente
lee lo que imprimió, así que la última salida tiene que bastarse sola. Si no puede, usá --una-vez:
  - respuesta ya está   -> la imprime y sale 0
  - todavía abierta     -> imprime `maestro: <clave> todavía abierta` y sale 3 (no es un error: aún no decidió)
  - el resto de los casos (ya resuelta, no existe, snoozeada) se comporta como abajo.
Salida de la espera normal:
  - recibida            -> imprime EXACTAMENTE la respuesta (ya empieza con
                           `/botonera respuesta · <clave>`) y sale 0
  - respondida_en_chat / aplicada -> aviso de que no queda nada por aplicar, sale 0
  - no_existe           -> aviso, sale 1
  - abierta y snoozeada -> si el usuario la snoozeó (bm_recibir trae `snooze_hasta`) a una hora distinta de la última
                           que avisé para esa clave, imprime
                           `maestro: <clave> snoozeada hasta <dd-mmm HH:MM>` (hora local de esta máquina) y sale 0.
                           La sesión relanza esta misma espera (SKILL.md). Relanzado con el mismo snooze, sigue esperando.
                           Lo avisado se guarda en un archivo por clave (`ruta_snooze`). Si no se puede guardar,
                           avisa por stderr una vez y sigue esperando: sin ese archivo el relanzado volvería a avisar.
  - abierta             -> duerme N segundos y vuelve a preguntar
Un corte de red o un 5xx no matan la espera: reintenta con el mismo intervalo. Un 4xx (salvo 408 y 429)
3 veces seguidas sí: imprime `maestro: esperar.py se rindió: <motivo>` y sale 1. Tope de 8 días
(el snooze más largo que acepta la base).
Si la respuesta es una re-entrega (el esperar anterior murió después de recibirla), avisa antes.
"""
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import maestro

TOPE_SEGUNDOS = 8 * 24 * 3600  # bm_snoozear acepta hasta 8 días; con 7 una botonera snoozeada al máximo se quedaba sin espera
OLVIDAR_SNOOZE_TRAS = 30 * 24 * 3600  # entradas del estado local más viejas que esto se sacan
MESES = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")
MAX_4XX = 3  # 4xx seguidos (salvo 408/429) antes de rendirse: no se arreglan solos


def marcar_entregada(clave):
    """Anota la clave en el estado del hook entregar.py, así no la vuelve a inyectar en el mismo turno.
    Evita que esperar.py y el hook entreguen la misma respuesta a la vez. Un error acá no rompe la espera."""
    try:
        import entregar
        estado = entregar.leer_estado()
        estado[clave] = time.time()
        entregar.guardar_estado(estado)
    except Exception:
        pass


def dir_snooze():
    """Junto a entregadas.json de entregar.py."""
    return Path(os.path.expanduser("~/.cache/botonera/snoozeadas"))


def ruta_snooze(clave):
    """Un archivo por clave, así dos esperar.py de claves distintas no se pisan.
    La clave se sanea para nombre de archivo; si el saneado la cambia, se suma un hash corto para que dos
    claves distintas no caigan en el mismo archivo. (El archivo único anterior, snoozeadas.json, se ignora.)"""
    seguro = re.sub(r"[^A-Za-z0-9_-]", "_", clave)[:80]
    if seguro != clave:
        seguro += "-" + hashlib.sha1(clave.encode("utf-8")).hexdigest()[:8]
    return dir_snooze() / f"{seguro}.json"


def leer_snooze(clave):
    """Último snooze avisado para la clave: {"hasta": <string de bm_recibir>, "at": <epoch>}; None si no hay o está roto."""
    try:
        dato = json.loads(ruta_snooze(clave).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if isinstance(dato, dict) and isinstance(dato.get("hasta"), str) and isinstance(dato.get("at"), (int, float)):
        return dato
    return None


def guardar_snooze(clave, hasta):
    ruta = ruta_snooze(clave)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_name(f"{ruta.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps({"hasta": hasta, "at": time.time()}, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, ruta)
    olvidar_viejos(ruta.parent)


def olvidar_viejos(carpeta):
    """Saca los archivos de claves que no se tocan hace más de OLVIDAR_SNOOZE_TRAS. Un error acá no rompe nada."""
    limite = time.time() - OLVIDAR_SNOOZE_TRAS
    try:
        for f in carpeta.glob("*.json"):
            try:
                if f.stat().st_mtime < limite:
                    f.unlink()
            except OSError:
                pass
    except OSError:
        pass


def parsear_utc(texto):
    """'2026-11-14T11:00:00.000Z' (o con +00:00, o sin milis) -> datetime con zona. Python 3.9 no lee la Z."""
    m = re.match(r"^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:?\d{2})?$", str(texto).strip())
    if not m:
        raise ValueError(f"snooze_hasta ilegible: {texto!r}")
    dia, hora, frac, zona = m.groups()
    frac = ((frac or "0") + "000000")[:6]
    if not zona or zona == "Z":
        zona = "+00:00"
    elif ":" not in zona:
        zona = zona[:3] + ":" + zona[3:]
    return datetime.fromisoformat(f"{dia}T{hora}.{frac}{zona}")


def cuando_local(texto):
    """'14-nov 08:00' en la hora local de esta máquina."""
    d = parsear_utc(texto).astimezone()
    return f"{d.day:02d}-{MESES[d.month - 1]} {d.hour:02d}:{d.minute:02d}"


def snooze_nuevo(clave, hasta, ya_avisadas):
    """True (y lo anota en el estado local) si `hasta` es distinto del último snooze avisado para esa clave.
    Si no puede guardar el estado devuelve False: avisa por stderr una vez por proceso (`ya_avisadas`) y la espera
    sigue. Si devolviera True sin poder guardar, el relanzado no vería nada anotado y volvería a salir, en bucle."""
    if ya_avisadas.get(clave) == hasta:
        return False
    previo = leer_snooze(clave)
    if previo and previo["hasta"] == hasta:
        return False
    try:
        guardar_snooze(clave, hasta)
    except OSError as ex:
        print(f"maestro: no pude guardar el estado del snooze ({ex}); sigo esperando sin avisar", file=sys.stderr, flush=True)
        ya_avisadas[clave] = hasta
        return False
    ya_avisadas[clave] = hasta
    return True


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # la respuesta trae «·» y acentos; sin esto un stdout cp1252/ASCII revienta
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__)
        return
    una_vez = "--una-vez" in args
    args = [a for a in args if a != "--una-vez"]
    cada = 15
    if "--cada" in args:
        i = args.index("--cada")
        try:
            cada = max(1, int(args[i + 1]))
        except (IndexError, ValueError):
            sys.exit("uso: python3 esperar.py <clave> [--cada 15] [--una-vez]")
        del args[i:i + 2]
    if len(args) != 1:
        sys.exit("uso: python3 esperar.py <clave> [--cada 15] [--una-vez]")
    clave = args[0]
    cfg = maestro.config()
    if not cfg:
        print("maestro: sin config (~/.config/botonera/env), no puedo esperar la respuesta")
        sys.exit(1)
    ya_avisadas = {}
    inicio = time.time()
    seguidos_4xx = 0
    while time.time() - inicio < TOPE_SEGUNDOS:
        try:
            res = maestro.rpc("bm_recibir", {"p_secret": cfg["BM_SECRET"], "p_clave": clave})
        except maestro.ErrorMaestro as ex:
            if ex.codigo and 400 <= ex.codigo < 500 and ex.codigo not in (408, 429):
                seguidos_4xx += 1
                if seguidos_4xx >= MAX_4XX:
                    print(f"maestro: esperar.py se rindió: {ex}", flush=True)
                    sys.exit(1)
            else:
                seguidos_4xx = 0
            print(f"maestro: reintento ({ex})", file=sys.stderr, flush=True)
            if una_vez:
                print(f"maestro: no pude consultar {clave} ({ex})", flush=True)
                sys.exit(1)
            time.sleep(cada)
            continue
        seguidos_4xx = 0
        res = res if isinstance(res, dict) else {}
        estado = res.get("estado")
        if estado == "recibida" and res.get("respuesta_texto") is not None:
            if res.get("reentrega"):
                print(f"maestro: REENTREGA de {clave}. Antes de aplicar, chequeá si ya lo aplicaste en esta sesión.", flush=True)
            print(res["respuesta_texto"], flush=True)
            marcar_entregada(clave)
            return
        if estado in ("respondida_en_chat", "aplicada"):
            print(f"maestro: {clave} ya se resolvió ({estado}), nada que aplicar")
            return
        if estado == "no_existe":
            print(f"maestro: {clave} no existe en la botonera")
            sys.exit(1)
        hasta = res.get("snooze_hasta") if estado == "abierta" else None
        if hasta:
            try:
                cuando = cuando_local(hasta)
            except ValueError as ex:
                print(f"maestro: {ex}", file=sys.stderr, flush=True)
            else:
                if snooze_nuevo(clave, hasta, ya_avisadas):
                    print(f"maestro: {clave} snoozeada hasta {cuando}", flush=True)
                    return
        if una_vez:
            print(f"maestro: {clave} todavía abierta", flush=True)
            sys.exit(3)
        time.sleep(cada)  # abierta (o recibida sin texto todavía)
    print(f"maestro: {clave} sin respuesta tras 8 días, dejo de esperar")


if __name__ == "__main__":
    main()

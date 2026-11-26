#!/usr/bin/env python3
"""PIN de la botonera: ponerlo, desbloquearla y ver cómo está.

Uso:
  python3 pin.py poner            # pide el PIN dos veces con el teclado oculto; 4 dígitos
  python3 pin.py desbloquear      # levanta ya el bloqueo (10 fallos seguidos bloquean la entrada un rato)
  python3 pin.py estado           # puesto / fallos / bloqueado (y hasta cuándo, si la base lo dice) / sesiones, y una línea de avisos

El PIN no se pasa por argumento: quedaría en el historial del shell y en la lista de procesos. Solo se pide
por teclado. Para pruebas automáticas existe la variable BM_PIN_PRUEBA, y solo la acepta si SUPABASE_URL es localhost.
Poner un PIN nuevo cierra todas las sesiones abiertas. Nunca se imprime el PIN.
"""
import getpass
import os
import re
import sys

import maestro

USO = "uso: python3 pin.py poner | desbloquear | estado"


def pin_de_prueba():
    """BM_PIN_PRUEBA solo vale contra una base local. Contra una base real, se ignora y se pide por teclado."""
    pin = os.environ.get("BM_PIN_PRUEBA", "")
    if not pin:
        return None
    cfg = maestro.config()
    if cfg and maestro.url_valida(cfg["SUPABASE_URL"]) and not cfg["SUPABASE_URL"].startswith("https://"):
        return pin
    print("pin: BM_PIN_PRUEBA se ignora salvo contra localhost", file=sys.stderr)
    return None


def pedir_pin():
    pin = pin_de_prueba()
    if pin is not None:
        return pin
    if not sys.stdin.isatty():
        sys.exit("pin: hace falta una terminal para escribir el PIN (no se acepta por argumento)")
    a = getpass.getpass("PIN nuevo (4 dígitos): ")
    b = getpass.getpass("Repetilo: ")
    if a != b:
        sys.exit("pin: no coinciden, no se cambió nada")
    return a


def llamar(nombre, extra=None):
    cfg = maestro.config()
    if not cfg:
        print("maestro: sin config (~/.config/botonera/env)", file=sys.stderr)
        sys.exit(1)
    body = {"p_secret": cfg["BM_SECRET"]}
    body.update(extra or {})
    try:
        return maestro.rpc(nombre, body)
    except maestro.ErrorMaestro as ex:
        print(f"maestro: falló ({ex})", file=sys.stderr)
        sys.exit(1)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(USO)
    cmd, resto = args[0], args[1:]

    if cmd == "poner" and resto:
        sys.exit("pin: el PIN no se pasa por argumento (quedaría en el historial y en la lista de procesos). "
                 "Corré `python3 pin.py poner` sin nada y escribilo cuando lo pida.")
    if cmd == "poner":
        pin = pedir_pin()
        if not re.fullmatch(r"[0-9]{4}", pin):
            sys.exit("pin: tiene que ser de 4 dígitos")
        res = llamar("bm_poner_pin", {"p_pin": pin})
        if res != "ok":
            print(f"pin: no se puso ({res})", file=sys.stderr)
            sys.exit(1)
        print("pin: puesto (se cerraron todas las sesiones)")
    elif cmd == "desbloquear" and not resto:
        res = llamar("bm_desbloquear")
        if res != "ok":
            print(f"pin: no se desbloqueó ({res})", file=sys.stderr)
            sys.exit(1)
        print("pin: desbloqueado")
    elif cmd == "estado" and not resto:
        e = llamar("bm_estado_pin")
        if not isinstance(e, dict):
            print(f"pin: respuesta rara ({e})", file=sys.stderr)
            sys.exit(1)
        hasta = e.get("hasta") or e.get("bloqueado_hasta")   # la base puede no mandarlo (versiones viejas)
        bloq = "sí" if e.get("bloqueado") else "no"
        if e.get("bloqueado") and hasta:
            bloq += f" (hasta {hasta})"
        print(f"pin: puesto={'sí' if e.get('puesto') else 'no'} fallos={e.get('fallos')} "
              f"bloqueado={bloq} sesiones={e.get('sesiones')}")
        av = llamar("bm_estado_avisos")
        if isinstance(av, dict):
            print(f"avisos: dispositivos={av.get('dispositivos')} ultimo={av.get('ultimo') or 'nunca'} "
                  f"error={av.get('error') or 'ninguno'}")
    else:
        sys.exit(USO)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Cliente mínimo de la botonera (Supabase). Lo usan armar.py, esperar.py y marcar.py.

La config sale de estos lugares, en este orden (gana el primero que esté completo):
  1. Variables de entorno SUPABASE_URL, SUPABASE_ANON_KEY y BM_SECRET, pero solo si están las TRES
     (así un SUPABASE_URL suelto de otro proyecto no pisa tu config). Es lo que usa un bot: su secret
     llega por el secret store como variable de entorno.
  2. El archivo que diga la variable BM_ENV_FILE (formato KEY=VALUE, las mismas tres claves).
  3. ~/.config/botonera/env (tu secret completo).
  4. ~/.config/botonera/env-bot (el secret de bot que escribe secret-bot.py).
BM_SECRET viaja en el body de cada RPC (p_secret): la anon key sola no alcanza.
SUPABASE_URL tiene que ser https://, salvo localhost / 127.0.0.1 (pruebas): si no, config() devuelve None.

  config()           -> dict con las tres claves, o None si falta el archivo o alguna clave
  rpc(nombre, body)  -> respuesta ya parseada de {SUPABASE_URL}/rest/v1/rpc/{nombre}
                        levanta ErrorMaestro con un motivo corto (red, HTTP, JSON); si hubo
                        respuesta HTTP, el error lleva su código en `.codigo`
"""
import http.client
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

TIMEOUT = 15  # segundos por llamada
CLAVES = ("SUPABASE_URL", "SUPABASE_ANON_KEY", "BM_SECRET")


class ErrorMaestro(Exception):
    """Falla de red, HTTP o JSON. El mensaje es el motivo corto, listo para imprimir.
    `codigo` es el status HTTP cuando el servidor llegó a contestar; None si falló antes (red, JSON)."""

    def __init__(self, motivo, codigo=None):
        super().__init__(motivo)
        self.codigo = codigo


def ruta_env():
    # os.path.expanduser y no Path.home(): respeta un HOME falso en las pruebas.
    return Path(os.path.expanduser("~/.config/botonera/env"))


def ruta_env_bot():
    return Path(os.path.expanduser("~/.config/botonera/env-bot"))


def url_valida(url):
    """https:// siempre; http:// solo contra localhost / 127.0.0.1 (pruebas). Con http:// el secret viajaría en claro."""
    if url.startswith("https://"):
        return True
    if url.startswith("http://"):
        host = url[len("http://"):].split("/", 1)[0].rsplit("@", 1)[-1]
        host = host[1:].split("]", 1)[0] if host.startswith("[") else host.split(":", 1)[0]
        return host in ("localhost", "127.0.0.1", "::1")
    return False


def _leer_archivo(ruta):
    try:
        texto = Path(ruta).read_text(encoding="utf-8")
    except OSError:
        return None
    cfg = {}
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        k, v = linea.split("=", 1)
        cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg if all(cfg.get(k) for k in CLAVES) else None


def config():
    candidatas = []
    # 1. Variables de entorno, solo si están las tres.
    env = {k: os.environ.get(k, "").strip().strip('"').strip("'") for k in CLAVES}
    if all(env.values()):
        candidatas.append(env)
    # 2-4. Archivos, en orden.
    rutas = []
    if os.environ.get("BM_ENV_FILE", "").strip():
        rutas.append(os.path.expanduser(os.environ["BM_ENV_FILE"].strip()))
    rutas += [ruta_env(), ruta_env_bot()]
    for r in rutas:
        cfg = _leer_archivo(r)
        if cfg:
            candidatas.append(cfg)
    if not candidatas:
        return None
    cfg = candidatas[0]
    if not url_valida(cfg["SUPABASE_URL"]):
        print("maestro: SUPABASE_URL tiene que empezar con https:// (http:// solo vale para localhost)", file=sys.stderr)
        return None
    return cfg


def cabeceras(cfg):
    h = {"apikey": cfg["SUPABASE_ANON_KEY"], "Content-Type": "application/json"}
    # Una key publishable (prefijo sb_) no es un JWT: va solo en apikey. Con un JWT viejo sí va el Bearer.
    if not cfg["SUPABASE_ANON_KEY"].startswith("sb_"):
        h["Authorization"] = f"Bearer {cfg['SUPABASE_ANON_KEY']}"
    return h


def rpc(nombre, body):
    cfg = config()
    if not cfg:
        raise ErrorMaestro("sin config")
    url = f"{cfg['SUPABASE_URL'].rstrip('/')}/rest/v1/rpc/{nombre}"
    req = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers=cabeceras(cfg),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            crudo = r.read().decode("utf-8")
    except urllib.error.HTTPError as ex:
        detalle = ex.read().decode("utf-8", "replace")
        try:  # PostgREST: {"message": "..."} cuando la función hace raise exception
            detalle = json.loads(detalle).get("message") or detalle
        except (ValueError, AttributeError):
            pass
        raise ErrorMaestro(f"HTTP {ex.code}: {detalle[:160]}".replace("\n", " "), codigo=ex.code)
    except (urllib.error.URLError, TimeoutError, OSError) as ex:
        raise ErrorMaestro(f"red: {getattr(ex, 'reason', ex)}")
    except http.client.HTTPException as ex:  # IncompleteRead, RemoteDisconnected, BadStatusLine…
        raise ErrorMaestro(f"red: {type(ex).__name__}")
    except ValueError:  # el cuerpo no decodifica como utf-8
        raise ErrorMaestro("respuesta que no se puede decodificar")
    if not crudo.strip():
        return None
    try:
        res = json.loads(crudo)
    except ValueError:
        raise ErrorMaestro("respuesta que no es JSON")
    # Una función que devuelve tabla llega como lista de una fila: la dejamos en dict.
    if isinstance(res, list) and len(res) == 1:
        res = res[0]
    return res

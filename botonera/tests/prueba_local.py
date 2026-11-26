#!/usr/bin/env python3
"""Prueba de punta a punta de la botonera contra un Supabase LOCAL.

Precondiciones:
  - Docker andando y `supabase start` corrido en la carpeta del repo (aplica la migración sola).
  - Python 3.9+. Solo usa la librería estándar.

Uso:
  supabase start
  python3 tests/prueba_local.py

Qué hace (todo con un HOME temporal: no toca tu ~/.claude ni tu ~/.config):
  1. Lee la URL y la clave pública de `supabase status -o env` (o de --url / --key).
  2. Corre install.sh en el HOME temporal y aplica bootstrap.sql dentro del contenedor de la base
     (no hace falta psql: usa `docker exec`).
  3. Pone el PIN, publica tests/ejemplo.json con armar.py, entra con el PIN, decide como la web,
     recibe con esperar.py y cierra con marcar.py.
  4. Chequea los casos que tienen que fallar: PIN malo, clave pública sola, secreto malo,
     respuesta con prefijo malo.
  5. Editar (campos que vuelven en la respuesta), retomar una tanda decidida con `retomar.py`, la fila
     «Con error» (`errores.py`, listar y marcar «Visto») y el secret de bot, que solo sirve para claves `bot-`.

Opciones:
  --url <url>            URL de la API (default: la de `supabase status`)
  --key <clave>          clave publishable/anon (default: la de `supabase status`)
  --workdir <dir>        carpeta que contiene supabase/ para `supabase status` (default: la del repo)
  --db-container <name>  contenedor de la base (default: supabase_db_<project_id del config.toml>)

Solo corre contra localhost: la prueba pone un PIN y publica datos de ejemplo, no es para un proyecto real.
Sale con 0 si todo pasa y con 1 si algo falla.
"""
import argparse
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
PIN = "1234"
RESULTADOS = []  # (ok, nombre, detalle)


# ───────────────────────── utilidades ─────────────────────────

def registrar(ok, nombre, detalle=""):
    RESULTADOS.append((bool(ok), nombre, detalle))
    marca = "PASS" if ok else "FAIL"
    extra = f"  ({detalle})" if (detalle and not ok) else ""
    print(f"  [{marca}] {nombre}{extra}", flush=True)
    return bool(ok)


def correr(cmd, env=None, cwd=None, timeout=120, entrada=None):
    return subprocess.run(cmd, env=env, cwd=cwd, input=entrada, capture_output=True, text=True, timeout=timeout)


def leer_project_id():
    try:
        m = re.search(r'^project_id\s*=\s*"([^"]+)"', (REPO / "supabase" / "config.toml").read_text(encoding="utf-8"), re.M)
        return m.group(1) if m else "botonera"
    except OSError:
        return "botonera"


def supabase_status(workdir):
    if not shutil.which("supabase"):
        return None, "no encuentro el CLI de supabase en el PATH"
    cmd = ["supabase", "status", "-o", "env"]
    if workdir:
        cmd += ["--workdir", workdir]
    r = correr(cmd, cwd=str(REPO), timeout=60)
    if r.returncode != 0:
        return None, (r.stderr or r.stdout).strip().splitlines()[-1:] or "supabase status falló (¿corriste supabase start?)"
    env = {}
    for linea in r.stdout.splitlines():
        m = re.match(r'^([A-Z_0-9]+)="?(.*?)"?$', linea.strip())
        if m:
            env[m.group(1)] = m.group(2)
    return env, None


def http(metodo, url, clave_publica, cuerpo=None):
    """Devuelve (status, json_o_texto). No levanta por HTTP 4xx/5xx."""
    h = {"apikey": clave_publica, "Content-Type": "application/json"}
    if not clave_publica.startswith("sb_"):
        h["Authorization"] = f"Bearer {clave_publica}"
    datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, headers=h, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status, crudo = r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as ex:
        status, crudo = ex.code, ex.read().decode("utf-8", "replace")
    try:
        return status, json.loads(crudo) if crudo.strip() else None
    except ValueError:
        return status, crudo


def mensaje(cuerpo):
    return (cuerpo.get("message") if isinstance(cuerpo, dict) else str(cuerpo)) or ""


# ───────────────────────── la prueba ─────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Prueba local de la botonera contra Supabase local.")
    ap.add_argument("--url")
    ap.add_argument("--key")
    ap.add_argument("--workdir")
    ap.add_argument("--db-container")
    args = ap.parse_args()

    print("Botonera: prueba local\n")

    url, key = args.url, args.key
    if not (url and key):
        st, err = supabase_status(args.workdir)
        if st is None:
            print(f"No pude leer `supabase status`: {err}\n¿Corriste `supabase start`? También podés pasar --url y --key.")
            return 1
        url = url or st.get("API_URL")
        key = key or st.get("PUBLISHABLE_KEY") or st.get("ANON_KEY")
    if not (url and key):
        print("Falta la URL o la clave pública de Supabase.")
        return 1
    url = url.rstrip("/")
    host = urlparse(url).hostname
    if host not in ("127.0.0.1", "localhost", "::1"):
        print(f"Me niego a correr contra {host}: esta prueba solo es para un Supabase local.")
        return 1
    contenedor = args.db_container or f"supabase_db_{leer_project_id()}"

    tmp = Path(tempfile.mkdtemp(prefix="botonera-prueba-"))
    home = tmp / "home"
    home.mkdir()
    env = dict(os.environ, HOME=str(home))
    for k in ("CLAUDE_CODE_HOST_SESSION_ID", "BM_SECRET", "SUPABASE_URL", "SUPABASE_ANON_KEY"):
        env.pop(k, None)
    skill = home / ".claude" / "skills" / "botonera"
    clave = f"prueba-local-{int(time.time())}"
    web_config = REPO / "web" / "config.js"
    web_config_antes = web_config.read_text(encoding="utf-8") if web_config.exists() else None

    def rpc(nombre, cuerpo):
        return http("POST", f"{url}/rest/v1/rpc/{nombre}", key, cuerpo)

    def py(script, *a, timeout=60, entorno=None):
        return correr([sys.executable, str(skill / script), *a], env=entorno or env, timeout=timeout)

    def sql(texto):
        return correr(["docker", "exec", "-i", contenedor, "psql", "-U", "postgres", "-v", "ON_ERROR_STOP=1", "-t", "-A"],
                      entrada=texto, timeout=60)

    def leer_env(ruta):
        cfg = {}
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.strip().startswith("#"):
                k, v = linea.split("=", 1)
                cfg[k.strip()] = v.strip()
        return cfg

    try:
        # 1. instalar
        print("Instalación")
        r = correr(["bash", str(REPO / "install.sh"), "--url", url, "--key", key, "--yes",
                    "--avisar-url", f"http://supabase_kong_{leer_project_id()}:8000/functions/v1/bm-avisar"],
                   env=env, timeout=60)
        if not registrar(r.returncode == 0 and (skill / "armar.py").exists(), "install.sh copia el skill y escribe la config",
                         (r.stderr or r.stdout)[-300:]):
            return resumen()
        env_file = home / ".config" / "botonera" / "env"
        modo = oct(env_file.stat().st_mode & 0o777)
        registrar(modo == "0o600", "~/.config/botonera/env queda con permisos 600", modo)

        bootstrap = (home / ".config" / "botonera" / "bootstrap.sql").read_text(encoding="utf-8")
        r = correr(["docker", "exec", "-i", contenedor, "psql", "-U", "postgres", "-v", "ON_ERROR_STOP=1", "-t", "-A"],
                   entrada=bootstrap, timeout=60)
        if not registrar(r.returncode == 0 and r.stdout.strip() == "ok", "bm_instalar devuelve ok",
                         (r.stderr or r.stdout).strip()[-300:] or f"¿el contenedor {contenedor} está andando?"):
            return resumen()

        # 2. PIN y publicación
        print("\nPIN y publicación")
        r = py("pin.py", "poner", entorno={**env, "BM_PIN_PRUEBA": PIN})
        registrar(r.returncode == 0 and "puesto" in r.stdout, "pin.py poner", r.stderr or r.stdout)
        r = py("pin.py", "estado")
        registrar(r.returncode == 0 and "puesto=sí" in r.stdout, "pin.py estado dice puesto=sí", r.stderr or r.stdout)

        datos = json.loads((REPO / "tests" / "ejemplo.json").read_text(encoding="utf-8"))
        datos = copy.deepcopy(datos)
        datos["clave"] = clave
        json_path = tmp / "tanda.json"
        json_path.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
        html_path = tmp / "tanda.html"
        r = py("armar.py", "--publicar", str(json_path), str(html_path))
        registrar(r.returncode == 0 and f"maestro: creada · {clave}" in r.stdout, "armar.py --publicar crea la tanda", r.stderr or r.stdout)
        r = py("armar.py", "--publicar", str(json_path), str(html_path))
        registrar(r.returncode == 0 and f"maestro: actualizada · {clave}" in r.stdout, "republicar mientras está abierta la actualiza", r.stderr or r.stdout)

        # 3. entrar con el PIN (lo que hace la web)
        print("\nEntrada con PIN")
        st, res = rpc("bm_entrar", {"p_pin": "0000" if PIN != "0000" else "9999"})
        registrar(st == 200 and isinstance(res, dict) and res.get("ok") is False and res.get("motivo") == "pin_incorrecto",
                  "PIN incorrecto devuelve pin_incorrecto", f"{st} {res}")
        st, res = rpc("bm_entrar", {"p_pin": PIN})
        token = res.get("token") if isinstance(res, dict) else None
        if not registrar(st == 200 and token and len(token) == 64, "PIN correcto devuelve un token", f"{st} {res}"):
            return resumen()

        # 4. lista y fila con el token
        st, lista = rpc("bm_lista", {"p_token": token})
        fila = next((x for x in lista if x.get("clave") == clave), None) if isinstance(lista, list) else None
        registrar(fila is not None and fila.get("estado") == "abierta" and fila.get("n_items") == 4,
                  "bm_lista con token muestra la tanda abierta con 4 ítems", f"{st} {str(lista)[:200]}")
        st, fl = rpc("bm_fila", {"p_token": token, "p_clave": clave})
        f = fl[0] if isinstance(fl, list) and fl else (fl if isinstance(fl, dict) else {})
        registrar(st == 200 and f.get("clave") == clave and "<html" in (f.get("html") or "").lower()
                  and len((f.get("datos") or {}).get("items", [])) == 4,
                  "bm_fila con token trae el html y los datos", f"{st} {str(fl)[:200]}")
        version = f.get("updated_at")

        # 5. negativos de seguridad
        print("\nChequeos de seguridad")
        st, res = http("GET", f"{url}/rest/v1/botoneras?select=clave", key)
        registrar((st in (401, 403)) or (st == 200 and res == []), "la clave pública sola no puede leer la tabla botoneras", f"{st} {str(res)[:120]}")
        st, res = http("GET", f"{url}/rest/v1/bm_config?select=k,v", key)
        registrar((st in (401, 403)) or (st == 200 and res == []), "la clave pública sola no puede leer bm_config", f"{st} {str(res)[:120]}")
        st, res = http("POST", f"{url}/rest/v1/botoneras", key, {"clave": "x", "titulo": "x", "datos": {}, "html": "x"})
        registrar(st in (401, 403), "la clave pública sola no puede insertar en botoneras", f"{st} {str(res)[:120]}")
        st, res = rpc("bm_lista", {"p_token": "token-falso"})
        registrar(st >= 400 and "token invalido" in mensaje(res), "bm_lista con token falso se rechaza", f"{st} {res}")
        st, res = rpc("bm_recibir", {"p_secret": "secreto-falso", "p_clave": clave})
        registrar(st >= 400 and "secret invalido" in mensaje(res), "bm_recibir con secreto equivocado se rechaza", f"{st} {res}")
        st, res = rpc("bm_publicar", {"p_secret": "secreto-falso", "p_clave": "intruso", "p_session_id": None,
                                      "p_sesion_titulo": None, "p_skill": None, "p_proyecto": None, "p_titulo": "x",
                                      "p_n_items": 1, "p_datos": {}, "p_html": "<html></html>"})
        registrar(st >= 400 and "secret invalido" in mensaje(res), "bm_publicar con secreto equivocado se rechaza", f"{st} {res}")
        st, res = rpc("bm_poner_pin", {"p_secret": "secreto-falso", "p_pin": "9999"})
        registrar(st >= 400 and "secret invalido" in mensaje(res), "bm_poner_pin con secreto equivocado se rechaza", f"{st} {res}")
        st, res = rpc("bm_avisos_datos", {})
        registrar(st in (401, 403, 404), "bm_avisos_datos (solo service_role) no se puede llamar con la clave pública", f"{st} {str(res)[:120]}")
        # Las funciones internas (instalación, avisos, llaves) no se pueden llamar con la clave pública.
        internas = {
            "bm_instalar": {"p_secret_sha256": "0" * 64, "p_avisar_url": "http://x", "p_zona": "UTC", "p_contacto": "x"},
            "bm_avisos_tick": {},
            "bm_avisos_llamar": {"p_cuerpo": {}},
            "bm_avisos_guardar_vapid": {"p_publica": "a", "p_privada": "b"},
            "bm_avisos_resultado": {"p_ok": [], "p_muertos": [], "p_fallidos": [], "p_claves": [], "p_error": "x"},
            "bm_check": {"p_secret": "x"},
            "bm_rol": {"p_secret": "x"},
            "bm_es_bot": {"p_texto": "bot-x"},
        }
        abiertas = [n for n, cuerpo in internas.items() if rpc(n, cuerpo)[0] not in (401, 403, 404)]
        registrar(not abiertas, "las funciones internas (instalar, avisos, llaves) no se llaman con la clave pública", ", ".join(abiertas))
        st, res = rpc("bm_decidir_pin", {"p_token": token, "p_clave": clave, "p_respuesta": "/botonera respuesta · otra-clave\n1. va"})
        registrar(st >= 400 and "respuesta invalida" in mensaje(res), "respuesta con prefijo de otra clave se rechaza", f"{st} {res}")
        st, res = rpc("bm_decidir_pin", {"p_token": token, "p_clave": clave, "p_respuesta": "1. va · sin prefijo"})
        registrar(st >= 400 and "respuesta invalida" in mensaje(res), "respuesta sin prefijo se rechaza", f"{st} {res}")
        st, res = rpc("bm_decidir_pin", {"p_token": "token-falso", "p_clave": clave, "p_respuesta": f"/botonera respuesta · {clave}\n1. va"})
        registrar(st >= 400 and "token invalido" in mensaje(res), "decidir con token falso se rechaza", f"{st} {res}")
        st, res = rpc("bm_decidir_pin", {"p_token": token, "p_clave": clave, "p_respuesta": f"/botonera respuesta · {clave}\n1. va",
                                         "p_version": "2020-01-01T00:00:00Z"})
        registrar(st == 200 and res == "cambio", "decidir contra una versión vieja devuelve cambio", f"{st} {res}")
        st, res = http("GET", f"{url}/rest/v1/rpc/bm_lista", key)
        registrar(st >= 400, "las funciones no se llaman con GET sin parámetros", f"{st}")

        # 6. decidir y recibir: esperar.py arranca ANTES de la decisión
        print("\nDecidir, recibir y marcar")
        respuesta = (f"/botonera respuesta · {clave}\n"
                     "1. va · Subir el precio de los envíos → Subir el envío\n"
                     "2. eligió mail · Elegir el canal para los avisos → Mail\n"
                     "3. no va · Archivar los pedidos viejos → Dejarlos")
        proc = subprocess.Popen([sys.executable, str(skill / "esperar.py"), clave, "--cada", "1"], env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        salida = {}
        hilo = threading.Thread(target=lambda: salida.update(zip(("out", "err"), proc.communicate())), daemon=True)
        hilo.start()
        time.sleep(3)
        registrar(proc.poll() is None, "esperar.py sigue esperando mientras nadie decide")
        st, res = rpc("bm_decidir_pin", {"p_token": token, "p_clave": clave, "p_respuesta": respuesta, "p_version": version})
        registrar(st == 200 and res == "decidida", "bm_decidir_pin con token y prefijo correctos deja la tanda decidida", f"{st} {res}")
        hilo.join(timeout=30)
        if hilo.is_alive():
            proc.kill()
            hilo.join(timeout=5)
        out = (salida.get("out") or "").strip()
        registrar(not hilo.is_alive() and proc.returncode == 0 and out == respuesta,
                  "esperar.py sale con exactamente la respuesta decidida", f"rc={proc.returncode} salida={out[:200]!r} err={(salida.get('err') or '')[:200]!r}")
        st, res = rpc("bm_decidir_pin", {"p_token": token, "p_clave": clave, "p_respuesta": respuesta})
        registrar(st == 200 and res == "recibida", "decidir de nuevo no pisa una tanda ya recibida", f"{st} {res}")

        r = py("pendientes.py", "--horas", "0")
        registrar(r.returncode == 0 and clave in r.stdout, "pendientes.py lista la tanda recibida sin aplicar", r.stdout + r.stderr)

        r = py("marcar.py", clave, "aplicada", "1. hecho\\n2. hecho\\n3. no se hizo, el usuario dijo que no")
        registrar(r.returncode == 0 and "→ aplicada (antes: recibida)" in r.stdout, "marcar.py aplicada desde recibida", r.stdout + r.stderr)
        st, fl = rpc("bm_fila", {"p_token": token, "p_clave": clave})
        f = fl[0] if isinstance(fl, list) and fl else {}
        registrar(f.get("estado") == "aplicada" and "no se hizo" in (f.get("resumen_aplicado") or ""),
                  "la fila queda aplicada y con el resumen guardado", f"{st} {str(fl)[:200]}")
        r = py("marcar.py", clave, "aplicada")
        registrar(r.returncode == 1 and "NO se marcó" in r.stdout, "marcar.py aplicada dos veces se rechaza (transición inválida)", r.stdout + r.stderr)
        r = py("esperar.py", clave, "--cada", "1", timeout=30)
        registrar(r.returncode == 0 and "ya se resolvió (aplicada)" in r.stdout, "esperar.py sobre una tanda aplicada avisa que no hay nada que aplicar", r.stdout + r.stderr)
        r = py("esperar.py", "clave-que-no-existe", "--cada", "1", timeout=30)
        registrar(r.returncode == 1 and "no existe" in r.stdout, "esperar.py sobre una clave inexistente sale con 1", r.stdout + r.stderr)
        r = py("armar.py", "--publicar", str(json_path), str(html_path))
        registrar(r.returncode != 0 and "ya está" in r.stderr, "republicar una tanda ya cerrada se rechaza", r.stdout + r.stderr)
        r = py("pendientes.py", "--horas", "0")
        registrar(r.returncode == 0 and clave not in r.stdout, "pendientes.py ya no la lista", r.stdout + r.stderr)


        # 6b. Editar (campos), retomar, «Con error» y rol de bot. El token del paso 3 sigue vivo (el PIN cambia al final).
        print("\nEditar: campos que viajan y vuelven")
        secreto = leer_env(env_file)["BM_SECRET"]

        def armar_variante(nombre, cambio, extra=()):
            d = copy.deepcopy(datos)
            d["clave"] = f"{clave}-{nombre}"
            cambio(d)
            ruta = tmp / f"{nombre}.json"
            ruta.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
            return py("armar.py", *extra, str(ruta), str(tmp / f"{nombre}.html"))

        seis = [{"id": f"c{i}", "etiqueta": f"Campo {i}", "valor": "x", "tipo": "texto"} for i in range(6)]
        r = armar_variante("seis", lambda d: d["items"][0].__setitem__("campos", seis), ("--html",))
        registrar(r.returncode == 1 and "'campos' tiene que ser una lista de 1 a 5" in r.stderr,
                  "armar.py rechaza más de 5 campos", r.stderr)
        r = armar_variante("tipo", lambda d: d["items"][0]["campos"][0].__setitem__("tipo", "color"), ("--html",))
        registrar(r.returncode == 1 and "tiene que ser texto | textarea | numero | fecha | opcion" in r.stderr,
                  "armar.py rechaza un tipo de campo desconocido", r.stderr)
        r = armar_variante("etiqueta", lambda d: d["items"][0]["campos"][0].__setitem__("etiqueta", "una etiqueta con muchas más de seis palabras"), ("--html",))
        registrar(r.returncode == 1 and "palabras (techo 6)" in r.stderr, "armar.py rechaza una etiqueta de más de 6 palabras", r.stderr)
        r = armar_variante("en-opciones", lambda d: d["items"][1].__setitem__("campos", d["items"][0]["campos"]), ("--html",))
        registrar(r.returncode == 1 and "'campos' va solo en cards sí/no" in r.stderr, "armar.py rechaza campos en una card con opciones", r.stderr)
        r = armar_variante("aplicar", lambda d: d["items"][0].__setitem__("aplicar", {"quizas": "algo"}), ("--html",))
        registrar(r.returncode == 1 and "no es una respuesta de esta card" in r.stderr, "armar.py rechaza una clave de aplicar que no es una respuesta", r.stderr)
        r = armar_variante("aplicar-largo", lambda d: d["items"][0].__setitem__("aplicar", {"va": " ".join(["palabra"] * 41)}), ("--html",))
        registrar(r.returncode == 1 and "techo 40" in r.stderr, "armar.py rechaza un plan de aplicar de más de 40 palabras", r.stderr)
        r = armar_variante("sin-aplicar", lambda d: [i.pop("aplicar", None) for i in d["items"]], ("--html",))
        registrar(r.returncode == 0 and "sin 'aplicar'" in r.stderr, "armar.py avisa (sin frenar) cuando faltan los planes de aplicar", r.stderr)

        clave_c = f"{clave}-campos"
        ruta_c = tmp / "campos.json"
        d_c = copy.deepcopy(datos)
        d_c["clave"] = clave_c
        ruta_c.write_text(json.dumps(d_c, ensure_ascii=False), encoding="utf-8")
        r = py("armar.py", "--publicar", str(ruta_c), str(tmp / "campos.html"))
        registrar(r.returncode == 0 and f"maestro: creada · {clave_c}" in r.stdout and "aviso" not in r.stderr,
                  "armar.py --publicar sube una tanda con campos y planes de aplicar", r.stderr or r.stdout)
        st, fl = rpc("bm_fila", {"p_token": token, "p_clave": clave_c})
        f = fl[0] if isinstance(fl, list) and fl else {}
        campos = ((f.get("datos") or {}).get("items") or [{}])[0].get("campos") or []
        registrar([c.get("id") for c in campos] == ["precio", "desde", "alcance"] and campos[0].get("valor") == 3500,
                  "los campos viajan a la base tal cual", f"{st} {str(campos)[:200]}")

        respuesta_c = (f"/botonera respuesta · {clave_c}\n"
                       "1. va con cambios · Subir el precio de los envíos → Subir el envío · "
                       "campos: precio=4200 (antes 3500); desde=2026-11-22 (antes 2026-11-15) · comentario: Solo hasta fin de mes.\n"
                       "2. eligió whatsapp · Elegir el canal para los avisos → Mensaje de WhatsApp\n"
                       "3. sin marcar · Archivar los pedidos viejos")
        st, res = rpc("bm_decidir_pin", {"p_token": token, "p_clave": clave_c, "p_respuesta": respuesta_c})
        registrar(st == 200 and res == "decidida", "la respuesta «va con cambios · campos: …» se guarda entera", f"{st} {res}")

        print("\nRetomar sin la sesión viva")
        st, res = rpc("bm_retomar", {"p_secret": secreto, "p_clave": clave_c})
        its = res.get("items") if isinstance(res, dict) else []
        registrar(st == 200 and res.get("estado") == "decidida" and res.get("respuesta_texto") == respuesta_c and len(its) == 4
                  and "Cambiar la tarifa" in (its[0].get("aplicar") or {}).get("va", "") and "whatsapp" in (its[1].get("aplicar") or {}),
                  "bm_retomar trae la respuesta y el plan aplicar de cada ítem, sin cambiar el estado", f"{st} {str(res)[:200]}")
        st, res = rpc("bm_retomar", {"p_secret": secreto, "p_clave": "clave-que-no-existe"})
        registrar(st == 200 and isinstance(res, dict) and res.get("estado") == "no_existe", "bm_retomar sobre una clave inexistente dice no_existe", f"{st} {res}")
        st, res = rpc("bm_retomar", {"p_secret": "secreto-falso", "p_clave": clave_c})
        registrar(st >= 400 and "secret invalido" in mensaje(res), "bm_retomar con secreto equivocado se rechaza", f"{st} {res}")
        r = py("retomar.py", clave_c)
        registrar(r.returncode == 0 and "precio=4200 (antes 3500)" in r.stdout and "Cambiar la tarifa" in r.stdout
                  and "[whatsapp] Pedir el alta" in r.stdout and "sin marcar: no se hace" in r.stdout,
                  "retomar.py arma el brief: los valores nuevos, el plan de cada respuesta y lo sin marcar", r.stdout + r.stderr)
        r = py("retomar.py", clave_c, "--json")
        try:
            a = json.loads(r.stdout)
        except ValueError:
            a = {}
        registrar(r.returncode == 0 and a.get("todo_con_plan") is True and a["items"][0]["campos"].startswith("precio=4200")
                  and a["items"][0]["comentario"] == "Solo hasta fin de mes." and a["items"][2]["accion"] == "nada",
                  "retomar.py --json separa campos, comentario y acción de cada ítem", r.stdout[:200] + r.stderr)
        r = py("retomar.py", clave_c, "--tomar")
        st, fl = rpc("bm_fila", {"p_token": token, "p_clave": clave_c})
        f = fl[0] if isinstance(fl, list) and fl else {}
        registrar(r.returncode == 0 and f.get("estado") == "recibida", "retomar.py --tomar pasa la tanda de decidida a recibida", f"{r.stderr} {f.get('estado')}")
        r = py("retomar.py", "clave-que-no-existe")
        registrar(r.returncode == 1 and "no existe" in r.stderr, "retomar.py sobre una clave inexistente sale con 1", r.stdout + r.stderr)

        st, res = rpc("bm_retomar", {"p_secret": secreto, "p_clave": clave_c})
        tipos = [i.get("tipo") for i in (res.get("items") or [])] if isinstance(res, dict) else []
        registrar(st == 200 and tipos == [None, None, None, "revision"], "bm_retomar devuelve el tipo de cada card (la revisión se reconoce)", f"{st} {tipos}")

        print("\nColgadas y fila «Con error»")
        r = py("colgadas.py")
        registrar(r.returncode == 0 and clave_c in r.stdout and "plan aplicar 3/3" in r.stdout,
                  "colgadas.py lista la tanda recibida con su «plan aplicar 3/3»", r.stdout + r.stderr)
        r = py("colgadas.py", "--archivar", clave_c, "la sesión ya no está")
        registrar(r.returncode == 0 and "→ archivada (antes: recibida)" in r.stdout and "errores: creado" in r.stdout,
                  "colgadas.py --archivar archiva y publica un error si había una respuesta sin aplicar", r.stdout + r.stderr)

        def errores_vistos():
            st_, lista_ = rpc("bm_errores_lista", {"p_token": token})
            return st_, (lista_ if isinstance(lista_, list) else [])
        st, lista = errores_vistos()
        e_sesion = next((e for e in lista if e.get("origen_id") == clave_c), None)
        registrar(st == 200 and e_sesion is not None and e_sesion.get("tipo") == "sesion" and clave_c in e_sesion.get("titulo", ""),
                  "bm_errores_lista (con token) muestra el error de la tanda archivada sin aplicar", f"{st} {str(lista)[:200]}")

        tarea_id = f"tarea-prueba-{int(time.time())}"
        err_tarea = {"tipo": "tarea", "origen_id": tarea_id, "titulo": "Tarea de prueba", "motivo": "Límite de uso",
                     "ocurrio_at": "2026-11-01T03:00:00Z"}
        r = py("errores.py", "publicar", json.dumps(err_tarea), "--seco")
        registrar(r.returncode == 0 and "WOULD publish" in r.stdout, "errores.py --seco muestra lo que publicaría", r.stdout + r.stderr)
        st, lista = errores_vistos()
        registrar(not any(e.get("origen_id") == tarea_id for e in lista), "…y no escribe nada", str(lista)[:200])
        r = py("errores.py", "publicar", json.dumps(err_tarea))
        registrar(r.returncode == 0 and "errores: 1 creado" in r.stdout, "errores.py publicar crea el error", r.stdout + r.stderr)
        r = py("errores.py", "publicar", json.dumps(err_tarea))
        registrar(r.returncode == 0 and "errores: 1 repetido" in r.stdout, "publicar dos veces el mismo error no lo duplica", r.stdout + r.stderr)
        ahora = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        runs = {"taskId": f"tarea-runs-{int(time.time())}", "runs": [
            {"status": "failed", "started_at": ahora, "error": "401 invalid_grant", "title": "Tarea con runs"},
            {"status": "failed", "started_at": "2020-01-01T00:00:00Z", "error": "viejo"},
            {"status": "success", "started_at": ahora}]}
        ruta_runs = tmp / "runs.json"
        ruta_runs.write_text(json.dumps(runs), encoding="utf-8")
        r = py("errores.py", "desde-runs", str(ruta_runs))
        registrar(r.returncode == 0 and "errores: 1 creado" in r.stdout and "401 invalid_grant" in r.stdout,
                  "errores.py desde-runs publica solo los runs fallidos de las últimas 24 h", r.stdout + r.stderr)
        st, res = rpc("bm_error_publicar", {"p_secret": "secreto-falso", "p_tipo": "tarea", "p_origen_id": "x", "p_titulo": "x",
                                            "p_motivo": None, "p_ocurrio_at": ahora})
        registrar(st >= 400 and "secret invalido" in mensaje(res), "bm_error_publicar con secreto equivocado se rechaza", f"{st} {res}")
        st, res = rpc("bm_error_publicar", {"p_secret": secreto, "p_tipo": "otro", "p_origen_id": "x", "p_titulo": "x",
                                            "p_motivo": None, "p_ocurrio_at": ahora})
        registrar(st >= 400 and "tipo invalido" in mensaje(res), "bm_error_publicar rechaza un tipo desconocido", f"{st} {res}")
        st, res = rpc("bm_errores_lista", {"p_token": "token-falso"})
        registrar(st >= 400 and "token invalido" in mensaje(res), "bm_errores_lista con token falso se rechaza", f"{st} {res}")
        st, res = http("GET", f"{url}/rest/v1/bm_errores?select=titulo", key)
        registrar((st in (401, 403)) or (st == 200 and res == []), "la clave pública sola no puede leer la tabla bm_errores", f"{st} {str(res)[:120]}")
        st, lista = errores_vistos()
        e_tarea = next((e for e in lista if e.get("origen_id") == tarea_id), None)
        registrar(e_tarea is not None and len(lista) >= 3, "la lista trae los errores sin ver", str(lista)[:300])
        ids = [e["id"] for e in lista]
        st, res = rpc("bm_error_visto", {"p_token": token, "p_id": e_tarea["id"]})
        registrar(st == 200 and res is True, "bm_error_visto marca uno como visto", f"{st} {res}")
        st, res = rpc("bm_error_visto", {"p_token": token, "p_id": e_tarea["id"]})
        registrar(st == 200 and res is False, "marcar visto dos veces devuelve false", f"{st} {res}")
        st, lista2 = errores_vistos()
        registrar([e["id"] for e in lista2] == [i for i in ids if i != e_tarea["id"]], "el error visto sale de la lista y los demás quedan",
                  f"{[e['id'] for e in lista2]} vs {ids}")
        st, res = rpc("bm_error_visto", {"p_token": "token-falso", "p_id": 1})
        registrar(st >= 400 and "token invalido" in mensaje(res), "bm_error_visto con token falso se rechaza", f"{st} {res}")
        for e in lista2:   # la prueba deja la fila «Con error» vacía
            rpc("bm_error_visto", {"p_token": token, "p_id": e["id"]})

        print("\nRol de bot")
        r = py("secret-bot.py")
        env_bot = home / ".config" / "botonera" / "env-bot"
        m = re.search(r"'([0-9a-f]{64})'", r.stdout)
        cfg_bot = leer_env(env_bot) if env_bot.exists() else {}
        bs = cfg_bot.get("BM_SECRET", "")
        registrar(r.returncode == 0 and m and bs and bs not in r.stdout and oct(env_bot.stat().st_mode & 0o777) == "0o600",
                  "secret-bot.py escribe env-bot (600), imprime el hash y nunca el secret", r.stderr or r.stdout[-200:])
        r = py("secret-bot.py")
        registrar(r.returncode != 0 and "ya existe" in (r.stderr + r.stdout), "secret-bot.py no pisa un env-bot existente sin --rotar", r.stdout + r.stderr)
        st, res = rpc("bm_pendientes", {"p_secret": bs, "p_horas": 0})
        registrar(st >= 400 and "secret invalido" in mensaje(res), "mientras el hash no está cargado el secret de bot no entra a nada", f"{st} {res}")
        r = sql(f"insert into public.bm_config (k, v) values ('bot_secret_sha256', '{m.group(1)}') on conflict (k) do update set v = excluded.v;")
        registrar(r.returncode == 0, "se carga el hash del secret de bot", r.stderr)

        cb = f"bot-prueba-{int(time.time())}"
        datos_bot = {"titulo": "Tanda de un bot", "clave": cb, "items": [{"n": 1, "titulo": "Algo del bot"}]}
        def publicar_bot(c, session, skill="otro"):
            return rpc("bm_publicar", {"p_secret": bs, "p_clave": c, "p_session_id": session, "p_sesion_titulo": "Bot",
                                       "p_skill": skill, "p_proyecto": None, "p_titulo": "Tanda de un bot", "p_n_items": 1,
                                       "p_datos": datos_bot, "p_html": "<html></html>"})
        st, res = publicar_bot(cb, "bot-agente")
        registrar(st == 200 and res == "creada", "el secret de bot publica una clave bot- con session_id bot-", f"{st} {res}")
        st, lista = rpc("bm_lista", {"p_token": token})
        fb = next((x for x in lista if x.get("clave") == cb), {}) if isinstance(lista, list) else {}
        registrar(fb.get("skill") == "bot" and fb.get("session_id") == "bot-agente", "el servidor fuerza skill = bot", str(fb)[:200])
        st, res = publicar_bot("tanda-comun", "bot-agente")
        registrar(st >= 400 and "rol bot: solo claves bot-" in mensaje(res), "el secret de bot no publica una clave que no empieza con bot-", f"{st} {res}")
        st, res = publicar_bot(cb, "sesion-de-claude-code")
        registrar(st >= 400 and "session_id tiene que empezar con bot-" in mensaje(res), "el secret de bot no ata su tanda a una sesión de Claude Code", f"{st} {res}")
        st, res = publicar_bot(cb, None)
        registrar(st >= 400 and "session_id tiene que empezar con bot-" in mensaje(res), "…ni publica sin session_id", f"{st} {res}")
        for nombre, cuerpo in (("bm_recibir", {"p_clave": clave}), ("bm_marcar", {"p_clave": clave, "p_estado": "archivada", "p_resumen": "x"}),
                               ("bm_retomar", {"p_clave": clave})):
            st, res = rpc(nombre, dict(cuerpo, p_secret=bs))
            registrar(st >= 400 and "rol bot: solo claves bot-" in mensaje(res), f"{nombre} con el secret de bot no toca una clave ajena", f"{st} {res}")
        for nombre, cuerpo in (("bm_poner_pin", {"p_pin": "1111"}), ("bm_desbloquear", {}), ("bm_estado_pin", {}), ("bm_sin_cerrar", {}),
                               ("bm_estado_avisos", {})):
            st, res = rpc(nombre, dict(cuerpo, p_secret=bs))
            registrar(st >= 400 and "secret invalido" in mensaje(res), f"{nombre} no acepta el secret de bot", f"{st} {res}")
        st, res = rpc("bm_error_publicar", {"p_secret": bs, "p_tipo": "tarea", "p_origen_id": "x", "p_titulo": "x", "p_motivo": None, "p_ocurrio_at": ahora})
        registrar(st >= 400 and "rol bot: no publica errores" in mensaje(res), "el secret de bot no publica errores", f"{st} {res}")
        for nombre, cuerpo in (("bm_obstaculo_publicar", {"p_titulo": "x", "p_por_que": "", "p_de": "", "p_frena": "", "p_link": "https://ejemplo.com", "p_comando": ""}),
                               ("bm_obstaculos_resueltos", {}), ("bm_obstaculo_llevado", {"p_id": 1}),
                               ("bm_vuelo_anotar", {"p_session_id": "bot-x", "p_titulo": "x", "p_que_hace": "x", "p_proximo": "x"}),
                               ("bm_vuelo_cerrar", {"p_session_id": "bot-x"}), ("bm_trabadas", {"p_horas": 0})):
            st, res = rpc(nombre, dict(cuerpo, p_secret=bs))
            registrar(st >= 400 and "secret invalido" in mensaje(res), f"{nombre} no acepta el secret de bot (obstáculos, vuelos y trabadas son del dueño)", f"{st} {res}")
        st, res = rpc("bm_reemplazar", {"p_secret": bs, "p_clave": clave, "p_n": 1, "p_por": f"{cb}#1"})
        registrar(st >= 400 and "rol bot: solo claves bot-" in mensaje(res), "bm_reemplazar con el secret de bot no toca una clave ajena", f"{st} {res}")
        r = py("colgadas.py")
        registrar(r.returncode == 0 and cb not in r.stdout and "bot- salteadas" in r.stdout, "colgadas.py no lista las tandas bot-", r.stdout + r.stderr)
        r = py("colgadas.py", "--archivar", cb, "prueba")
        registrar(r.returncode == 1 and "es de un bot" in r.stdout, "colgadas.py --archivar no archiva una tanda bot-", r.stdout + r.stderr)

        # pendientes: el bot ve solo lo suyo; el secret total ve todo
        clave_o = f"{clave}-otra"
        d_o = copy.deepcopy(datos)
        d_o["clave"] = clave_o
        (tmp / "otra.json").write_text(json.dumps(d_o, ensure_ascii=False), encoding="utf-8")
        py("armar.py", "--publicar", str(tmp / "otra.json"), str(tmp / "otra.html"))
        for c in (clave_o, cb):
            rpc("bm_decidir_pin", {"p_token": token, "p_clave": c, "p_respuesta": f"/botonera respuesta · {c}\n1. va · x"})
        st, pb = rpc("bm_pendientes", {"p_secret": bs, "p_horas": 0})
        st2, pt = rpc("bm_pendientes", {"p_secret": secreto, "p_horas": 0})
        claves_b = sorted(x["clave"] for x in pb) if isinstance(pb, list) else None
        claves_t = {x["clave"] for x in pt} if isinstance(pt, list) else set()
        registrar(claves_b == [cb] and {cb, clave_o} <= claves_t,
                  "bm_pendientes: el bot ve solo sus tandas bot-, el secret total ve todas", f"bot={claves_b} total={sorted(claves_t)}")
        st, res = rpc("bm_recibir", {"p_secret": bs, "p_clave": cb})
        registrar(st == 200 and res.get("estado") == "recibida" and res.get("respuesta_texto", "").endswith("1. va · x"),
                  "bm_recibir con el secret de bot entrega la respuesta de su tanda", f"{st} {res}")
        st, res = rpc("bm_marcar", {"p_secret": bs, "p_clave": cb, "p_estado": "aplicada", "p_resumen": "hecho"})
        registrar(st == 200 and res.get("cambiado") is True, "bm_marcar con el secret de bot cierra su tanda", f"{st} {res}")
        py("marcar.py", clave_o, "archivada", "fin de la prueba")

        # el bot por variables de entorno (sin archivo de config): armar.py, esperar.py y session_id bot-
        home_bot = tmp / "home-bot"
        home_bot.mkdir()
        entorno_bot = dict(env, HOME=str(home_bot), SUPABASE_URL=url, SUPABASE_ANON_KEY=key, BM_SECRET=bs, BM_SESSION_ID="bot-por-env")
        cb2 = f"bot-env-{int(time.time())}"
        d_b = copy.deepcopy(datos)
        d_b["clave"] = cb2
        (tmp / "bot.json").write_text(json.dumps(d_b, ensure_ascii=False), encoding="utf-8")
        r = py("armar.py", "--publicar", str(tmp / "bot.json"), str(tmp / "bot.html"), entorno=entorno_bot)
        st, fl = rpc("bm_fila", {"p_token": token, "p_clave": cb2})
        f = fl[0] if isinstance(fl, list) and fl else {}
        registrar(r.returncode == 0 and f"creada · {cb2}" in r.stdout and not (home_bot / ".config").exists(),
                  "armar.py publica como bot con SUPABASE_URL, SUPABASE_ANON_KEY y BM_SECRET en el entorno", r.stderr or r.stdout)
        sesion_bot = f.get("session_id") if f else None
        registrar(not (home_bot / ".cache" / "botonera" / "sesiones" / "bot-por-env").exists(),
                  "una sesión bot- no deja la marca que despierta al hook entregar.py", str(sesion_bot))
        r = py("armar.py", "--publicar", str(ruta_c), str(tmp / "campos2.html"), entorno=entorno_bot)
        registrar(r.returncode == 1 and "solo publica claves que empiezan con bot-" in r.stderr,
                  "armar.py como bot no publica una clave que no es suya: falla en la validación local", r.stderr + r.stdout)
        proc = subprocess.Popen([sys.executable, str(skill / "esperar.py"), cb2, "--cada", "1"], env=entorno_bot,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(2)
        respuesta_b = f"/botonera respuesta · {cb2}\n1. va · Subir el precio de los envíos → Subir el envío"
        rpc("bm_decidir_pin", {"p_token": token, "p_clave": cb2, "p_respuesta": respuesta_b})
        try:
            out_b, err_b = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            out_b, err_b = proc.communicate()
        registrar(proc.returncode == 0 and out_b.strip() == respuesta_b, "esperar.py como bot recibe la respuesta de su tanda", f"rc={proc.returncode} {out_b[:150]!r} {err_b[:150]!r}")
        py("marcar.py", cb2, "aplicada", "hecho", entorno=entorno_bot)

        r = sql("delete from public.bm_config where k = 'bot_secret_sha256';")
        st, res = rpc("bm_pendientes", {"p_secret": bs, "p_horas": 0})
        registrar(r.returncode == 0 and st >= 400 and "secret invalido" in mensaje(res), "borrar la fila da de baja al bot", f"{st} {res}")


        # 6c. «Ya no aplica» (--reemplaza)
        print("\nYa no aplica (--reemplaza)")
        clave_ra, clave_rb = f"{clave}-ra", f"{clave}-rb"
        for cl in (clave_ra, clave_rb):
            d_r = copy.deepcopy(datos)
            d_r["clave"] = cl
            (tmp / f"{cl}.json").write_text(json.dumps(d_r, ensure_ascii=False), encoding="utf-8")
        r = py("armar.py", "--publicar", str(tmp / f"{clave_ra}.json"), str(tmp / "ra.html"))
        registrar(r.returncode == 0 and f"creada · {clave_ra}" in r.stdout, "se publica la tanda que después se reemplaza", r.stderr or r.stdout)
        r = py("armar.py", "--publicar", "--reemplaza", f"{clave_ra}#2:1", str(tmp / f"{clave_rb}.json"), str(tmp / "rb.html"))
        registrar(r.returncode == 0 and "ya no aplica" in r.stdout and clave_rb in r.stdout,
                  "armar.py --publicar --reemplaza publica la nueva y marca la card vieja", r.stderr or r.stdout)
        st, fl = rpc("bm_fila", {"p_token": token, "p_clave": clave_ra})
        f = fl[0] if isinstance(fl, list) and fl else {}
        its_ra = (f.get("datos") or {}).get("items", [])
        st, lista_r = rpc("bm_lista", {"p_token": token})
        n_act = next((x.get("n_items") for x in lista_r if x.get("clave") == clave_ra), None) if isinstance(lista_r, list) else None
        registrar(len(its_ra) == 4 and its_ra[1].get("reemplazada_por") == f"{clave_rb}#1" and n_act == 3,
                  "la card queda marcada reemplazada_por y n_items baja a las activas", f"items={len(its_ra)} marca={its_ra[1].get('reemplazada_por') if len(its_ra) > 1 else None} n_items={n_act}")
        st, res = rpc("bm_reemplazar", {"p_secret": secreto, "p_clave": clave_ra, "p_n": 2, "p_por": f"{clave_rb}#1"})
        registrar(st == 200 and res == "reemplazada:3", "marcar dos veces la misma card no cambia nada (idempotente)", f"{st} {res}")
        st, res = rpc("bm_reemplazar", {"p_secret": secreto, "p_clave": clave_ra, "p_n": 99, "p_por": f"{clave_rb}#1"})
        registrar(st == 200 and res == "sin_card", "una card que no existe devuelve sin_card", f"{st} {res}")
        st, res = rpc("bm_reemplazar", {"p_secret": secreto, "p_clave": "clave-que-no-existe", "p_n": 1, "p_por": f"{clave_rb}#1"})
        registrar(st == 200 and res == "no_existe", "una tanda que no existe devuelve no_existe", f"{st} {res}")
        st, res = rpc("bm_reemplazar", {"p_secret": secreto, "p_clave": clave_ra, "p_n": 1, "p_por": f"{clave_ra}#1"})
        registrar(st >= 400 and "no se reemplaza a sí misma" in mensaje(res), "una tanda no se reemplaza a sí misma", f"{st} {res}")
        r = py("armar.py", "--reemplaza", f"{clave_ra}#1", str(tmp / f"{clave_rb}.json"), str(tmp / "rb.html"))
        registrar(r.returncode != 0 and "solo va con --publicar" in (r.stderr + r.stdout), "--reemplaza sin --publicar se rechaza", r.stderr + r.stdout)
        st, res = rpc("bm_decidir_pin", {"p_token": token, "p_clave": clave_rb, "p_respuesta": f"/decisiones respuesta · {clave_rb}\n1. va"})
        registrar(st >= 400 and "respuesta invalida" in mensaje(res), "bm_decidir_pin rechaza el prefijo «/decisiones respuesta»", f"{st} {res}")
        rpc("bm_decidir_pin", {"p_token": token, "p_clave": clave_ra, "p_respuesta": f"/botonera respuesta · {clave_ra}\n1. va"})
        st, res = rpc("bm_reemplazar", {"p_secret": secreto, "p_clave": clave_ra, "p_n": 3, "p_por": f"{clave_rb}#1"})
        registrar(st == 200 and str(res).startswith("ya_decidida:"), "una tanda ya decidida no se toca", f"{st} {res}")
        # publicar contra un servidor que no responde sale ≠ 0
        entorno_caido = dict(env, HOME=str(tmp / "home-caido"), SUPABASE_URL="http://127.0.0.1:9", SUPABASE_ANON_KEY=key, BM_SECRET=secreto)
        (tmp / "home-caido").mkdir(exist_ok=True)
        r = py("armar.py", "--publicar", str(tmp / f"{clave_rb}.json"), str(tmp / "caido.html"), entorno=entorno_caido)
        registrar(r.returncode == 1 and "falló" in r.stderr, "armar.py --publicar con la red caída sale con 1", f"rc={r.returncode} {r.stderr[:200]}")
        py("marcar.py", clave_ra, "archivada", "fin de la prueba")
        py("marcar.py", clave_rb, "archivada", "fin de la prueba")

        # 6d. validar: textarea, revisión, detalle, intro y fyi
        print("\nTipos de card nuevos")
        r = py("armar.py", "--html", str(json_path), str(tmp / "tipos.html"))
        registrar(r.returncode == 0, "textarea, revisión, detalle, intro y fyi pasan validar (tests/ejemplo.json)", r.stderr or r.stdout)
        r = armar_variante("rev-vacia", lambda d: d["items"][3].pop("link"), ("--html",))
        registrar(r.returncode == 1 and "revisión sin nada para mirar" in r.stderr, "una revisión sin imagen ni link se rechaza", r.stderr)
        r = armar_variante("rev-reco", lambda d: d["items"][3].__setitem__("reco", "va"), ("--html",))
        registrar(r.returncode == 1 and "una revisión no lleva" in r.stderr, "una revisión con reco se rechaza", r.stderr)
        r = armar_variante("rev-http", lambda d: d["items"][3].__setitem__("link", "http://ejemplo.com"), ("--html",))
        registrar(r.returncode == 1 and "URL https" in r.stderr, "el link de una revisión tiene que ser https", r.stderr)
        r = armar_variante("ta-larga", lambda d: d["items"][2]["campos"][0].__setitem__("valor", "x" * 3001), ("--html",))
        registrar(r.returncode == 1 and "textarea" in r.stderr and "3000" in r.stderr, "un textarea de más de 3000 caracteres se rechaza", r.stderr)
        r = armar_variante("ta-salto", lambda d: d["items"][2]["campos"][0].__setitem__("valor", "uno ⏎ dos"), ("--html",))
        registrar(r.returncode == 1 and "⏎" in r.stderr, "un textarea con el marcador ⏎ se rechaza", r.stderr)
        r = armar_variante("detalle-largo", lambda d: d["items"][1].__setitem__("detalle", " ".join(["palabra"] * 61)), ("--html",))
        registrar(r.returncode == 1 and "'detalle' tiene 61 palabras" in r.stderr, "un detalle de más de 60 palabras se rechaza", r.stderr)
        r = armar_variante("intro-texto", lambda d: d.__setitem__("intro", "un texto suelto"), ("--html",))
        registrar(r.returncode == 1 and "'intro' tiene que ser una lista" in r.stderr, "una intro que no es lista se rechaza", r.stderr)
        r = armar_variante("fyi-lista", lambda d: d.__setitem__("fyi", ["una línea"]), ("--html",))
        registrar(r.returncode == 1 and "'fyi' tiene que ser un objeto" in r.stderr, "un fyi que no es objeto se rechaza", r.stderr)
        html_tipos = (tmp / "tipos.html").read_text(encoding="utf-8")
        registrar("El agente recomienda" in html_tipos and "Si no decidís" in html_tipos and "CLAUDE recomienda" not in html_tipos and "recomienda CLAUDE" not in html_tipos,
                  "la plantilla usa los rótulos «El agente recomienda» y «Si no decidís»", "")
        r = py("armar.py", "--inline", str(json_path), str(tmp / "tipos-inline.html"))
        inline = (tmp / "tipos-inline.html").read_text(encoding="utf-8") if (tmp / "tipos-inline.html").exists() else ""
        registrar(r.returncode == 0 and "REVISIÓN" in inline and "El agente recomienda" in inline, "el widget inline arma la card de revisión", r.stderr or r.stdout)

        # 6e. vuelo: vuelo.py -> bm_seguimiento
        print("\nVuelo y Sesiones")
        env_vuelo = dict(env, BM_SESSION_ID="vuelo-prueba-1")
        r = py("vuelo.py", "anotar", "Armo el reporte", "Revisar las cifras", "--titulo", "Reporte de prueba", entorno=env_vuelo)
        registrar(r.returncode == 0 and "anotado" in r.stdout, "vuelo.py anotar escribe la fila de la sesión", r.stderr or r.stdout)
        st, seg = rpc("bm_seguimiento", {"p_token": token})
        fila_v = next((v for v in (seg.get("vuelo") or []) if v.get("session_id") == "vuelo-prueba-1"), {}) if isinstance(seg, dict) else {}
        registrar(st == 200 and set(seg) == {"vuelo", "pedidos", "escucha_at", "activos"} and seg.get("pedidos") == []
                  and seg.get("escucha_at") is None and seg.get("activos") == 0,
                  "bm_seguimiento devuelve vuelo, pedidos, escucha_at y activos (la forma que lee la web)", f"{st} {str(seg)[:200]}")
        registrar(set(fila_v) == {"session_id", "titulo", "que_hace", "proximo", "estado", "updated_at", "desde"}
                  and fila_v.get("que_hace") == "Armo el reporte" and fila_v.get("proximo") == "Revisar las cifras"
                  and fila_v.get("titulo") == "Reporte de prueba" and fila_v.get("estado") == "trabajando",
                  "cada elemento de vuelo trae los siete campos de siempre", str(fila_v))
        py("vuelo.py", "anotar", "Espero tu respuesta", "Seguir con la tanda", "--estado", "esperando", entorno=env_vuelo)
        st, seg = rpc("bm_seguimiento", {"p_token": token})
        fila_v = next((v for v in (seg.get("vuelo") or []) if v.get("session_id") == "vuelo-prueba-1"), {})
        registrar(fila_v.get("estado") == "esperando" and fila_v.get("que_hace") == "Espero tu respuesta", "anotar de nuevo actualiza la misma fila", str(fila_v))
        st, res = rpc("bm_seguimiento", {"p_token": "token-falso"})
        registrar(st >= 400 and "token invalido" in mensaje(res), "bm_seguimiento con token falso se rechaza", f"{st} {res}")
        st, res = rpc("bm_vuelo_anotar", {"p_secret": "secreto-falso", "p_session_id": "x", "p_titulo": "x", "p_que_hace": "x", "p_proximo": "x"})
        registrar(st >= 400 and "secret invalido" in mensaje(res), "bm_vuelo_anotar con secreto equivocado se rechaza", f"{st} {res}")
        r = py("vuelo.py", "cerrar", entorno=env_vuelo)
        st, seg = rpc("bm_seguimiento", {"p_token": token})
        registrar(r.returncode == 0 and not any(v.get("session_id") == "vuelo-prueba-1" for v in (seg.get("vuelo") or [])),
                  "vuelo.py cerrar saca la sesión de En vuelo", r.stderr or r.stdout)
        r = py("vuelo.py", "anotar", "x", "y", "--seco", entorno=env_vuelo)
        registrar(r.returncode == 0 and "bm_vuelo_anotar" in r.stdout and "secret" not in r.stdout.lower(), "vuelo.py --seco no llama a la red ni imprime el secret", r.stdout)
        st, res = rpc("bm_archivar_pin", {"p_token": token, "p_clave": clave_ra})
        registrar(st == 200 and isinstance(res, dict) and res.get("cambiado") is False, "bm_archivar_pin sobre una tanda ya archivada no cambia nada", f"{st} {res}")
        st, res = rpc("bm_archivar_pin", {"p_token": "token-falso", "p_clave": clave_ra})
        registrar(st >= 400 and "token invalido" in mensaje(res), "bm_archivar_pin con token falso se rechaza", f"{st} {res}")
        st, tr = rpc("bm_trabadas", {"p_secret": secreto, "p_horas": 0})
        registrar(st == 200 and isinstance(tr, list), "bm_trabadas devuelve una lista", f"{st} {str(tr)[:120]}")

        # 6f. obstáculos: obstaculo.py -> bm_acciones_lista -> bm_accion_hecha -> bm_obstaculos_resueltos -> bm_obstaculo_llevado
        print("\nBloqueos: obstáculos")
        sql("delete from public.bm_obstaculos;")
        r = py("obstaculo.py", "--titulo", "Iniciá sesión en el panel de ejemplo", "--link", "https://ejemplo.com/panel",
               "--frena", "el reporte semanal", "--por-que", "pide un login tuyo", "--retoma", "corro el reporte", "--de", "reportes")
        m_ob = re.search(r"#(\d+)", r.stdout)
        registrar(r.returncode == 0 and "publicado" in r.stdout and m_ob, "obstaculo.py publica un obstáculo", r.stderr or r.stdout)
        id_ob = int(m_ob.group(1)) if m_ob else 0
        r = py("obstaculo.py", "--titulo", "Iniciá sesión en el panel de ejemplo", "--link", "https://ejemplo.com/panel")
        registrar(r.returncode == 0 and "ya había uno abierto" in r.stdout, "el mismo título abierto no se publica dos veces", r.stderr or r.stdout)
        r = py("obstaculo.py", "--titulo", "Sin dónde")
        registrar(r.returncode == 1 and "falta el dónde" in r.stderr, "sin link ni comando se rechaza", r.stderr)
        r = py("obstaculo.py", "--titulo", "Link malo", "--link", "http://ejemplo.com")
        registrar(r.returncode == 1 and "https" in r.stderr, "un link http se rechaza", r.stderr)
        st, res = rpc("bm_obstaculo_publicar", {"p_secret": secreto, "p_titulo": "Link con espacios", "p_por_que": "", "p_de": "", "p_frena": "",
                                                "p_link": "https://ejemplo.com/a b", "p_comando": ""})
        registrar(st >= 400 and "link invalido" in mensaje(res), "el servidor rechaza un link con espacios", f"{st} {res}")
        r = py("obstaculo.py", "--titulo", "Pegá este comando", "--comando", "echo hola", "--seco")
        registrar(r.returncode == 0 and "bm_obstaculo_publicar" in r.stdout, "obstaculo.py --seco no publica nada", r.stdout)
        st, lst = rpc("bm_acciones_lista", {"p_token": token})
        its_o = lst.get("items") if isinstance(lst, dict) else []
        it_o = next((x for x in its_o if x.get("ref") == str(id_ob)), {})
        claves_o = {"origen", "ref", "titulo", "por_que", "de", "fecha", "frena", "link", "comando", "estado", "comentario"}
        registrar(st == 200 and set(lst) == {"items"} and len(its_o) == 1 and set(it_o) == claves_o and it_o.get("origen") == "item"
                  and it_o.get("estado") == "abierta" and it_o.get("frena") == "el reporte semanal" and it_o.get("de") == "reportes"
                  and it_o.get("link") == "https://ejemplo.com/panel",
                  "bm_acciones_lista devuelve {items:[…]} con los once campos de siempre", f"{st} {str(lst)[:300]}")
        st, res = rpc("bm_acciones_lista", {"p_token": "token-falso"})
        registrar(st >= 400 and "token invalido" in mensaje(res), "bm_acciones_lista con token falso se rechaza", f"{st} {res}")
        st, res = rpc("bm_accion_marcar", {"p_token": token, "p_origen": "item", "p_ref": str(id_ob), "p_estado": "comentada", "p_comentario": ""})
        registrar(st >= 400 and "falta comentario" in mensaje(res), "Comentar sin comentario se rechaza", f"{st} {res}")
        st, res = rpc("bm_accion_marcar", {"p_token": token, "p_origen": "item", "p_ref": str(id_ob), "p_estado": "comentada", "p_comentario": "Lo hago a la tarde"})
        registrar(st == 200 and res.get("estado") == "comentada" and res.get("comentario") == "Lo hago a la tarde" and res.get("ref") == str(id_ob),
                  "Comentar deja la marca comentada", f"{st} {res}")
        st, res = rpc("bm_accion_marcar", {"p_token": token, "p_origen": "item", "p_ref": str(id_ob), "p_estado": "no_puedo", "p_comentario": ""})
        registrar(st == 200 and res.get("estado") == "no_puedo", "«No puedo» no exige comentario", f"{st} {res}")
        st, res = rpc("bm_accion_marcar", {"p_token": token, "p_origen": "item", "p_ref": str(id_ob), "p_estado": "comentada", "p_comentario": "Sigo sin poder"})
        registrar(st == 200 and res.get("estado") == "no_puedo" and res.get("comentario") == "Sigo sin poder", "Comentar no pisa un «No puedo»", f"{st} {res}")
        st, rs = rpc("bm_obstaculos_resueltos", {"p_secret": secreto})
        registrar(st == 200 and any(x.get("id") == id_ob and x.get("estado") == "no_puedo" and x.get("retoma") == "corro el reporte" for x in rs),
                  "bm_obstaculos_resueltos lista el «No puedo» con la pista de retomar", f"{st} {str(rs)[:200]}")
        st, res = rpc("bm_accion_marcar", {"p_token": token, "p_origen": "inbox", "p_ref": str(id_ob), "p_estado": "no_puedo", "p_comentario": ""})
        registrar(st >= 400 and "origen invalido" in mensaje(res), "un origen que no es «item» se rechaza", f"{st} {res}")
        st, res = rpc("bm_accion_hecha", {"p_token": token, "p_origen": "item", "p_ref": str(id_ob), "p_comentario": "Ya inicié sesión"})
        registrar(st == 200 and res == {"resultado": "en_cola"}, "bm_accion_hecha (Listo) anota el obstáculo como resuelto", f"{st} {res}")
        st, lst = rpc("bm_acciones_lista", {"p_token": token})
        registrar(st == 200 and lst.get("items") == [], "un obstáculo con Listo sale de la lista", f"{st} {str(lst)[:200]}")
        st, res = rpc("bm_accion_hecha", {"p_token": token, "p_origen": "item", "p_ref": str(id_ob), "p_comentario": ""})
        registrar(st == 200 and res == {"resultado": "ya no esta trabado"}, "Listo dos veces devuelve «ya no esta trabado»", f"{st} {res}")
        st, res = rpc("bm_accion_marcar", {"p_token": token, "p_origen": "item", "p_ref": str(id_ob), "p_estado": "no_puedo", "p_comentario": ""})
        registrar(st >= 400 and "ya no esta trabado" in mensaje(res), "marcar un obstáculo ya resuelto se rechaza", f"{st} {res}")
        st, rs = rpc("bm_obstaculos_resueltos", {"p_secret": secreto})
        ob_r = next((x for x in rs if x.get("id") == id_ob), {}) if isinstance(rs, list) else {}
        registrar(st == 200 and ob_r.get("estado") == "hecho" and "Ya inicié sesión" in ob_r.get("comentario", ""),
                  "bm_obstaculos_resueltos trae el obstáculo hecho con su comentario", f"{st} {str(rs)[:200]}")
        r = py("pendientes.py", "--horas", "0")
        registrar(r.returncode == 0 and "obstáculos resueltos" in r.stdout and "Iniciá sesión en el panel de ejemplo" in r.stdout and f"#{id_ob}" in r.stdout,
                  "pendientes.py suma la línea de obstáculos resueltos", r.stdout + r.stderr)
        r = py("obstaculo.py", "--llevado", str(id_ob))
        registrar(r.returncode == 0 and "recogido" in r.stdout, "obstaculo.py --llevado recoge el obstáculo", r.stdout + r.stderr)
        st, rs = rpc("bm_obstaculos_resueltos", {"p_secret": secreto})
        registrar(st == 200 and rs == [], "un obstáculo recogido no vuelve a salir en resueltos", f"{st} {rs}")
        st, res = rpc("bm_obstaculo_llevado", {"p_secret": secreto, "p_id": id_ob})
        registrar(st == 200 and res.get("llevado") is False, "recoger dos veces devuelve llevado=false", f"{st} {res}")
        for nombre, cuerpo in (("bm_obstaculos_resueltos", {}), ("bm_obstaculo_llevado", {"p_id": 1})):
            st, res = rpc(nombre, dict(cuerpo, p_secret="secreto-falso"))
            registrar(st >= 400 and "secret invalido" in mensaje(res), f"{nombre} con secreto equivocado se rechaza", f"{st} {res}")
        st, res = http("GET", f"{url}/rest/v1/bm_obstaculos?select=titulo", key)
        registrar((st in (401, 403)) or (st == 200 and res == []), "la clave pública sola no puede leer la tabla bm_obstaculos", f"{st} {str(res)[:120]}")
        sql("delete from public.bm_obstaculos;")

        # 6g. avisos: un solo push por ráfaga (bm_avisos_tick con p_solo_prueba)
        print("\nAvisos por ráfaga")
        puso_vapid = sql("select count(*) from public.bm_config where k = 'vapid_publica';").stdout.strip() == "0"
        if puso_vapid:
            sql("insert into public.bm_config (k, v) values ('vapid_publica', 'prueba') on conflict (k) do nothing;")
        sql("insert into public.bm_push (endpoint, p256dh, auth) values ('https://prueba.invalid/avisos', 'x', 'x') on conflict (endpoint) do nothing;")
        sql("delete from public.bm_config where k = 'aviso_intento'; delete from public.botoneras where clave like 'prueba-avisos-%';")
        # las 12 del mediodía de hoy en la zona de la base: así la franja de silencio no depende de la hora en que corra la prueba
        BASE = "((date_trunc('day', now() at time zone public.bm_zona()) + interval '12 hours') at time zone public.bm_zona())"

        def tick(intervalo):
            return sql(f"select public.bm_avisos_tick({BASE} + interval '{intervalo}', true);").stdout.strip()

        def tanda_aviso(sufijo, minutos):
            cl = f"prueba-avisos-{sufijo}"
            rpc("bm_publicar", {"p_secret": secreto, "p_clave": cl, "p_session_id": None, "p_sesion_titulo": None, "p_skill": "botonera",
                                "p_proyecto": None, "p_titulo": f"Aviso de prueba {sufijo}", "p_n_items": 1,
                                "p_datos": {"items": []}, "p_html": "<html></html>"})
            sql(f"update public.botoneras set created_at = {BASE} + interval '{minutos} minutes' where clave = '{cl}';")

        tanda_aviso("a", 0)
        tanda_aviso("b", 1)
        res_t = tick("1 minute 30 seconds")
        registrar(res_t == "esperando 2", "la ráfaga sigue (la última entró hace menos de 2 minutos): se espera", res_t)
        res_t = tick("3 minutes")
        registrar(res_t == "avisado 2", "la ráfaga terminó (2 minutos sin entradas): un solo aviso por las dos tandas", res_t)
        res_t = tick("4 minutes")
        registrar(res_t == "reintento_espera 2", "las mismas tandas no se vuelven a mandar antes de 5 minutos", res_t)
        res_t = tick("9 minutes")
        registrar(res_t == "avisado 2", "pasados los 5 minutos del reintento, se vuelve a mandar", res_t)
        sql("delete from public.bm_config where k = 'aviso_intento'; delete from public.botoneras where clave like 'prueba-avisos-%';")
        tanda_aviso("c", 0)
        tanda_aviso("d", 9)
        res_t = tick("10 minutes")
        registrar(res_t == "avisado 2", "tope: un goteo que ya espera 10 minutos avisa igual", res_t)
        res_t = tick("11 hours")
        registrar(res_t == "silencio", "a las 23 hay silencio (la franja usa la zona de la base)", res_t)
        cron = sql("select schedule from cron.job where jobname = 'bm-avisos-nuevas';").stdout.strip()
        registrar(cron == "* * * * *", "el cron de avisos corre cada minuto", cron)
        sql("delete from public.bm_config where k = 'aviso_intento'; delete from public.botoneras where clave like 'prueba-avisos-%';"
            " delete from public.bm_push where endpoint = 'https://prueba.invalid/avisos';")
        if puso_vapid:
            sql("delete from public.bm_config where k = 'vapid_publica';")

        # 7. el PIN se bloquea tras 10 fallos y pin.py desbloquear lo abre
        print("\nBloqueo del PIN (temporal y creciente)")
        sql("update public.bm_config set v = '0' where k in ('pin_fallos', 'pin_escalon'); update public.bm_config set v = 'false' where k = 'pin_bloqueado';"
            " update public.bm_config set v = '' where k = 'pin_bloqueo_hasta';")

        def fallar_diez():
            ultimo = None
            for _ in range(10):
                ultimo = rpc("bm_entrar", {"p_pin": "0000" if PIN != "0000" else "9999"})[1]
            return ultimo

        def vencer_bloqueo():
            sql("update public.bm_config set v = (now() - interval '1 minute')::text where k = 'pin_bloqueo_hasta';")

        res = fallar_diez()
        registrar(isinstance(res, dict) and res.get("motivo") == "bloqueado" and res.get("ok") is False, "10 PIN malos seguidos bloquean la entrada", str(res))
        registrar(isinstance(res, dict) and 880 <= (res.get("espera_seg") or 0) <= 900 and res.get("hasta"),
                  "el primer bloqueo dura 15 minutos y la respuesta trae hasta y espera_seg", str(res))
        res = rpc("bm_entrar", {"p_pin": PIN})[1]
        registrar(isinstance(res, dict) and res.get("ok") is False and res.get("motivo") == "bloqueado" and "token" not in res,
                  "bloqueada, ni el PIN correcto entra", str(res))
        e = rpc("bm_estado_pin", {"p_secret": secreto})[1]
        registrar(isinstance(e, dict) and e.get("bloqueado") is True and e.get("bloqueado_hasta") and e.get("escalon") == 1
                  and {"puesto", "fallos", "bloqueado", "sesiones"} <= set(e),
                  "bm_estado_pin dice bloqueado, hasta cuándo y el escalón, y conserva sus campos de siempre", str(e))
        r = py("pin.py", "estado")
        registrar(r.returncode == 0 and "bloqueado=sí" in r.stdout, "pin.py estado sigue leyendo bm_estado_pin", r.stdout + r.stderr)
        vencer_bloqueo()
        e = rpc("bm_estado_pin", {"p_secret": secreto})[1]
        registrar(isinstance(e, dict) and e.get("bloqueado") is False, "con el reloj adelantado el bloqueo vencido ya no figura como bloqueado", str(e))
        res = rpc("bm_entrar", {"p_pin": PIN})[1]
        registrar(isinstance(res, dict) and res.get("ok") is True, "vencido el bloqueo, el PIN correcto entra", str(res))
        e = rpc("bm_estado_pin", {"p_secret": secreto})[1]
        registrar(isinstance(e, dict) and e.get("escalon") == 0 and e.get("fallos") == 0 and e.get("bloqueado") is False,
                  "un ingreso correcto pone el contador y el escalón en cero", str(e))
        # segunda tanda sin ingreso correcto de por medio: la espera se duplica
        fallar_diez()
        vencer_bloqueo()
        res = fallar_diez()
        registrar(isinstance(res, dict) and res.get("motivo") == "bloqueado" and 1780 <= (res.get("espera_seg") or 0) <= 1800,
                  "la segunda tanda de 10 fallos bloquea el doble (30 minutos)", str(res))
        vencer_bloqueo()
        res = fallar_diez()
        registrar(isinstance(res, dict) and 3580 <= (res.get("espera_seg") or 0) <= 3600, "la tercera tanda bloquea 60 minutos", str(res))
        sql("update public.bm_config set v = '20' where k = 'pin_escalon';")
        vencer_bloqueo()
        res = fallar_diez()
        registrar(isinstance(res, dict) and res.get("espera_seg") == 86400, "la espera tiene tope de 24 horas", str(res))
        r = py("pin.py", "desbloquear")
        registrar(r.returncode == 0 and "desbloqueado" in r.stdout, "pin.py desbloquear levanta el bloqueo en el acto", r.stdout + r.stderr)
        e = rpc("bm_estado_pin", {"p_secret": secreto})[1]
        registrar(isinstance(e, dict) and e.get("bloqueado") is False and e.get("escalon") == 0, "desbloquear pone el escalón en cero", str(e))
        res = rpc("bm_entrar", {"p_pin": PIN})[1]
        registrar(isinstance(res, dict) and res.get("ok") is True, "después de desbloquear el PIN correcto entra", str(res))
        r = py("pin.py", "poner", entorno={**env, "BM_PIN_PRUEBA": "4321"})
        st, res = rpc("bm_lista", {"p_token": token})
        registrar(r.returncode == 0 and st >= 400 and "token invalido" in mensaje(res), "poner un PIN nuevo cierra las sesiones viejas", f"{st} {res}")

    except Exception as ex:  # cualquier error inesperado es un FAIL, no un traceback mudo
        registrar(False, "la prueba terminó sin excepciones", f"{type(ex).__name__}: {ex}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        # install.sh reescribe web/config.js (no se versiona): lo dejamos como estaba.
        try:
            if web_config_antes is None:
                web_config.unlink(missing_ok=True)
            else:
                web_config.write_text(web_config_antes, encoding="utf-8")
        except OSError:
            pass
    return resumen()


def resumen():
    total = len(RESULTADOS)
    fallos = [n for ok, n, _ in RESULTADOS if not ok]
    print(f"\n{total - len(fallos)}/{total} chequeos pasaron.")
    if fallos:
        print("FAIL:")
        for n in fallos:
            print(f"  - {n}")
        return 1
    print("PASS: todo el loop anda (publicar, entrar con PIN, decidir, recibir y marcar).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

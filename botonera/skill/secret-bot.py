#!/usr/bin/env python3
"""Genera el secret «de bot» de la botonera. Corre UNA vez (o para rotar), en tu máquina.

Uso:
  python3 secret-bot.py            # crea ~/.config/botonera/env-bot y muestra el SQL con el HASH
  python3 secret-bot.py --rotar    # pisa un env-bot que ya existe (otro secret, otro hash)

Para qué sirve: un bot (un agente que no es tu sesión de Claude Code) puede publicar tandas y recibir tus respuestas
sin tener tu secret completo. El secret de bot solo trabaja con claves y session_id que empiezan con `bot-`:
no ve ni toca el resto de las tandas, ni el PIN, ni lista lo que está sin cerrar.

Qué hace:
  1. Genera un secret al azar (256 bits).
  2. Lo escribe SOLO en ~/.config/botonera/env-bot (chmod 600), junto con SUPABASE_URL y SUPABASE_ANON_KEY
     copiadas de ~/.config/botonera/env. Mismo formato que `env`: es el archivo que le pasás al bot
     (o sus tres claves como variables de entorno; maestro.py las lee si están las tres).
  3. Imprime el SQL para cargar el hash en `bm_config` (fila `bot_secret_sha256`). El secret NUNCA se imprime.

El hash es sha256 hex del secret, igual que `bm_check`/`bm_rol` en la base:
  encode(digest(p_secret, 'sha256'), 'hex').

NO ejecuta el SQL: lo corrés vos en el editor SQL de Supabase, después de aplicar las migraciones 20261106*.
Nunca va a un chat, a un log ni a un commit.
"""
import hashlib
import os
import secrets
import sys
from pathlib import Path

CARPETA = Path(os.path.expanduser("~/.config/botonera"))
ENV = CARPETA / "env"
ENV_BOT = CARPETA / "env-bot"


def leer_env():
    """SUPABASE_URL y SUPABASE_ANON_KEY del env de siempre (los únicos valores que se copian)."""
    try:
        texto = ENV.read_text(encoding="utf-8")
    except OSError:
        sys.exit(f"no encuentro {ENV}: sin ese archivo no sé la URL ni la anon key")
    cfg = {}
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        k, v = linea.split("=", 1)
        cfg[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("SUPABASE_URL", "SUPABASE_ANON_KEY"):
        if not cfg.get(k):
            sys.exit(f"a {ENV} le falta {k}")
    return cfg


def main():
    args = sys.argv[1:]
    if any(a not in ("--rotar",) for a in args):
        sys.exit("uso: python3 secret-bot.py [--rotar]")
    if ENV_BOT.exists() and "--rotar" not in args:
        sys.exit(f"{ENV_BOT} ya existe. Para pisarlo con otro secret: python3 secret-bot.py --rotar")
    cfg = leer_env()

    secreto = secrets.token_urlsafe(32)
    hash_hex = hashlib.sha256(secreto.encode("utf-8")).hexdigest()

    CARPETA.mkdir(parents=True, exist_ok=True)
    contenido = (
        "# Secret de BOT de la botonera (solo publica y recibe claves bot-). NO es el secret total.\n"
        f"SUPABASE_URL={cfg['SUPABASE_URL']}\n"
        f"SUPABASE_ANON_KEY={cfg['SUPABASE_ANON_KEY']}\n"
        f"BM_SECRET={secreto}\n"
    )
    # 0o600 desde la creación (no hay ventana con permisos abiertos). Se escribe a un temporal y se renombra.
    tmp = ENV_BOT.with_name(ENV_BOT.name + ".tmp")
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(contenido)
        os.chmod(tmp, 0o600)
        os.replace(tmp, ENV_BOT)
    finally:
        if tmp.exists():
            tmp.unlink()
    os.chmod(ENV_BOT, 0o600)

    print(f"Secret de bot escrito en {ENV_BOT} (chmod 600). No se imprime.")
    print()
    print("SQL para cargar el hash (en el editor SQL de Supabase, después de aplicar las migraciones 20261106*):")
    print()
    print("insert into public.bm_config (k, v)")
    print(f"values ('bot_secret_sha256', '{hash_hex}')")
    print("on conflict (k) do update set v = excluded.v;")
    print()
    print("Dónde poner el archivo en el servidor del bot:")
    print("  - copiá el contenido de ~/.config/botonera/env-bot a un archivo del servidor (por ejemplo")
    print("    /etc/botonera/env, permisos 600, solo legible por el usuario que corre el bot) o a su secret store;")
    print("  - apuntá el bot a ese archivo con la variable BM_ENV_FILE=/etc/botonera/env")
    print("    (o dale SUPABASE_URL, SUPABASE_ANON_KEY y BM_SECRET como variables de entorno: tienen que estar las tres);")
    print("  - el bot publica con BM_SESSION_ID=bot-<nombre> y claves bot-<algo>.")
    print("  - el archivo no va a un repo, a un chat ni a un log.")
    print("Rotar: python3 secret-bot.py --rotar + el SQL de arriba. Dar de baja a los bots: "
          "delete from public.bm_config where k = 'bot_secret_sha256';")


if __name__ == "__main__":
    main()

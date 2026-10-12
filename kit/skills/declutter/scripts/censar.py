#!/usr/bin/env python3
"""Censo de un target para declutter. MIDE Y AGRUPA. No dictamina.

    python3 censar.py <target> [--out censo.json]

Emite JSON a stdout (o a --out). Nunca escribe en el target.
"""
import argparse, hashlib, json, os, re, sys, time
from collections import defaultdict
from datetime import datetime, timedelta

# Nunca se recorre ni se propone nada de acá adentro.
DIRS_VEDADOS = {
    ".git", ".obsidian", "node_modules", "__pycache__", ".pytest_cache",
    ".venv", "venv", ".mypy_cache", ".ruff_cache", ".next", ".DS_Store",
    # Intocables del SKILL.md. Una invariante sin script que la chequee es una intencion.
    "backups", "archive", "ARCHIVE",
}
# Suma aca los archivos de identidad de tu sistema: los que definen como trabajas
# y nunca deberian moverse solos.
ARCHIVOS_VEDADOS = {
    "package-lock.json", "uv.lock", "poetry.lock", "yarn.lock", "bun.lockb",
    "Cargo.lock", "Gemfile.lock", "composer.lock", "pnpm-lock.yaml",
}
PATRON_VEDADO = re.compile(r"^(\.env|_declutter-\d{4}-\d{2}-\d{2})")
TEXTO = {".md",".txt",".py",".sh",".json",".yaml",".yml",".tsv",".csv",".html",".js",".ts",".css",".toml"}


def vedado(nombre):
    return (nombre in DIRS_VEDADOS or nombre in ARCHIVOS_VEDADOS
            or bool(PATRON_VEDADO.match(nombre)))


def md5(path, tope=200 * 1024 * 1024):
    if os.path.getsize(path) > tope:
        return None
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def recorrer(target):
    salida = []
    for raiz, dirs, archivos in os.walk(target):
        dirs[:] = sorted(d for d in dirs if not vedado(d))
        for a in sorted(archivos):
            if vedado(a) or a == ".DS_Store":
                continue
            p = os.path.join(raiz, a)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            salida.append(p)
    return salida


def detectar_perfil(target):
    if os.path.isfile(target):
        return "archivo-unico"
    hay = lambda n: os.path.exists(os.path.join(target, n))
    if hay(".git"):
        return "repo-codigo"
    if hay("SKILL.md"):
        return "skill"
    if hay("CLAUDE.md"):
        return "sb-proyecto"
    return "carpeta-suelta"


def en_vuelo(target, horas=48):
    """Subcarpetas de 1er nivel escritas hace poco, o con la fecha de hoy en el nombre."""
    if os.path.isfile(target):
        return []
    corte = time.time() - horas * 3600
    hoy = datetime.now().strftime("%Y-%m-%d")
    fuera = []
    for d in sorted(os.listdir(target)):
        full = os.path.join(target, d)
        if not os.path.isdir(full) or vedado(d):
            continue
        reciente = any(os.path.getmtime(p) > corte for p in recorrer(full)) if os.path.isdir(full) else False
        if reciente or hoy in d:
            fuera.append({"carpeta": d, "motivo": "fecha de hoy en el nombre" if hoy in d
                          else f"escrita hace menos de {horas} h"})
    return fuera


def duplicados(paths):
    """Hashea SOLO lo que comparte tamaño exacto. Un duplicado byte-idéntico siempre lo comparte."""
    por_tam = defaultdict(list)
    for p in paths:
        try:
            por_tam[os.path.getsize(p)].append(p)
        except OSError:
            pass
    grupos = []
    for tam, cands in por_tam.items():
        if len(cands) < 2 or tam == 0:
            continue
        por_hash = defaultdict(list)
        for p in cands:
            h = md5(p)
            if h:
                por_hash[h].append(p)
        for h, iguales in por_hash.items():
            if len(iguales) > 1:
                grupos.append({"hash": h[:8], "bytes_c_u": tam, "n": len(iguales),
                               "recuperable": tam * (len(iguales) - 1),
                               "paths": sorted(iguales)})
    return sorted(grupos, key=lambda g: -g["recuperable"])


def procedencia(target, paths):
    """¿Algún script o SKILL.md del target nombra este patrón de archivo?

    Devuelve, por sufijo/patrón frecuente, quién lo menciona. NO concluye que sea basura:
    eso lo decide el agente leyendo lo que el generador hace con el archivo.
    """
    fuentes = [p for p in paths if p.endswith((".py", ".sh", ".js", ".ts")) or
               os.path.basename(p) in ("SKILL.md", "CLAUDE.md")]
    texto = {}
    for f in fuentes:
        try:
            texto[f] = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            pass
    patrones = defaultdict(int)
    for p in paths:
        n = os.path.basename(p)
        m = re.search(r"[-_]([a-z]{3,})\.[a-z0-9]+$", n)
        if m:
            patrones[m.group(1)] += 1
        if os.path.basename(os.path.dirname(p)).endswith("-recortes"):
            patrones["-recortes"] += 1
    salida = []
    for pat, n in sorted(patrones.items(), key=lambda kv: -kv[1]):
        if n < 5:
            continue
        quien = [os.path.relpath(f, target) for f, t in texto.items() if pat.strip("-") in t]
        salida.append({"patron": pat, "archivos": n,
                       "mencionado_en": quien,
                       "nota": "sin dueño declarado" if not quien else "revisar qué hace el generador"})
    return salida


def huerfanos(target, paths):
    """Archivos que nadie linkea ni nombra desde ningún texto del target."""
    corpus = ""
    for p in paths:
        if os.path.splitext(p)[1].lower() in TEXTO:
            try:
                corpus += open(p, encoding="utf-8", errors="ignore").read()
            except OSError:
                pass
    sueltos = []
    for p in paths:
        n = os.path.basename(p)
        if os.path.splitext(n)[1].lower() in TEXTO:
            continue
        if n not in corpus:
            sueltos.append(os.path.relpath(p, target))
    return sueltos


def clusters(target, paths):
    """Agrupa sospechosos por vecindad. Es una PISTA para el lector, no un veredicto."""
    por_carpeta = defaultdict(list)
    for p in paths:
        if os.path.splitext(p)[1].lower() in TEXTO:
            por_carpeta[os.path.dirname(p)].append(p)
    out = []
    for carpeta, ps in sorted(por_carpeta.items()):
        if len(ps) < 2:
            continue
        base = defaultdict(list)
        for p in ps:
            raiz = re.sub(r"[-_]?v?\d+$", "", os.path.splitext(os.path.basename(p))[0])
            base[raiz].append(os.path.relpath(p, target))
        for raiz, grupo in base.items():
            if len(grupo) > 1:
                out.append({"motivo": "nombres vecinos", "raiz": raiz, "paths": sorted(grupo)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--out")
    a = ap.parse_args()
    target = os.path.abspath(a.target)
    if not os.path.exists(target):
        sys.exit(f"no existe: {target}")

    paths = [target] if os.path.isfile(target) else recorrer(target)
    total = sum(os.path.getsize(p) for p in paths if os.path.exists(p))

    censo = {
        "target": target,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "perfil": detectar_perfil(target),
        "archivos": len(paths),
        "bytes": total,
        "mb": round(total / 1024 / 1024, 1),
        "trabajo_en_vuelo": en_vuelo(target),
        "duplicados_exactos": duplicados(paths),
        "procedencia": procedencia(target, paths),
        "huerfanos": huerfanos(target, paths)[:50],
        "clusters": clusters(target, paths)[:60],
        "nota": "Este censo MIDE Y AGRUPA. No dictamina. El veredicto lo pone el agente leyendo.",
    }
    txt = json.dumps(censo, ensure_ascii=False, indent=2)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(txt)
        print(f"censo -> {a.out}  ({censo['archivos']} archivos, {censo['mb']} MB, perfil {censo['perfil']})")
    else:
        print(txt)


if __name__ == "__main__":
    main()

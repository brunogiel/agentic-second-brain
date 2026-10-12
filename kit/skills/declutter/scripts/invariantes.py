#!/usr/bin/env python3
"""Gate de invariantes. Corre ANTES de proponer cualquier se va / tirar / se une /
se achica / se muda.

    python3 invariantes.py <archivo> [<archivo>...]            # inventaria
    python3 invariantes.py --mapeo mapeo.json                  # verifica y corta

Existe porque cuando partis un documento largo lo que se pierde no es el detalle: es la
guarda. El archivo queda mas corto y mas legible, y meses despues reaparece un bug que ya
estaba resuelto. El archivo de referencia se lleva el COMO, nunca el NO.
"""
import argparse, json, os, re, sys

SENAL = re.compile(
    r"(\bNO\b|\bnunca\b|\bsiempre\b|\bojo\b|ABORTAR|⚠|🔴|⛔|límite duro|limite duro"
    r"|no se toca|no borrar|jamás|jamas)", re.IGNORECASE)

# Un README que explica por que dos cosas se parecen ES una guarda.
EXPLICA_DUP = re.compile(
    r"(a propósito|a proposito|intencional|ciego|no hace trampa|duplicad|copia|misma imagen"
    r"|mismo archivo|por eso están|por eso estan|anónimo|anonimo)", re.IGNORECASE)


TEXTO = {".md",".txt",".py",".sh",".json",".yaml",".yml",".tsv",".csv",".html",
         ".js",".ts",".css",".toml",".cfg",".ini",""}


def es_texto(path):
    return os.path.splitext(path)[1].lower() in TEXTO


def invariantes_de(path):
    if not es_texto(path):
        return []          # un binario no declara invariantes: las declara su README
    try:
        lineas = open(path, encoding="utf-8", errors="ignore").read().splitlines()
    except OSError:
        return []
    out = []
    for i, l in enumerate(lineas, 1):
        if SENAL.search(l) and len(l.strip()) > 12:
            out.append({"archivo": path, "linea": i, "texto": l.strip()[:220]})
    return out


def duplicado_explicado(path, niveles=3):
    """Busca un README/LEEME que explique por que hay copias.

    Sube hasta `niveles` carpetas: un set de evaluacion suele guardar sus copias en una
    subcarpeta y el README que explica por que son copias vive un nivel arriba. Buscar
    solo en la carpeta del archivo deja pasar justo el caso que el gate existe para frenar.
    """
    hallazgos = []
    carpeta = os.path.dirname(os.path.abspath(path))
    for _ in range(niveles + 1):
        hallazgos += _leer_readmes(carpeta)
        padre = os.path.dirname(carpeta)
        if padre == carpeta:
            break
        carpeta = padre
    return hallazgos


def _leer_readmes(carpeta):
    hallazgos = []
    for nombre in os.listdir(carpeta) if os.path.isdir(carpeta) else []:
        if not re.match(r"(README|LEEME|LEER)", nombre, re.IGNORECASE):
            continue
        p = os.path.join(carpeta, nombre)
        try:
            txt = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for parrafo in txt.split("\n\n"):
            if EXPLICA_DUP.search(parrafo):
                hallazgos.append({"archivo": p, "tipo": "duplicado-explicado",
                                  "texto": " ".join(parrafo.split())[:300]})
                break
    return hallazgos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archivos", nargs="*")
    ap.add_argument("--mapeo", help="JSON [{invariante, destino}] para verificar")
    a = ap.parse_args()

    if a.mapeo:
        filas = json.load(open(a.mapeo, encoding="utf-8"))
        sin_destino = [f for f in filas if not (f.get("destino") or "").strip()]
        for f in sin_destino:
            print(f"SIN DESTINO -> {f.get('invariante','')[:160]}", file=sys.stderr)
        if sin_destino:
            print(f"\nGATE CERRADO: {len(sin_destino)} de {len(filas)} invariantes sin destino "
                  f"nombrado. Esos items NO entran a la botonera.", file=sys.stderr)
            sys.exit(1)
        print(f"GATE ABIERTO: {len(filas)}/{len(filas)} invariantes mapeadas a un destino.")
        return

    if not a.archivos:
        sys.exit("pasá archivos, o --mapeo")

    todas, dups = [], []
    for p in a.archivos:
        todas += invariantes_de(p)
        dups += duplicado_explicado(p)
    vistos, unicos = set(), []
    for d in dups:
        if d["archivo"] not in vistos:
            vistos.add(d["archivo"])
            unicos.append(d)

    print(json.dumps({
        "invariantes": todas,
        "duplicados_explicados": unicos,
        "total": len(todas) + len(unicos),
        "siguiente_paso": "Mapear CADA una a un destino nombrado y verificar con --mapeo. "
                          "Una invariante sin destino bloquea su item.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

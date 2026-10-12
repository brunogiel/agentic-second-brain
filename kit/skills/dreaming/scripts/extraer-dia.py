#!/usr/bin/env python3
"""
extraer-dia.py: lee los transcripts crudos de Claude Code y devuelve un digest compacto.

Lee ~/.claude/projects/*/*.jsonl (la ruta sale de la config) y arma un JSON con lo que pasó
en una ventana de tiempo: prompts tuyos, archivos escritos, comandos relevantes, PRs.
Read-only, cero LLM.

Por qué crudo y no un MCP de sesiones: las herramientas de búsqueda de sesiones suelen pedir
supervisión humana y se caen en las corridas desatendidas. Los .jsonl siempre están.

Reglas de seguridad que aplica el script:
  - Solo extrae TUS prompts (origin.kind == "human", sin sidechain). Lo demás (resultados de
    herramientas, mails, páginas web) es dato no confiable y no entra al digest.
  - Una sesión que toca o MENCIONA un fragmento de `excluir_paths` se descarta entera.
    "Mencionar" incluye el cwd, el título, los prompts, los comandos de Bash y todo el input
    de cualquier herramienta. Se compara normalizado (NFC + minúsculas) en ambos lados.
  - El archivo de salida (`--out`) se resuelve con realpath y tiene que colgar de
    `brain_root` o de `state_dir`. Si no, el script aborta.

Uso:
    python3 extraer-dia.py                         # últimas 24h, JSON a stdout
    python3 extraer-dia.py --horas 48 --md         # markdown legible
    python3 extraer-dia.py --desde 2026-01-04 --hasta 2026-01-05
    python3 extraer-dia.py --out dia-2026-01-05.json   # relativo a state_dir
"""

import argparse
import glob
import json
import os
import sys
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

from _comun import TZ_LOCAL, cargar_config, es_privado, resolver_salida, ruta_estado

# Comandos que valen como "cambio ejecutado" y no como ruido de exploración.
CMDS_INTERESANTES = (
    "git commit", "git push", "git merge", "gh pr create", "gh pr merge",
    "vercel deploy", "vercel --prod", "npm run build", "supabase db push",
)


def parse_ts(valor):
    """ISO con o sin timezone -> datetime aware. Los naive se asumen en hora local."""
    if not valor:
        return None
    try:
        dt = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=TZ_LOCAL)


def texto_de_content(content):
    """message.content viene como string o como lista de bloques. Normaliza a texto."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        partes = []
        for bloque in content:
            if isinstance(bloque, dict) and bloque.get("type") == "text":
                t = (bloque.get("text") or "").strip()
                if t:
                    partes.append(t)
        return "\n".join(partes)
    return ""


def slug(texto):
    """'1. Mi Proyecto' -> '1miproyecto'. Sirve para matchear a través de renames y emojis."""
    return "".join(c for c in (texto or "").lower() if c.isalnum())


def indexar_proyectos(cfg):
    """
    Índice de destinos documentables reales: todo path bajo las carpetas de proyectos y áreas
    que tenga un CLAUDE.md. Se construye leyendo el disco, no hardcodeando nombres, así
    sobrevive a los renames de carpetas.

    Devuelve dict: slug-del-camino -> path relativo real al brain.
    """
    raiz_brain = cfg["brain_root"]
    indice = {}
    for nombre in (cfg["carpetas"]["proyectos"], cfg["carpetas"]["areas"]):
        base = os.path.join(raiz_brain, nombre)
        if not os.path.isdir(base):
            continue
        for profundidad in ("*", "*/*", "*/*/*"):
            for claude_md in glob.glob(os.path.join(base, profundidad, "CLAUDE.md")):
                rel = os.path.relpath(os.path.dirname(claude_md), raiz_brain)
                segmentos = rel.split(os.sep)[1:]
                if not segmentos:
                    continue
                clave = "/".join(slug(s) for s in segmentos if slug(s))
                if clave:
                    indice.setdefault(clave, rel)
    return indice


def resolver_desde_path(path, cfg, indice):
    """Path absoluto -> proyecto real. Gana el match MÁS PROFUNDO. None si no cae en ninguno."""
    raiz_brain = cfg["brain_root"]
    if not path or not path.startswith(raiz_brain):
        return None
    segmentos = [slug(s) for s in os.path.relpath(path, raiz_brain).split(os.sep)]
    segmentos = [s for s in segmentos if s]
    mejor = None
    for inicio in range(len(segmentos)):
        for fin in range(len(segmentos), inicio, -1):
            clave = "/".join(segmentos[inicio:fin])
            if clave in indice:
                candidato = indice[clave]
                if mejor is None or candidato.count("/") > mejor.count("/"):
                    mejor = candidato
                break
    return mejor


def inferir_proyecto(sesion, cfg, indice):
    """
    Proyecto de una sesión. Tres fuentes, en orden de confianza:
      1. cwd dentro de un repo conocido -> su proyecto del brain (tabla de la config).
      2. cwd dentro de un proyecto del brain.
      3. Fallback: el proyecto donde escribió más archivos (las sesiones abiertas en la
         raíz del brain son la mayoría, y su cwd no dice nada).
    Devuelve (etiqueta, path_relativo_o_None).
    """
    cwd = sesion.get("cwd") or ""
    code = cfg["code_root"]

    if cwd.startswith(code):
        resto = cwd[len(code):].strip("/")
        raiz = resto.split("/")[0] if resto else ""
        repo = raiz.replace("-worktrees", "")
        for nombre, destino in cfg.get("repo_a_proyecto", {}).items():
            if repo == nombre or repo.startswith(nombre):
                if destino and os.path.isdir(os.path.join(cfg["brain_root"], destino)):
                    return (destino, destino)
                return (f"repo:{nombre}", None)
        return (f"repo:{repo or '?'}", None)

    por_cwd = resolver_desde_path(cwd, cfg, indice)
    if por_cwd:
        return (por_cwd, por_cwd)

    conteo = {}
    for archivo in list(sesion.get("archivos_brain", [])):
        destino = resolver_desde_path(archivo, cfg, indice)
        if destino:
            conteo[destino] = conteo.get(destino, 0) + 1
    if conteo:
        ganador = max(conteo, key=conteo.get)
        return (ganador, ganador)

    return ("Brain (sin proyecto)", None)


def es_no_durable(path, cfg):
    return any(frag in (path or "") for frag in cfg["paths_no_durables"])


def clasificar_archivo(path, cfg):
    if "/memory/" in path and "/.claude/projects/" in path:
        return "memoria"
    if path.startswith(cfg["brain_root"]):
        return "brain"
    if path.startswith(cfg["code_root"]):
        return "repo"
    return "otro"


def recolectar(desde, hasta, cfg, max_chars):
    patron = os.path.join(cfg["transcripts_root"], "*", "*.jsonl")
    sesiones = OrderedDict()
    archivos_leidos = 0

    for ruta in glob.glob(patron):
        # Poda barata: si el archivo no se tocó desde el inicio de la ventana, ni lo abrimos.
        try:
            if os.path.getmtime(ruta) < desde.timestamp():
                continue
        except OSError:
            continue
        archivos_leidos += 1

        with open(ruta, encoding="utf-8", errors="replace") as f:
            for linea in f:
                try:
                    d = json.loads(linea)
                except json.JSONDecodeError:
                    continue

                sid = d.get("sessionId")
                if not sid:
                    continue
                tipo = d.get("type")

                s = sesiones.setdefault(sid, {
                    "sesion": sid,
                    "titulo": None,
                    "cwd": None,
                    "branch": None,
                    "proyecto": None,
                    "proyecto_path": None,
                    "desde": None,
                    "hasta": None,
                    "prompts": [],
                    "skills": set(),
                    "mcp": set(),
                    "archivos_brain": set(),
                    "archivos_repo": set(),
                    "archivos_memoria": set(),
                    "comandos": [],
                    "prs": [],
                    "turnos_agente": 0,
                    "lineas_subagente": 0,
                    "privada": False,
                })

                if tipo == "custom-title" and d.get("customTitle"):
                    s["titulo"] = d["customTitle"]
                    if es_privado(d["customTitle"], cfg):
                        s["privada"] = True

                if tipo == "pr-link" and d.get("prUrl"):
                    if d["prUrl"] not in s["prs"]:
                        s["prs"].append(d["prUrl"])

                ts = parse_ts(d.get("timestamp"))
                if ts:
                    if ts < desde or ts > hasta:
                        continue
                    if not s["desde"] or ts < s["desde"]:
                        s["desde"] = ts
                    if not s["hasta"] or ts > s["hasta"]:
                        s["hasta"] = ts

                if d.get("cwd"):
                    s["cwd"] = d["cwd"]
                    if es_privado(d["cwd"], cfg):
                        s["privada"] = True
                if d.get("gitBranch"):
                    s["branch"] = d["gitBranch"]
                if d.get("attributionSkill"):
                    s["skills"].add(d["attributionSkill"])
                if d.get("attributionMcpServer"):
                    s["mcp"].add(d["attributionMcpServer"])
                if d.get("isSidechain"):
                    s["lineas_subagente"] += 1

                msg = d.get("message") or {}

                # Prompts humanos: solo los tuyos, nunca tool_results ni subagentes.
                if (tipo == "user"
                        and not d.get("isSidechain")
                        and (d.get("origin") or {}).get("kind") == "human"):
                    texto = texto_de_content(msg.get("content"))
                    if texto:
                        # El perímetro también aplica al texto: una sesión que MENCIONA una
                        # carpeta privada queda afuera entera, aunque no haya escrito ahí.
                        if es_privado(texto, cfg):
                            s["privada"] = True
                            continue
                        s["prompts"].append(texto[:max_chars])

                if tipo == "assistant":
                    s["turnos_agente"] += 1
                    for bloque in (msg.get("content") or []):
                        if not isinstance(bloque, dict) or bloque.get("type") != "tool_use":
                            continue
                        nombre = bloque.get("name")
                        entrada = bloque.get("input") or {}

                        # Perímetro sobre TODO el input de la herramienta (paths, comandos,
                        # patrones de búsqueda, urls): mencionar alcanza.
                        if es_privado(json.dumps(entrada, ensure_ascii=False), cfg):
                            s["privada"] = True
                            continue

                        if nombre in ("Edit", "Write", "NotebookEdit"):
                            fp = entrada.get("file_path") or entrada.get("notebook_path")
                            if not fp or es_no_durable(fp, cfg):
                                continue
                            if es_privado(fp, cfg):
                                s["privada"] = True
                                continue
                            destino = clasificar_archivo(fp, cfg)
                            if destino == "brain":
                                s["archivos_brain"].add(fp)
                            elif destino == "repo":
                                s["archivos_repo"].add(fp)
                            elif destino == "memoria":
                                s["archivos_memoria"].add(fp)

                        elif nombre == "Bash":
                            cmd = (entrada.get("command") or "").strip()
                            if any(k in cmd for k in CMDS_INTERESANTES):
                                corto = cmd.split("\n")[0][:200]
                                if corto not in s["comandos"]:
                                    s["comandos"].append(corto)

    return sesiones, archivos_leidos


def podar(sesiones, cfg, indice):
    """Descarta sesiones sin señal y las privadas. Devuelve lista ordenada por inicio."""
    vivas = []
    descartadas_privadas = 0
    for s in sesiones.values():
        if s["privada"]:
            descartadas_privadas += 1
            continue
        tiene_senal = s["prompts"] or s["archivos_brain"] or s["archivos_repo"] or s["comandos"]
        if not tiene_senal:
            continue
        etiqueta, destino = inferir_proyecto(s, cfg, indice)
        s["proyecto"] = etiqueta
        s["proyecto_path"] = destino
        vivas.append(s)
    vivas.sort(key=lambda x: x["desde"] or datetime.max.replace(tzinfo=timezone.utc))
    return vivas, descartadas_privadas


def serializar(s):
    def iso(v):
        return v.astimezone(TZ_LOCAL).isoformat(timespec="minutes") if v else None
    return {
        "sesion": s["sesion"],
        "titulo": s["titulo"],
        "proyecto": s["proyecto"],
        "proyecto_path": s["proyecto_path"],
        "cwd": s["cwd"],
        "branch": s["branch"],
        "desde": iso(s["desde"]),
        "hasta": iso(s["hasta"]),
        "prompts": s["prompts"],
        "skills": sorted(s["skills"]),
        "mcp": sorted(s["mcp"]),
        "archivos_brain": sorted(s["archivos_brain"]),
        "archivos_repo": sorted(s["archivos_repo"]),
        "archivos_memoria": sorted(s["archivos_memoria"]),
        "comandos": s["comandos"],
        "prs": s["prs"],
        "turnos_agente": s["turnos_agente"],
        "lineas_subagente": s["lineas_subagente"],
    }


def a_markdown(payload):
    v = payload["ventana"]
    r = payload["resumen"]
    out = [f"# Digest de sesiones: {v['desde']} a {v['hasta']}", ""]
    out.append(f"{r['sesiones']} sesiones, {r['proyectos']} proyectos, "
               f"{r['archivos_brain']} archivos del brain tocados, ~{r['tokens_aprox']} tokens de digest")
    if r["sesiones_privadas_excluidas"]:
        out.append(f"({r['sesiones_privadas_excluidas']} sesión/es excluida/s por perímetro de privacidad)")
    out.append("")

    for proyecto, sesiones in payload["por_proyecto"].items():
        out.append(f"## {proyecto}")
        for s in sesiones:
            out.append(f"### {s['titulo'] or '(sin título)'} · `{s['sesion'][:8]}` · {s['desde']}")
            if s["branch"] and s["branch"] != "HEAD":
                out.append(f"- branch: `{s['branch']}`")
            for p in s["prompts"]:
                out.append(f"- prompt: {p}")
            for a in s["archivos_brain"]:
                out.append(f"- brain: {a}")
            for a in s["archivos_repo"]:
                out.append(f"- repo: {a}")
            for a in s["archivos_memoria"]:
                out.append(f"- memoria: {a}")
            for c in s["comandos"]:
                out.append(f"- $ {c}")
            for pr in s["prs"]:
                out.append(f"- PR: {pr}")
            if s["skills"]:
                out.append(f"- skills: {', '.join(s['skills'])}")
            out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Digest de sesiones de Claude Code para el ciclo dreaming.")
    ap.add_argument("--horas", type=float, default=None, help="Ventana hacia atrás desde ahora (default: config).")
    ap.add_argument("--desde", help="Inicio explícito, YYYY-MM-DD o ISO. Pisa --horas.")
    ap.add_argument("--hasta", help="Fin explícito, YYYY-MM-DD o ISO. Default: ahora.")
    ap.add_argument("--max-chars-prompt", type=int, default=None, help="Trunca cada prompt (default: config).")
    ap.add_argument("--md", action="store_true", help="Salida markdown en vez de JSON.")
    ap.add_argument("--out", help="Escribe el JSON a este path (relativo a state_dir) además de stdout.")
    args = ap.parse_args()

    cfg = cargar_config()
    max_chars = args.max_chars_prompt or cfg["topes"]["max_chars_prompt"]
    horas = args.horas if args.horas is not None else cfg.get("ventana", {}).get("horas", 24)

    hasta = parse_ts(args.hasta) if args.hasta else datetime.now(timezone.utc)
    desde = parse_ts(args.desde) if args.desde else hasta - timedelta(hours=horas)
    if desde is None or hasta is None:
        sys.exit("Fecha inválida. Usá YYYY-MM-DD o ISO completo.")
    if desde == hasta:
        # '--desde X --hasta X' se lee como "el día X entero", no como un instante.
        hasta = desde + timedelta(days=1)

    indice = indexar_proyectos(cfg)
    sesiones, archivos_leidos = recolectar(desde, hasta, cfg, max_chars)
    vivas, privadas = podar(sesiones, cfg, indice)

    por_proyecto = OrderedDict()
    for s in vivas:
        por_proyecto.setdefault(s["proyecto"], []).append(serializar(s))

    chars = sum(len(p) for s in vivas for p in s["prompts"])
    payload = {
        "generado": datetime.now(TZ_LOCAL).isoformat(timespec="seconds"),
        "ventana": {
            "desde": desde.astimezone(TZ_LOCAL).isoformat(timespec="minutes"),
            "hasta": hasta.astimezone(TZ_LOCAL).isoformat(timespec="minutes"),
        },
        "resumen": {
            "jsonl_leidos": archivos_leidos,
            "sesiones": len(vivas),
            "proyectos": len(por_proyecto),
            "archivos_brain": sum(len(s["archivos_brain"]) for s in vivas),
            "archivos_repo": sum(len(s["archivos_repo"]) for s in vivas),
            "memorias_tocadas": sum(len(s["archivos_memoria"]) for s in vivas),
            "sesiones_privadas_excluidas": privadas,
            "tokens_aprox": chars // 4,
        },
        "por_proyecto": por_proyecto,
    }

    if args.out:
        destino = resolver_salida(
            cfg, args.out if os.path.isabs(args.out) else ruta_estado(cfg, args.out))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    if args.md:
        print(a_markdown(payload))
    else:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        print()


if __name__ == "__main__":
    main()

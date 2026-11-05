#!/usr/bin/env python3
"""Arma la botonera de /brain-decide a partir de un JSON de ítems.

Uso:
  python3 armar.py datos.json salida.html            # elige solo por cantidad (ver MAX_INLINE)
  python3 armar.py --inline datos.json salida.html   # fuerza widget inline (fragmento para show_widget)
  python3 armar.py --html datos.json salida.html     # fuerza html completo

Por cantidad: hasta 5 decisiones, widget inline; de 6 en
adelante, html. El índice lateral no va por cantidad: aparece cuando el JSON trae
2 o más `secciones` (y cada ítem su `seccion`). Muchas decisiones sin secciones
da un aviso, no un error.

Valida los campos y los techos de palabras (la carga visual baja es el contrato
del skill). Si algo se pasa, avisa por stderr y sale con código 1 sin escribir.
"""
import html as H
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).parent
ICONOS = json.loads((AQUI / "iconos.json").read_text(encoding="utf-8"))
MAX_INLINE = 5      # hasta acá, widget inline; arriba, html
SUGERIR_SECCIONES = 12  # desde acá, si no hay secciones, avisar
PREFIJO = "/brain-decide respuesta · "  # encabeza la respuesta que arma la página completa
TECHOS = {"titulo": 9, "contexto": 25, "reco_motivo": 15}
OBLIGATORIOS = ("n", "titulo", "contexto", "reco", "reco_motivo")


def palabras(s):
    return len(str(s).split())


def es_va(it):
    return str(it.get("reco", "")).strip().lower() == "va"


def validar(d):
    errores = []
    for k in ("titulo", "fecha", "clave", "items"):
        if not d.get(k):
            errores.append(f"falta '{k}' en la raíz")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(d.get("fecha", ""))):
        errores.append("fecha tiene que ser AAAA-MM-DD")
    secciones = d.get("secciones") or []
    ids = [x.get("id") for x in secciones]
    for x in secciones:
        if not x.get("id") or not x.get("titulo"):
            errores.append("cada sección necesita 'id' y 'titulo'")
    if len(ids) != len(set(ids)):
        errores.append("id de sección repetido")
    vistos = set()
    for it in d.get("items", []):
        if secciones and it.get("seccion") not in ids:
            errores.append(f"ítem {it.get('n', '?')}: seccion '{it.get('seccion')}' no está en 'secciones'")
        n = it.get("n", "?")
        for k in OBLIGATORIOS:
            if it.get(k) in (None, ""):
                errores.append(f"ítem {n}: falta '{k}'")
        if n in vistos:
            errores.append(f"ítem {n}: número repetido")
        vistos.add(n)
        if str(it.get("reco", "")).strip().lower() not in ("va", "no va"):
            errores.append(f"ítem {n}: reco tiene que ser 'va' o 'no va'")
        if it.get("icono") and it["icono"] not in ICONOS:
            errores.append(f"ítem {n}: icono '{it.get('icono')}' no existe (o pasá 'svg' propio)")
        dib = it.get("dibujo")
        if dib is not None and not (isinstance(dib, dict) and dib.get("svg")):
            errores.append(f"ítem {n}: 'dibujo' tiene que ser {{viewBox, svg, alt}} con svg")
        imp = it.get("impacto")
        if imp is not None and not (isinstance(imp, dict) and (imp.get("positivo") or imp.get("negativo"))):
            errores.append(f"ítem {n}: 'impacto' tiene que ser {{positivo, negativo}}")
        if it.get("accent") not in (None, "", "warning", "danger"):
            errores.append(f"ítem {n}: accent solo 'warning' o 'danger'")
        for campo, techo in TECHOS.items():
            if palabras(it.get(campo, "")) > techo:
                errores.append(f"ítem {n}: '{campo}' tiene {palabras(it[campo])} palabras (techo {techo})")
    return errores


def armar_html(d):
    blob = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
    iconos = json.dumps(ICONOS, ensure_ascii=False).replace("</", "<\\/")
    s = (AQUI / "plantilla.html").read_text(encoding="utf-8")
    return (s.replace("/*__DATA__*/null", blob)
             .replace("/*__ICONOS__*/{}", iconos)
             .replace("/*__PREFIJO__*/''", json.dumps(PREFIJO, ensure_ascii=False))
             .replace("__TITULO__", H.escape(d["titulo"])))


HEADER_SVG = (AQUI / "elicit-header.svg").read_text(encoding="utf-8").strip()  # chrome fijo del shell, byte a byte


CLASES_INLINE = {
    # Las de trazo llevan fill:none: sin eso, una flecha <path> sale rellena de negro.
    "a": "stroke:var(--text-accent);fill:none", "b": "fill:var(--border-warning)", "fa": "fill:var(--text-accent)",
    "t": "fill:var(--text-primary);font:500 12px var(--font-sans)", "tm": "fill:var(--text-secondary);font:400 11px var(--font-sans)",
    "go": "fill:var(--text-success)", "no": "fill:var(--text-danger)",
    "sgo": "stroke:var(--text-success);fill:none", "sno": "stroke:var(--text-danger);fill:none",
    "box": "fill:var(--surface-1);stroke:var(--border)",
}


def svg_inline(svg):
    """Íconos y dibujos usan clases; el widget no lleva <style> para eso, así que van a style inline."""
    return re.sub(r'class="(\w+)"', lambda m: f'style="{CLASES_INLINE[m.group(1)]}"' if m.group(1) in CLASES_INLINE else m.group(0), svg)


def armar_inline(d):
    """Widget con el shell de elicitación: el host cablea toggles y envío. Cero <script>."""
    e = H.escape
    fondo = {"warning": "var(--bg-warning)", "danger": "var(--bg-danger)"}
    # Sin tocar: el recomendado va solo bordeado (data-rec, no data-accent: el shell le pinta el fondo).
    # Tocado: Va se pinta entero de verde y No va de rojo, en vez del azul de selección del shell.
    css = ('<style>'
           '.elicit-pill[data-rec]:not([aria-pressed="true"]){background:transparent!important;border-width:2px!important}'
           '.elicit-pill[data-rec="go"]:not([aria-pressed="true"]){border-color:var(--text-success)!important;color:var(--text-success)!important}'
           '.elicit-pill[data-rec="no"]:not([aria-pressed="true"]){border-color:var(--text-danger)!important;color:var(--text-danger)!important}'
           '.elicit-pill[data-value="Va"][aria-pressed="true"]{background:var(--text-success)!important;border-color:var(--text-success)!important;color:var(--surface-2)!important}'
           '.elicit-pill[data-value="No va"][aria-pressed="true"]{background:var(--text-danger)!important;border-color:var(--text-danger)!important;color:var(--surface-2)!important}'
           '</style>')
    out = [css, '<form class="elicit">',
           f'<div class="elicit-header">{HEADER_SVG}<span>{e(d.get("encabezado") or "Decisiones")}</span></div>',
           '<div class="elicit-body">']
    for it in d["items"]:
        n, va = e(str(it["n"])), es_va(it)
        tag = {"danger": " · ojo", "warning": " · sensible"}.get(it.get("accent") or "", "")
        imp = it.get("impacto") or {}
        det_imp = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px">'
                   f'<div style="padding:6px 8px;border-left:3px solid var(--text-success);background:var(--bg-success)"><span style="font-weight:500">Impacto positivo</span><br>{e(imp.get("positivo") or "nada relevante")}</div>'
                   f'<div style="padding:6px 8px;border-left:3px solid var(--text-danger);background:var(--bg-danger)"><span style="font-weight:500">Impacto negativo</span><br>{e(imp.get("negativo") or "nada relevante")}</div></div>') if imp else ""
        det = det_imp + "".join(
            f'<p style="margin:6px 0 0"><span style="font-weight:500">{lab}:</span> {e(it[k])}</p>'
            for k, lab in (("porque", "Por qué"), ("si_va", "Si va"), ("si_no_va", "Si no va"), ("fuente", "Fuente")) if it.get(k))
        icono = it.get("svg") or (ICONOS[it["icono"]] if it.get("icono") else "")
        dib = it.get("dibujo")
        acc_va = ' data-rec="go"' if va else ''
        acc_no = '' if va else ' data-rec="no"'
        reco = (f'<span style="color:var(--text-{"success" if va else "danger"});font-weight:500">{"Va" if va else "No va"}</span>')
        out.append(
            '<div class="elicit-group">'
            f'<label class="elicit-question">{n}{tag} · {e(it["titulo"])}</label>'
            + (f'<div style="margin:6px 0 4px;padding:10px;border-radius:12px;background:var(--surface-1)"><svg viewBox="{e(dib.get("viewBox") or "0 0 240 100")}" style="display:block;width:100%;max-width:440px;height:auto;margin:0 auto" role="img" aria-label="{e(dib.get("alt") or "")}">{svg_inline(dib["svg"])}</svg></div>' if dib else "")
            + '<div style="display:flex;gap:14px;align-items:flex-start;margin:4px 0 10px">'
            + (f'<div style="flex:0 0 64px;height:64px;border-radius:12px;background:{fondo.get(it.get("accent") or "", "var(--bg-accent)")};display:flex;align-items:center;justify-content:center">'
               f'<svg viewBox="0 0 64 64" width="46" height="46" aria-hidden="true">{svg_inline(icono)}</svg></div>' if icono and not dib else "")
            +             f'<div style="font-size:14px;line-height:1.5;color:var(--text-secondary)">{e(it["contexto"])}'
            f'<br><span style="font-size:13px">Te recomiendo {reco}: {e(it["reco_motivo"])}</span></div></div>'
            f'<div class="elicit-pills" data-name="decision_{n}" data-multi="false">'
            f'<button type="button" class="elicit-pill" data-value="Va"{acc_va}>Va</button>'
            f'<button type="button" class="elicit-pill" data-value="No va"{acc_no}>No va</button></div>'
            f'<textarea class="elicit-textarea" data-name="comentario_{n}" rows="1" placeholder="Comentario (opcional)"></textarea>'
            + (f'<details style="font-size:13px;color:var(--text-secondary);margin-top:6px"><summary style="cursor:pointer;color:var(--text-accent)">Ver el detalle</summary>{det}</details>' if det else "")
            + '</div>')
    out.append('<div class="elicit-group"><label class="elicit-question">¿Algo que la botonera no previó?</label>'
               '<textarea class="elicit-textarea" data-name="notas" placeholder="Opcional"></textarea></div>')
    out.append('</div><div class="elicit-footer"><button type="button" class="elicit-skip">Saltar</button>'
               '<button type="button" class="elicit-submit">Enviar respuesta</button></div></form>')
    return "\n".join(out)


def main():
    args = sys.argv[1:]
    forzado = next((a for a in args if a in ("--html", "--inline")), None)
    args = [a for a in args if a not in ("--html", "--inline")]
    if len(args) != 2:
        sys.exit("uso: python3 armar.py [--html|--inline] datos.json salida.html")
    datos = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    errores = validar(datos)
    if errores:
        print("\n".join(errores), file=sys.stderr)
        sys.exit(1)
    n = len(datos["items"])
    modo_html = forzado == "--html" or (forzado is None and n > MAX_INLINE)
    salida = Path(args[1])
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(armar_html(datos) if modo_html else armar_inline(datos), encoding="utf-8")
    con_indice = len(datos.get("secciones") or []) >= 2
    if modo_html and not con_indice and n >= SUGERIR_SECCIONES:
        print(f"aviso: {n} decisiones sin secciones. Si se agrupan por tema, sumá 'secciones' y sale el índice.", file=sys.stderr)
    modo = ("html + índice" if con_indice else "html") if modo_html else "inline"
    print(f"ok · {modo} · {n} ítems · {salida}")


if __name__ == "__main__":
    main()

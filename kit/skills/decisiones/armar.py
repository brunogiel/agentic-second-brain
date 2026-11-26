#!/usr/bin/env python3
"""Arma la botonera de /brain-decide a partir de un JSON de ítems.

Uso:
  python3 armar.py datos.json salida.html            # elige solo por cantidad (ver MAX_INLINE)
  python3 armar.py --inline datos.json salida.html   # fuerza widget inline (fragmento para show_widget)
  python3 armar.py --html datos.json salida.html     # fuerza html completo
  python3 armar.py --artifact datos.json salida.json # documento para la página privada de Claude (ver abajo)

Por cantidad: hasta 5 decisiones, widget inline; de 6 en
adelante, html. El índice lateral no va por cantidad: aparece cuando el JSON trae
2 o más `secciones` (y cada ítem su `seccion`). Muchas decisiones sin secciones
da un aviso, no un error.

--artifact corre las MISMAS validaciones y escribe un JSON (no un html): la tanda con los dibujos saneados,
el ícono resuelto a svg, `creada` (ISO UTC) y `estado: "abierta"`. Claude lo sube a la base de la página privada
(`tandas/<clave>`). Con --artifact además valen las tarjetas de opciones (`opciones`, `varias`) y de revisión
(`tipo: "revision"` con `hice`, `verifique`, `mirar`). Campos opcionales que la página usa: accion_va,
accion_no_va, antecedentes, si_no_decidis, vence, campos, aplicar, detalle y fyi.

Valida los campos y los techos de palabras (la carga visual baja es el contrato
del skill). Si algo se pasa, avisa por stderr y sale con código 1 sin escribir.
"""
import datetime
import html as H
import json
import re
import sys
from html.parser import HTMLParser
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


TECHO_ANTECEDENTE = 15   # palabras por viñeta de antecedentes (y por si_no_decidis)
TECHO_APLICAR = 40       # palabras por plan de `aplicar` (y por su `comun`)
TECHO_DETALLE = 60       # palabras del `detalle` plegado
TECHO_REVISION = 15      # palabras por viñeta de hice / verifique / mirar
MAX_CAMPOS = 5           # campos editables por tarjeta (botón Editar)
TIPOS_CAMPO = ("texto", "numero", "fecha", "opcion")
ID_SEGURO = re.compile(r"[A-Za-z0-9_-]{1,40}")   # ids de sección: van a atributos y a selectores del html
ID_OPCION = re.compile(r"[a-z0-9_-]{1,30}")
SOLO_ARTIFACT = "solo las muestra la página privada de Claude: armá con --artifact"


# --- SVG seguro -------------------------------------------------------------------------------
# Un dibujo o ícono propio llega crudo en el JSON y se inyecta como html. Whitelist sobre html.parser:
# lo que no está en la lista se descarta (y se avisa), el texto se re-escapa, las etiquetas salen balanceadas.
SVG_TAGS = frozenset("svg g path rect circle ellipse line polyline polygon text tspan title desc defs marker use".split())
SVG_ATTRS = ("d x y x1 y1 x2 y2 cx cy r rx ry width height points viewBox transform class fill stroke "
             "stroke-width stroke-linecap stroke-linejoin stroke-dasharray opacity font-size font-weight "
             "text-anchor dominant-baseline marker-start marker-end markerWidth markerHeight refX refY orient "
             "id preserveAspectRatio xmlns").split()
ATTR_CANON = {a.lower(): a for a in SVG_ATTRS}   # html.parser baja todo a minúsculas: viewBox vuelve a su forma
SVG_SALTAR = frozenset("script style foreignobject iframe object embed noscript template".split())  # se va con todo su contenido
URL_EXTERNA = re.compile(r"url\(\s*(?![\'\"]?\s*#)", re.I)   # url(#id) sí; url(http…) / url(data:…) no


class _SaneadorSvg(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.abiertas, self.quitado = [], [], []
        self.saltando, self.prof = None, 0   # etiqueta cuyo contenido se descarta, y su profundidad

    def _attrs(self, tag, attrs):
        res = []
        for nombre, val in attrs:
            val = "" if val is None else val
            canon = ATTR_CANON.get(nombre)
            if canon == "xmlns" and not val.startswith("http://www.w3.org/"):
                canon = None
            elif canon == "id" and not ID_SEGURO.fullmatch(val):
                canon = None
            elif canon and URL_EXTERNA.search(val):
                canon = None
            if tag == "use" and nombre in ("href", "xlink:href") and val.strip().startswith("#"):
                canon = nombre
            if canon:
                res.append(f' {canon}="{H.escape(val, quote=True)}"')
            else:
                self.quitado.append(f"{nombre}= en <{tag}>")
        return "".join(res)

    def _abrir(self, tag, attrs, cerrada):
        if self.saltando:
            if tag == self.saltando and not cerrada:
                self.prof += 1
            return
        if tag in SVG_SALTAR:
            self.quitado.append(f"<{tag}> con su contenido")
            if not cerrada:
                self.saltando, self.prof = tag, 1
            return
        if tag not in SVG_TAGS:
            self.quitado.append(f"<{tag}>")
            return
        self.out.append(f"<{tag}{self._attrs(tag, attrs)}{'/' if cerrada else ''}>")
        if not cerrada:
            self.abiertas.append(tag)

    def handle_starttag(self, tag, attrs):
        self._abrir(tag, attrs, False)

    def handle_startendtag(self, tag, attrs):
        self._abrir(tag, attrs, True)

    def handle_endtag(self, tag):
        if self.saltando:
            if tag == self.saltando:
                self.prof -= 1
                if self.prof == 0:
                    self.saltando = None
            return
        if tag not in self.abiertas:
            self.quitado.append(f"</{tag}> sin abrir")
            return
        while self.abiertas:
            t = self.abiertas.pop()
            self.out.append(f"</{t}>")
            if t == tag:
                break

    def handle_data(self, data):
        if not self.saltando:
            self.out.append(H.escape(data, quote=False))

    def terminar(self):
        self.close()
        while self.abiertas:
            self.out.append(f"</{self.abiertas.pop()}>")
        return "".join(self.out), self.quitado


def sanear_svg(svg):
    """-> (svg limpio, lista de lo que se quitó). Sin nada que quitar, es el mismo dibujo re-serializado."""
    p = _SaneadorSvg()
    p.feed(svg)
    return p.terminar()


# --- validación ---------------------------------------------------------------------------------
def lista_textos(n, it, campo, maximo, techo):
    """Lista de 1..maximo textos de hasta `techo` palabras. -> errores."""
    v = it.get(campo)
    if v is None:
        return []
    if not (isinstance(v, list) and 1 <= len(v) <= maximo and all(isinstance(a, str) and a.strip() for a in v)):
        return [f"ítem {n}: '{campo}' tiene que ser una lista de 1 a {maximo} textos"]
    return [f"ítem {n}: un texto de '{campo}' tiene {palabras(a)} palabras (techo {techo})" for a in v if palabras(a) > techo]


def validar_opciones(n, it):
    errores = []
    ops = it.get("opciones")
    if ops is None:
        if it.get("varias") is not None:
            errores.append(f"ítem {n}: 'varias' va solo con 'opciones'")
        r = str(it.get("reco", "")).strip().lower()
        if r not in ("va", "no va"):
            errores.append(f"ítem {n}: reco tiene que ser 'va' (la recomendada es siempre Va)")
        elif r == "no va":
            # la recomendada es siempre Va, a la derecha: avanzar es aceptar la recomendación
            errores.append(f"ítem {n}: la recomendada es siempre Va (el botón de la derecha). Si recomendás no hacerlo, "
                           "reescribí el título para que Va sea eso (ej.: «Seguir con el plan gratis» en vez de «Pasar al plan pago»)")
        return errores
    if not (isinstance(ops, list) and 2 <= len(ops) <= 5):
        return [f"ítem {n}: 'opciones' tiene que ser una lista de 2 a 5 {{id, etiqueta, abierta?}}"]
    ids = []
    for o in ops:
        if not (isinstance(o, dict) and isinstance(o.get("id"), str) and ID_OPCION.fullmatch(o["id"])):
            errores.append(f"ítem {n}: cada opción necesita un 'id' en minúscula, sin espacios (a-z 0-9 _ -, hasta 30)")
            continue
        if not (isinstance(o.get("etiqueta"), str) and o["etiqueta"].strip()):
            errores.append(f"ítem {n}: la opción '{o['id']}' no tiene 'etiqueta'")
        elif palabras(o["etiqueta"]) > 6:
            errores.append(f"ítem {n}: la etiqueta de '{o['id']}' tiene {palabras(o['etiqueta'])} palabras (techo 6: es un botón)")
        if o.get("abierta") not in (None, True, False):
            errores.append(f"ítem {n}: 'abierta' de '{o['id']}' tiene que ser true o false")
        ids.append(o["id"])
    if len(ids) != len(set(ids)):
        errores.append(f"ítem {n}: id de opción repetido")
    if it.get("varias") not in (None, True, False):
        errores.append(f"ítem {n}: 'varias' tiene que ser true o false")
    reco = it.get("reco")
    rec = [str(x).strip() for x in reco] if isinstance(reco, list) else [str(reco or "").strip()]
    if isinstance(reco, list) and it.get("varias") is not True:
        errores.append(f"ítem {n}: 'reco' como lista va solo con 'varias': true")
    fuera = [r for r in rec if r not in ids]
    if fuera:
        errores.append(f"ítem {n}: reco '{', '.join(fuera)}' no es el id de ninguna opción ({', '.join(ids)})")
    for k in ("accion_va", "accion_no_va"):
        if it.get(k):
            errores.append(f"ítem {n}: '{k}' no va en una tarjeta con 'opciones' (la tarjeta es de un tipo o del otro)")
    return errores


def validar_campos(n, it):
    """`campos`: valores editables de una tarjeta sí/no (botón Editar). Máx. 5, etiqueta ≤6 palabras, valor del tipo declarado."""
    cs = it.get("campos")
    if cs is None:
        return []
    if not (isinstance(cs, list) and 1 <= len(cs) <= MAX_CAMPOS):
        return [f"ítem {n}: 'campos' tiene que ser una lista de 1 a {MAX_CAMPOS} {{id, etiqueta, valor, tipo}}"]
    errores, ids = [], []
    if it.get("opciones") is not None:
        errores.append(f"ítem {n}: 'campos' va solo en tarjetas sí/no")
    for c in cs:
        if not isinstance(c, dict):
            errores.append(f"ítem {n}: cada campo tiene que ser {{id, etiqueta, valor, tipo}}")
            continue
        cid = c.get("id")
        if not (isinstance(cid, str) and ID_OPCION.fullmatch(cid)):
            errores.append(f"ítem {n}: el 'id' de un campo va en minúscula, sin espacios (a-z 0-9 _ -, hasta 30)")
            continue
        if cid in ids:
            errores.append(f"ítem {n}: id de campo repetido ('{cid}')")
        ids.append(cid)
        et = c.get("etiqueta")
        if not (isinstance(et, str) and et.strip()):
            errores.append(f"ítem {n}: el campo '{cid}' no tiene 'etiqueta'")
        elif palabras(et) > 6:
            errores.append(f"ítem {n}: la etiqueta de '{cid}' tiene {palabras(et)} palabras (techo 6)")
        tipo, val = c.get("tipo"), c.get("valor")
        if tipo not in TIPOS_CAMPO:
            errores.append(f"ítem {n}: el tipo del campo '{cid}' tiene que ser {' | '.join(TIPOS_CAMPO)}")
            continue
        if tipo == "numero":
            ok = (isinstance(val, (int, float)) and not isinstance(val, bool)) or (isinstance(val, str) and re.fullmatch(r"-?\d+(\.\d+)?", val.strip() or "x"))
            if not ok:
                errores.append(f"ítem {n}: el valor del campo numérico '{cid}' tiene que ser un número")
        elif tipo == "fecha":
            try:
                if not (isinstance(val, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", val)):
                    raise ValueError
                datetime.date.fromisoformat(val)
            except ValueError:
                errores.append(f"ítem {n}: el valor del campo fecha '{cid}' tiene que ser AAAA-MM-DD válida")
        elif tipo == "opcion":
            ops = c.get("opciones")
            if not (isinstance(ops, list) and 2 <= len(ops) <= 8 and all(isinstance(o, str) and o.strip() for o in ops)):
                errores.append(f"ítem {n}: el campo '{cid}' (opcion) necesita 'opciones': una lista de 2 a 8 textos")
            elif val not in ops:
                errores.append(f"ítem {n}: el valor de '{cid}' tiene que ser una de sus opciones")
        else:  # texto
            if not (isinstance(val, str) and val.strip()):
                errores.append(f"ítem {n}: el valor del campo de texto '{cid}' tiene que ser un texto")
            elif len(val) > 200:
                errores.append(f"ítem {n}: el valor de '{cid}' pasa los 200 caracteres")
    return errores


def validar_aplicar(n, it):
    """`aplicar`: el plan de cada respuesta posible. Lo lee Claude cuando aplica la respuesta."""
    ap = it.get("aplicar")
    if ap is None:
        return []
    if not isinstance(ap, dict) or not ap:
        return [f"ítem {n}: 'aplicar' tiene que ser un objeto {{va, no_va, comun?}} (o {{<id de opción>: plan}} en una tarjeta con 'opciones')"]
    ops = it.get("opciones")
    base = [o["id"] for o in ops if isinstance(o, dict) and isinstance(o.get("id"), str)] if isinstance(ops, list) else ["va", "no_va"]
    errores = []
    for k, v in ap.items():
        if k not in base + ["comun"]:
            errores.append(f"ítem {n}: 'aplicar.{k}' no es una respuesta de esta tarjeta (claves posibles: {', '.join(base + ['comun'])})")
        elif not (isinstance(v, str) and v.strip()):
            errores.append(f"ítem {n}: 'aplicar.{k}' tiene que ser un texto con el plan")
        elif palabras(v) > TECHO_APLICAR:
            errores.append(f"ítem {n}: 'aplicar.{k}' tiene {palabras(v)} palabras (techo {TECHO_APLICAR})")
    return errores


def validar_svg(n, campo, svg):
    if not isinstance(svg, str) or not svg.strip():
        return [f"ítem {n}: '{campo}' tiene que ser un texto svg"]
    _, quitado = sanear_svg(svg)
    if quitado:
        return [f"ítem {n}: '{campo}' trae algo que no se permite ({', '.join(quitado[:3])}): sacalo del dibujo"]
    return []


def validar(d, artifact=False):
    errores = []
    for k in ("titulo", "fecha", "clave", "items"):
        if not d.get(k):
            errores.append(f"falta '{k}' en la raíz")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(d.get("fecha", ""))):
        errores.append("fecha tiene que ser AAAA-MM-DD")
    if artifact and not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", str(d.get("clave", ""))):
        errores.append("clave: solo letras, números, _ y - (va en la ruta de la base), hasta 100")
    secciones = d.get("secciones") or []
    ids = [x.get("id") for x in secciones]
    for x in secciones:
        if not x.get("id") or not x.get("titulo"):
            errores.append("cada sección necesita 'id' y 'titulo'")
        elif not (isinstance(x["id"], str) and ID_SEGURO.fullmatch(x["id"])):
            errores.append(f"sección '{x['id']}': el id solo admite letras, números, _ y - (hasta 40)")
    if len(ids) != len(set(ids)):
        errores.append("id de sección repetido")
    vistos = set()
    for it in d.get("items", []):
        if secciones and it.get("seccion") not in ids:
            errores.append(f"ítem {it.get('n', '?')}: seccion '{it.get('seccion')}' no está en 'secciones'")
        n = it.get("n", "?")
        rev = it.get("tipo") == "revision"
        if it.get("tipo") not in (None, "", "revision"):
            errores.append(f"ítem {n}: 'tipo' solo puede ser 'revision'")
        if (rev or it.get("opciones") is not None) and not artifact:
            errores.append(f"ítem {n}: las tarjetas de {'revisión' if rev else 'opciones'} {SOLO_ARTIFACT}")
        for k in (("n", "titulo", "contexto") if rev else OBLIGATORIOS):
            if it.get(k) in (None, ""):
                errores.append(f"ítem {n}: falta '{k}'")
        if n in vistos:
            errores.append(f"ítem {n}: número repetido")
        vistos.add(n)
        if rev:
            if not any(it.get(k) for k in ("hice", "verifique", "mirar")):
                errores.append(f"ítem {n}: una revisión necesita 'hice', 'verifique' o 'mirar'")
            for k in ("hice", "verifique", "mirar"):
                errores += lista_textos(n, it, k, 3, TECHO_REVISION)
            for k in ("opciones", "campos", "accion_va", "accion_no_va"):
                if it.get(k):
                    errores.append(f"ítem {n}: '{k}' no va en una tarjeta de revisión (solo tiene el botón «Revisado»)")
        else:
            errores += validar_opciones(n, it)
            errores += validar_campos(n, it)
            for k in ("hice", "verifique", "mirar"):
                if it.get(k):
                    errores.append(f"ítem {n}: '{k}' va solo con tipo 'revision'")
        errores += validar_aplicar(n, it)
        if it.get("icono") and it["icono"] not in ICONOS:
            errores.append(f"ítem {n}: icono '{it.get('icono')}' no existe (o pasá 'svg' propio)")
        dib = it.get("dibujo")
        if dib is not None:
            if not (isinstance(dib, dict) and dib.get("svg")):
                errores.append(f"ítem {n}: 'dibujo' tiene que ser {{viewBox, svg, alt}} con svg")
            else:
                errores += validar_svg(n, "dibujo", dib["svg"])
        if it.get("svg") is not None:
            errores += validar_svg(n, "svg", it["svg"])
        imp = it.get("impacto")
        if imp is not None and not (isinstance(imp, dict) and (imp.get("positivo") or imp.get("negativo"))):
            errores.append(f"ítem {n}: 'impacto' tiene que ser {{positivo, negativo}}")
        if it.get("accent") not in (None, "", "warning", "danger"):
            errores.append(f"ítem {n}: accent solo 'warning' o 'danger'")
        for campo, techo in TECHOS.items():
            if palabras(it.get(campo, "")) > techo:
                errores.append(f"ítem {n}: '{campo}' tiene {palabras(it[campo])} palabras (techo {techo})")
        errores += lista_textos(n, it, "antecedentes", 3, TECHO_ANTECEDENTE)
        snd = it.get("si_no_decidis")
        if snd is not None:
            if not (isinstance(snd, str) and snd.strip()):
                errores.append(f"ítem {n}: 'si_no_decidis' tiene que ser un texto")
            elif palabras(snd) > TECHO_ANTECEDENTE:
                errores.append(f"ítem {n}: 'si_no_decidis' tiene {palabras(snd)} palabras (techo {TECHO_ANTECEDENTE})")
        det = it.get("detalle")
        if det is not None:
            if not (isinstance(det, str) and det.strip()):
                errores.append(f"ítem {n}: 'detalle' tiene que ser un texto")
            elif palabras(det) > TECHO_DETALLE:
                errores.append(f"ítem {n}: 'detalle' tiene {palabras(det)} palabras (techo {TECHO_DETALLE}; es plegado, pero no un informe)")
        venc = it.get("vence")
        if venc is not None:
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(venc)):
                    raise ValueError
                datetime.date.fromisoformat(venc)
            except ValueError:
                errores.append(f"ítem {n}: 'vence' tiene que ser una fecha AAAA-MM-DD válida")
        for campo in ("accion_va", "accion_no_va"):
            if it.get(campo) and palabras(it[campo]) > 6:
                errores.append(f"ítem {n}: '{campo}' tiene {palabras(it[campo])} palabras (techo 6: es la etiqueta del botón)")
    fyi = d.get("fyi")
    if fyi is not None:
        if not (isinstance(fyi, dict) and isinstance(fyi.get("grupos"), list)):
            errores.append("'fyi' tiene que ser un objeto {titulo, lead?, grupos:[{titulo, items:[...]}]}")
        else:
            for g in fyi["grupos"]:
                if not (isinstance(g, dict) and isinstance(g.get("items"), list) and g["items"]
                        and all(isinstance(x, str) for x in g["items"])):
                    errores.append("cada grupo de 'fyi' necesita 'items' (una lista de textos)")
    return errores


def armar_artifact(d):
    """El documento listo para subir a la base de la página privada de Claude: la tanda validada, con los
    dibujos saneados, el ícono resuelto a svg (la página no trae el catálogo) y los campos que agrega Claude."""
    doc = json.loads(json.dumps(d, ensure_ascii=False))
    for it in doc["items"]:
        if isinstance(it.get("dibujo"), dict):
            it["dibujo"]["svg"] = sanear_svg(it["dibujo"]["svg"])[0]
        if it.get("svg"):
            it["svg"] = sanear_svg(it["svg"])[0]
        elif it.get("icono"):
            it["svg"] = sanear_svg(ICONOS[it["icono"]])[0]
    doc["creada"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    doc["estado"] = "abierta"
    return doc


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
            f'<button type="button" class="elicit-pill" data-value="No va"{acc_no}>No va</button>'
            f'<button type="button" class="elicit-pill" data-value="Va"{acc_va}>Va</button></div>'
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
    forzado = next((a for a in args if a in ("--html", "--inline", "--artifact")), None)
    args = [a for a in args if a not in ("--html", "--inline", "--artifact")]
    if len(args) != 2:
        sys.exit("uso: python3 armar.py [--html|--inline|--artifact] datos.json salida.(html|json)")
    datos = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    errores = validar(datos, artifact=forzado == "--artifact")
    if errores:
        print("\n".join(errores), file=sys.stderr)
        sys.exit(1)
    n = len(datos["items"])
    salida = Path(args[1])
    salida.parent.mkdir(parents=True, exist_ok=True)
    if forzado == "--artifact":
        doc = armar_artifact(datos)
        texto = json.dumps(doc, ensure_ascii=False, indent=1)
        if len(texto.encode("utf-8")) > 200_000:
            sys.exit("el documento pasa los 200 KB (la base admite 256 KiB por documento): recortá dibujos o textos")
        salida.write_text(texto, encoding="utf-8")
        print(f"ok · artifact · {n} ítems · {salida}")
        return
    modo_html = forzado == "--html" or (forzado is None and n > MAX_INLINE)
    salida.write_text(armar_html(datos) if modo_html else armar_inline(datos), encoding="utf-8")
    con_indice = len(datos.get("secciones") or []) >= 2
    if modo_html and not con_indice and n >= SUGERIR_SECCIONES:
        print(f"aviso: {n} decisiones sin secciones. Si se agrupan por tema, sumá 'secciones' y sale el índice.", file=sys.stderr)
    modo = ("html + índice" if con_indice else "html") if modo_html else "inline"
    print(f"ok · {modo} · {n} ítems · {salida}")


if __name__ == "__main__":
    main()

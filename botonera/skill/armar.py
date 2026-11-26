#!/usr/bin/env python3
"""Arma la botonera de /botonera a partir de un JSON de ítems.

Uso:
  python3 armar.py datos.json salida.html            # elige solo por cantidad (ver MAX_INLINE)
  python3 armar.py --inline datos.json salida.html   # fuerza widget inline (fragmento para show_widget)
  python3 armar.py --html datos.json salida.html     # fuerza html completo
  python3 armar.py --publicar [--inline|--html] datos.json salida.html
                                                     # además publica la tanda a la botonera
  python3 armar.py --publicar --reemplaza <clave>#<n>[:<m>] datos.json salida.html
                                                     # además marca la card vieja «Ya no aplica» (la nueva es la <m>, por defecto la 1)

Por cantidad: hasta 5 decisiones, widget inline; de 6 en
adelante, html. El índice lateral no va por cantidad: aparece cuando el JSON trae
2 o más `secciones` (y cada ítem su `seccion`). Muchas decisiones sin secciones
da un aviso, no un error.

Valida los campos y los techos de palabras (la carga visual baja es el contrato
del skill). Si algo se pasa, avisa por stderr y sale con código 1 sin escribir.

Campos opcionales (un JSON sin ellos arma igual que siempre):
  tanda: origen {sesion_titulo, skill, proyecto, categoria}   (skill: texto libre, por defecto `botonera`)
         categoria: un id de categorias.json (trabajo, clientes, casa, ..., otras). Si falta, sale del alias de
         `proyecto`; si tampoco, y hay `proyecto`, se arma una categoría libre con ese nombre; si no hay nada,
         queda en `otras` con un aviso. Nunca frena el armado. Va embebida en datos.categoria
         ({id, nombre, color, icono, orden, privada}): la web ordena por `orden` y el aviso push
         oculta el nombre de las categorías `privada`.
  ítem:  antecedentes (1 a 3 viñetas), si_no_decidis, vence (AAAA-MM-DD)
  ítem:  imagen {path | src, alt, link}: lo que se aprueba se tiene que ver (un mapa, una maqueta).
         `path` es un png/jpg/webp local: se achica a 1200 px de ancho y viaja como data: URI (el
         la web solo deja ver imágenes data:). `link` (https) abre lo mismo afuera, p. ej. el board.

  ítem:  campos [{id, etiqueta, valor, tipo: texto|numero|fecha|opcion, opciones?}]: los valores que propuso el agente, para que
         el botón Editar los abra ya cargados en campos (máx. 5; etiqueta ≤6 palabras). Solo en cards sí/no. La respuesta vuelve
         «N. va con cambios · título → acción · campos: id=nuevo (antes viejo); … · comentario: …».
  ítem:  detalle (≤60 palabras): texto largo plegado en «Ver el detalle». campos de tipo `textarea` (≤3000 caracteres): un borrador entero.
  ítem:  tipo "revision" {n, titulo, hice, verifique, mirar, imagen|link}: no es una decisión, es algo hecho para mirar; un solo botón (Revisado).
  tanda: intro [{titulo?, texto?, items?}] y fyi {titulo?, lead?, grupos:[{titulo?, items:[texto]}]}.
  ítem:  aplicar {va, no_va | <id de cada opción>, comun?}: el plan concreto de cada respuesta posible (qué hacer, qué
         archivo o comando), ≤40 palabras cada uno. Lo lee retomar.py cuando la sesión ya no está viva. Opcional, pero
         una card sin `aplicar` da un aviso (no frena): sin plan, nadie más puede aplicar la respuesta.

Obligatorio: `impacto` {positivo, negativo} en cada ítem (los dos lados de la decisión). Las URLs https de fuente, antecedentes e intro salen como link.

--publicar manda la tanda a Supabase (maestro.py) después de escribir la salida local. Siempre
sube el html completo, aunque lo local sea inline. Publicar nunca borra el armado local (ya quedó escrito), pero
avisa con el código de salida: 0 si se publicó (o si no hay config), 1 si el servidor rechazó la tanda o la red falló,
2 si la clave ya está decidida (el servidor no pisa) o si una card de --reemplaza no se pudo marcar.
Una sesión de bot (BM_SESSION_ID=bot-…) solo publica claves bot-…: si no, falla en la validación local (código 1).

Seguridad: todo svg que venga en el JSON (dibujo.svg, svg de ícono propio) pasa por una whitelist
antes de armar nada (sanear_svg): sin scripts, handlers on*, style, href externos ni foreignObject.
El html completo además lleva un CSP por meta con el hash de cada <script> inline, sin
'unsafe-inline' en script-src: un handler inyectado no corre aunque el sanitizador falle.
"""
import base64
import datetime
import hashlib
import html as H
import json
import os
import re
import shutil
import subprocess
import unicodedata
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

import maestro

AQUI = Path(__file__).resolve().parent
ICONOS = json.loads((AQUI / "iconos.json").read_text(encoding="utf-8"))
MAX_INLINE = 5      # hasta acá, widget inline; arriba, html
SUGERIR_SECCIONES = 12  # desde acá, si no hay secciones, avisar
TECHOS = {"titulo": 9, "contexto": 25, "reco_motivo": 15}
OBLIGATORIOS = ("n", "titulo", "contexto", "reco", "reco_motivo")
TECHO_ANTECEDENTE = 15   # palabras por viñeta (y por si_no_decidis)
OTRAS = "otras"
TECHO_APLICAR = 40       # palabras por plan de `aplicar` (y por su `comun`)
MAX_CAMPOS = 5           # campos editables por card (botón Editar)
TIPOS_CAMPO = ("texto", "textarea", "numero", "fecha", "opcion")
MAX_TEXTAREA = 3000      # caracteres de un campo textarea (un mail entero: ~450 palabras)
TECHO_DETALLE = 60       # palabras del `detalle` de una card (plegado en «Ver el detalle»)
PREFIJO_BOT = "bot-"     # los bots publican con session_id «bot-<nombre>» y su secret solo sirve para claves así
ORDEN_OTRAS = 999   # `otras` va siempre al final, sin importar dónde esté en el catálogo
COLOR_LIBRE = "#E0DCD2"   # gris neutro de las categorías libres y de `otras`
ICONO_LIBRE = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
               'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8Z"/>'
               '<circle cx="7.5" cy="7.5" r="1.3"/></svg>')


def _cargar_categorias():
    """Catálogo de categorias.json. Si falta o está roto, [] (la categoría nunca frena el armado)."""
    try:
        cats = json.loads((AQUI / "categorias.json").read_text(encoding="utf-8"))
        return [c for c in cats if isinstance(c, dict) and isinstance(c.get("id"), str)]
    except (OSError, ValueError):
        return []


CATEGORIAS = _cargar_categorias()


def _norm(x):
    """Para comparar nombres: sin mayúsculas, sin tildes, sin emoji ni signos, espacios colapsados."""
    t = unicodedata.normalize("NFKD", str(x)).casefold()
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return re.sub(r"[\W_]+", " ", t).strip()


def _slug(texto):
    s = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower()).strip("-")[:30].strip("-")
    return s or "cat-" + hashlib.sha1(str(texto).encode("utf-8")).hexdigest()[:8]


def _objeto_categoria(c):
    """Entrada del catálogo -> lo que se embebe en datos["categoria"]. `orden` es su posición en el catálogo."""
    pos = next((i for i, x in enumerate(CATEGORIAS) if x["id"] == c["id"]), len(CATEGORIAS))
    return {"id": c["id"], "nombre": c.get("nombre") or c["id"], "color": c.get("color") or COLOR_LIBRE,
            "icono": c.get("icono") or ICONO_LIBRE, "orden": ORDEN_OTRAS if c["id"] == OTRAS else pos,
            "privada": bool(c.get("privada", False))}


def _por_alias(texto):
    """Entrada del catálogo cuyo id o alias coincide con `texto` (ver _norm), o None."""
    if not isinstance(texto, str) or not _norm(texto):
        return None
    for c in CATEGORIAS:
        if _norm(texto) == _norm(c["id"]) or _norm(texto) in {_norm(a) for a in c.get("alias", [])}:
            return c
    return None


def resolver_categoria(origen):
    """origen (dict o None) -> (objeto, aviso|None). Función pura: no imprime ni sale.
    objeto = {id, nombre, color, icono, orden, privada}, lo que se embebe en datos["categoria"]
    (la web ordena por `orden`; el aviso push oculta el nombre de las `privada`).
    1) origen.categoria si es un id del catálogo; 2) si no, ese texto o origen.proyecto como alias del catálogo
    (sin mayúsculas, tildes ni emoji); 3) si no, y hay origen.proyecto, una categoría libre armada con ese nombre
    (orden = tamaño del catálogo, color e ícono neutros); 4) si no hay nada, `otras` con un aviso que lista los ids."""
    origen = origen if isinstance(origen, dict) else {}
    por_id = {c["id"]: c for c in CATEGORIAS}
    pedida = origen.get("categoria")
    proyecto = origen.get("proyecto")

    if pedida == OTRAS and isinstance(proyecto, str):
        # «otras» a mano tapaba a un proyecto que sí está en el catálogo: si el proyecto resuelve por alias, gana él.
        c = _por_alias(proyecto)
        if c and c["id"] != OTRAS:
            return _objeto_categoria(c), None
    if isinstance(pedida, str) and pedida in por_id:
        return _objeto_categoria(por_id[pedida]), None
    for rotulo in ("categoria", "proyecto"):
        texto = origen.get(rotulo)
        c = _por_alias(texto)
        if c:
            aviso = f"aviso: origen.categoria '{texto}' no es un id del catálogo: usé '{c['id']}' por alias" if rotulo == "categoria" else None
            return _objeto_categoria(c), aviso
    if isinstance(proyecto, str) and _norm(proyecto):
        nombre = proyecto.strip()
        libre = {"id": _slug(nombre), "nombre": nombre, "color": COLOR_LIBRE, "icono": ICONO_LIBRE,
                 "orden": len(CATEGORIAS), "privada": False}
        aviso = None
        if isinstance(pedida, str) and pedida.strip():
            aviso = f"aviso: origen.categoria '{pedida}' no es un id ni un alias del catálogo: armé la categoría libre '{nombre}' desde origen.proyecto"
        return libre, aviso
    ids = ", ".join(por_id) or "(catálogo vacío)"
    base = por_id.get(OTRAS) or {"id": OTRAS, "nombre": "Otras", "color": COLOR_LIBRE, "icono": ICONO_LIBRE}
    motivo = f"categoria {pedida!r} no matchea" if pedida else "sin categoria ni proyecto"
    return (_objeto_categoria(base),
            f"aviso: la tanda cae en '{OTRAS}' ({motivo}). Ids válidos: {ids}. Pasá origen.categoria u origen.proyecto.")


ID_SEGURO = re.compile(r"[A-Za-z0-9_-]{1,40}")   # ids de sección: van a atributos y a selectores del html
IMAGEN_SRC = re.compile(r"data:image/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+")
IMAGEN_ANCHO = 1200          # px: alcanza para leer un mapa en el celu y no infla la fila
IMAGEN_TECHO = 900_000       # bytes del data: URI; arriba de esto, achicala o recortala antes


def palabras(s):
    return len(str(s).split())


def es_va(it):
    return str(it.get("reco", "")).strip().lower() == "va"


# Tipos de card. Sin `opciones` = sí/no.
# Con `opciones` = una opción (lista); con `varias: true` = varias (casillas). `reco` es el id (o la lista de ids).
ID_OPCION = re.compile(r"[a-z0-9_-]{1,30}")
REC_GO = ' data-rec="go"'


def recos_opcion(it):
    r = it.get("reco")
    return [str(x).strip() for x in r] if isinstance(r, list) else [str(r or "").strip()]


def validar_opciones(n, it):
    errores = []
    ops = it.get("opciones")
    if ops is None:
        for k in ("varias", "condiciones"):
            if k == "varias" and it.get(k) is not None:
                errores.append(f"ítem {n}: 'varias' va solo con 'opciones'")
        r = str(it.get("reco", "")).strip().lower()
        if r not in ("va", "no va"):
            errores.append(f"ítem {n}: reco tiene que ser 'va' o 'no va' (o el id de una opción, si la card trae 'opciones')")
        elif r == "no va":
            # la recomendada va siempre a la derecha: avanzar = lo que recomiendo
            errores.append(f"ítem {n}: en sí/no, la recomendada es siempre Va (el botón de la derecha). Si recomendás no hacerlo, "
                           "reescribí el título y los botones para que Va sea eso (ej.: «Seguir con la campaña» en vez de «Pausarla»)")
    else:
        if not (isinstance(ops, list) and 2 <= len(ops) <= 5):
            return [f"ítem {n}: 'opciones' tiene que ser una lista de 2 a 5 {{id, etiqueta, abierta?}}"]
        ids = []
        for o in ops:
            if not (isinstance(o, dict) and isinstance(o.get("id"), str) and ID_OPCION.fullmatch(o["id"])):
                errores.append(f"ítem {n}: cada opción necesita un 'id' en minúscula, sin espacios (a-z 0-9 _ -, hasta 30)")
                continue
            if o["id"] == "otra":
                errores.append(f"ítem {n}: el id 'otra' es de la página («Otra cosa…»): usá otro")
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
        rec = recos_opcion(it)
        if isinstance(it.get("reco"), list) and it.get("varias") is not True:
            errores.append(f"ítem {n}: 'reco' como lista va solo con 'varias': true")
        fuera = [r for r in rec if r not in ids]
        if fuera:
            errores.append(f"ítem {n}: reco '{', '.join(fuera)}' no es el id de ninguna opción ({', '.join(ids)})")
        for k in ("accion_va", "accion_no_va"):
            if it.get(k):
                errores.append(f"ítem {n}: '{k}' no va en una card con 'opciones' (la card es de un tipo o del otro)")
    cond = it.get("condiciones")
    if cond is not None:
        if not (isinstance(cond, list) and 1 <= len(cond) <= 3 and all(isinstance(c, str) and c.strip() for c in cond)):
            errores.append(f"ítem {n}: 'condiciones' tiene que ser una lista de 1 a 3 textos")
        else:
            for c in cond:
                if palabras(c) > 8:
                    errores.append(f"ítem {n}: una condición tiene {palabras(c)} palabras (techo 8)")
    return errores


def validar_campos(n, it):
    """`campos`: los valores editables de una card sí/no (botón Editar). Máx. 5, etiqueta ≤6 palabras, valor del tipo declarado."""
    cs = it.get("campos")
    if cs is None:
        return []
    if not (isinstance(cs, list) and 1 <= len(cs) <= MAX_CAMPOS):
        return [f"ítem {n}: 'campos' tiene que ser una lista de 1 a {MAX_CAMPOS} {{id, etiqueta, valor, tipo}}"]
    errores, ids = [], []
    if it.get("opciones") is not None:
        errores.append(f"ítem {n}: 'campos' va solo en cards sí/no (en una card con 'opciones', Editar abre la elección + el comentario, sin campos)")
    for c in cs:
        if not isinstance(c, dict):
            errores.append(f"ítem {n}: cada campo tiene que ser {{id, etiqueta, valor, tipo}}")
            continue
        cid = c.get("id")
        if not (isinstance(cid, str) and ID_OPCION.fullmatch(cid.lower()) and cid == cid.lower()):
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
        if tipo != "opcion" and c.get("opciones") is not None:
            errores.append(f"ítem {n}: 'opciones' va solo en un campo de tipo opcion ('{cid}')")
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
            else:
                if any(palabras(o) > 6 for o in ops):
                    errores.append(f"ítem {n}: una opción de '{cid}' pasa las 6 palabras")
                if val not in ops:
                    errores.append(f"ítem {n}: el valor de '{cid}' tiene que ser una de sus opciones")
        elif tipo == "textarea":
            if not (isinstance(val, str) and val.strip()):
                errores.append(f"ítem {n}: el valor del campo textarea '{cid}' tiene que ser un texto")
            elif len(val) > MAX_TEXTAREA:
                errores.append(f"ítem {n}: el valor de '{cid}' (textarea) pasa los {MAX_TEXTAREA} caracteres ({len(val)}): recortá el borrador")
            elif "⏎" in val:
                errores.append(f"ítem {n}: el valor de '{cid}' (textarea) no puede traer el carácter ⏎ (es el marcador del salto de línea en la respuesta)")
        else:  # texto
            if not (isinstance(val, str) and val.strip()):
                errores.append(f"ítem {n}: el valor del campo de texto '{cid}' tiene que ser un texto")
            elif len(val) > 200:
                errores.append(f"ítem {n}: el valor de '{cid}' pasa los 200 caracteres")
    return errores


def claves_aplicar(it):
    """Las claves que admite `aplicar` en esta card: va / no_va en sí/no, el id de cada opción en `opciones`; siempre `comun`."""
    ops = it.get("opciones")
    base = [o["id"] for o in ops if isinstance(o, dict) and isinstance(o.get("id"), str)] if isinstance(ops, list) else ["va", "no_va"]
    return base + ["comun"]


def validar_aplicar(n, it):
    ap = it.get("aplicar")
    if ap is None:
        return []
    if not isinstance(ap, dict) or not ap:
        return [f"ítem {n}: 'aplicar' tiene que ser un objeto {{va, no_va, comun?}} (o {{<id de opción>: plan}} en una card con 'opciones')"]
    errores = []
    admitidas = claves_aplicar(it)
    if not any(k in ap for k in admitidas if k != "comun"):
        errores.append(f"ítem {n}: 'aplicar' no trae el plan de ninguna respuesta (claves posibles: {', '.join(k for k in admitidas if k != 'comun')})")
    for k, v in ap.items():
        if k not in admitidas:
            errores.append(f"ítem {n}: 'aplicar.{k}' no es una respuesta de esta card (claves posibles: {', '.join(admitidas)})")
        elif not (isinstance(v, str) and v.strip()):
            errores.append(f"ítem {n}: 'aplicar.{k}' tiene que ser un texto con el plan")
        elif palabras(v) > TECHO_APLICAR:
            errores.append(f"ítem {n}: 'aplicar.{k}' tiene {palabras(v)} palabras (techo {TECHO_APLICAR})")
    return errores


def avisos_aplicar(d):
    """Aviso (no error) por cada card sin `aplicar`: si la sesión muere, nadie sabe qué hacer con la respuesta."""
    sin = [str(it.get("n", "?")) for it in d.get("items", []) if not it.get("aplicar")]
    if sin:
        return (f"aviso: {len(sin)} de {len(d.get('items', []))} ítems sin 'aplicar' (n: {', '.join(sin)}). Si la sesión no está viva cuando "
                "decidís, nadie sabe qué aplicar y la respuesta queda sin plan. Sumá el plan de cada respuesta (≤40 palabras).")
    return None


NOMBRE_TIPO = {"str": "texto", "list": "lista", "dict": "objeto", "int": "número", "float": "número", "bool": "sí/no", "NoneType": "vacío"}


def _tipo(x):
    return NOMBRE_TIPO.get(type(x).__name__, type(x).__name__)


def _lista_de_textos(x):
    return isinstance(x, list) and all(isinstance(i, str) and i.strip() for i in x)


def validar_intro(intro):
    """`intro` es una LISTA de bloques {titulo?, texto?, items?}. Un texto suelto pasaba la validación y rompía el armado inline."""
    if intro is None:
        return []
    forma = "una lista de bloques [{\"titulo\": ..., \"texto\": ..., \"items\": [...]}]"
    if not isinstance(intro, list):
        return [f"'intro' tiene que ser {forma}, recibí {_tipo(intro)}. Para un solo párrafo: [{{\"texto\": \"...\"}}]"]
    errores = []
    for i, b in enumerate(intro, 1):
        if not isinstance(b, dict):
            errores.append(f"intro[{i}] tiene que ser un bloque {{titulo?, texto?, items?}}, recibí {_tipo(b)}")
            continue
        for k in ("titulo", "texto"):
            if b.get(k) is not None and not isinstance(b[k], str):
                errores.append(f"intro[{i}].{k} tiene que ser un texto")
        if b.get("items") is not None and not _lista_de_textos(b["items"]):
            errores.append(f"intro[{i}].items tiene que ser una lista de textos")
    return errores


def validar_fyi(fyi):
    """`fyi` es UN objeto {titulo?, lead?, grupos:[{titulo?, items:[texto]}]}."""
    if fyi is None:
        return []
    if not isinstance(fyi, dict):
        return [f"'fyi' tiene que ser un objeto {{titulo, lead?, grupos:[{{titulo, items:[...]}}]}}, recibí {_tipo(fyi)}"]
    errores = []
    for k in ("titulo", "lead"):
        if fyi.get(k) is not None and not isinstance(fyi[k], str):
            errores.append(f"fyi.{k} tiene que ser un texto")
    grupos = fyi.get("grupos")
    if grupos is not None and not isinstance(grupos, list):
        errores.append("fyi.grupos tiene que ser una lista de grupos {titulo, items:[...]}")
        return errores
    for i, g in enumerate(grupos or [], 1):
        if not isinstance(g, dict) or not g.get("items"):
            errores.append(f"fyi.grupos[{i}] necesita 'items' (una lista de textos)")
            continue
        if not _lista_de_textos(g["items"]):
            errores.append(f"fyi.grupos[{i}].items tiene que ser una lista de textos")
        if g.get("titulo") is not None and not isinstance(g["titulo"], str):
            errores.append(f"fyi.grupos[{i}].titulo tiene que ser un texto")
    return errores


TECHOS_REVISION = {"titulo": 12, "hice": 25, "verifique": 25, "mirar": 25}
OBLIGATORIOS_REVISION = ("n", "titulo", "hice", "verifique", "mirar")
PROHIBIDOS_REVISION = ("reco", "reco_motivo", "accion_va", "accion_no_va", "antecedentes", "si_no_decidis", "impacto", "opciones", "campos")
URL_HTTPS = re.compile(r"https://[^\s\"'<>]+")


def es_revision(it):
    return isinstance(it, dict) and it.get("tipo") == "revision"


def validar_revision(n, it):
    """Ítem `tipo: "revision"`. Sin reco/impacto/opciones (no es una decisión). Solo entra si trae algo para mirar:
    `imagen` (con `link` https) o `link` https; si no, va como una línea en el `fyi` de la tanda (anti-inundación)."""
    errores = []
    for k in OBLIGATORIOS_REVISION:
        if it.get(k) in (None, ""):
            errores.append(f"ítem {n}: falta '{k}' (una revisión lleva n, titulo, hice, verifique y mirar)")
    for campo, techo in TECHOS_REVISION.items():
        v = it.get(campo)
        if v in (None, ""):
            continue
        if not isinstance(v, str):
            errores.append(f"ítem {n}: '{campo}' tiene que ser un texto")
        elif palabras(v) > techo:
            errores.append(f"ítem {n}: '{campo}' tiene {palabras(v)} palabras (techo {techo} en una revisión)")
    prohibidos = [k for k in PROHIBIDOS_REVISION if it.get(k) not in (None, "", [], {})]
    if prohibidos:
        errores.append(f"ítem {n}: una revisión no lleva {', '.join(repr(k) for k in prohibidos)} (es de una decisión sí/no u opciones): "
                       "sacalos, o armá una card de decisión")
    img, link = it.get("imagen"), it.get("link")
    if not img and not link:
        errores.append(f"ítem {n}: revisión sin nada para mirar: va como una línea en el `fyi` de la tanda, no como card")
    else:
        if link and not (isinstance(link, str) and URL_HTTPS.fullmatch(link)):
            errores.append(f"ítem {n}: 'link' tiene que ser una URL https")
        if img:
            errores += validar_imagen(n, img)
            if isinstance(img, dict) and not img.get("link") and not link:
                errores.append(f"ítem {n}: la imagen de una revisión necesita 'link' https (el de la imagen o un 'link' del ítem)")
    ap = it.get("aplicar")
    if ap is not None:
        if not (isinstance(ap, dict) and ap):
            errores.append(f"ítem {n}: 'aplicar' de una revisión es {{comun: texto}} (o se omite)")
        else:
            for k, v in ap.items():
                if k != "comun":
                    errores.append(f"ítem {n}: 'aplicar.{k}' no va en una revisión (solo 'comun': no hay un Va ni un No va)")
                elif not (isinstance(v, str) and v.strip()):
                    errores.append(f"ítem {n}: 'aplicar.comun' tiene que ser un texto")
                elif palabras(v) > TECHO_APLICAR:
                    errores.append(f"ítem {n}: 'aplicar.comun' tiene {palabras(v)} palabras (techo {TECHO_APLICAR})")
    return errores


def validar(d):
    errores = []
    for k in ("titulo", "fecha", "clave", "items"):
        if not d.get(k):
            errores.append(f"falta '{k}' en la raíz")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(d.get("fecha", ""))):
        errores.append("fecha tiene que ser AAAA-MM-DD")
    origen = d.get("origen")
    if origen is not None:
        if not isinstance(origen, dict):
            errores.append("'origen' tiene que ser {sesion_titulo, skill, proyecto, categoria}")
        else:
            for k in ("sesion_titulo", "skill", "proyecto", "categoria"):
                if origen.get(k) is not None and not isinstance(origen[k], str):
                    errores.append(f"origen.{k} tiene que ser un string")
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
        if "n" in it and (not isinstance(it["n"], int) or isinstance(it["n"], bool)):
            errores.append(f"ítem {n}: 'n' tiene que ser un entero")
        if it.get("seccion") is not None and not (isinstance(it["seccion"], str) and ID_SEGURO.fullmatch(it["seccion"])):
            errores.append(f"ítem {n}: 'seccion' solo admite letras, números, _ y - (hasta 40)")
        if it.get("svg") is not None and not isinstance(it["svg"], str):
            errores.append(f"ítem {n}: 'svg' tiene que ser un texto")
        if es_revision(it):   # card de revisión: no es una decisión, no pasa por los chequeos de sí/no
            if n in vistos:
                errores.append(f"ítem {n}: número repetido")
            vistos.add(n)
            errores += validar_revision(n, it)
            continue
        for k in OBLIGATORIOS:
            if it.get(k) in (None, ""):
                errores.append(f"ítem {n}: falta '{k}'")
        if n in vistos:
            errores.append(f"ítem {n}: número repetido")
        vistos.add(n)
        errores += validar_opciones(n, it)
        errores += validar_aplicar(n, it)
        errores += validar_campos(n, it)
        if it.get("icono") and it["icono"] not in ICONOS:
            errores.append(f"ítem {n}: icono '{it.get('icono')}' no existe (o pasá 'svg' propio)")
        dib = it.get("dibujo")
        if dib is not None and not (isinstance(dib, dict) and isinstance(dib.get("svg"), str) and dib.get("svg")):
            errores.append(f"ítem {n}: 'dibujo' tiene que ser {{viewBox, svg, alt}} con svg")
        imp = it.get("impacto")
        if not (isinstance(imp, dict) and isinstance(imp.get("positivo"), str) and imp["positivo"].strip()
                and isinstance(imp.get("negativo"), str) and imp["negativo"].strip()):
            errores.append(f"ítem {n}: falta 'impacto' {{positivo, negativo}} (obligatorio, los dos lados)")
        errores += validar_imagen(n, it.get("imagen"))
        if it.get("accent") not in (None, "", "warning", "danger"):
            errores.append(f"ítem {n}: accent solo 'warning' o 'danger'")
        for campo, techo in TECHOS.items():
            if palabras(it.get(campo, "")) > techo:
                errores.append(f"ítem {n}: '{campo}' tiene {palabras(it[campo])} palabras (techo {techo})")
        ant = it.get("antecedentes")
        if ant is not None:
            if not (isinstance(ant, list) and 1 <= len(ant) <= 3 and all(isinstance(a, str) and a.strip() for a in ant)):
                errores.append(f"ítem {n}: 'antecedentes' tiene que ser una lista de 1 a 3 textos")
            else:
                for a in ant:
                    if palabras(a) > TECHO_ANTECEDENTE:
                        errores.append(f"ítem {n}: un antecedente tiene {palabras(a)} palabras (techo {TECHO_ANTECEDENTE})")
        snd = it.get("si_no_decidis")
        if snd is not None:
            if not (isinstance(snd, str) and snd.strip()):
                errores.append(f"ítem {n}: 'si_no_decidis' tiene que ser un texto")
            elif palabras(snd) > TECHO_ANTECEDENTE:
                errores.append(f"ítem {n}: 'si_no_decidis' tiene {palabras(snd)} palabras (techo {TECHO_ANTECEDENTE})")
        venc = it.get("vence")
        if venc is not None:
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(venc)):
                    raise ValueError
                datetime.date.fromisoformat(venc)
            except ValueError:
                errores.append(f"ítem {n}: 'vence' tiene que ser una fecha AAAA-MM-DD válida")
        det = it.get("detalle")
        if det is not None:
            if not (isinstance(det, str) and det.strip()):
                errores.append(f"ítem {n}: 'detalle' tiene que ser un texto")
            elif palabras(det) > TECHO_DETALLE:
                errores.append(f"ítem {n}: 'detalle' tiene {palabras(det)} palabras (techo {TECHO_DETALLE})")
        for campo in ("accion_va", "accion_no_va"):
            if it.get(campo) and palabras(it[campo]) > 6:
                errores.append(f"ítem {n}: '{campo}' tiene {palabras(it[campo])} palabras (techo 6: es la etiqueta del botón)")
    errores += validar_intro(d.get("intro"))
    errores += validar_fyi(d.get("fyi"))
    return errores


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
            self.quitado.append(f"</{tag}> sin abrir")   # un </svg> suelto no puede cerrar el svg de la plantilla
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


def validar_imagen(n, img):
    if img is None:
        return []
    if not isinstance(img, dict):
        return [f"ítem {n}: 'imagen' tiene que ser {{path | src, alt, link}}"]
    err = []
    if img.get("path"):
        f = Path(str(img["path"])).expanduser()
        if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp") or not f.is_file():
            err.append(f"ítem {n}: imagen.path no es un png/jpg/webp que exista ({img['path']})")
    elif not (isinstance(img.get("src"), str) and IMAGEN_SRC.fullmatch(img["src"])):
        err.append(f"ítem {n}: imagen necesita 'path' local o 'src' data:image/(png|jpeg|webp);base64")
    if not (isinstance(img.get("alt"), str) and img["alt"].strip()):
        err.append(f"ítem {n}: imagen.alt dice qué muestra (obligatorio)")
    if img.get("link") is not None and not (isinstance(img["link"], str) and re.fullmatch(r"https://[^\s\"'<>]+", img["link"])):
        err.append(f"ítem {n}: imagen.link tiene que ser una URL https")
    return err


def _achicar_pillow(f, out, tipo):
    """Achica con Pillow a IMAGEN_ANCHO de ancho (respeta la orientación EXIF). Una imagen que ya entra se copia tal cual."""
    from PIL import Image, ImageOps
    with Image.open(f) as im:
        if im.width <= IMAGEN_ANCHO:
            out.write_bytes(f.read_bytes())
            return
        im = ImageOps.exif_transpose(im)
        remuestreo = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
        im = im.resize((IMAGEN_ANCHO, max(1, round(im.height * IMAGEN_ANCHO / im.width))), remuestreo)
        if tipo == "jpeg":
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            im.save(out, "JPEG", quality=85, optimize=True)
        elif tipo == "webp":
            im.save(out, "WEBP", quality=85)
        else:
            im.save(out, "PNG", optimize=True)


def _achicar_sips(f, out):
    """Achica con sips (macOS) a IMAGEN_ANCHO de ancho; si ya entra, copia el original."""
    ancho = subprocess.run(["sips", "-g", "pixelWidth", str(f)], capture_output=True, text=True).stdout
    m = re.search(r"pixelWidth: (\d+)", ancho)
    if m and int(m.group(1)) > IMAGEN_ANCHO:
        subprocess.run(["sips", "--resampleWidth", str(IMAGEN_ANCHO), str(f), "--out", str(out)],
                       capture_output=True, check=True)
    else:
        out.write_bytes(f.read_bytes())


def imagen_a_src(path):
    """png/jpg/webp local -> data: URI, achicado a IMAGEN_ANCHO de ancho. Herramienta, en este orden:
    Pillow (si se puede importar), sips (si está en el PATH), o el original tal cual si entra bajo IMAGEN_TECHO."""
    f = Path(path).expanduser()
    tipo = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp"}[f.suffix.lower()]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / ("img" + f.suffix.lower())
        hecho = False
        try:
            _achicar_pillow(f, out, tipo)
            hecho = True
        except ImportError:
            pass   # sin Pillow: se prueba lo siguiente
        except Exception:
            pass   # Pillow no pudo con esta imagen (formato raro): se prueba lo siguiente
        if not hecho and shutil.which("sips"):
            _achicar_sips(f, out)
            hecho = True
        if not hecho:
            out.write_bytes(f.read_bytes())   # sin herramienta: va el original; el techo de abajo decide si entra
        # Un mapa es casi todo blanco: pngquant lo deja en ~1/4. Es opcional: si no está, va sin.
        if tipo == "png" and shutil.which("pngquant"):
            subprocess.run(["pngquant", "--force", "--quality", "60-85", "--output", str(out), str(out)], capture_output=True)
        src = f"data:image/{tipo};base64," + base64.b64encode(out.read_bytes()).decode("ascii")
    if len(src) > IMAGEN_TECHO:
        raise ValueError(f"la imagen {f.name} pesa {len(src) // 1000} KB como data: URI (techo {IMAGEN_TECHO // 1000}). "
                         "Instalá Pillow (pip install pillow) para que se achique sola, o achicala antes")
    return src


def sanear_datos(d):
    """Sanea in situ todo svg del JSON (dibujo.svg y svg de ícono propio). Avisa por stderr qué sacó.
    Convierte imagen.path en imagen.src: el path local no viaja a la web."""
    for it in d.get("items", []):
        img = it.get("imagen")
        if isinstance(img, dict) and img.get("path"):
            img["src"] = imagen_a_src(img.pop("path"))
        blancos = [(it, "svg", "svg"), (it.get("dibujo"), "svg", "dibujo")]
        for dueno, clave, rotulo in blancos:
            if isinstance(dueno, dict) and isinstance(dueno.get(clave), str):
                limpio, quitado = sanear_svg(dueno[clave])
                if quitado:
                    print(f"aviso: SVG saneado en ítem {it.get('n', '?')} ({rotulo}): quité " + ", ".join(quitado), file=sys.stderr)
                dueno[clave] = limpio


def con_csp(doc):
    """Mete un CSP por meta con el sha256 de cada <script> inline. Sin 'unsafe-inline' en script-src:
    un handler inline inyectado no corre. Se calcula sobre el documento ya armado, así sigue valiendo
    si la plantilla cambia (salvo que empiece a usar on*= o javascript:, que el CSP bloquearía)."""
    hashes = []
    for m in re.finditer(r"<script\b[^>]*>(.*?)</script>", doc, re.S | re.I):
        h = base64.b64encode(hashlib.sha256(m.group(1).encode("utf-8")).digest()).decode("ascii")
        hashes.append(f"'sha256-{h}'")
    csp = ("default-src 'none'; script-src " + " ".join(hashes or ["'none'"]) +
           "; style-src 'unsafe-inline'; img-src data:; font-src data:; base-uri 'none'; form-action 'none'")
    meta = f'<meta http-equiv="Content-Security-Policy" content="{csp}">'
    # Después del charset (que tiene que ir en los primeros 1024 bytes); el CSP rige para lo que viene detrás.
    if re.search(r"<meta charset[^>]*>", doc, re.I):
        return re.sub(r"(<meta charset[^>]*>)", lambda m: m.group(1) + "\n" + meta, doc, count=1, flags=re.I)
    return doc.replace("<head>", "<head>\n" + meta, 1)


def armar_html(d):
    # `<!--` dentro de un <script> cambia el estado del parser de html: se escapa junto con `</`.
    blob = json.dumps(d, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\u0021--")
    iconos = json.dumps(ICONOS, ensure_ascii=False).replace("</", "<\\/")
    s = (AQUI / "plantilla.html").read_text(encoding="utf-8")
    doc = (s.replace("/*__DATA__*/null", blob)
            .replace("/*__ICONOS__*/{}", iconos)
            .replace("__TITULO__", H.escape(d["titulo"])))
    return con_csp(doc)


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
    # Acepta comillas simples y dobles: con simples no traducía nada y el dibujo salía roto.
    return re.sub(r'class=(["\'])(\w+)\1', lambda m: f'style="{CLASES_INLINE[m.group(2)]}"' if m.group(2) in CLASES_INLINE else m.group(0), svg)


def inline_revision(it):
    """Card de revisión para el widget inline: tres líneas, la imagen o el link, un solo botón (Revisado) y el comentario."""
    e = H.escape
    n = e(str(it["n"]))
    img = it.get("imagen") or {}
    link = img.get("link") or it.get("link")
    lineas = "".join(f'<p style="margin:2px 0"><span style="font-weight:500">{rot}:</span> {e(it[k])}</p>'
                     for k, rot in (("hice", "Qué hice"), ("verifique", "Qué verifiqué"), ("mirar", "Qué te queda mirar")))
    foto = (f'<div style="margin:6px 0 4px"><img src="{e(img["src"])}" alt="{e(img.get("alt") or "")}" '
            'style="display:block;width:100%;height:auto;border-radius:8px;border:1px solid var(--border)"></div>') if img.get("src") else ""
    return ('<div class="elicit-group">'
            f'<label class="elicit-question">{n} · REVISIÓN · {e(it["titulo"])}</label>'
            f'<div style="font-size:14px;line-height:1.5;color:var(--text-secondary);margin:4px 0 8px">{lineas}</div>'
            + foto
            + (f'<div style="font-size:12px;margin-bottom:8px">Abrir: {e(link)}</div>' if link else "")
            + f'<div class="elicit-pills" data-name="decision_{n}" data-multi="false">'
              '<button type="button" class="elicit-pill" data-value="Revisado">Revisado</button></div>'
            + f'<textarea class="elicit-textarea" data-name="comentario_{n}" rows="1" placeholder="Comentar sirve para pedir un cambio"></textarea>'
            + '</div>')


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
           f'<div class="elicit-header">{HEADER_SVG}<span>{e(d.get("encabezado") or "Botonera")}</span></div>',
           '<div class="elicit-body">']
    for b in (d.get("intro") or []):
        cuerpo = ""
        if b.get("titulo"):
            cuerpo += f'<div style="font-weight:600;font-size:13px;margin-bottom:4px">{e(b["titulo"])}</div>'
        if b.get("texto"):
            cuerpo += "".join(f'<p style="font-size:13px;color:var(--text-secondary);margin:2px 0">{e(p)}</p>' for p in str(b["texto"]).split("\n\n"))
        if b.get("items"):
            cuerpo += '<ul style="margin:2px 0 0 16px;font-size:13px;color:var(--text-secondary)">' + "".join(f'<li>{e(i)}</li>' for i in b["items"]) + '</ul>'
        out.append(f'<div style="background:var(--surface-1);border-radius:12px;padding:10px 12px;margin-bottom:8px">{cuerpo}</div>')
    for it in d["items"]:
        if es_revision(it):
            out.append(inline_revision(it))
            continue
        n, va = e(str(it["n"])), es_va(it)
        tag = {"danger": " · ojo", "warning": " · sensible"}.get(it.get("accent") or "", "")
        imp = it.get("impacto") or {}
        det_imp = (f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px">'
                   f'<div style="padding:6px 8px;border-left:3px solid var(--text-success);background:var(--bg-success)"><span style="font-weight:500">Impacto positivo</span><br>{e(imp.get("positivo") or "nada relevante")}</div>'
                   f'<div style="padding:6px 8px;border-left:3px solid var(--text-danger);background:var(--bg-danger)"><span style="font-weight:500">Impacto negativo</span><br>{e(imp.get("negativo") or "nada relevante")}</div></div>') if imp else ""
        det = (f'<p style="margin:6px 0 0">{e(it["detalle"])}</p>' if it.get("detalle") else "") + det_imp + "".join(
            f'<p style="margin:6px 0 0"><span style="font-weight:500">{lab}:</span> {e(it[k])}</p>'
            for k, lab in (("porque", "Por qué"), ("si_va", "Si va"), ("si_no_va", "Si no va"), ("fuente", "Fuente")) if it.get(k))
        icono = it.get("svg") or (ICONOS[it["icono"]] if it.get("icono") else "")
        dib = it.get("dibujo")
        img = it.get("imagen") or {}
        img_html = (f'<div style="margin:6px 0 4px"><img src="{e(img["src"])}" alt="{e(img.get("alt") or "")}" '
                    f'style="display:block;width:100%;height:auto;border-radius:8px;border:1px solid var(--border)">'
                    + (f'<div style="font-size:12px;margin-top:3px">Abrir afuera: {e(img["link"])}</div>' if img.get("link") else "")
                    + '</div>') if img.get("src") else ""
        acc_va = ' data-rec="go"' if va else ''
        acc_no = '' if va else ' data-rec="no"'
        ops = it.get("opciones")
        if ops:
            recs = recos_opcion(it)
            reco_txt = ", ".join(o["etiqueta"] for o in ops if o["id"] in recs)
            pills = (f'<div class="elicit-pills" data-name="decision_{n}" data-multi="{"true" if it.get("varias") else "false"}">'
                     + "".join(f'<button type="button" class="elicit-pill" data-value="{e(o["id"])}"{REC_GO if o["id"] in recs else ""}>{e(o["etiqueta"])}</button>' for o in ops)
                     + '</div>')
            va = True
        else:
            reco_txt = (it.get("accion_va") if va else it.get("accion_no_va")) or ("Va" if va else "No va")
            pills = (f'<div class="elicit-pills" data-name="decision_{n}" data-multi="false">'
                     # No va a la izquierda, Va (la recomendada) a la derecha, como en el swipe
                     f'<button type="button" class="elicit-pill" data-value="No va"{acc_no}>{e(it.get("accion_no_va") or "No va")}</button>'
                     f'<button type="button" class="elicit-pill" data-value="Va"{acc_va}>{e(it.get("accion_va") or "Va")}</button></div>')
        reco = (f'<span style="color:var(--text-{"success" if va else "danger"});font-weight:500">{e(reco_txt)}</span>')
        # Antecedentes y "si no decidís" van visibles, chicos, entre el contexto y la recomendación.
        previo = "".join(f'<br><span style="font-size:12px">· {e(a)}</span>' for a in (it.get("antecedentes") or []))
        if it.get("si_no_decidis"):
            previo += f'<br><span style="font-size:12px">Si no decidís: {e(it["si_no_decidis"])}</span>'
        out.append(
            '<div class="elicit-group">'
            f'<label class="elicit-question">{n}{tag} · {e(it["titulo"])}</label>'
            + (f'<div style="margin:6px 0 4px;padding:10px;border-radius:12px;background:var(--surface-1)"><svg viewBox="{e(dib.get("viewBox") or "0 0 240 100")}" style="display:block;width:100%;max-width:320px;height:auto;margin:0 auto" role="img" aria-label="{e(dib.get("alt") or "")}">{svg_inline(dib["svg"])}</svg></div>' if dib else "")
            + img_html
            + '<div style="display:flex;gap:14px;align-items:flex-start;margin:4px 0 10px">'
            + (f'<div style="flex:0 0 64px;height:64px;border-radius:12px;background:{fondo.get(it.get("accent") or "", "var(--bg-accent)")};display:flex;align-items:center;justify-content:center">'
               f'<svg viewBox="0 0 64 64" width="46" height="46" aria-hidden="true">{svg_inline(icono)}</svg></div>' if icono and not dib else "")
            +             f'<div style="font-size:14px;line-height:1.5;color:var(--text-secondary)">{e(it["contexto"])}{previo}'
            f'<br><span style="font-size:13px">El agente recomienda {reco}: {e(it["reco_motivo"])}</span></div></div>'
            + pills +
            f'<textarea class="elicit-textarea" data-name="comentario_{n}" rows="1" placeholder="Comentario (opcional)"></textarea>'
            + (f'<details style="font-size:13px;color:var(--text-secondary);margin-top:6px"><summary style="cursor:pointer;color:var(--text-accent)">Ver el detalle</summary>{det}</details>' if det else "")
            + '</div>')
    f = d.get("fyi")
    if f:
        bloque = f'<div style="font-weight:600;font-size:13px;margin-bottom:3px">{e(f.get("titulo") or "Para tu info — no son decisiones")}</div>'
        if f.get("lead"):
            bloque += f'<p style="font-size:12px;color:var(--text-secondary);margin-bottom:6px">{e(f["lead"])}</p>'
        for g in (f.get("grupos") or []):
            if g.get("titulo"):
                bloque += f'<div style="font-weight:600;font-size:12px;margin:6px 0 1px">{e(g["titulo"])}</div>'
            bloque += '<ul style="margin:0 0 0 16px;font-size:12px;color:var(--text-secondary)">' + "".join(f'<li>{e(i)}</li>' for i in (g.get("items") or [])) + '</ul>'
        out.append(f'<div style="border:1px dashed var(--border);border-radius:12px;padding:10px 12px;margin:4px 0 8px">{bloque}</div>')
    out.append('<div class="elicit-group"><label class="elicit-question">¿Algo que la botonera no previó?</label>'
               '<textarea class="elicit-textarea" data-name="notas" placeholder="Opcional"></textarea></div>')
    out.append('</div><div class="elicit-footer"><button type="button" class="elicit-skip">Saltar</button>'
               '<button type="button" class="elicit-submit">Enviar respuesta</button></div></form>')
    return "\n".join(out)


def id_sesion():
    """El session_id que viaja con la tanda: el de la sesión de Claude Code (CLAUDE_CODE_HOST_SESSION_ID) o,
    si no hay, BM_SESSION_ID (lo pone un bot: `bot-<nombre>`). Sin ninguno, None."""
    return (os.environ.get("CLAUDE_CODE_HOST_SESSION_ID") or os.environ.get("BM_SESSION_ID") or "").strip() or None


def marcar_sesion(session_id):
    """Deja la marca que habilita a entregar.py en esta sesión: sin marca, el hook sale sin ir a la red.
    Solo para sesiones de Claude Code: un id `bot-…` no tiene hook que despertar, no se marca."""
    if not session_id or session_id.startswith(PREFIJO_BOT):
        return
    try:
        d = Path(os.path.expanduser("~/.cache/botonera/sesiones"))
        d.mkdir(parents=True, exist_ok=True)
        (d / session_id).touch()
    except OSError:
        pass


def publicar(datos):
    """Sube la tanda a la botonera. Nunca levanta: el armado local ya está hecho.
    Devuelve el código de salida: 0 si se publicó (o si no hay config: no hay a dónde publicar), 2 si la clave ya estaba
    decidida (no se publicó nada) y 1 si el servidor rechazó la tanda o la red falló."""
    if not maestro.config():
        print("maestro: sin config (~/.config/botonera/env), no publicado")
        return 0
    origen = datos.get("origen") or {}
    if "categoria" not in datos:
        datos["categoria"], _ = resolver_categoria(origen)
    try:
        res = maestro.rpc("bm_publicar", {
            "p_secret": maestro.config()["BM_SECRET"],
            "p_clave": datos["clave"],
            "p_session_id": id_sesion(),
            "p_sesion_titulo": origen.get("sesion_titulo"),
            "p_skill": origen.get("skill") or "botonera",
            "p_proyecto": origen.get("proyecto"),
            "p_titulo": datos["titulo"],
            "p_n_items": len(datos["items"]),
            "p_datos": datos,
            "p_html": armar_html(datos),   # siempre el html completo, aunque lo local sea inline
        })
    except maestro.ErrorMaestro as ex:
        print(f"maestro: falló ({ex})", file=sys.stderr)
        return 1
    # El servidor contesta un texto: "creada", "actualizada" o "ya_decidida:<estado>" (no pisa).
    quedo = str(res or "").strip().lower()
    if quedo in ("creada", "actualizada"):
        print(f"maestro: {quedo} · {datos['clave']}")
        marcar_sesion(id_sesion())
        return 0
    if quedo.startswith("ya_decidida:"):
        print(f"maestro: NO publicado: la clave {datos['clave']} ya está {quedo.split(':', 1)[1]}. Usá una clave nueva.", file=sys.stderr)
        return 2
    print(f"maestro: respuesta inesperada del servidor ({quedo!r}), no sé si se publicó", file=sys.stderr)
    return 1


RE_REEMPLAZA = re.compile(r"([A-Za-z0-9._-]{1,120})#(\d{1,4})(?::(\d{1,4}))?")


def sacar_reemplaza(args):
    """Saca de los args cada `--reemplaza <clave>#<n>[:<m>]` y los devuelve como [(clave, n, m)] (m = la card nueva, default 1)."""
    resto, out, i = [], [], 0
    while i < len(args):
        if args[i] == "--reemplaza":
            m = RE_REEMPLAZA.fullmatch(args[i + 1]) if i + 1 < len(args) else None
            if not m:
                sys.exit("--reemplaza necesita <clave>#<n> (opcional :<m>, la card nueva), p. ej. --reemplaza botonera-2026-11-21-x#2")
            out.append((m.group(1), int(m.group(2)), int(m.group(3) or 1)))
            i += 2
        else:
            resto.append(args[i])
            i += 1
    return resto, out


def reemplazar(datos, reemplazos):
    """«Ya no aplica»: marca cada card vieja con bm_reemplazar, DESPUÉS de publicar la tanda nueva.
    Devuelve el código de salida: 0 si todo salió, 2 si alguna no se pudo marcar (la nueva ya quedó publicada)."""
    cfg = maestro.config()
    if not cfg:
        print("maestro: sin config, no se marcó ninguna card como reemplazada", file=sys.stderr)
        return 2
    # antes de dar una card por reemplazada, la nueva tiene que existir en la base
    try:
        nueva = maestro.rpc("bm_retomar", {"p_secret": cfg["BM_SECRET"], "p_clave": datos["clave"]})
    except maestro.ErrorMaestro as ex:
        nueva = {"estado": f"error: {ex}"}
    if not isinstance(nueva, dict) or nueva.get("estado") in (None, "no_existe") or str(nueva.get("estado")).startswith("error"):
        print(f"reemplaza: {datos['clave']} no está en la base: no se marcó ninguna card como reemplazada "
              f"({(nueva or {}).get('estado') if isinstance(nueva, dict) else nueva})", file=sys.stderr)
        return 2
    items_nueva = nueva.get("items") or []
    fallo = False
    for clave, n, m in reemplazos:
        por = f"{datos['clave']}#{m}"
        if not any(isinstance(i, dict) and i.get("n") == m for i in items_nueva):
            print(f"reemplaza: la tanda {datos['clave']} que está en la base no tiene card {m} (¿se publicó otra versión?): {clave}#{n} NO marcada", file=sys.stderr)
            fallo = True
            continue
        try:
            res = str(maestro.rpc("bm_reemplazar", {"p_secret": cfg["BM_SECRET"], "p_clave": clave, "p_n": n, "p_por": por}) or "").strip()
        except maestro.ErrorMaestro as ex:
            print(f"reemplaza: {clave}#{n} falló ({ex})", file=sys.stderr)
            fallo = True
            continue
        if res.startswith("reemplazada:"):
            activas = int(res.split(":", 1)[1] or 0)
            print(f"reemplaza: {clave}#{n} ya no aplica; la reemplaza {por}")
            if activas == 0:
                print(f"aviso: a {clave} no le queda ninguna card activa: nadie la va a contestar. Dejá de esperarla (cortá el esperar.py de esa clave).", file=sys.stderr)
        elif res.startswith("ya_decidida:"):
            print(f"aviso: {clave} ya estaba {res.split(':', 1)[1]}: la card {n} no se toca (su respuesta ya salió).", file=sys.stderr)
        else:
            print(f"reemplaza: {clave}#{n} NO marcada ({res})", file=sys.stderr)
            fallo = True
    return 2 if fallo else 0


def main():
    args = sys.argv[1:]
    args, reemplazos = sacar_reemplaza(args)
    forzado = next((a for a in args if a in ("--html", "--inline")), None)
    quiere_publicar = "--publicar" in args
    args = [a for a in args if a not in ("--html", "--inline", "--publicar")]
    if len(args) != 2:
        sys.exit("uso: python3 armar.py [--html|--inline] [--publicar [--reemplaza <clave>#<n>]] datos.json salida.html")
    if reemplazos and not quiere_publicar:
        sys.exit("--reemplaza solo va con --publicar: la card vieja se marca después de publicar la nueva")
    datos = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    errores = validar(datos)
    if quiere_publicar and (id_sesion() or "").startswith(PREFIJO_BOT) and not str(datos.get("clave", "")).startswith(PREFIJO_BOT):
        errores.append(f"una sesión de bot (BM_SESSION_ID={id_sesion()}) solo publica claves que empiezan con {PREFIJO_BOT}: "
                       f"'{datos.get('clave')}' no vale")
    for clave, n, m in reemplazos:
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,120}", str(datos.get("clave", ""))):
            errores.append(f"--reemplaza: la clave '{datos.get('clave')}' tiene que ser [A-Za-z0-9._-] (hasta 120) para poder enlazar la card vieja")
        if clave == datos.get("clave"):
            errores.append(f"--reemplaza {clave}#{n}: una tanda no se reemplaza a sí misma (usá la misma clave para republicar)")
        if not any(it.get("n") == m for it in datos.get("items", [])):
            errores.append(f"--reemplaza {clave}#{n}:{m}: esta tanda no tiene card {m}")
        if (id_sesion() or "").startswith(PREFIJO_BOT) and not clave.startswith(PREFIJO_BOT):
            errores.append(f"--reemplaza {clave}#{n}: una sesión de bot solo reemplaza cards de claves {PREFIJO_BOT}")
    if errores:
        print("\n".join(errores), file=sys.stderr)
        sys.exit(1)
    try:
        sanear_datos(datos)   # antes de armar nada: html, inline y lo que sube --publicar salen del mismo JSON limpio
    except (ValueError, subprocess.CalledProcessError) as ex:
        sys.exit(f"imagen: {ex}")
    datos["categoria"], aviso_cat = resolver_categoria(datos.get("origen"))   # nunca frena: la categoría viaja embebida en datos
    if aviso_cat:
        print(aviso_cat, file=sys.stderr)
    aviso_ap = avisos_aplicar(datos)
    if aviso_ap:
        print(aviso_ap, file=sys.stderr)
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
    if quiere_publicar:
        codigo = publicar(datos)
        if codigo == 0 and reemplazos:
            codigo = reemplazar(datos, reemplazos)
        sys.exit(codigo)


if __name__ == "__main__":
    main()

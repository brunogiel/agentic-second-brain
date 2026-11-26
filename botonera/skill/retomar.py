#!/usr/bin/env python3
"""Retoma una botonera decidida cuando la sesión que la publicó ya no está viva.

Uso:
  python3 retomar.py <clave>                 # imprime el brief: la respuesta + el plan `aplicar` que le toca a cada ítem
  python3 retomar.py <clave> --tomar         # igual, pero antes pasa decidida -> recibida (como esperar.py), para poder cerrar con `aplicada`
  python3 retomar.py <clave> --json          # lo mismo en JSON, para que lo lea otro script
  python3 retomar.py --desde respuesta.json  # prueba en seco: lee la respuesta de la RPC desde un archivo, sin red

Por qué existe: `esperar.py` muere si se cierra la app, el hook `entregar.py` solo corre si la sesión recibe otro mensaje,
y una limpieza periódica podría archivar las tandas decididas sin aplicarlas. La decisión queda guardada en la base con su
clave; este script la lee y arma un brief que se entiende solo, así cualquier sesión nueva la aplica.

Lee con `bm_retomar` (lectura pura, secret normal). Cada ítem puede traer `aplicar` {va, no_va | <id de opción>, comun}:
el plan concreto de cada respuesta. El comentario del usuario manda sobre el plan.
Un `va con cambios` de Editar trae `· campos: id=nuevo (antes viejo); …`: esos valores reemplazan a los del plan.
Un ítem `sin marcar` o `después` no se aplica nunca. Un `revisado` (card de revisión) tampoco: no hay nada que aplicar.
Un `rot` (el usuario tocó «+info»: no entendió la card) tampoco es un Va: se reescribe la card con `rot.md` (en la carpeta
de este skill). Un `comentario` sin decidir tampoco es un Va.

Sale 0 siempre que pueda leer; 1 si la clave no existe o no hay config/red.
"""
import json
import re
import sys
from pathlib import Path

import maestro

AQUI = Path(__file__).resolve().parent
LINEA = re.compile(r"^(\d+)\.\s+(.*)$")
SEP_COMENTARIO = " · comentario: "
SEP_CAMPOS = " · campos: "   # Editar: «· campos: id=nuevo (antes viejo); …», entre la acción y el comentario


def parsear_respuesta(texto):
    """'/botonera respuesta · <clave>\\nN. va · título → acción · comentario: …' -> ({n: {...}}, notas).

    Cada ítem: veredicto (el texto crudo antes del primer « · »), clave_respuesta ('va' | 'no_va' | ['id',…] | None),
    comentario (puede ocupar varias líneas). `clave_respuesta` None = no hay nada que aplicar con un plan."""
    items, notas, actual = {}, [], None
    for linea in (texto or "").splitlines():
        m = LINEA.match(linea)
        if m:
            n, resto = int(m.group(1)), m.group(2)
            veredicto = resto.split(" · ", 1)[0].strip()
            comentario = resto.split(SEP_COMENTARIO, 1)[1].strip() if SEP_COMENTARIO in resto else ""
            head = resto.split(SEP_COMENTARIO, 1)[0]
            campos = head.split(SEP_CAMPOS, 1)[1].strip() if SEP_CAMPOS in head else ""
            actual = {"n": n, "veredicto": veredicto, "comentario": comentario, "campos": campos, "crudo": resto, "respuesta": _respuesta(veredicto)}
            items[n] = actual
        elif linea.startswith("notas:"):
            notas.append(linea[len("notas:"):].strip())
            actual = None
        elif linea.startswith("/") or not linea.strip():
            continue
        elif actual is not None:  # un comentario con saltos de línea
            actual["comentario"] = (actual["comentario"] + "\n" + linea).strip() if actual["comentario"] else linea.strip()
    return items, "\n".join(notas)


def _respuesta(veredicto):
    v = veredicto.strip().lower()
    if v in ("va", "va con cambios"):
        return "va"
    if v == "no va":
        return "no_va"
    if v == "revisado":
        return None  # card de revisión: Revisado = visto, no hay nada que aplicar
    if v.startswith("eligió"):
        ids = [x.strip() for x in veredicto[len("eligió"):].split(",") if x.strip()]
        return ids or None
    return None  # comentario, después, sin marcar, o algo que no conozco: no hay plan que aplicar


def es_revision(item):
    return isinstance(item, dict) and item.get("tipo") == "revision"


def plan_de(item, resp):
    """Qué hacer con un ítem según la respuesta ya parseada. Devuelve un dict:
    accion: 'aplicar' | 'nada' | 'despues' | 'preguntar'; plan (texto o None); con_plan (bool: el plan de ESTA respuesta existe)."""
    ap = item.get("aplicar") or {}
    ver = resp["veredicto"].strip().lower() if resp else "sin marcar"
    comun = ap.get("comun")
    if resp is None or ver == "sin marcar":
        return {"accion": "nada", "plan": None, "con_plan": True, "comun": None, "por_que": "sin marcar: no se hace"}
    if ver == "revisado":
        return {"accion": "nada", "plan": None, "con_plan": True, "comun": None, "por_que": "revisión: no hay nada que aplicar"}
    if ver == "después":
        return {"accion": "despues", "plan": None, "con_plan": True, "comun": None,
                "por_que": "el usuario eligió «después»: no se aplica. Anotalo donde guardás tus pendientes, o dejalo sin hacer y decile al usuario"}
    if ver == "rot":
        return {"accion": "preguntar", "plan": None, "con_plan": True, "comun": comun,
                "por_que": "el usuario tocó «+info»: no entendió la card (no es un Va). Reescribila siguiendo rot.md (en la carpeta de este skill); "
                           "si no podés, dejala pendiente y avisale"}
    if ver == "comentario":
        return {"accion": "preguntar", "plan": None, "con_plan": True, "comun": comun,
                "por_que": "el usuario comentó sin decidir (no es un Va): una orden clara en el comentario se aplica; una pregunta o nota se responde en el chat, no se aplica"}
    clave = resp["respuesta"]
    if clave == "no_va":
        plan = ap.get("no_va")
        return {"accion": "nada", "plan": plan, "con_plan": True, "comun": None,
                "por_que": "no va: no se hace nada"}
    if clave == "va":
        plan = ap.get("va")
        return {"accion": "aplicar", "plan": plan, "con_plan": bool(plan), "comun": comun, "por_que": ver}
    if isinstance(clave, list):
        ids = [c for c in clave if c != "otra"]
        planes = [f"[{c}] {ap[c]}" for c in ids if ap.get(c)]
        faltan = [c for c in ids if not ap.get(c)]
        if "otra" in clave:
            # «otra»: el comentario del usuario ES la opción; no hay plan escrito
            return {"accion": "preguntar", "plan": "\n".join(planes) or None, "con_plan": False, "comun": comun,
                    "por_que": "eligió «otra»: el comentario del usuario es la opción (no hay plan escrito)"}
        return {"accion": "aplicar", "plan": "\n".join(planes) or None, "con_plan": not faltan and bool(planes), "comun": comun,
                "por_que": ver, "sin_plan_de": faltan}
    return {"accion": "preguntar", "plan": None, "con_plan": False, "comun": comun, "por_que": f"veredicto que no reconozco: «{ver}»"}


def analizar(res):
    """res = respuesta de bm_retomar -> dict con todo lo que necesitan el brief y otros scripts."""
    items_datos = {int(i["n"]): i for i in (res.get("items") or []) if isinstance(i.get("n"), int)}
    marcadas, notas = parsear_respuesta(res.get("respuesta_texto"))
    filas = []
    for n in sorted(set(items_datos) | set(marcadas)):
        it = items_datos.get(n, {"n": n, "titulo": "(ítem que ya no está en la tanda)"})
        resp = marcadas.get(n)
        p = plan_de(it, resp)
        filas.append({
            "n": n, "titulo": it.get("titulo"), "veredicto": resp["veredicto"] if resp else "sin marcar",
            "comentario": resp["comentario"] if resp else "", "campos": resp.get("campos", "") if resp else "", "tiene_aplicar": bool(it.get("aplicar")) and not es_revision(it), **p,
        })
    accionables = [f for f in filas if f["accion"] in ("aplicar", "preguntar")]
    return {
        "clave": res.get("clave"), "estado": res.get("estado"), "titulo": res.get("titulo"),
        "sesion_titulo": res.get("sesion_titulo"), "decided_at": res.get("decided_at"), "notas": notas,
        "items": filas,
        # todos los ítems que hay que aplicar traen el plan de SU respuesta
        "todo_con_plan": all(f["con_plan"] for f in accionables),
        "algun_plan": any(f["tiene_aplicar"] for f in filas),
        "respuesta_texto": res.get("respuesta_texto"),
    }


def cuantos_con_plan(res):
    """(cards con `aplicar`, total de cards) de la tanda: lo que muestra colgadas.py."""
    its = [i for i in (res.get("items") or []) if not es_revision(i)]   # una revisión no lleva `aplicar` obligatorio: no cuenta como «sin plan»
    return sum(1 for i in its if i.get("aplicar")), len(its)


def brief(a, ruta_marcar=None):
    marcar = ruta_marcar or str(AQUI / "marcar.py")
    clave = a["clave"]
    L = [f"RETOMAR {clave} · «{a['titulo']}» · estado: {a['estado']}",
         f"La publicó «{a['sesion_titulo'] or 'sin título'}». el usuario decidió"
         + (f" el {str(a['decided_at'])[:10]}" if a.get("decided_at") else "")
         + ". Si esa sesión ya no está, esta la aplica; si sigue viva, que la aplique ella.",
         ""]
    if a["estado"] in ("aplicada", "archivada", "respondida_en_chat"):
        L += [f"OJO: la tanda ya está {a['estado']}. No apliques nada; si querés rehacerlo, preguntale al usuario.", ""]
    elif a["estado"] == "abierta":
        L += ["OJO: la tanda sigue abierta, el usuario todavía no decidió. No hay nada que aplicar.", ""]
    L += ["Reglas: el comentario del usuario manda sobre el plan. Lo `sin marcar` y lo `después` no se hacen. Un `comentario` sin decidir",
          "no es un Va. Lo interno y reversible se hace y se avisa; lo que sale a un tercero, borra o mueve plata no se hace sin un Va explícito.",
          ""]
    if a["notas"]:
        L += [f"Comentario final del usuario (habla de todo el mazo): {a['notas']}", ""]
    L.append("Ítem por ítem:")
    for f in a["items"]:
        L.append(f"\n{f['n']}. {f['titulo']}  →  Usuario: {f['veredicto']}")
        if f.get("campos"):
            L.append(f"   Valores que el usuario cambió (usá estos, no los del plan): {f['campos']}")
            if "⏎" in f["campos"]:
                L.append("   (en un campo de texto largo, cada ⏎ es un salto de línea: el texto del usuario viene entero)")
        if f["comentario"]:
            L.append("   Comentario del usuario (manda sobre el plan): " + f['comentario'].replace("\n", "\n      "))
        if f["accion"] == "aplicar":
            if f["plan"]:
                L.append("   Plan: " + f["plan"].replace("\n", "\n         "))
            if f.get("sin_plan_de"):
                L.append(f"   SIN PLAN para: {', '.join(f['sin_plan_de'])}. Sin plan escrito no se inventa: anotalo donde guardás tus pendientes y avisale al usuario.")
            if not f["plan"] and not f.get("sin_plan_de"):
                L.append("   SIN PLAN para esta respuesta. Sin plan escrito no se inventa: anotalo donde guardás tus pendientes y avisale al usuario.")
            if f.get("comun"):
                L.append(f"   Contexto común: {f['comun']}")
        elif f["accion"] == "nada":
            L.append(f"   {f['por_que']}." + (f" Plan de «no va» (si lo hay, se hace): {f['plan']}" if f["plan"] and f["plan"].strip().lower().rstrip('.') not in ('nada', 'no se hace nada') else ""))
        elif f["accion"] == "despues":
            L.append(f"   {f['por_que']}.")
        else:
            L.append(f"   {f['por_que']}." + (f" Plan: {f['plan']}" if f["plan"] else ""))
            if f.get("comun"):
                L.append(f"   Contexto común: {f['comun']}")
    L += ["", "Respuesta original, tal cual llegó:", "  " + (a["respuesta_texto"] or "(vacía)").replace("\n", "\n  "), "",
          f'Cuando termines: python3 "{marcar}" {clave} aplicada "<una línea por ítem: hecho / anotado en pendientes / no hecho y por qué>"']
    if a["estado"] == "decidida":
        L.append(f"(La tanda está `decidida`, no `recibida`: `aplicada` solo se acepta desde `recibida`. Corré antes "
                 f"`python3 \"{AQUI / 'retomar.py'}\" {clave} --tomar`.)")
    return "\n".join(L)


def leer(clave, tomar=False):
    cfg = maestro.config()
    if not cfg:
        print("maestro: sin config (~/.config/botonera/env), no puedo retomar", file=sys.stderr)
        sys.exit(1)
    try:
        if tomar:
            # Mismo paso que esperar.py: decidida -> recibida. Si ya estaba recibida, devuelve la respuesta de nuevo.
            maestro.rpc("bm_recibir", {"p_secret": cfg["BM_SECRET"], "p_clave": clave})
        res = maestro.rpc("bm_retomar", {"p_secret": cfg["BM_SECRET"], "p_clave": clave})
    except maestro.ErrorMaestro as ex:
        print(f"maestro: falló ({ex})", file=sys.stderr)
        sys.exit(1)
    return res if isinstance(res, dict) else {}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    solo_json = "--json" in args
    tomar = "--tomar" in args
    desde = None
    if "--desde" in args:
        i = args.index("--desde")
        try:
            desde = args[i + 1]
        except IndexError:
            sys.exit("uso: python3 retomar.py <clave> [--tomar] [--json] | --desde respuesta.json")
        del args[i:i + 2]
    args = [a for a in args if a not in ("--json", "--tomar")]
    if desde:
        res = json.loads(Path(desde).read_text(encoding="utf-8"))
    else:
        if len(args) != 1:
            sys.exit("uso: python3 retomar.py <clave> [--tomar] [--json] | --desde respuesta.json")
        res = leer(args[0], tomar)
    if res.get("estado") == "no_existe" or not res:
        print(f"maestro: {args[0] if args else '?'} no existe en la botonera", file=sys.stderr)
        sys.exit(1)
    a = analizar(res)
    print(json.dumps(a, ensure_ascii=False, indent=2) if solo_json else brief(a))


if __name__ == "__main__":
    main()

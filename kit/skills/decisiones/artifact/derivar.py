#!/usr/bin/env python3
"""Deriva `pagina.html` (la página privada de Claude) de la web real de la botonera.

    python3 derivar.py [--web ruta/a/botonera/web/index.html] [--salida pagina.html] [--check]

`pagina.html` es la MISMA web que `botonera/web/index.html` (mismo html, css y js de mazo, tarjeta, hojas, snooze,
lista y confeti) con cambios mínimos y marcados con `ARTIFACT`. Este script los aplica en orden sobre la web; cada
cambio exige que el texto original aparezca exactamente las veces esperadas, así que si la web cambia por ese lado el
script falla en voz alta en vez de generar una página rota. Receta en LEEME.md.
"""
import argparse
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
WEB_POR_DEFECTO = AQUI.parents[3] / "botonera" / "web" / "index.html"

CSS = """
  /* ARTIFACT: la barra de arriba conserva el alto que tiene con el botón Salir (acá no hay Salir), así todo queda en el mismo lugar */
  .top{min-height:60.8px}
  /* ARTIFACT: el paso de avisar a Claude (usa los botones y colores de la web) */
  .av{width:100%;max-width:340px;margin:12px auto 0;display:flex;flex-direction:column;gap:10px;text-align:center}
  .av-b{display:flex;flex-direction:column;align-items:center;gap:6px}
  .av .sw-big{max-width:none;cursor:pointer;font-family:inherit;color:#1C1B1B}
  .av-k{margin:0;font-weight:700;font-size:14px;color:#1C1B1B}
  .av-t{font-weight:700;font-size:13px;color:#1C1B1B}
  .av-h{margin:0;font-size:12.5px;color:#6b6866}
  .av-r{margin:0;font-size:12.5px;font-weight:700}
  .av-r.ok{color:#1F6F6B}
  .av-r.mal{color:#A1263A}
  .home-res + .av{margin-top:14px}
"""


class Derivador:
    def __init__(self, src):
        self.src = src
        self.cambios = []

    def sub(self, viejo, nuevo, veces=1, nombre=None):
        n = self.src.count(viejo)
        if n != veces:
            sys.exit(f"derivar: «{nombre or viejo[:60]}»: esperaba {veces} aparición(es) y hay {n}. La web cambió por ese lado: revisá este cambio.")
        self.src = self.src.replace(viejo, nuevo)
        self.cambios.append(nombre or viejo[:50])

    def entre(self, ini, fin, nuevo, nombre, incluir_fin=False):
        """Reemplaza desde `ini` (incluido) hasta `fin` (excluido, o incluido con incluir_fin)."""
        if self.src.count(ini) != 1:
            sys.exit(f"derivar: «{nombre}»: el inicio {ini[:50]!r} aparece {self.src.count(ini)} veces (esperaba 1).")
        a = self.src.index(ini)
        b = self.src.find(fin, a + len(ini))
        if b < 0:
            sys.exit(f"derivar: «{nombre}»: no encuentro el final {fin[:50]!r}.")
        if incluir_fin:
            b += len(fin)
        self.src = self.src[:a] + nuevo + self.src[b:]
        self.cambios.append(nombre)


def derivar(web):
    d = Derivador(web)
    leer = lambda n: (AQUI / n).read_text(encoding="utf-8")
    adaptador, confeti, avisar = leer("adaptador.js"), leer("confeti.js"), leer("avisar.js")

    # 1. <head>: título corto, sin íconos ni manifest por ruta (una página privada no sirve archivos aparte)
    d.sub("<title>Botonera</title>", "<title>Tus pendientes</title>", nombre="título")
    for linea in ('<link rel="icon" type="image/svg+xml" href="/icon.svg">\n', '<link rel="icon" type="image/png" sizes="32x32" href="/icon-32.png">\n',
                  '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n', '<link rel="manifest" href="/manifest.webmanifest">\n',
                  '<meta name="apple-mobile-web-app-title" content="Botonera">\n'):
        d.sub(linea, "", nombre="sin " + linea[:40].strip())
    d.sub("</style>\n</head>", CSS + "</style>\n</head>", nombre="css del aviso a Claude")

    # 2. los datos: sin supabase-js ni config.js, el adaptador va inline y contesta con la base de la página
    d.sub('<script src="/vendor/supabase.min.js"></script>\n<script src="/config.js"></script>\n<script>\n(function(){',
          "<script>\n" + adaptador.rstrip() + "\n</script>\n<script>\n" + confeti.rstrip() + "\n</script>\n<script>\n(function(){", nombre="adaptador de datos inline")
    d.entre("// Config de tu proyecto Supabase", "var SIETE_DIAS", "/* ARTIFACT: sin Supabase ni config.js: los datos salen del adaptador */\nfunction configValida(){ return true; }\n", "sin config de Supabase")

    # 3. sin PIN: el acceso es la cuenta de Claude. La pantalla del PIN pasa a ser el aviso de «entrá a Claude»
    d.entre("/* ---------- pantalla del PIN ---------- */", "/* ---------- app ---------- */",
            """/* ARTIFACT: sin PIN. Esta pantalla solo avisa que falta la cuenta de Claude, o que la base tarda. */
function vistaEntrada(msg){
  swipeDesmontar(); estado.swd = null; estado.hd = {}; estado.listaCargada = false; estado.homeVisto = false; estado.homeEnvs = {}; estado.homeEnviando = false; estado.festejo = null;
  document.body.classList.remove('con-barra');
  raiz.innerHTML = '<div class="entrada"><h1>Tus pendientes</h1><p>' + esc(msg || 'Esta página necesita que entres a Claude con tu cuenta.') + '</p></div>';
}
function salir(){}

""", "pantalla del PIN -> aviso de la cuenta")
    d.sub("""'<div class="top"><h1>Botonera</h1>' +
      '<button class="btn" id="b-salir">Salir</button></div>' +""", """'<div class="top"><h1>Tus pendientes</h1></div>' +""", nombre="sin botón Salir")
    d.sub("  document.getElementById('b-salir').onclick = salir;\n", "", nombre="sin oyente de Salir")

    # 4. marcas a medio decidir: además del navegador, a la base (marcas/<clave>)
    d.sub("  try{ localStorage.setItem(CLAVE_MARCAS, JSON.stringify(estado.marcas)); }catch(e){}\n  homePintar();   // los conteos del home siguen a las marcas",
          "  try{ localStorage.setItem(CLAVE_MARCAS, JSON.stringify(estado.marcas)); }catch(e){}\n  window.__art.guardarMarcas(estado.marcas);   /* ARTIFACT: también a la base */\n  homePintar();   // los conteos del home siguen a las marcas",
          nombre="marcas a la base")
    d.sub("      limpiarMarcas();\n      snzSacarDormidas();", "      limpiarMarcas();\n      adoptarMarcasRemotas();   /* ARTIFACT */\n      snzSacarDormidas();", nombre="adoptar marcas de otro dispositivo")

    # 5. sin avisos al celu (service worker, push): el bloque entero se reemplaza por stubs
    d.entre("/* ---------- avisos (Web Push) ---------- */", "// la fila «Con error» (en Bloqueos)",
            """/* ARTIFACT: sin avisos al celu ni service worker (una página privada no puede registrar ninguno) */
function avisosHTML(){ return ''; }
function avisosActivar(){}
function avisosAlEntrar(){}
function avisosIcono(n){
  if(!navigator.setAppBadge) return;
  try{ (n ? navigator.setAppBadge(n) : navigator.clearAppBadge()).catch(function(){}); }catch(e){}
}

""", "sin avisos push")
    d.sub("  if(!enCat) h += avisosHTML();\n",
          "  h += avisarHTML(claves.filter(function(c){ return envs[c].st === 'ok'; }));   /* ARTIFACT: avisar a Claude (en lugar de los avisos al celu) */\n",
          nombre="avisar tras el envío del home")
    d.entre("function segRpcKeepalive(nombre, args){", "// cerrar, recargar o mandar a segundo plano",
            "function segRpcKeepalive(nombre, args){ return sb.rpc(nombre, args); }   /* ARTIFACT: sin fetch directo */\n", "archivar sin fetch directo")

    # 6. confeti sin script de afuera
    d.entre("var CONFETI_SRC = '/vendor/confetti.min.js';", "function festejoTras(p){",
            """var CONFETI_COLORES = ['#8ECAC8', '#F5F0E8', '#FFD166', '#EF476F', '#FFFFFF'];
function confetiCargar(){ return Promise.resolve(window.confetti); }   /* ARTIFACT: confeti propio, inline (artifact/confeti.js) */
""", "confeti inline")

    # 7. rótulos: «Claude» en vez de «el agente»; «tarjetas» en vez de «cards» en los textos visibles
    for viejo, nuevo, veces in [
        ("'El agente está trabajando'", "'Claude está trabajando'", 1),
        ("'El agente está trabajando · hace '", "'Claude está trabajando · hace '", 1),
        ("El agente recomienda esta</span>", "Claude recomienda esta</span>", 2),
        ("El agente recomienda: ", "Claude recomienda: ", 3),
        ("Esto propuso el agente. Cambiá lo que quieras.", "Esto propuso Claude. Cambiá lo que quieras.", 1),
        ("queda como lo propuso el agente", "queda como lo propuso Claude", 1),
        ("'Algo para el agente (opcional)'", "'Algo para Claude (opcional)'", 1),
        ("'Tu comentario para el agente'", "'Tu comentario para Claude'", 1),
        ("'Anotado: se lo aviso al agente'", "'Anotado: se lo aviso a Claude'", 1),
        ("'Listo: el agente sigue solo'", "'Listo: Claude sigue solo'", 1),
        ("volver a la card</div>", "volver a la tarjeta</div>", 1),
        ("La reemplaza la card ", "La reemplaza la tarjeta ", 1),
        (" · la reemplaza la card ", " · la reemplaza la tarjeta ", 1),
        ("'card', 'cards'", "'tarjeta', 'tarjetas'", 4),
        ("'card sin marcar va', 'cards sin marcar van'", "'tarjeta sin marcar va', 'tarjetas sin marcar van'", 1),
        ("aria-label=\"Card '", "aria-label=\"Tarjeta '", 1),
        (" solo quedan las cards que dejaste para el final.", " solo quedan las tarjetas que dejaste para el final.", 1),
        ("'esta card' : 'estas ' + sin.length + ' cards'", "'esta tarjeta' : 'estas ' + sin.length + ' tarjetas'", 1),
        ("No hay cards pendientes.", "No hay tarjetas pendientes.", 1),
        (", hay cards abiertas'", ", hay tarjetas abiertas'", 1),
    ]:
        d.sub(viejo, nuevo, veces, nombre="rótulo: " + viejo[:40])

    # 8. «Ver la botonera original» necesita el html de la tanda, que esta página no guarda
    d.sub("""      if(t.baseFila) h += '<details class="plegable" id="orig"><summary>Ver la botonera original</summary><div class="marco orig" id="orig-marco"></div></details>';\n""", "",
          nombre="sin «Ver la botonera original»")

    # 9. Sesiones: lo que Claude escribe en estado/<clave> se ve en la fila
    d.sub("      multi: t.vueltas.length > 1,\n", "      estado_texto: ref.estado_texto || '',   /* ARTIFACT */\n      multi: t.vueltas.length > 1,\n", nombre="estado de Claude en la entrada")
    d.sub("var base = {titulo: e.titulo || b, ses: e.sesion_titulo || '',", "var base = {texto: e.estado_texto || '', titulo: e.titulo || b, ses: e.sesion_titulo || '',", nombre="estado de Claude en la fila")
    d.sub("    if(x.ses && x.est !== 'aplicada' && x.est !== 'archivada') l.push(x.ses);\n",
          "    if(x.texto && (x.est === 'decidida' || x.est === 'recibida')) l.push(x.texto);   /* ARTIFACT: lo que Claude va escribiendo */\n    if(x.ses && x.est !== 'aplicada' && x.est !== 'archivada') l.push(x.ses);\n", nombre="estado de Claude en el detalle")

    # 10. avisar a Claude después de Enviar, en las dos pantallas de cierre del mazo
    d.sub("(env.st === 'ok' ? '<p>La sesión ya tiene tu respuesta.</p>' : '') + '</div>';",
          "(env.st === 'ok' ? avisarHTML([estado.swd && estado.swd.clave]) : '') + '</div>';", nombre="avisar tras el envío de un mazo")
    d.sub("  return h + '<button type=\"button\" class=\"sw-big alt\" data-a=\"home\">Volver al home</button></div>';",
          "  h += avisarHTML(R.filter(function(r){ return r.env && r.env.st === 'ok'; }).map(function(r){ return r.bot.clave; }));   /* ARTIFACT */\n"
          "  return h + '<button type=\"button\" class=\"sw-big alt\" data-a=\"home\">Volver al home</button></div>';", nombre="avisar tras el envío de varios mazos")

    # 11. arranque: sin PIN ni Supabase; entra con la cuenta de Claude
    d.entre("/* ---------- arranque ---------- */", "\n})();\n</script>",
            avisar + """
/* ---------- arranque ---------- */
/* ARTIFACT: sin PIN ni Supabase. La sesión es la cuenta de Claude; los datos vienen del adaptador (db de la página). */
function init(){
  sb = window.supabase.createClient();
  window.__art.alCambiar = function(){ if(estado.token) cargarLista(); };
  document.addEventListener('visibilitychange', function(){ if(!document.hidden && estado.token){ cargarLista(); homePintar(); } });
  window.addEventListener('focus', function(){ if(estado.token) cargarLista(); });
  var listo = false;
  var tarda = setTimeout(function(){ if(!listo) vistaEntrada('Todavía no pude leer tus tarjetas. La página sigue intentando.'); }, 10000);
  window.__art.listo.then(function(ok){
    listo = true; clearTimeout(tarda);
    if(!ok){ vistaEntrada('Esta página necesita que entres a Claude con tu cuenta.'); return; }
    estado.token = 'claude';
    vistaApp();
  });
}
init();
""", "arranque sin PIN")
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--web", default=str(WEB_POR_DEFECTO))
    ap.add_argument("--salida", default=str(AQUI / "pagina.html"))
    ap.add_argument("--check", action="store_true", help="no escribe: sale con 1 si pagina.html no coincide con lo que saldría")
    a = ap.parse_args()
    web = Path(a.web).read_text(encoding="utf-8")
    d = derivar(web)
    salida = Path(a.salida)
    if a.check:
        if not salida.exists() or salida.read_text(encoding="utf-8") != d.src:
            sys.exit("pagina.html no coincide con botonera/web/index.html + los cambios: corré derivar.py")
        print("ok · pagina.html está al día")
        return
    salida.write_text(d.src, encoding="utf-8")
    print(f"ok · {len(d.cambios)} cambios · {len(d.src.splitlines())} líneas · {len(d.src.encode('utf-8')) // 1024} KB · {salida}")


if __name__ == "__main__":
    main()

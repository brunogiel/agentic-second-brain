# ppt-builder · referencia de video

Lo que carga `ppt-builder` cuando `MEDIO` es `video`: los gates, los formatos y la receta técnica del Asset.
Las herramientas viven en `video/`, al lado de este archivo (plantilla, render, tiempos de voz, alineación,
mezcla, empalme). Las rutas son relativas a esta carpeta; ubicala con:

```bash
PPT="$(dirname "$(find ~/.claude -name 'reference-video.md' -path '*ppt-builder*' 2>/dev/null | head -1)")"
VID="$PPT/video"
```

Requisitos: `ffmpeg` en el PATH, Playwright de Python (para el render) y Whisper local
(`pip install openai-whisper`, para los tiempos). La voz sale de un servicio de voz sintética (ElevenLabs u otro)
o de una grabación tuya.

---

## Antes de arrancar: tres preguntas (gate)

Las tres se contestan antes de escribir el guion. Saltearlas es la forma más cara de hacer un video que nadie usa.

1. **¿Quién lo publica y lo quiere?** Si la pieza sale con la marca de otro (un socio, una agencia, un cliente),
   esa persona dice si quiere un video y con qué estilo, **antes** de construir. Una agencia que vende oficio puede
   no querer mandar nada que parezca hecho con IA, por bueno que sea. Si lo descubrís con el video terminado,
   perdiste el día y la voz.
2. **¿Se va a leer como hecho con IA?** Voz sintética + animación de vectores abstractos (puntos, cajas grises) se
   lee como relleno para una audiencia que juzga oficio. Si eso pesa, cambiá el formato (abajo), no la paleta.
3. **¿Qué tiene que hacer quien lo ve después?** Abrir un informe, agendar, comprar. El cierre se diseña para eso
   desde el guion, no en la última vuelta.

## Por qué por etapas

Las 5 etapas, con bloqueo duro entre una y otra, cortan los errores caros de un video:

| Etapa | Qué evita |
|---|---|
| 1 · Brief (límites de marca, quién publica) | Construir un video que el dueño de la marca no va a mandar. Ahí entra el gate 1 |
| 2 · Historia (mensaje central en una frase) | Un video que es un cronograma sin una idea que empuje |
| 4 · Copy (voz + anti-slop, OK antes del asset) | Pagar la voz varias veces porque el texto cambió después de generarla |
| 5 · Asset | Recién acá va la receta técnica de abajo (HTML + render + voz) |

El panel va al cerrar la Historia o el Copy, sobre el guion y una escena de muestra, no recién sobre el video entero.

## Formatos, del más "humano" al más "IA"

| Formato | Cuándo | Riesgo de que se lea como IA |
|---|---|---|
| Tu voz grabada + pantallas reales (el informe, el producto, clips) | Va a alguien que juzga oficio | Bajo |
| Animación con material real (capturas, slides, citas) + tu voz | Explicar un proceso con prueba | Bajo-medio |
| Animación abstracta + voz sintética | Uso interno, redes propias, borradores | Alto |

Si el panel dice "abstracto" ("siempre cajas grises, sin una pantalla ni una cita real"), sumá material real.

## Cómo se hace (la receta técnica)

Todo es un HTML que se renderiza cuadro por cuadro. No hay editor de video. Copiá las herramientas a
`{BASE}/{SLUG}/assets/video/` al arrancar el Asset.

1. **Guion** en `pieza.md` §4 como tabla: `| n | narración | en pantalla | acción visual | fuente |`. `alinear.py` lee
   la columna de la narración de las filas `| n |`. Una fila sin narración es una escena muda.
2. **`video/plantilla.html`** → `video.html`. SVG + HTML a 1920×1080. `window.renderAt(t)` dibuja el cuadro exacto del
   segundo `t` (todo es función del tiempo, nada de animaciones CSS). Las acciones se anclan con `W(escena,'palabra')`:
   el segundo en que la voz dice esa palabra. Escenas con `t`, `hold`, `ost` (texto grande), `subW`/`subF` (ancho y letra
   del subtítulo), `mute:true, dur:N` (escena muda). **La paleta va en el objeto `C`** y la tipografía en un slot
   `@font-face` arriba del archivo: poné ahí los colores y las fuentes de tu marca (o de la marca para la que es la
   pieza). `?t=7.5` muestra un cuadro; sin parámetro corre el preview en loop. Dejá aire entre anclas: dos acciones a
   menos de 0,3 s se pisan.
3. **`video/render.py <video.html> <salida.mp4> [hasta_s]`**: Playwright abre el HTML 4 veces en paralelo, llama
   `renderAt(i/30)`, saca screenshot y lo pasa a `ffmpeg` (H.264, 30 fps). Toma `voz/tiempos.json` de al lado del HTML
   y escribe `escenas.json` junto a la salida. `hasta_s = 0.1` es un probe para leer la duración total.
4. **Voz**, con la narración congelada: una toma por escena (mejor) o una de todo. Si el servicio permite estimar el
   costo antes de generar, estimalo primero.
5. **`video/tiempos_voz.py <voz.mp3> --atempo 1.08`**: acelera 8 % sin cambiar el tono (opcional), corre `ffmpeg
   silencedetect` y Whisper local (`small`, `word_timestamps`). Deja `-rapida.mp3`, `-silencios.txt` y `-palabras.json`.
   Corre con `python3` sin `-I` (Whisper vive en el site-packages del usuario).
6. **`video/alinear.py <guion.md> <voz.mp3>`**: cruza las palabras de Whisper con las del guion (números 0-30 y palabras
   pegadas tipo "FaseB" normalizadas) y corta cada escena en el silencio real más cercano. Escribe `tiempos.json` y
   `segmentos.json` junto al mp3.
7. **`video/mezclar.py <video.mp4> <salida.mp4> <carpeta-voz> <escenas.json>`**: pone cada tramo de voz al arrancar su
   escena. Un `extra.json` en la carpeta de la voz suma audio a escenas mudas.
8. **`video/empalmar.py <base.mp3> <parche.mp3> <salida.mp3> base:0:24.5 parche:0:21.5 base:46.3:fin …`**: cambia una
   o varias frases sin regenerar toda la voz. Los cortes van en silencios (ver `-silencios.txt`).
9. **Chequeos**: el cuadro final de cada escena, mirado. Whisper sobre el mp4 final para medir voz contra acción (la
   meta: cada acción a menos de 0,1 s de su palabra). Conteos y colores fuera de paleta por script. QR decodificado
   (por ejemplo con `cv2.QRCodeDetector`).
10. **Revisión**: el panel de 4 lentes sobre el storyboard (Etapa 2), no recién sobre el render. Por tanda, cada cambio
   como antes/después, uno por decisión (`decisiones` sirve para eso).

La plantilla trae tres escenas de ejemplo (puntos que aparecen en su palabra, una ventana de navegador que se arma con
un cursor que hace clic, una escena muda). Copiá el patrón que necesites y borrá el resto.

## Lecciones de costo y de proceso

- **Cerrá el texto antes de generar la voz.** Cada cambio de frase con la voz ya hecha cuesta otra toma. La ronda de
  frases va ANTES de la voz, no después.
- **Generá la voz por escena, no de corrido.** Así un cambio regenera solo esa escena. Si va de corrido, empalmá en
  silencios (`silencedetect`), nunca a mitad de palabra.
- **El costo se va en rehacer.** Cada cambio de texto después del render pide otra vuelta de código, render y voz.
  Con las etapas cerradas antes del asset, el mismo video sale con un panel y la mitad de las tandas.
- **Las cuentas gratis de voz sintética se traban** ("busy right now") justo cuando más las necesitás. Si hay apuro,
  plan pago o grabar la voz.
- **El subagente afirma, el cuadro prueba.** Siempre mirá los cuadros antes de dar algo por hecho.
- **Una tarea programada larga puede fallar en silencio** si el límite de uso está cerca. Revisá que haya terminado.
- **ffmpeg 7:** `apad` infinito + `-shortest` corta con "No space left on device" (no es el disco). Usá
  `apad=whole_dur=` y `-t` (así lo hace `mezclar.py`).
- **Subtítulos largos:** `text-wrap: balance` evita palabras huérfanas; un `subW` / `subF` por escena evita la 3.ª línea.

---
description: Transcribe un audio local con Whisper corriendo en tu máquina. Gratis y sin mandar nada a la nube.
---

Transcribí el audio que te pasen ($ARGUMENTS) con Whisper local. Seguí esto:

# transcribir — audio a texto, sin nube

## Qué es

Whisper, el modelo de OpenAI, es open source con licencia MIT y corre entero en tu
computadora. Eso cambia dos cosas respecto de mandar el audio a una API: no cuesta plata y
el audio no sale de tu máquina. Lo segundo importa más de lo que parece cuando el archivo
es una reunión, una nota de voz de alguien o algo que no es tuyo para repartir.

Pagás CPU y tiempo, nada más.

## Parámetros

| Param | Default | Qué es |
|---|---|---|
| `AUDIO_PATH` | (requerido) | Path al archivo de audio |
| `MODELO` | `base` | Cuál Whisper. Subir si el texto sale con muchos errores |
| `IDIOMA` | `es` | Idioma del audio. Cambialo si claramente es otro |

## Flujo

1. **[DET] Dependencias.** Chequear que estén `ffmpeg` y `openai-whisper`. Instalar solo lo
   que falte, nunca a ciegas.
2. **[DET] Transcribir.** Correr Whisper con el modelo y el idioma sobre el archivo.
3. **[LATENT] Limpiar el final.** Whisper alucina cuando el audio termina en silencio o
   música. Recortar lo que sobra (ver abajo). Este paso no es opcional.
4. **[DET] Entregar.** Guardar el `.txt` **al lado del audio**, mismo nombre, y reportar el
   path con un resumen de una línea. Nunca dejarlo en `/tmp/`, que es donde va a morir.

## Instalación, la primera vez

```bash
which ffmpeg || brew install ffmpeg
pip3 show openai-whisper 2>/dev/null || pip3 install --user --quiet openai-whisper
```

⚠ En macOS el binario `whisper` queda en `~/Library/Python/3.x/bin/whisper`, que **no está
en el PATH**. Si lo llamás por nombre falla y parece que no se instaló. Invocalo desde
Python o con el path completo.

## Cómo invocar

Forma recomendada, porque no depende del PATH:

```bash
python3 -c "
import whisper
m = whisper.load_model('base')
r = m.transcribe('/ruta/al/audio.opus', language='es')
print(r['text'])
" > "/ruta/al/audio.txt"
```

## Qué modelo elegir

| Modelo | Peso | Velocidad | Cuándo |
|---|---|---|---|
| `tiny` | 39 MB | Más rápido | Audios cortos, habla clara |
| `base` | 74 MB | Rápido | **Default.** Notas de voz, reuniones casuales |
| `small` | 244 MB | Medio | Material técnico, acentos marcados, jerga |
| `medium` | 769 MB | Lento | Cuando la calidad importa de verdad |
| `large` | 1.5 GB | Muy lento | Casi humana. Material que se publica |

En una Mac M1 de 16 GB, `base` y `small` rinden bien. `medium` y `large` andan, pero tardan.
Empezá siempre por `base` y subí solo si el texto sale mal: pasar de `base` a `medium`
multiplica el tiempo por mucho y la mejora suele ser chica en audio limpio.

## La limpieza del final, que es donde se nota

Whisper inventa cuando se queda sin habla. Los síntomas son siempre los mismos: caracteres
raros, palabras que no existen, un idioma que aparece de la nada, o una frase que se repite
tres veces. Pasa al final, después de un silencio largo o de música.

Cortar todo lo que va después del último párrafo coherente y marcarlo como `(fin)`. Una
transcripción con la alucinación pegada al final es peor que una cortada: el que la lee no
sabe dónde dejó de ser cierta.

## Casos típicos

Notas de voz de mensajería, grabaciones de iPhone en `.m4a`, reuniones grabadas, y videos
donde solo te importa lo que se dice: `.mp4` también funciona, Whisper le saca el audio solo.

## Si además querés un resumen

Transcribí primero y resumí después, en dos pasos. Para el resumen no hace falta un modelo
grande: es una tarea de alto volumen y baja complejidad, justo donde conviene un modelo
chico o local.

## Success metrics

- El `.txt` quedó al lado del audio original, con el mismo nombre. No en `/tmp/`.
- La alucinación de cierre está recortada del archivo entregado, no solo mencionada.
- Cero llamadas a APIs de nube durante la transcripción.

## Si te queda chico

`mlx-whisper` es la versión optimizada para Apple Silicon: mismo modelo, mismo output, entre
5 y 10 veces más rápido porque usa el Neural Engine. Para uso esporádico `openai-whisper`
alcanza; si vas a transcribir seguido, vale la instalación.

```bash
pip3 install --user mlx-whisper
mlx_whisper "/ruta/al/audio.opus" --language es --model mlx-community/whisper-base
```

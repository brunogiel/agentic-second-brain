#!/usr/bin/env python3
"""Saca los tiempos de una voz: silencios (ffmpeg) y palabras con su inicio y fin (Whisper local).
Uso:  python3 tiempos_voz.py <voz.mp3> [--atempo 1.08] [--modelo small]   (sin -I: Whisper vive en el site-packages del usuario y -I no lo ve)
Escribe junto al mp3:
  <voz>-silencios.txt   una línea por silencio: inicio y duración en segundos (ffmpeg silencedetect, -35 dB, 0,15 s)
  <voz>-palabras.json   [{"w": palabra, "s": inicio, "e": fin}] (Whisper, language='es', word_timestamps=True)
Con --atempo 1.08 primero genera <voz>-rapida.mp3 (la voz 8 % más rápida, mismo tono) y trabaja sobre esa:
los dos archivos de tiempos se llaman <voz>-rapida-*, y ese es el mp3 que va a alinear.py y a mezclar.py.
Requiere ffmpeg en el PATH y `pip install openai-whisper` (el modelo se baja una vez a ~/.cache/whisper)."""
import argparse, json, os, re, subprocess, sys

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('voz')
ap.add_argument('--atempo', type=float, help='acelera la voz antes de medir (ej. 1.08)')
ap.add_argument('--modelo', default='small', help='modelo de Whisper (default small)')
a = ap.parse_args()

voz = os.path.abspath(a.voz)
if a.atempo:
    rapida = os.path.splitext(voz)[0] + '-rapida.mp3'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', voz, '-filter:a', f'atempo={a.atempo}', rapida], check=True)
    print('listo', rapida)
    voz = rapida
base = os.path.splitext(voz)[0]

# --- silencios
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', voz]))
log = subprocess.run(['ffmpeg', '-nostats', '-i', voz, '-af', 'silencedetect=noise=-35dB:d=0.15', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
filas, ini = [], None
for l in log.splitlines():
    m = re.search(r'silence_start: (-?[\d.]+)', l)
    if m: ini = max(0.0, float(m.group(1)))
    m = re.search(r'silence_end: ([\d.]+) \| silence_duration: ([\d.]+)', l)
    if m and ini is not None:
        filas.append((ini, float(m.group(2)))); ini = None
if ini is not None:   # el audio termina en silencio: ffmpeg no escribe silence_end
    filas.append((ini, dur - ini))
open(base + '-silencios.txt', 'w').write(''.join(f'{s:.3f} {d:.3f}\n' for s, d in filas))
print('listo', base + '-silencios.txt', f'({len(filas)} silencios)')

# --- palabras
import whisper
r = whisper.load_model(a.modelo).transcribe(voz, language='es', word_timestamps=True)
pal = [{'w': w['word'].strip(), 's': round(w['start'], 3), 'e': round(w['end'], 3)} for seg in r['segments'] for w in seg['words']]
json.dump(pal, open(base + '-palabras.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('listo', base + '-palabras.json', f'({len(pal)} palabras)')

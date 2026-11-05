#!/usr/bin/env python3
"""Le pone la voz a un mp4 ya renderizado. Cada tramo del mp3 (segmentos.json) suena al arrancar su escena
(escenas.json, que escribe render.py), corrido `lead` segundos. Escenas que el mp4 no llega a mostrar se saltean.
Si existe extra.json en la carpeta de voz, suma tramos de otros audios con la misma forma ({audio, n, desde, hasta, lead}):
sirve para escenas mudas del guion, que alinear.py no conoce y por eso no van en segmentos.json.
Uso:  python3 -I mezclar.py <video.mp4> <salida.mp4> <carpeta-voz> <escenas.json>
  carpeta-voz: donde están segmentos.json y los mp3 que nombra (la misma donde corrió alinear.py).
Sin -shortest: con apad infinito ffmpeg 7 corta con «No space left on device» (no es el disco)."""
import json, os, subprocess, sys
if len(sys.argv) != 5:
    sys.exit(__doc__)
vid, out, voz, escjson = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3]), sys.argv[4]
esc = {e['n']: e for e in json.load(open(escjson))['escenas']}
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', vid]))
tramos = json.load(open(os.path.join(voz, 'segmentos.json')))
if os.path.exists(os.path.join(voz, 'extra.json')):
    tramos += json.load(open(os.path.join(voz, 'extra.json')))
audios = list(dict.fromkeys(s['audio'] for s in tramos))   # un -i por audio, en orden de aparición
partes, n_in = [], 0
for s in tramos:
    e = esc.get(s['n'])
    if not e or e['start'] >= dur - .2: continue
    ms = int(round((e['start'] + s['lead']) * 1000))
    k = audios.index(s['audio']) + 1
    partes.append(f"[{k}:a]atrim={s['desde']}:{s['hasta']},asetpts=PTS-STARTPTS,adelay={ms}|{ms}[a{n_in}]")
    n_in += 1
fil = ';'.join(partes) + ';' + ''.join(f'[a{i}]' for i in range(n_in)) + f'amix=inputs={n_in}:normalize=0,apad=whole_dur={dur:.3f}[voz]'
entradas = sum((['-i', os.path.join(voz, a)] for a in audios), [])
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vid, *entradas,
                '-filter_complex', fil, '-map', '0:v', '-map', '[voz]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                '-t', f'{dur:.3f}', out], check=True)
print('listo', out, f'({n_in} tramos de voz)')

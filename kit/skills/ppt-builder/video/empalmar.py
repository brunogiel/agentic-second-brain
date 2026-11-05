#!/usr/bin/env python3
"""Arma un mp3 nuevo pegando tramos de dos audios, para cambiar una frase sin regenerar toda la voz.
Uso:  python3 -I empalmar.py <base.mp3> <parche.mp3> <salida.mp3> <corte> [<corte> ...]
  corte = fuente:desde:hasta   (segundos; fuente = base | parche; `hasta` vacío o `fin` = hasta el final del audio)
  Los tramos se pegan en el orden en que se dan. Ejemplo: cambiar la frase que va de 14,8 s a 19,1 s de la base:
    python3 -I empalmar.py voz.mp3 parche.mp3 voz-v2.mp3 base:0:14.8 parche:0:4.1 base:19.1:fin
Cortar SIEMPRE en el medio de un silencio de <voz>-silencios.txt (tiempos_voz.py), nunca a mitad de palabra.
El parche tiene que salir con el mismo tempo que la base (si la base se aceleró con --atempo, el parche también).
Todo se pasa al formato de la base (frecuencia y canales) antes de concatenar. Después de empalmar, volver a correr
tiempos_voz.py y alinear.py sobre el mp3 nuevo."""
import os, subprocess, sys
if len(sys.argv) < 5:
    sys.exit(__doc__)
base, parche, salida, cortes = [os.path.abspath(x) for x in sys.argv[1:4]] + [sys.argv[4:]]
fuentes = {'base': (0, base), 'parche': (1, parche)}
def sonda(f, campo):
    return subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', f'stream={campo}', '-of', 'csv=p=0', f]).decode().strip()
sr, ch = sonda(base, 'sample_rate'), int(sonda(base, 'channels'))
layout = 'mono' if ch == 1 else 'stereo'
partes, ins = [], ''
for i, c in enumerate(cortes):
    f, d, h = (c.split(':') + ['', ''])[:3]
    if f not in fuentes: sys.exit(f'corte "{c}": la fuente es base o parche')
    k = fuentes[f][0]
    trim = f'start={float(d)}' + (f':end={float(h)}' if h not in ('', 'fin') else '')
    partes.append(f'[{k}:a]atrim={trim},asetpts=PTS-STARTPTS,aresample={sr},aformat=channel_layouts={layout}[c{i}]')
    ins += f'[c{i}]'
fil = ';'.join(partes) + f';{ins}concat=n={len(cortes)}:v=0:a=1[out]'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', base, '-i', parche, '-filter_complex', fil, '-map', '[out]',
                '-c:a', 'libmp3lame', '-b:a', '128k', salida], check=True)
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', salida]))
print('listo', salida, f'({dur:.3f} s)')

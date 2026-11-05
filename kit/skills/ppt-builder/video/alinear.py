#!/usr/bin/env python3
"""Alinea la voz con el guion y escribe los tiempos por palabra para el video.
Uso:  python3 -I alinear.py <guion.md> <voz.mp3>
Lee el guion (las filas de la tabla que empiezan con `| n |`; columna 1 = número de escena, columna 2 = narración;
una fila sin narración se saltea, es una escena muda) y, junto al mp3, <voz>-palabras.json y <voz>-silencios.txt
(los saca tiempos_voz.py). Escribe en la carpeta del mp3:
  tiempos.json    lo lee render.py (formato en el comentario del script de plantilla.html)
  segmentos.json  qué tramo del mp3 suena en cada escena; lo usa mezclar.py
Los cortes van en el silencio real más cercano: Whisper a veces pega el final de una escena con el arranque de la siguiente."""
import difflib, json, os, re, sys, unicodedata
if len(sys.argv) != 3:
    sys.exit(__doc__)
GUION, MP3 = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
AQUI = os.path.dirname(MP3)
AUDIO = os.path.basename(MP3); BASE = os.path.splitext(MP3)[0]
LEAD, POST = 0.3, 0.2   # silencio al arrancar la escena; margen al final del audio
# Whisper escribe los números con cifras: se pasan a palabra para poder comparar con el guion (0 a 30)
UNI = ['cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve', 'diez', 'once', 'doce', 'trece', 'catorce',
       'quince', 'dieciseis', 'diecisiete', 'dieciocho', 'diecinueve', 'veinte', 'veintiuno', 'veintidos', 'veintitres', 'veinticuatro',
       'veinticinco', 'veintiseis', 'veintisiete', 'veintiocho', 'veintinueve', 'treinta']
NUM = {str(i): w for i, w in enumerate(UNI)}

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', s)

escenas, nums = [], []
for l in open(GUION, encoding='utf-8'):
    if re.match(r'\| *\d+ *\|', l):
        c = [x.strip() for x in l.split('|')]
        if c[2]: nums.append(int(c[1])); escenas.append(c[2])
guion = [(i, w) for i, t in enumerate(escenas) for w in t.split()]
a = [norm(w) for _, w in guion]
# Whisper pega «Fase B» en «FaseB»: una palabra seguida de UNA mayúscula se parte en dos, si el guion las trae separadas
sueltas = {(a[k - 1], a[k]) for k in range(1, len(a)) if len(a[k]) == 1}
voz = []
for p in json.load(open(BASE + '-palabras.json', encoding='utf-8')):
    w = re.sub(r'[^\wáéíóúüñÁÉÍÓÚÜÑ]', '', p['w'])
    m = re.fullmatch(r'(\w*[a-záéíóúüñ])([A-ZÁÉÍÓÚÜÑ])', w)
    if m and (norm(m.group(1)), norm(m.group(2))) in sueltas:
        mid = (p['s'] + p['e']) / 2
        voz += [(norm(m.group(1)), p['s'], mid), (norm(m.group(2)), mid, p['e'])]
    else:
        n = norm(w)
        voz.append((NUM.get(n, n), p['s'], p['e']))
b = [v[0] for v in voz]
t = [None] * len(guion)
for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
    for k in range(blk.size):
        t[blk.a + k] = (voz[blk.b + k][1], voz[blk.b + k][2])
faltan = [guion[k][1] for k, x in enumerate(t) if x is None]
for k in range(len(t)):   # lo que no calzó se interpola entre vecinos
    if t[k] is None:
        prev = next((t[j] for j in range(k - 1, -1, -1) if t[j]), (0, 0))
        nxt = next((t[j] for j in range(k + 1, len(t)) if t[j]), (prev[1] + .3, prev[1] + .5))
        t[k] = (prev[1], nxt[0])
sil = [(float(x), float(x) + float(d)) for x, d in (l.split() for l in open(BASE + '-silencios.txt') if l.strip())]
def corte(fin, ini):   # entre la última palabra de una escena y la primera de la siguiente
    est = (fin + ini) / 2
    cerca = [(abs((a + b) / 2 - est), (a + b) / 2) for a, b in sil if abs((a + b) / 2 - est) < 1.0]
    return min(cerca)[1] if cerca else est
tiempos, segs = {'escenas': []}, []
for i, texto in enumerate(escenas):
    ks = [k for k, (e, _) in enumerate(guion) if e == i]
    # El corte entre escenas va en el medio del silencio: Whisper estira el final de la última palabra.
    a0 = 0.0 if i == 0 else corte(t[ks[0] - 1][1], t[ks[0]][0])
    a1 = t[ks[-1]][1] + POST if i == len(escenas) - 1 else corte(t[ks[-1]][1], t[ks[-1] + 1][0])
    tiempos['escenas'].append({'n': nums[i], 'dur': round(LEAD + a1 - a0, 3),
                               'palabras': [[guion[k][1], round(LEAD + max(t[k][0] - a0, .02), 3)] for k in ks]})
    segs.append({'audio': AUDIO, 'n': nums[i], 'desde': round(a0, 3), 'hasta': round(a1, 3), 'lead': LEAD})
json.dump(tiempos, open(os.path.join(AQUI, 'tiempos.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(segs, open(os.path.join(AQUI, 'segmentos.json'), 'w'), ensure_ascii=False, indent=1)
print(f'{len(guion)} palabras del guion, {len(voz)} de la voz, {len(faltan)} interpoladas: {faltan}')
for s in segs: print(s)

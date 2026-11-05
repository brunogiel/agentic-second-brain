#!/usr/bin/env python3
"""Renderiza un HTML de video (plantilla.html) a MP4 (1920x1080, 30 fps, H.264 yuv420p) cuadro a cuadro.
Uso, desde cualquier carpeta:  python3 -I /ruta/a/render.py <video.html> [salida.mp4] [hasta_segundos]
  - salida.mp4: por defecto <video>.mp4 junto al HTML. escenas.json (inicio y fin real de cada escena) se escribe junto a la salida.
  - hasta_segundos: corta el render ahí. Con 0.1 renderiza 4 cuadros y deja escenas.json con el total: sirve para medir.
Requiere Playwright de Python (si el python del sistema no lo tiene: python3 -m venv v && v/bin/pip install playwright,
y correr v/bin/python -I render.py ...) y ffmpeg en el PATH.
Para cada cuadro llama window.renderAt(t), saca screenshot y lo manda por pipe a ffmpeg.
Voz: si junto al HTML existe voz/tiempos.json (o tiempos.json), se inyecta como window.__TIEMPOS__ antes de cargar el HTML:
los tiempos por palabra de la voz pisan el WPS (formato en el comentario del script de plantilla.html).
Lo escribe alinear.py; para usar otro archivo, variable de entorno TIEMPOS=/ruta/tiempos.json."""
import asyncio, json, os, pathlib, subprocess, sys
from playwright.async_api import async_playwright

if len(sys.argv) < 2:
    sys.exit(__doc__)
HTML = os.path.abspath(sys.argv[1])
AQUI = os.path.dirname(HTML)
OUT = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.splitext(HTML)[0] + '.mp4'
HASTA = float(sys.argv[3]) if len(sys.argv) > 3 else None
WORKERS = 4
# tiempos.json se busca junto al HTML, no junto a este script
TIEMPOS = next((p for p in [os.environ.get('TIEMPOS'), os.path.join(AQUI, 'voz', 'tiempos.json'), os.path.join(AQUI, 'tiempos.json')]
                if p and os.path.exists(p)), None)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        pages = []
        for _ in range(WORKERS):
            pg = await browser.new_page(viewport={'width': 1920, 'height': 1080}, device_scale_factor=1)
            if TIEMPOS:
                await pg.add_init_script('window.__TIEMPOS__=' + open(TIEMPOS, encoding='utf8').read())
            pg.on('console', lambda m: print('[console]', m.text) if m.type in ('warning', 'error') else None)
            pg.on('pageerror', lambda e: print('[pageerror]', e))
            await pg.goto(pathlib.Path(HTML).as_uri() + '?render=1')   # as_uri escapa espacios y emojis de la ruta
            await pg.wait_for_function('window.__ready===true', timeout=30000)
            pages.append(pg)
        print('tiempos:', TIEMPOS or 'ninguno (WPS, sin voz)')
        total = await pages[0].evaluate('window.TOTAL')
        fps = await pages[0].evaluate('window.FPS')
        scenes = await pages[0].evaluate('window.SCENES')
        n = int(round(total * fps)) + 1
        if HASTA: n = min(n, int(round(HASTA * fps)) + 1)
        with open(os.path.join(os.path.dirname(OUT), 'escenas.json'), 'w', encoding='utf8') as f:
            json.dump({'fps': fps, 'total': round(total, 3), 'frames': n, 'escenas': scenes}, f, ensure_ascii=False, indent=1)
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(fps), '-c:v', 'png', '-i', '-',
                               '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', str(fps),
                               '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
        async def shot(pg, i):
            await pg.evaluate(f'window.renderAt({i / fps})')
            return await pg.screenshot(type='png')
        i = 0
        while i < n:
            idx = list(range(i, min(n, i + WORKERS)))
            imgs = await asyncio.gather(*[shot(pages[k], j) for k, j in enumerate(idx)])
            for im in imgs:
                ff.stdin.write(im)
            i += len(idx)
            if i % 300 < WORKERS:
                print(f'{i}/{n}', flush=True)
        ff.stdin.close(); ff.wait()
        await browser.close()
    print('listo', OUT)

asyncio.run(main())

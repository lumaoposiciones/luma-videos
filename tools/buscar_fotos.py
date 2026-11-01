#!/usr/bin/env python3
"""Busca fotos en Pixabay y crea una hoja de contacto con sus ids para elegir a ojo.

Uso:  PIXABAY_KEY=... python3 tools/buscar_fotos.py "classroom teacher" [salida.jpg]
Muestra hasta 12 fotos verticales no usadas aún, con su id encima. Pon el id elegido en "foto_id".
"""
import json, os, sys, urllib.request, urllib.parse, pathlib, io
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "Mozilla/5.0"}
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
used = set((ROOT / "tools" / "fotos_usadas.txt").read_text().split())
q, out = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "/tmp/fotos.jpg")
p = urllib.parse.urlencode(dict(key=os.environ["PIXABAY_KEY"], q=q, image_type="photo", orientation="vertical",
                                per_page=40, safesearch="true", min_width=1080))
hits = [h for h in json.loads(get("https://pixabay.com/api/?" + p))["hits"] if str(h["id"]) not in used][:12]
if not hits:
    sys.exit("Sin resultados: prueba otras palabras en inglés")
sheet = Image.new("RGB", (6 * 200, 2 * 330), "white"); d = ImageDraw.Draw(sheet)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
for k, h in enumerate(hits):
    im = Image.open(io.BytesIO(get(h["webformatURL"]))).convert("RGB"); im.thumbnail((200, 300))
    x, y = (k % 6) * 200, (k // 6) * 330
    sheet.paste(im, (x, y + 28)); d.text((x + 4, y + 4), str(h["id"]), font=f, fill="black")
    print(h["id"], h["tags"][:80])
sheet.save(out, quality=85); print("hoja:", out)

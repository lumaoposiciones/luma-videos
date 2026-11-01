#!/usr/bin/env python3
"""Genera un vídeo vertical de LuMa Oposiciones a partir de un guion JSON.

Uso:  PIXABAY_KEY=... ELEVEN_KEY=... python3 tools/make_video.py guiones/AAAA-MM-DD-tema.json

Salida: videos/<slug>.mp4 y portadas/<slug>.jpg  (y apunta las fotos usadas en tools/fotos_usadas.txt)

Formato del guion (ver guiones/ para ejemplos):
{
  "slug": "2026-11-04-dua",
  "portada": ["Diseño Universal", "de Aprendizaje"],     # 1-3 líneas, letra amarilla inclinada
  "escenas": [
    {"foto": "classroom teacher", "recuadro": "¿TEXTO DEL GANCHO?", "titulo": "...", "texto": "...", "voz": "..."},
    {"foto": "notebook desk", "num": "1", "titulo": "...", "texto": "...", "voz": "..."},
    ...
  ],
  "recuadro_comun": "Texto del recuadro superior para escenas sin 'recuadro'"
}
"""
import json, os, sys, subprocess, urllib.request, urllib.parse, pathlib, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1080, 1920
BW, BH = round(W * 1.12), round(H * 1.12)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FCN = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheroscn-bold.otf"
VOICE = "onwK4e9ZLuTAKqWW03F9"  # Daniel (voz predeterminada, plan gratuito)
UA = {"User-Agent": "Mozilla/5.0"}
font = lambda p, s: ImageFont.truetype(p, s)


def get(url, headers=None, data=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})}, data=data)
    return urllib.request.urlopen(req, timeout=90).read()


# ---------- fotos ----------
USED = ROOT / "tools" / "fotos_usadas.txt"


def pick_photo(query, dest):
    used = set(USED.read_text().split()) if USED.exists() else set()
    key = os.environ["PIXABAY_KEY"]
    for orient in ("vertical", "all"):
        q = urllib.parse.urlencode(dict(key=key, q=query, image_type="photo", orientation=orient,
                                        per_page=30, safesearch="true", min_width=1080, lang="en"))
        hits = json.loads(get("https://pixabay.com/api/?" + q))["hits"]
        bad = ("isolated", "transparent", "cutout", "png", "white background", "black background",
               "illustration", "vector", "3d", "render", "clipart", "mockup", "christmas", "halloween")
        hits = [h for h in hits if str(h["id"]) not in used and h["imageHeight"] >= 1300
                and not any(b in h["tags"].lower() for b in bad)]
        if hits:
            h = hits[0]
            open(dest, "wb").write(get(h["largeImageURL"]))
            with open(USED, "a") as f:
                f.write(f"{h['id']}\n")
            return h["id"]
    raise SystemExit(f"Sin fotos para '{query}': prueba otra búsqueda en inglés")


def cover_crop(path):
    im = Image.open(path).convert("RGB")
    s = max(BW / im.width, BH / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - BW) // 2, (im.height - BH) // 2
    return im.crop((x, y, x + BW, y + BH))


# ---------- textos ----------
def wrap(d, t, f, mw):
    out, cur = [], ""
    for w in t.split():
        tt = (cur + " " + w).strip()
        if d.textlength(tt, font=f) <= mw:
            cur = tt
        else:
            out.append(cur); cur = w
    out.append(cur)
    return out


def overlay(box, num, title, body):
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = Image.new("L", (1, H))
    for y in range(H):
        g.putpixel((0, y), int(70 + 90 * abs(y - H * 0.55) / (H * 0.55)))
    o.alpha_composite(Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [g.resize((W, H))]))
    d = ImageDraw.Draw(o)
    fh = font(FB, 52); y = 190
    for l in wrap(d, box, fh, 900):
        tw = d.textlength(l, font=fh)
        d.rectangle([W / 2 - tw / 2 - 22, y - 8, W / 2 + tw / 2 + 22, y + 66], fill="white")
        d.text((W / 2, y + 29), l, font=fh, fill="black", anchor="mm"); y += 74
    y = 760
    if num:
        d.ellipse([W / 2 - 60, y, W / 2 + 60, y + 120], fill="#e07a3c")
        d.text((W / 2, y + 60), str(num), font=font(FB, 70), fill="white", anchor="mm"); y += 160
    ft = font(FB, 92 if len(title) < 22 else 76)
    for l in wrap(d, title, ft, 960):
        d.text((W / 2, y + 46), l, font=ft, fill="white", anchor="mm", stroke_width=6, stroke_fill="black"); y += 108
    y += 30; fb = font(FB, 54)
    for l in wrap(d, body, fb, 920):
        d.text((W / 2, y + 30), l, font=fb, fill="white", anchor="mm", stroke_width=5, stroke_fill="black"); y += 72
    d.text((W / 2, 1690), "@luma.oposiciones", font=font(FB, 38), fill=(255, 255, 255, 220), anchor="mm",
           stroke_width=3, stroke_fill="black")
    return o


def cover(bg, lines):
    b = bg.crop(((BW - W) // 2, (BH - H) // 2, (BW - W) // 2 + W, (BH - H) // 2 + H)).convert("RGBA")
    size = 128 if max(len(l) for l in lines) <= 16 else 108
    f = font(FCN, size); L = Image.new("RGBA", (1600, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    lh = int(size * 1.06); y = 450 - len(lines) * lh // 2
    for l in lines:
        d.text((800, y + lh // 2), l, font=f, fill="#ffe500", anchor="mm", stroke_width=11, stroke_fill="black"); y += lh
    sh = L.split()[3].filter(ImageFilter.GaussianBlur(12)).point(lambda a: int(a * 0.6))
    S = Image.new("RGBA", L.size, (0, 0, 0, 0)); S.putalpha(sh); S.alpha_composite(L)
    R = S.rotate(25, expand=True, resample=Image.BICUBIC)
    R = R.crop(R.getbbox())
    if R.width > W - 40:
        R = R.resize((W - 40, round(R.height * (W - 40) / R.width)), Image.LANCZOS)
    b.alpha_composite(R, (W // 2 - R.width // 2, 1000 - R.height // 2))
    return b.convert("RGB")


# ---------- voz ----------
def tts(text, dest):
    body = json.dumps(dict(text=text, model_id="eleven_multilingual_v2", language_code="es",
                           voice_settings=dict(stability=0.5, similarity_boost=0.75, speed=1.2))).encode()
    open(dest, "wb").write(get(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",
                               {"xi-api-key": os.environ["ELEVEN_KEY"], "Content-Type": "application/json"}, body))


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]).decode())


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, args)], check=True)


# ---------- principal ----------
def main(spec_path):
    s = json.load(open(spec_path)); slug = s["slug"]
    work = pathlib.Path("/tmp/luma_" + slug); work.mkdir(parents=True, exist_ok=True)
    (ROOT / "videos").mkdir(exist_ok=True); (ROOT / "portadas").mkdir(exist_ok=True)
    chars = sum(len(e["voz"]) for e in s["escenas"])
    print("caracteres de voz:", chars)
    if chars > 450:
        raise SystemExit("Guion demasiado largo (>450 caracteres de voz): acórtalo")
    lst = work / "list.txt"; lines = []
    bgs = []
    for i, e in enumerate(s["escenas"]):
        if e.get("foto_id"):  # forzar una foto concreta de Pixabay por su id
            h = json.loads(get("https://pixabay.com/api/?" + urllib.parse.urlencode(
                dict(key=os.environ["PIXABAY_KEY"], id=e["foto_id"]))))["hits"][0]
            open(work / f"p{i}.jpg", "wb").write(get(h["largeImageURL"]))
            if str(e["foto_id"]) not in (USED.read_text().split() if USED.exists() else []):
                with open(USED, "a") as f:
                    f.write(f"{e['foto_id']}\n")
        else:
            pick_photo(e["foto"], work / f"p{i}.jpg")
        bg = cover_crop(work / f"p{i}.jpg"); bg.save(work / f"bg{i}.png"); bgs.append(bg)
        overlay(e.get("recuadro") or s["recuadro_comun"], e.get("num"), e["titulo"], e["texto"]).save(work / f"ov{i}.png")
        # reutiliza la voz si el texto no ha cambiado (ahorra créditos de ElevenLabs)
        tag = work / f"a{i}.txt"
        if not ((work / f"a{i}.mp3").exists() and tag.exists() and tag.read_text() == e["voz"]):
            tts(e["voz"], work / f"a{i}.mp3"); tag.write_text(e["voz"])
    cov = cover(bgs[0], s["portada"])
    cov.save(ROOT / "portadas" / f"{slug}.jpg", quality=90); cov.save(work / "cover.png")
    ff("-framerate", 30, "-i", work / "cover.png", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
       "-filter_complex", "[0:v]loop=-1:1,trim=duration=0.1,setpts=PTS-STARTPTS,fps=30,format=yuv420p[v]",
       "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", 20, "-r", 30,
       "-c:a", "aac", "-b:a", "160k", "-ac", 2, "-t", 0.1, work / "tmp_c.mp4")
    os.replace(work / "tmp_c.mp4", work / "sc_c.mp4"); lines.append("file 'sc_c.mp4'")
    for i in range(len(s["escenas"])):
        D = round(dur(work / f"a{i}.mp3") + 0.35, 2)
        fc = (f"[0:v]loop=-1:1,trim=duration={D},setpts=PTS-STARTPTS,"
              f"scale=w='2*trunc(({BW}-125*t/{D})/2)':h=-2:eval=frame,crop={W}:{H},setsar=1[b];"
              f"[1:v]loop=-1:1,trim=duration={D},setpts=PTS-STARTPTS[o];"
              f"[b][o]overlay=0:0,fps=30,format=yuv420p[v];"
              f"[2:a]adelay=100|100,apad,atrim=duration={D},aresample=44100[a]")
        ff("-framerate", 30, "-i", work / f"bg{i}.png", "-framerate", 30, "-i", work / f"ov{i}.png",
           "-i", work / f"a{i}.mp3", "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", 20, "-r", 30, "-c:a", "aac", "-b:a", "160k",
           "-ac", 2, "-t", D, work / f"tmp_{i}.mp4")
        os.replace(work / f"tmp_{i}.mp4", work / f"sc_{i}.mp4"); lines.append(f"file 'sc_{i}.mp4'")
    lst.write_text("\n".join(lines) + "\n")
    out = ROOT / "videos" / f"{slug}.mp4"
    ff("-f", "concat", "-safe", 0, "-i", lst, "-c", "copy", "-movflags", "+faststart", work / "final_tmp.mp4")
    os.replace(work / "final_tmp.mp4", out)
    # hoja de control: portada + cada escena con su texto, para revisarla antes de publicar
    thumbs = [cov.resize((270, 480))]
    for i, bg in enumerate(bgs):
        t = bg.crop(((BW - W) // 2, (BH - H) // 2, (BW - W) // 2 + W, (BH - H) // 2 + H)).convert("RGBA")
        t.alpha_composite(Image.open(work / f"ov{i}.png")); thumbs.append(t.convert("RGB").resize((270, 480)))
    sheet = Image.new("RGB", (270 * len(thumbs), 480))
    for k, t in enumerate(thumbs):
        sheet.paste(t, (270 * k, 0))
    sheet.save(work / "control.jpg", quality=85)
    print("OK", out, round(dur(out), 1), "s")
    print("control:", work / "control.jpg")


if __name__ == "__main__":
    main(sys.argv[1])

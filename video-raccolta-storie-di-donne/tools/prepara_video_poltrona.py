"""Compone i fotogrammi RGBA della poltrona dal video sorgente e dalle maschere.

Uso: python3 tools/prepara_video_poltrona.py <video.mp4> <cartella_maschere> <cartella_uscita>
Scrive <uscita>/0001.png ... (ritagliati sul riquadro comune) e <uscita>/meta.json,
più assets/poltrona_dritta.png (ultimo fotogramma, poltrona "a sedia") e assets/poltrona_icona.png.
Le maschere si ottengono con tools/scontorna_fotogrammi.py (rembg, modello birefnet-general-lite).
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageFilter

video, masks, out = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
fps = 24
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, f"{tmp}/%04d.png"], check=True)
    frames = sorted(pathlib.Path(tmp).glob("*.png"))
    alphas = []
    for f in frames:
        m = Image.open(masks / f.name).convert("L")
        # pulizia: niente aloni deboli, bordo appena ammorbidito
        m = m.point(lambda v: 0 if v < 24 else min(255, int((v - 24) * 255 / 200)))
        alphas.append(m.filter(ImageFilter.GaussianBlur(0.5)))
    union = np.zeros(np.asarray(alphas[0]).shape, bool)
    for m in alphas:
        union |= np.asarray(m) > 10
    ys, xs = np.where(union)
    pad = 6
    box = [int(xs.min()) - pad, int(ys.min()) - pad, int(xs.max()) + pad, int(ys.max()) + pad]
    # piedini e base: righe più basse della maschera nel primo fotogramma
    # base: fascia in basso della maschera del primo fotogramma (posa reclinata)
    a0 = np.asarray(alphas[0]) > 128
    rows = np.where(a0.any(axis=1))[0]
    foot_y = int(rows.max())
    base = a0[foot_y - 90:foot_y + 1]
    bys, bx = np.where(base)
    base_y = [int(foot_y - 90 + bys.min()), foot_y]
    for f, m in zip(frames, alphas):
        im = Image.open(f).convert("RGBA")
        im.putalpha(m)
        im.crop(box).save(out / f.name, optimize=False, compress_level=3)
    # poltrona "a sedia" (ultimo fotogramma della sorgente) per le 8 poltrone grandi e per l'icona
    assets = pathlib.Path(__file__).resolve().parent.parent / "assets"
    im = Image.open(frames[-1]).convert("RGBA")
    im.putalpha(alphas[-1])
    im = im.crop(alphas[-1].point(lambda v: 255 if v > 10 else 0).getbbox())
    im.save(assets / "poltrona_dritta.png", optimize=True)
    sil = Image.new("RGBA", im.size, (146, 67, 62, 255))
    sil.putalpha(im.getchannel("A").point(lambda v: 255 if v > 110 else 0).filter(ImageFilter.GaussianBlur(0.8)))
    sil = sil.resize((round(im.size[0] * 132 / im.size[1]), 132), Image.LANCZOS)
    sil.save(assets / "poltrona_icona.png", optimize=True)
    upright_ar = round(im.size[0] / im.size[1], 4)
meta = {"dir": out.name, "frames": len(frames), "fps": fps, "box": box,
        "foot": [int((box[0] + box[2]) / 2), foot_y], "base": [int(bx.min()), int(bx.max())], "baseY": base_y, "drittaAR": upright_ar}
(out / "meta.json").write_text(json.dumps(meta))
print(meta)

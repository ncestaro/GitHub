"""Ritaglia la foto della poltrona (fondo bianco) e crea l'icona bordeaux per la barra.

Uso: python3 prepara_poltrona.py <foto.jpg>
Scrive assets/poltrona.png (ritaglio a colori) e assets/poltrona_icona.png (sagoma bordeaux).
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

im = Image.open(sys.argv[1]).convert("RGB")
a = np.asarray(im).astype(np.int16)
# "bianco" = tutti i canali alti e poco saturo
white = (a.min(axis=2) > 236) & (a.max(axis=2) - a.min(axis=2) < 14)
# sfondo = bianco connesso al bordo dell'immagine
lab, _ = ndimage.label(white)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border))
# anche i "buchi" chiusi di bianco puro (tra bracciolo e schienale, nella meccanica)
for l in set(range(1, lab.max() + 1)) - border:
    m = lab == l
    if m.sum() > 400 and a[m].mean() > 250:
        bg |= m
fg = ~bg
fg = ndimage.binary_opening(fg, iterations=1)
# bordo morbido: alpha proporzionale alla distanza dal bianco nei pixel di contorno
dist = (255 - a.min(axis=2)).clip(0, 40) / 40.0
edge = ndimage.binary_dilation(fg, iterations=2) & ~ndimage.binary_erosion(fg, iterations=2)
alpha = np.where(fg, 1.0, 0.0)
alpha = np.where(edge, np.maximum(alpha * 0.6, dist) * ndimage.binary_dilation(fg, iterations=2), alpha)
A = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))

out = im.convert("RGBA"); out.putalpha(A)
bb = A.point(lambda v: 255 if v > 10 else 0).getbbox()
out = out.crop(bb)
out.save("assets/poltrona.png", optimize=True)
print("poltrona", out.size, "rapporto", round(out.size[0] / out.size[1], 3))

# icona: sagoma piena bordeaux, alta 132 px (mostrata a 66 px)
sil = Image.new("RGBA", out.size, (146, 67, 62, 255)); sil.putalpha(out.getchannel("A"))
h = 132; sil = sil.resize((round(out.size[0] * h / out.size[1]), h), Image.LANCZOS)
sil.save("assets/poltrona_icona.png", optimize=True)
print("icona", sil.size)

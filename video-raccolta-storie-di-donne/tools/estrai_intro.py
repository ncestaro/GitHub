"""Estrae dal file Illustrator (SVG) i ritagli della figura e le righe del titolo, uno per file.

Uso: python3 tools/estrai_intro.py [assets/intro/progetto_illustrator.svgz]
Scrive assets/intro/figura_NN.svg (stesso riquadro per tutti, con l'ombra di ciascun ritaglio),
assets/intro/titolo_N.svg (una riga del titolo ciascuno) e assets/intro/intro.json (riquadri e proporzioni).
"""
import copy
import gzip
import json
import pathlib
import sys

from lxml import etree
from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).resolve().parent.parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else here / "assets/intro/progetto_illustrator.svgz"
out = here / "assets/intro"
SVG = "http://www.w3.org/2000/svg"
ns = {"s": SVG}

raw = gzip.open(src).read() if src.suffix == ".svgz" else src.read_bytes()
root = etree.fromstring(raw)
defs = root.find("s:defs", ns)
figure = root.xpath("//s:g[@id='Livello_1']", namespaces=ns)[0]
pieces = [g for g in figure if g.tag == f"{{{SVG}}}g"]
title_root = root.xpath("//s:g[@id='Livello_5']/s:g", namespaces=ns)[1]   # [0] = riga dell'ospedale
lines = [g for g in title_root.iter(f"{{{SVG}}}g") if g is not title_root and g.getparent() is title_root]

# riquadri reali misurati nel browser
for i, g in enumerate(pieces):
    g.set("data-k", f"f{i}")
for i, g in enumerate(lines):
    g.set("data-k", f"t{i}")
tmp = out / "_misura.svg"
tmp.write_bytes(etree.tostring(root))
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = b.new_page()
    pg.goto(tmp.as_uri())
    boxes = pg.evaluate("""() => Object.fromEntries([...document.querySelectorAll('[data-k]')].map(e => {
        const b = e.getBBox(); return [e.dataset.k, [b.x, b.y, b.width, b.height]]; }))""")
    b.close()
tmp.unlink()


def write(path, vb, groups):
    svg = etree.Element(f"{{{SVG}}}svg", nsmap={None: SVG, "xlink": "http://www.w3.org/1999/xlink"})
    svg.set("viewBox", " ".join(f"{v:.1f}" for v in vb))
    svg.set("width", f"{vb[2]:.1f}")
    svg.set("height", f"{vb[3]:.1f}")
    svg.append(copy.deepcopy(defs))
    for g in groups:
        c = copy.deepcopy(g)
        c.attrib.pop("data-k", None)
        svg.append(c)
    path.write_bytes(etree.tostring(svg, xml_declaration=True, encoding="UTF-8"))


# figura: un unico riquadro per tutti i ritagli (più margine per le ombre)
xs = [boxes[f"f{i}"] for i in range(len(pieces))]
m = 24
x0 = min(b[0] for b in xs) - m; y0 = min(b[1] for b in xs) - m
x1 = max(b[0] + b[2] for b in xs) + m; y1 = max(b[1] + b[3] for b in xs) + m
fig_vb = [x0, y0, x1 - x0, y1 - y0]
meta = {"figura": {"viewBox": fig_vb, "pezzi": []}, "titolo": []}
for i, g in enumerate(pieces):
    name = f"figura_{i + 1:02d}.svg"
    write(out / name, fig_vb, [g])
    fill = g[0].get("class")
    meta["figura"]["pezzi"].append({"file": name, "classe": fill, "box": boxes[f"f{i}"]})
for i, g in enumerate(lines):
    bx = boxes[f"t{i}"]; m = 6
    vb = [bx[0] - m, bx[1] - m, bx[2] + 2 * m, bx[3] + 2 * m]
    name = f"titolo_{i + 1}.svg"
    write(out / name, vb, [g])
    meta["titolo"].append({"file": name, "viewBox": vb})
(out / "intro.json").write_text(json.dumps(meta, indent=1))
print(json.dumps(meta, indent=1))

"""Esporta il contatore animato in MP4 (verticale 1080x1920 e orizzontale 1920x1080).

Uso:
  pip install playwright && python3 render.py              # entrambi i formati
  python3 render.py --stills                                # solo anteprime PNG
  python3 render.py --totale 9320 --fps 30
Richiede ffmpeg nel PATH.
"""
import argparse
import pathlib
import subprocess
import tempfile

from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent
out = here / "export"
out.mkdir(exist_ok=True)

FORMATS = {"v": (1080, 1920, "verticale_1080x1920"), "h": (1920, 1080, "orizzontale_1920x1080")}
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

ap = argparse.ArgumentParser()
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--totale", type=int, default=9320)
ap.add_argument("--stills", action="store_true")
ap.add_argument("--formati", default="h")  # "v" = verticale 1080x1920
args = ap.parse_args()

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME if pathlib.Path(CHROME).exists() else None)
    for f in args.formati:
        w, h, name = FORMATS[f]
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto((here / "counter.html").resolve().as_uri() + f"?f={f}&totale={args.totale}")
        T = pg.evaluate("window.ready")
        if args.stills:
            for t in (2.0, 4.2, 5.0, 5.7, 9.0, T["dur"]):
                pg.evaluate(f"renderAt({t})")
                pg.screenshot(path=str(out / f"anteprima_{name}_{t:04.1f}s.png"))
            continue
        frames = round(T["dur"] * args.fps)
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(frames):
                pg.evaluate(f"renderAt({i / args.fps})")
                pg.screenshot(path=f"{tmp}/{i:05d}.png")
            mp4 = out / f"raccolta_{args.totale}_{name}.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(args.fps),
                            "-i", f"{tmp}/%05d.png", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)], check=True)
            # ultimo fotogramma come immagine fissa
            pg.screenshot(path=str(out / f"finale_{name}.png"))
        print("ok", mp4.name)
        pg.close()
    b.close()

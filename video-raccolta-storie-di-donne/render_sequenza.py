"""Esporta la sequenza per il teatro (1920x1080, 30 fps) da sequenza.html.

  0_apertura.mp4        la figura della locandina si compone, logo, titolo, ospedale; transizione alla poltrona
  1_poltrona.mp4        la poltrona si reclina (video invertito) sullo sfondo dell'evento
  2_fermo_poltrona.png  ultimo fotogramma della parte 1
  3_contatore.mp4       la poltrona sparisce, ringraziamento, contatore con 8 poltroncine, fuochi
  4_fermo_importo.png   ultimo fotogramma della parte 3
  5_poltrone.mp4        la cifra si riduce e compaiono le 8 poltrone grandi
  6_fermo_poltrone.png  ultimo fotogramma della parte 5
  sequenza_completa.mp4 tutte le parti di fila (fermi immagine da 3 s), solo per anteprima
Con --formato 43 la versione 4:3 (1440x1080) va in export/4_3/.

Prima: tools/prepara_video_poltrona.py deve aver creato build/sedia/ (fotogrammi + meta.json).
Uso: python3 render_sequenza.py [--parti 135] [--stills] [--totale 9320]
"""
import argparse
import json
import pathlib
import subprocess
import tempfile
from urllib.parse import quote

from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent
out = here / "export"
out.mkdir(exist_ok=True)
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
NAMES = {0: "0_apertura", 1: "1_poltrona", 3: "3_contatore", 5: "5_poltrone"}
STILLS = {1: "2_fermo_poltrona.png", 3: "4_fermo_importo.png", 5: "6_fermo_poltrone.png"}

ap = argparse.ArgumentParser()
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--totale", type=int, default=9320)
ap.add_argument("--parti", default="0135")
ap.add_argument("--stills", action="store_true", help="solo anteprime PNG")
ap.add_argument("--formato", default="169", choices=["169", "43"], help="16:9 (1920x1080) o 4:3 (1440x1080, in export/4_3)")
ap.add_argument("--fermo", type=float, default=3.0, help="durata dei fermi immagine nella sequenza completa")
args = ap.parse_args()

W = 1920 if args.formato == "169" else 1440
if args.formato == "43":
    out = out / "4_3"
    out.mkdir(exist_ok=True)
meta = json.loads((here / "build/sedia/meta.json").read_text())
meta["dir"] = "build/sedia"


def mp4(frames_glob, dst, fps):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", frames_glob,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(dst)], check=True)


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME if pathlib.Path(CHROME).exists() else None)
    for parte in map(int, args.parti):
        pg = b.new_page(viewport={"width": W, "height": 1080})
        q = f"?parte={parte}&ar={args.formato}&totale={args.totale}&sedia={quote(json.dumps(meta))}"
        pg.goto((here / "sequenza.html").resolve().as_uri() + q)
        T = pg.evaluate("window.ready")
        if args.stills:
            for t in [x * T["dur"] for x in (0, .1, .25, .4, .55, .7, .85, 1)]:
                pg.evaluate(f"renderAt({t})")
                pg.screenshot(path=str(out / f"anteprima_{parte}_{t:05.2f}s.png"))
            pg.close()
            continue
        frames = round(T["dur"] * args.fps)
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(frames):
                pg.evaluate(f"renderAt({i / args.fps})")
                pg.screenshot(path=f"{tmp}/{i:05d}.png")
            mp4(f"{tmp}/%05d.png", out / f"{NAMES[parte]}.mp4", args.fps)
            if parte in STILLS:
                # fermo immagine = ultimo fotogramma esportato
                pathlib.Path(f"{tmp}/{frames - 1:05d}.png").replace(out / STILLS[parte])
        print("ok", NAMES[parte])
        pg.close()
    b.close()

if not args.stills and all((out / f"{n}.mp4").exists() for n in NAMES.values()):
    with tempfile.TemporaryDirectory() as tmp:
        parts = []
        for parte, name in list(NAMES.items())[1:]:
            # ogni video seguito dal suo fermo immagine (l'apertura passa direttamente alla poltrona)
            still = pathlib.Path(tmp) / f"fermo{parte}.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(args.fps),
                            "-i", str(out / STILLS[parte]), "-t", str(args.fermo), "-c:v", "libx264", "-crf", "16",
                            "-pix_fmt", "yuv420p", str(still)], check=True)
            parts += [out / f"{name}.mp4", still]
        parts = [out / "0_apertura.mp4"] + parts
        lst = pathlib.Path(tmp) / "lista.txt"
        lst.write_text("".join(f"file '{x.resolve()}'\n" for x in parts))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", str(out / "sequenza_completa.mp4")], check=True)
    print("ok sequenza_completa")

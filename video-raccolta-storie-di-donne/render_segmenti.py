"""Esporta i video per il player a clic (sequenza.html), uno per ogni passo dello spettacolo.

  0_inizio.png              fermo iniziale: solo lo sfondo
  1_locandina.mp4           la figura della locandina si compone; logo, titolo, ospedale    -> si ferma
  2_poltrona.mp4            capelli, viso e foglie escono, entra la poltrona e si reclina   -> si ferma
  3_contatore.mp4           escono poltrona e testi, ringraziamento, contatore, fuochi      -> si ferma
  4_otto_poltrone.mp4       la cifra si riduce e compaiono le 8 poltrone                    -> si ferma
  N_..._fine.png            ultimo fotogramma di ogni video
  anteprima_completa.mp4    tutto di fila (pause da 2 s al posto dei clic), solo per controllo

Ogni video inizia esattamente sull'ultimo fotogramma del precedente: nessuna transizione.
Uscita in export/16_9/ (1920x1080) o export/4_3/ (1440x1080), 30 fps.
Prima: tools/prepara_video_poltrona.py deve aver creato build/sedia/.
Uso: python3 render_segmenti.py [--formato 169|43] [--solo 1234] [--totale 9320]
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import tempfile
from urllib.parse import quote

from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# segmento -> lista di (parte di sequenza.html, da secondi, a secondi)
SEGMENTI = {
    1: ("1_locandina", [(0, 0.0, 7.6)]),
    2: ("2_poltrona", [(0, 10.0, 12.6), (1, 0.0, 10.0)]),
    3: ("3_contatore", [(3, 0.0, 21.2)]),
    4: ("4_otto_poltrone", [(5, 0.0, 7.0)]),
}

ap = argparse.ArgumentParser()
ap.add_argument("--formato", default="169", choices=["169", "43"])
ap.add_argument("--solo", default="1234", help="quali segmenti esportare")
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--totale", type=int, default=9320)
ap.add_argument("--pausa", type=float, default=2.0, help="pausa al posto del clic nell'anteprima completa")
args = ap.parse_args()

W = 1920 if args.formato == "169" else 1440
out = here / "export" / ("16_9" if args.formato == "169" else "4_3")
out.mkdir(parents=True, exist_ok=True)
meta = json.loads((here / "build/sedia/meta.json").read_text())
meta["dir"] = "build/sedia"


def encode(src_glob, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(args.fps), "-i", src_glob,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(dst)], check=True)


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME if pathlib.Path(CHROME).exists() else None)
    pages = {}

    def page(parte):
        if parte not in pages:
            pg = b.new_page(viewport={"width": W, "height": 1080})
            q = f"?parte={parte}&ar={args.formato}&totale={args.totale}&sedia={quote(json.dumps(meta))}"
            pg.goto((here / "sequenza.html").resolve().as_uri() + q)
            pg.evaluate("window.ready")
            pages[parte] = pg
        return pages[parte]

    # fermo iniziale = primo fotogramma della locandina
    pg = page(0)
    pg.evaluate("renderAt(0)")
    pg.screenshot(path=str(out / "0_inizio.png"))

    for k in map(int, args.solo):
        name, pezzi = SEGMENTI[k]
        with tempfile.TemporaryDirectory() as tmp:
            n = 0
            for parte, t0, t1 in pezzi:
                pg = page(parte)
                for i in range(round((t1 - t0) * args.fps)):
                    pg.evaluate(f"renderAt({t0 + i / args.fps})")
                    pg.screenshot(path=f"{tmp}/{n:05d}.png")
                    n += 1
            encode(f"{tmp}/%05d.png", out / f"{name}.mp4")
            shutil.copy(f"{tmp}/{n - 1:05d}.png", out / f"{name}_fine.png")
        print("ok", name, f"{n / args.fps:.1f} s")
    b.close()

# anteprima: tutti i segmenti di fila, con una pausa sul fermo al posto di ogni clic
if all((out / f"{n}.mp4").exists() for n, _ in SEGMENTI.values()):
    with tempfile.TemporaryDirectory() as tmp:
        parts = []
        for still, video in [("0_inizio.png", None)] + [(f"{n}_fine.png", f"{n}.mp4") for n, _ in SEGMENTI.values()]:
            if video:
                parts.append(out / video)
            hold = pathlib.Path(tmp) / f"hold{len(parts)}.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(args.fps),
                            "-i", str(out / still), "-t", str(args.pausa), "-c:v", "libx264", "-crf", "16",
                            "-pix_fmt", "yuv420p", str(hold)], check=True)
            parts.append(hold)
        lst = pathlib.Path(tmp) / "lista.txt"
        lst.write_text("".join(f"file '{x.resolve()}'\n" for x in parts))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", str(out / "anteprima_completa.mp4")], check=True)
    print("ok anteprima_completa")

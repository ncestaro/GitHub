# Contatore raccolta fondi – "Storie di donne straordinariamente semplici"

Video 16:9 per lo schermo del teatro (1920 × 1080, 30 fps, 15 s, senza audio) con la grafica della
locandina/brochure e scritte grandi.

- `export/raccolta_9320_orizzontale_1920x1080.mp4` – il video
- `export/finale_orizzontale_1920x1080.png` – ultimo fotogramma (immagine fissa)

Sequenza:
- 0–4,5 s: logo in alto; al centro, in grande, "Grazie a tutti voi" (scritto da sinistra) e
  "siamo riusciti a raccogliere" con i tre puntini che compaiono uno alla volta
- 4,5–5,6 s: la scritta si riduce e sale al suo posto, compare € 0
- 6–13 s: la cifra sale fino a € 9.320 (parte piano, accelera, rallenta sul finale) con la barra
- 13 s: "battito" della cifra all'arrivo, poi fermo fino a 15 s

Per rigenerare (anche con un altro importo):
`pip install playwright && python3 render.py --totale 9320` (richiede ffmpeg).
`--formati vh` esporta anche una versione verticale 1080 × 1920.

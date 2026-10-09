# Raccolta fondi – "Storie di donne straordinariamente semplici"

Materiali per lo schermo del teatro (16:9, 1920 × 1080, 30 fps, senza audio) con la grafica di
locandina e brochure.

## Sequenza con la poltrona (`sequenza.html`, `render_sequenza.py`)

| file | cosa | durata |
|---|---|---|
| `export/1_poltrona.mp4` | la poltrona si reclina (video Higgsfield invertito, scontornato) sullo sfondo dell'evento | 10 s |
| `export/2_fermo_poltrona.png` | fermo immagine: ultimo fotogramma di 1 | – |
| `export/3_contatore.mp4` | la poltrona sparisce, "Grazie a tutti voi – siamo riusciti a raccogliere…", contatore da € 0 a € 9.320 in 10,5 s; sulla barra compare una poltroncina ogni 1/8 dell'importo (≈ 1.165 €); a fine conteggio fuochi d'artificio sobri | 20,5 s |
| `export/4_fermo_importo.png` | fermo immagine: ultimo fotogramma di 3 | – |
| `export/5_poltrone.mp4` | la cifra si riduce e sale, compaiono le 8 poltrone grandi "a sedia" (griglia 4 × 2) | 7 s |
| `export/sequenza_completa.mp4` | le cinque parti di fila (fermi da 3 s), per anteprima | – |

Ogni parte inizia esattamente dove finisce la precedente, quindi si possono montare o lanciare una dopo l'altra.

Per rigenerare:

```
pip install playwright rembg[cpu]        # richiede anche ffmpeg
python3 tools/scontorna_fotogrammi.py <fotogrammi> <maschere>          # ~8 s a fotogramma su CPU
python3 tools/prepara_video_poltrona.py <video.mp4> <maschere> build/sedia   # anche assets/poltrona_dritta.png e l'icona
python3 render_sequenza.py --totale 9320
```

Le maschere già calcolate per il video sono in `assets/sedia_maschere/`.

## Solo contatore (`counter.html`, `render.py`)

Versione precedente senza poltrone: `export/raccolta_9320_orizzontale_1920x1080.mp4` (15 s).

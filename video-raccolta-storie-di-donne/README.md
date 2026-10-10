# Raccolta fondi – "Storie di donne straordinariamente semplici"

Materiali per lo schermo del teatro, con la grafica della locandina (file Illustrator in `assets/intro/`).
Formato **16:9** (1920 × 1080) in `export/16_9/`, 30 fps, senza audio. La versione 4:3 (1440 × 1080) non è esportata:
si rigenera con `python3 render_segmenti.py --formato 43` (va in `export/4_3/`, il player la apre con `?formato=43`).

## Come funziona in sala

Ogni passo parte con un clic e si ferma da solo sull'ultimo fotogramma; il passo successivo riparte
esattamente da lì, quindi non ci sono transizioni.

| clic | file | cosa succede | durata |
|---|---|---|---|
| – | `0_inizio.png` | fermo iniziale: solo lo sfondo | – |
| 1 | `1_locandina.mp4` | la figura si compone ritaglio per ritaglio (disco, collo e viso, capelli, foglie, occhio); a destra logo, titolo con il lettering originale e "per il Reparto di Oncologia dell'Ospedale “Luigi Curto” di Polla" | 7,6 s |
| 2 | `2_poltrona.mp4` | capelli, viso e foglie escono, davanti al disco entra la poltrona e si reclina (video Higgsfield invertito e scontornato) | 12,6 s |
| 3 | `3_contatore.mp4` | escono poltrona e testi, il disco va nell'angolo; "Grazie a tutti voi – siamo riusciti a raccogliere…", contatore da € 0 a € 11.770 in 20 s con una poltroncina sulla barra ogni 1/10 dell'importo; fuochi d'artificio sobri | 30,7 s |
| 4 | `4_poltrone.mp4` | la cifra si riduce e compaiono le 10 poltrone | 7 s |

Accanto a ogni video c'è `…_fine.png`, il suo ultimo fotogramma. `anteprima_completa.mp4` mette tutto di fila
(pause di 2 s al posto dei clic), solo per controllo.

### Player

`player.html`, aperto in Chrome/Edge dalla cartella del progetto:
**F** schermo intero; **clic, spazio, → o PagGiù** (anche da telecomando) passo successivo; **← o PagSu** torna al
fermo precedente. Durante un video i clic sono ignorati.

## Rigenerare

```
pip install playwright rembg[cpu]                                      # serve anche ffmpeg
python3 tools/estrai_intro.py                                          # ritagli e titolo dal file Illustrator
python3 tools/scontorna_fotogrammi.py <fotogrammi> <maschere>          # solo se cambia il video della poltrona
python3 tools/prepara_video_poltrona.py assets/poltrona_higgsfield.mp4 assets/sedia_maschere build/sedia
python3 render_segmenti.py [--formato 43] [--totale 11770] [--poltrone 10]
```

La scena è `sequenza.html` (parti 0, 1, 3, 5, pilotate da `renderAt(t)`); `render_sequenza.py --stills` ne esporta
anteprime. Le maschere della poltrona sono già calcolate in `assets/sedia_maschere/`.
`tools/crea_pptx.py` riguarda la vecchia versione PowerPoint (non aggiornata).

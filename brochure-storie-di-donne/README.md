# Brochure pieghevole – "Storie di donne straordinariamente semplici"

Pieghevole A4 a 3 ante, piega a C (formato chiuso 99 × 210 mm), stile ripreso dalla locandina.

- `export/brochure_stampa_A4_abbondanze3mm.pdf` – PDF di stampa, 2 pagine (esterno + interno), 303 × 216 mm con 3 mm di abbondanza
- `export/anteprima_esterno.png`, `export/anteprima_interno.png` – anteprime al vivo

Esterno (da sinistra): anta interna (Rosanna, 97 mm) · retro con loghi (100 mm) · copertina (100 mm)
Interno (da sinistra): beneficenza (100 mm) · spettacolo teatrale (100 mm) · spettacolo musicale (97 mm)

Illustrazioni interne generate con Higgsfield (GPT Image 2.5); figura e loghi ritagliati dalla locandina.
I testi segnati con la classe `ph` in `brochure.html` sono provvisori; la foto di Rosanna è un segnaposto.

Per rigenerare: `pip install playwright pillow && python3 render.py`

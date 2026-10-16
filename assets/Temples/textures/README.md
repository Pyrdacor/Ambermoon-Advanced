# Texturen

**Hinweis:** Die Tempel nutzen inzwischen die Gala-Wände mit Palette 59 (`../Labdata 46.md`). Die hier erzeugten Fries-Texturen 193–195 sind nicht mehr in den Spieldaten, die Werkzeuge bleiben für spätere Vorlagen.

| Datei | Inhalt |
|---|---|
| `Pixelart-Sandsteinmauer mit ägyptischen Säulen.png` | Aktuelle Vorlage (1585×992, 16:10), breite dunkle Fugen |
| `Pixel-Art-Sandsteinwand mit Tempelfriesen.png` | Erste Vorlage (zu wenig Kontrast), über `SANDSTONE_SRC` weiter nutzbar |
| `generated/sandstone_193..195.tex` | Wände 193–195 als Texture4Bit (128×80), daneben die Vorschauen `_x4.png` |
| `generated/wuestentempel.pal` | Palette 59 „Wüstentempel“ (32 Farben). Steinfarben 1–6/12/13 passend zur Vorlage, der Rest wie Palette 6 |

Beim Verkleinern werden Kanten (Fugen, Steinkanten) verstärkt und Flächen geglättet (`sharpen()`, Standard für die aktuelle Vorlage: Stärke 1,0, Kontrast 1,05, Schwelle 8), sonst wirkt die Wand flach.

Wand 194 (ohne Säulen) wiederholt den Mittelteil, jede Steinreihe mit eigenem Versatz, damit die Stoßfugen nicht über die ganze Höhe durchlaufen.

Neu erzeugen: `python assets/Temples/tools/make_sandstone_walls.py`, danach `build_prototype.py`.
Für weitere Vorlagen: `tools/convert_texture.py` (Verkleinern mit Flächenmittel, Palette ableiten oder vorgeben, optional Dithering).

# Texturen

| Datei | Inhalt |
|---|---|
| `Pixel-Art-Sandsteinwand mit Tempelfriesen.png` | Vorlage (1586×992, 16:10) |
| `generated/sandstone_193..195.tex` | Wände 193–195 als Texture4Bit (128×80), daneben die Vorschauen `_x4.png` |
| `generated/wuestentempel.pal` | Palette 59 „Wüstentempel“ (32 Farben). Steinfarben 1–6/12/13 passend zur Vorlage, der Rest wie Palette 6 |

Neu erzeugen: `python assets/Temples/tools/make_sandstone_walls.py`, danach `build_prototype.py`.
Für weitere Vorlagen: `tools/convert_texture.py` (Verkleinern mit Flächenmittel, Palette ableiten oder vorgeben, optional Dithering).

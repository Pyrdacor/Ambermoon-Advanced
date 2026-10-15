# Ratsechsen-Tempel – Arbeitsordner

Hier sammeln wir Ideen und Assets für die Neugestaltung der sieben Ratspaläste (Maps 444–450).

| Pfad | Inhalt |
|---|---|
| `Ideen.md` | Ideensammlung (Gestaltung, Mechaniken, Story) |
| `Analyse Optik.md` | Was an Wänden, Objekten, Overlays, Böden und Paletten vorhanden ist und was sich eignet |
| `analysis/` | Übersichtsbilder aller 3D-Texturen mit Nummern, gerendert mit der Tempel-Palette 6 (`tools/ambtools/render3d.py`) |
| `mockups/` | Vorschauen: Kandidaten-Paletten und aus Overlays zusammengesetzte Wände (`tools/mockups.py`, Legende in `legend.txt`) |
| `tools/` | Skripte für die Vorschauen |
| `palettes/`, `textures/` | Für neue Paletten und Texturen (noch leer) |

Neu erzeugen:

```
python tools/ambtools/render3d.py assets/Temples/analysis --palette 6 --labdata 2:35
python assets/Temples/tools/mockups.py
```

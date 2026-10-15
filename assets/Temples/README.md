# Ratsechsen-Tempel – Arbeitsordner

Hier sammeln wir Ideen und Assets für die Neugestaltung der sieben Ratspaläste (Maps 444–450).

| Pfad | Inhalt |
|---|---|
| `Ideen.md` | Ideensammlung (Gestaltung, Mechaniken, Story) |
| `Analyse Optik.md` | Was an Wänden, Objekten, Overlays, Böden und Paletten vorhanden ist und was sich eignet |
| `analysis/` | Übersichtsbilder aller 3D-Texturen mit Nummern, gerendert mit der Tempel-Palette 6 (`tools/ambtools/render3d.py`) |
| `mockups/` | 3D-Ansichten je Tempel (`temples.png`) und die Gala-Halle in allen Kandidaten-Paletten (`palettes.png`), Legende in `legend.txt` (`tools/mockups.py`, Raycaster `tools/scene3d.py`) |
| `analysis/labdata/` | Wände und Objekte der Labdatas, die schon detaillierte Tempelwände nutzen (2:5 Gala, 2:32 Sansri, 2:34, 2:31, 2:36) |
| `prototypes/` | Spielbare Testmaps (Pilot: S'Riel, Map 487), Grundriss und Ansichten, Anleitung zum Testen (`prototypes/README.md`, gebaut mit `tools/build_prototype.py`) |
| `music/` | Musikversuche: „Psychedelic Dune Groove“ transponiert (`music/README.md`) |
| `tools/` | Skripte für die Vorschauen und die Musik |
| `palettes/`, `textures/` | Für neue Paletten und Texturen (noch leer) |

Neu erzeugen:

```
python tools/ambtools/render3d.py assets/Temples/analysis --palette 6 --labdata 2:35
python tools/ambtools/render3d.py assets/Temples/analysis/labdata --palette 6 --labdata 2:32:6 2:34:5 2:5:6 2:31:5 2:36:6
python assets/Temples/tools/mockups.py
```

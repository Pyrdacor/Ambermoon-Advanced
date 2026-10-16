# Tempel-Optik – Analyse der vorhandenen Assets

Stand 15.10.2026. Alle Nummern beziehen sich auf die Übersichtsbilder in `analysis/`. Wände, Objekte und Overlays stammen aus `2*.amb`, ergänzt durch `3*.amb`, so wie das Remake sie lädt.

## 1. Ist-Zustand

- Alle sieben Paläste (444–450) nutzen **Labdata 35** und **Palette 6**. Deshalb sehen sie gleich aus.
- **Labdata 35** (`analysis/labdata_2_35_walls.png`) besteht fast nur aus grünem und orangefarbenem Bruchstein (Texturen 69/70 mit Gittern, Treppen, Schaltern, Steinköpfen). Das wirkt wie eine Höhle, nicht wie ein Palast.
- **Palette 6, Farben 0–15:**

  | Index | Farbe | Rolle |
  |---|---|---|
  | 0 | Schwarz/transparent | |
  | 1–6 | `bba` … `311` | Stein-Abstufung (grau-beige) |
  | 7–11 | `a74 853 632 c82 ea4` | Orange/Braun: Holz, Lehm, Gold |
  | 12–13 | `672 452` | Grün: Moos, Verzierung |
  | 14–15 | `900 c40` | Rot/Glut |

- **Farbnutzung der Wände:**
  - Die grüne Wand 69 ist Stein-Abstufung plus 12/13.
  - Die orange Wand 70 nutzt nur 7–11.
  - Saubere Quaderwände (144, 148, 171) nutzen **nur** die Stein-Abstufung 1–6.
  - Die verzierten Wände 97–106 nutzen Stein plus 12/13 als feines Dither.

## 2. Geeignete Wände

### Tempelwände (erste Wahl): Gala/Sansri-Familie
Grundlage aller Mockups. Detaillierte Texturen, die bereits im Gala-Tempel (Labdata 2:5) und in Sansris Tempel (2:32) zusammengesetzt werden (`analysis/labdata/`).

| Nr. | Beschreibung |
|---|---|
| 99 | Grundmauer (Quader mit Relief-Fugen). Trägt fast alle Overlays. |
| 96 | Prunktür, mit Säulenrahmen-Overlays 96/97 als Hauptportal |
| 98 | Doppelbogen mit Säulen. Darin Fenster 72, Wappen 137, Schilder 135/136 |
| 100, 103, 104 | Reliefpfeiler mit Edelsteinen, Fries, dunkles Tor |
| 97, 101, 102 | Schlangen- und Kobra-Reliefs (Sansri) |
| 105–109 | Dieselben Reliefs mit Glut am Fuß (Sansri). Für S'Kat und S'Trog |
| 167, 168 | Bücherregale (stehen auch in Gala) |
| 58–64, 51–57 | Marmorsäulen und Vorhänge (S'Angrila, 2:34). Alternative für Thronsäle |
| 46–50 | Graue Bruchsteinwand mit Portalen (2:31). Nutzt dieselben Overlays wie 99 |

**Nicht verwenden:** Die Quaderwände 144–155 und 171/172. Sie sind eine Hommage an Dragonflight und ältere, weniger detaillierte Texturen. (184–192 sind dagegen eigene Advanced-Texturen für das Morag-Gefängnis und die alte Stadt.)

### Sandstein-Basis (Labdata 46, Palette 59)
Grundwand ist die Gala-Wand 99, dazu 96, 98, 100, 103, die Treppen 125/126 und die Overlays (Säulenrahmen 24/25, Bilder, Schalter, Rätselmund …). Palette 59 „Wüstentempel“ färbt alles in Sandstein, ohne neue Grafiken. Details und Wandtabelle: `Labdata 46.md`.

Die zwischenzeitlich erzeugten Fries-Texturen 193–195 (`textures/`) sind nicht mehr in den Spieldaten. Die Vorlagen liegen weiter in `textures/`.

### Thematische Wände
| Nr. | Beschreibung | Tempel |
|---|---|---|
| 167, 168 | Bücherregale | S'Riel (Gelehrter), S'Arin (Sternwarte) |
| 110–115 | Raue Mauer mit Schädelreliefs, Gitter | S'Kat (Folter, Labor) |
| 119, 120 | Spinnweben | S'Kat, verlassene Bereiche |
| 143, 169, 170 | Hecken bzw. Pflanzenwand | S'Lorwin (Garten) |
| 179–182 | Lehm bzw. Höhle | Dienstbotengänge, Keller (passt zu „Lehmhäuser der Echsen“) |
| 121–130, 157–166 | Treppen und Gänge | Ebenenwechsel |

## 3. Overlays (Wände ohne neue Grafik zusammensetzen)

Die Engine legt Overlays über Wände. Die Mockups halten sich an die Positionen aus Gala/Sansri: Säulenrahmen 24/25 ganz links/rechts ohne Blending, Fenster 72 bei x=48 bzw. in den Bögen von 98 bei x=16/80, Rosette 71 mittig. Neue Kombinationen nur im selben Stil, z. B. 99 + 24/25 + 71 (Rosette zwischen Säulen) oder 103 + 39 (Steinkopf im Fries).

| Overlay | Inhalt | Verwendung |
|---|---|---|
| 24, 25 / 96, 97 | Säulen-Rahmen links/rechts | Gliedern lange Wände, rahmen Türen |
| 71 | Rosettenfenster | Prunkwand im Sanktum |
| 72 | Spitzbogenfenster | Außenring („Fenster nach draußen“) |
| 74, 137 | Wappen mit gekreuzten Waffen | **Siegel/Wappen der Räte**, Orientierung |
| 15, 16 | Fackeln | Orientierung |
| 86 | Großes verziertes Tor | Sanktums- oder Boss-Tür |
| 39, 98 | Steinköpfe | Rätselmünder |
| 32–36, 138–141 | Skelett an Ketten, Ketten | S'Kat |
| 58–66, 80–83, 108 | Dreieck-Symbole (Morag-Rätsel) | Rätsel, Codes |
| 87–91, 105–107 | Achteck-Fenster und -Rahmen | Sternwarte (S'Arin) |
| 94, 99 | Feuerfenster, Feuerbogen | S'Trog/S'Kat, Feuerwalze |
| 95, 142 | Risse | Einsturz |
| 112, 115 | Gitter | Zellen |
| 67–70 | Gemälde | Gemächer |
| 122–131 | Tafeln und Rahmen | Inschriften, Hinweise |
| 132 | Rad | Mechanismus (rotierender Raum) |
| 133, 134 | Schalter | Schalter |

## 4. Objekte

| Nr. | Objekt | Verwendung |
|---|---|---|
| 100–103 | Säulen (gedreht, verziert, schlicht) | Hallen, Kolonnaden |
| 28–30 | Schlangen- bzw. Echsentotems | **Altäre der Räte**, Sanktum |
| 133, 143 | Statuen (Robe) | Wegweiser-Statuen |
| 13–15, 35 | Rüstungen, Golemstatue, Statue | Wachen-Deko, „lebende“ Statue |
| 121, 141, 16, 144 | Kohlebecken, Feuerstelle, Flammen | Licht-Rätsel, Feuerwalze |
| 142, 152 | Kerzenständer | Gemächer |
| 108 | Gong | Ritual, Alarm (Wachen rufen) |
| 117, 118 | Käfige (leer, mit Skelett) | S'Kat |
| 145, 155, 156, 159 | Rad, Folterbank, Tische | S'Kat-Labor |
| 96–99 | Runde und achteckige Mosaike | **Bodenmosaike/Teppiche** im Sanktum |
| 221, 226, 227, 379 | Kristalle | Morag-Kristalle (siehe Notiz), Licht |
| 181–187, 229–237 | Pflanzen, Baum, Blumen | S'Lorwins Garten |
| 125, 259 | Brunnen, Teich | Oase, Wasserbecken |
| 395, 201 | Ringe | Teleporter-Plattformen (S'Trog) |
| 307–311, 323–325 | Bodenlöcher und Gitter | Sprung-Rätsel |
| 313, 314, 384 | Leuchtstäbe | Energie, Barriere |
| 385, 405–409 | Antike Wand bzw. Maschinen | Verbindung zur antiken Stadt |
| 164, 347 | Truhen | Truhen |

## 5. Böden und Decken

- 20 Böden (`analysis/floors.png`).
- **Für Paläste geeignet:** 20 (Steinplatten), 16, 17 (große Platten), 8 (glatter Verlauf, eher Decke), 4/3 (Ornament auf Dunkel).
- **Für Garten bzw. Höhle:** 10, 11, 18 (grün), 1, 13 (Erde).

## 6. Paletten

- Es gibt 58 Paletten. In 3D zählen nur die Farben 0–15, Farbe 0 ist Schwarz bzw. transparent.
- **Ansatz:** Neue Palette pro Tempel. Dabei nur die **Stein-Abstufung 1–6** und die **Akzente 12/13** ändern. Orange (7–11) und Rot (14/15) bleiben, damit Holz, Feuer, Truhen und Gold normal aussehen.
- **Wichtig:** In der Gala/Sansri-Familie sind 12/13 Teil des Steins (rund 20 % der Pixel, sie machen den Olivton von Palette 6). Deshalb werden 1–6 und 12/13 **gemeinsam** getönt. Als knallige Akzentfarben flimmern sie (das war der Fehler der ersten Mockups).
- **Vorschläge** (`mockups/palettes.png`, `mockups/temples.png`, Werte in `mockups/legend.txt`):

| Palette | Wirkung | Tempel |
|---|---|---|
| Sandstein | warm, hell | S'Riel (Bibliothek) |
| Rotstein | rötlich, wehrhaft | S'Orel (Kaserne) |
| Lapis | kühl, blau, offene Decke | S'Arin (Sternwarte) |
| Amethyst | violett, unwirklich | S'Endar (Illusionist) |
| Basalt | neutral grau | S'Trog (Teleportation) |
| Moder | dunkel, oliv | S'Kat (Labor) |
| Jade | grün | S'Lorwin (Wasser/Garten) |

- **Pflanzen:** Pflanzen-Objekte nutzen 7–11 als Grün (in ihren Wald-Paletten). In den Tempelpaletten sind 7–11 Holz/Gold, deshalb werden Pflanzen rot-orange. Für S'Lorwins Garten entweder 7–11 umfärben (dann wird Holz grün) oder auf Wasser, Totems und Säulen setzen.
- **Vorsicht:** Die Palette gilt für die ganze Map, also auch für Monster und NPCs in 3D. Graue Monster, z. B. Golems und magische Wachen, werden mit eingefärbt. Das ist eventuell sogar gewünscht (Wachen passend zum Tempel), muss aber geprüft werden. Ob der Kampfbildschirm die Map-Palette nutzt, müsste ich noch nachsehen.
- **Technisch:** Neue Paletten werden an `Palettes.amb` angehängt (59, 60, …). Die Palette einer Map steht in Byte 9 des Map-Headers.

## 7. Neue Texturen aus bestehenden erzeugen

1. **Paletten-Tausch** (siehe oben): kein neues Bild, nur eine Palette.
2. **Overlays** (Abschnitt 3): Die Engine setzt Wände zur Laufzeit zusammen, kein neues Bild nötig.
3. **Index-Remap innerhalb einer Textur:** Farbindizes einer Textur werden auf andere umgelegt, z. B. bei 97–106 das Moos-Dither 12/13 auf Steinfarben 3/4. Die Reliefs bleiben, das Flimmern verschwindet, und 12/13 sind frei für echte Akzente. Erzeugt eine neue Wand-Textur als Kopie.
4. **Spiegeln, Ausschneiden, Kombinieren:** z. B. Säulen aus 97/98 an eine Quaderwand setzen, das Rosettenfenster mittig in eine andere Wand, linke und rechte Hälften verschiedener Texturen.
5. **Nacharbeit durch dich:** Die erzeugten PNGs als Vorlage nehmen, im Grafikprogramm verfeinern und wieder importieren.

Für 3–5 fehlt noch ein **Encoder** (PNG/Indexbild → Texture4Bit) und das Anhängen an `2Wall3D.amb`. Das kann ich bauen, wenn wir uns für Varianten entscheiden.

## 8. Rahmenbedingungen

- 16 Farben pro Map (3D), Farbe 0 = transparent bei Objekten und Overlays.
- Mehr verschiedene Texturen in einer Labdata bedeuten mehr Speicher auf dem Amiga. Das muss für die großen Tempel im Blick bleiben.
- Eigene Labdata pro Tempel heißt bis zu 7 neue Einträge in `2Lab_data.amb`, als Kopie von 35 angepasst.

## 9. Vorschlag zum Einstieg

1. **Einen Pilot-Tempel festlegen**, z. B. S'Riel (klein): eigene Labdata als Kopie von Gala 2:5 (Wände 96–104, 167/168, Overlays wie dort), Bodenmosaike, Säulen, Palette „Sandstein“, Boden 20, Decke 8.
2. In FS-UAE und im Remake ansehen und die Palette feinjustieren.
3. Danach dasselbe Schema mit anderem Thema und anderer Palette für die übrigen Tempel.

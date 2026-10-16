# Tempelmusik – Versuche

Basis ist Song 22 „Psychedelic Dune Groove“ (Sandschiff). Er passt zur Dramatik und zum Wüstensetting der Ratsechsen-Tempel. Die Tempel nutzen bisher die Dungeon-Songs 26, 18, 17 und 19.

| Datei | Inhalt |
|---|---|
| `SONIC.PsychedelicDuneGroove_-3`, `_-5` | Export-Format wie in `Music.amb` (ohne Replayer), 3 bzw. 5 Halbtöne tiefer |
| `SONIC.PsychedelicDuneGroove_ab34` | Original-Tonhöhe, Start und Wiederholung ab Position 34 (1:05, Beginn eines neuen Teils). Gespielt werden die Positionen 34–69, also 69 s pro Durchlauf. In FS-UAE heißt die Datei `DuneGroove34.sa`. Bleibt als Backup |
| `SONIC.PsychedelicDuneGroove_ab34_cut` | Wie `_ab34`, aber ohne die Positionen 52–53 (0:34,6–0:38,4). Danach folgt direkt der A-B-A-B-Block 54–57. Ein Durchlauf dauert 65 s. In FS-UAE: `DuneGroove34c.sa` |
| `SONIC.PsychedelicDuneGroove_ab34_cut2` | Wie `_cut`, aber ohne die letzten 3 Positionen (5,8 s Groove ohne Melodie). Endet mit dem Übergangstakt und springt zurück zu Position 34. Ein Durchlauf dauert 59,5 s. In FS-UAE: `DuneGroove34d.sa` |
| `SONIC.MellowCamelFunk_x2` | Song 2 „Mellow Camel Funk“ doppelt so schnell: Speed 6 → 3 Ticks pro Zeile, die 12 Slide-Befehle mit doppeltem Wert, damit sie dieselbe Tonhöhe erreichen. 57 s statt 115 s. In FS-UAE: `CamelFunkX2.sa` |
| `*.sa` | Dieselben Varianten als Sonic-Arranger-Modul. Liegen auch in FS-UAE unter `Workbench:SonicArranger/Temples/` |
| `*.wav` | Original und Varianten zum Anhören, je 134 s (nicht im Git) |

- Transponiert wird nur der Note-Transpose aller vier Stimmen in der Overtable (70 Positionen × 4 Stimmen). Noten, Instrumente und Tempo bleiben gleich.
- **Stimmen:**
  - Stimme 1: die Samples „Sybra2–4“. Das ist kein Schlagzeug: Sie spielen 11 verschiedene Tonhöhen und folgen denselben Transposes wie der Bass.
  - Stimme 2: Lead, PowerSynth und Glocken.
  - Stimme 3: Bass.
  - Stimme 4: Glocken und PowerSynth.
  - Deshalb werden alle Stimmen verschoben.
- **Tonhöhe** per Nulldurchgängen geprüft: −3 ergibt Faktor 1,17 (theoretisch 1,19), −5 ergibt 1,28 (theoretisch 1,33).
- **Werkzeug:** `tools/transpose_music.py`. Mit `--skip-voices` lassen sich Schlagzeugstimmen auslassen, mit `--start`/`--repeat` Start- und Wiederholposition setzen, mit `--remove ERSTE LETZTE` Positionen entfernen (Pointer, Stop- und Wiederholposition werden angepasst), mit `--speed N` das Tempo ändern (Speed-Befehle und Slides werden mit skaliert). Eine Position dauert bei diesem Song 1,92 s (Speed 6 × 16 Zeilen / 50 Hz).
- **Song 33:** `_ab34_cut2` ist als Tempelmusik ausgewählt.
  - Der Amiga-Code kann einen Song 33 abspielen (`Max_music` = 33 in `Set_music`).
  - Im Remake ist Song 33 aber im Enum `Song` schon „Intro“ (34 Outro, 35 Menu). Ein 33. Eintrag in Music.amb führt deshalb beim Laden der Daten zu „An item with the same key has already been added. Key: Intro“, und das Remake lädt die Advanced-Daten gar nicht.
  - Darum ist Music.amb vorerst wieder das Original. Sobald das Remake angepasst ist, wird `SONIC.PsychedelicDuneGroove_ab34_cut2` als Eintrag 33 angehängt.
  - Dabei bleiben die Einträge 1–32 roh übernommen. Nur Eintrag 33 wird mit AmbermoonPack (AMNP, Schlüssel = Eintragsnummer) gepackt, denn ein komplettes Neupacken verändert einige Original-Einträge um 2 Byte.

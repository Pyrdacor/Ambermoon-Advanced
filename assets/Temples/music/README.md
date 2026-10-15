# Tempelmusik – Versuche

Basis ist Song 22 „Psychedelic Dune Groove“ (Sandschiff). Er passt zur Dramatik und zum Wüstensetting der Ratsechsen-Tempel. Die Tempel nutzen bisher die Dungeon-Songs 26, 18, 17 und 19.

| Datei | Inhalt |
|---|---|
| `SONIC.PsychedelicDuneGroove_-3`, `_-5` | Export-Format wie in `Music.amb` (ohne Replayer), 3 bzw. 5 Halbtöne tiefer |
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
- **Werkzeug:** `tools/transpose_music.py` (auch mit `--skip-voices` für Schlagzeugstimmen).
- **Ins Spiel** kommt eine Variante erst, wenn wir sie ausgewählt haben: als neuer Eintrag 33 in `Music.amb`. Dafür muss geprüft werden, ob Code und Remake mehr als 32 Songs zulassen.

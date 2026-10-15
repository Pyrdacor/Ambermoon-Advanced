# Tempelmusik – Versuche

Song 12 „The Aum Remains The Same“ (Tempel des Lebens) heruntertransponiert, als sakrale Variante für die Ratsechsen-Tempel. Die Tempel nutzen bisher die Dungeon-Songs 26, 18, 17 und 19.

| Datei | Inhalt |
|---|---|
| `SONIC.TheAumRemainsTheSame_-3`, `_-5` | Export-Format wie in `Music.amb` (ohne Replayer), 3 bzw. 5 Halbtöne tiefer |
| `*.sa` | Dieselben Varianten als Sonic-Arranger-Modul zum Bearbeiten |
| `*.wav` | Zum Anhören (nicht im Git, mit `saprobe`-Render erzeugt, siehe unten) |

- Transponiert wird nur der Note-Transpose aller vier Stimmen in der Overtable (76 Positionen × 4 Stimmen). Noten, Instrumente und Tempo bleiben gleich.
- Stimmen 1/2 sind die Chor-Samples z5/z6, 3/4 Synth-Glocken und Lead. Es gibt kein Schlagzeug, deshalb werden alle Stimmen verschoben.
- Tonhöhe per Nulldurchgängen geprüft: −3 ergibt Faktor 1,17 (theoretisch 1,19), −5 ergibt 1,30 (theoretisch 1,33).
- Werkzeug: `tools/transpose_music.py` (auch mit `--skip-voices` für Schlagzeugstimmen).
- Ins Spiel kommt eine Variante erst, wenn wir sie ausgewählt haben: als neuer Eintrag 33 in `Music.amb`. Dafür muss geprüft werden, ob Code und Remake mehr als 32 Songs zulassen.


## 7. Einordnung

### Befunde
1. **Mystik ist der Engpass.** Die lernbare Mystik kostet in Advanced 880 SLP statt 235. Das liegt an 12 neuen Zaubern (78–89) und an teuren Hilfszaubern (Mystische Karte I–III 65–75, Globus 100, Mystische Skizze 60).
   - Targor (Mystiker, 10 SLP/Lvl) schafft bis Level 50 nur 13 von 20 Zaubern. Im Original hatte er bei Level 25 alles.
   - Für 100 % bis Level 50 bräuchte er etwa 27 SLP/Lvl.
2. **Alchemie** kostet 1010 statt 367 SLP (Faktor 2,8). Leonaria hat mit 20 SLP/Lvl bis Level 55 immer noch nicht alles, nötig wären etwa 30.
3. **Heilung** kostet 781 statt 373 SLP. Sabine (18 SLP/Lvl) ist erst mit Level 52–55 komplett.
4. **Zerstörung** ist unverändert (361). Nelvin hat bei Level 40 alles, wie im Original. Damit ist der Magier relativ zu den anderen Vollmagiern jetzt deutlich im Vorteil.
5. **Halbmagier** liegen weit unter „die Hälfte der Schule“:
   - Thalion: 315 von 505 SLP bis Level 50.
   - Valdyn: 240 von 425.
   - Gryban: 191 von 249. Er ist gut dran, weil er mit 90 Start-SLP beitritt.
6. **Früher Spielverlauf und R-M.** Thalion startet mit R-M 23 %. Jeder Lernversuch kostet die SLP auch bei Misserfolg, effektiv also etwa das 4,3-Fache (Licht: 5 SLP → effektiv ≈ 22 SLP).
   - Zusammen mit den erhöhten Kosten der billigen Zauber (Licht 2 → 5, Fackel 5 → 10, Monsterwissen 3 → 15) ist das ein wahrscheinlicher Grund für die Beschwerden.
   - In Advanced ist R-M-Max für alle 99, im Original war es für Halbmagier nur 50.
7. **INT gesenkt:** Thalion 27 → 20 und Valdyn 38 → 24. Damit fällt der INT/25-Bonus (+1 SLP pro Level) weg, gerade bei den Halbmagiern.

### Stellschrauben
Jeweils kombinierbar. Die Werte aus Abschnitt 6 dienen als Orientierung.

- **A) Hilfszauber billiger, Kampf- und Heilzauber teuer lassen.** Kandidaten sind die SLP-Treiber ohne Kampfwert:
  - Mystische Karte I–III (65/70/75), Mystischer Globus (100), Mystische Skizze (60), die „… finden“-Zauber (je 15)
  - Levitation (65), Alchemistischer Globus (100), Duplikation (65), Gegenstand laden (60), Wort des Markierens/der Rückkehr (50/40)
  - Das entlastet Voll- und Halbmagier gleichermaßen.
- **B) SLP/Level der Vollmagier angleichen.** Ziel z. B. „Schule bei ~Level 45–50 komplett“. Bei den heutigen Kosten wären das etwa:
  - Sabine 20–23
  - Leonaria 30
  - Targor 27–32
  - Nelvin 8–9 (heute 10, kann bleiben)
  - Alternativ mit A die Schulsummen auf etwa 600–650 senken; dann reichen für alle Vollmagier ~16–20.
- **C) Halbmagier:** Ziel „gute Auswahl, aber nicht alles“, z. B. 40–50 % der Schul-SLP bis Level 50. Das wären etwa:
  - Thalion ~13–15
  - Valdyn ~12–13
  - Gryban ~13, oder er behält 7 und die hohen Start-SLP.
  - Den INT von Thalion und Valdyn wieder auf ≥ 25 zu setzen, gibt +1 SLP/Lvl ohne Datenänderung an SLP/Lvl.
- **D) Lernversuch:** Fehlschläge kosten aktuell die vollen SLP plus die Rolle.
  - Die halben SLP bei Fehlschlag (Code-Änderung Amiga + Remake) oder höhere Start-R-M für Thalion würden den Frühspiel-Frust stark senken.
  - Die Balance im Late-Game ändert das kaum, weil R-M dort ohnehin hoch ist.

Hinweis zum Werkzeug: Die Tabellen werden mit `slp_report.py` aus den Spieldaten erzeugt. Nach Datenänderungen lässt sich das Dokument neu generieren und vergleichen.

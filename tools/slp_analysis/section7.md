
## 7. Einordnung

Stand nach der SLP-Anpassung vom 06.10.2026: 72 Zauber verbilligt (Amiga `DAT_SpellInfos`, Remake `adjustedSLP`), SLP/Level von Sabine 18 → 15, Valdyn 7 → 8, Targor 10 → 13, Leonaria 20 → 14, Gryban 7 → 8.

### Befunde
1. **Schulsummen** (lernbar, Original → Advanced): Heilung 373 → 546, Alchemie 367 → 621, Mystik 235 → 460, Zerstörung 361 → 361. Vor der Anpassung waren es 781, 1010 und 880. Nicht mitgezählt sind Geisterinferno (nur in einer Alchemistenwaffe) und Mystische Imitation (erhält Targor geschenkt).
2. **Vollmagier** (Erwartungswert, Start-INT; in Klammern mit Max-INT):
   - Nelvin hat seine Schule bei Level 40 komplett, unverändert.
   - Sabine (15 SLP/Lvl) bei Level 46 (43).
   - Targor (13 SLP/Lvl) bei Level 48 (45).
   - Leonaria (14 SLP/Lvl) bei Level 52 (50); bis Level 50 hat sie 18 von 19 Zaubern. Sie tritt erst mit Level 25 bei, deshalb wirkt bei ihr jeder SLP/Lvl-Punkt über weniger Level.
3. **Halbmagier** erreichen bis Level 50 etwa die Hälfte ihrer Schule:
   - Thalion (9): 315 von 621 SLP (51 %), 21 von 29 Zaubern.
   - Valdyn (8): 274 von 452 (61 %), 22 von 28.
   - Gryban (8): 203 von 450 (45 %), 14 von 22. Er tritt mit 90 Start-SLP bei.
   - „Günstigste zuerst“ zählt dabei viele billige Zauber. Die teuren Spitzenzauber (Globus, Wiederbelebung, Element zu X usw.) bekommen Halbmagier nur, wenn sie andere auslassen.
4. **Magische Klassen bleiben nötig:** Kein Halbmagier schafft seine Schule bis Level 55. Mystik und Alchemie haben aber jeweils einen Halbmagier (Valdyn, Thalion), der die meisten Hilfszauber selbst lernen kann. Das ist gewollt, sollte aber bewusst so sein.
5. **Früher Spielverlauf und R-M** bleiben unverändert. Thalion startet mit R-M 23 %, ein Fehlschlag kostet SLP und Rolle, effektiv also etwa das 4,3-Fache. Licht (5) und Fackel (10) sind weiterhin teurer als im Original (2/5).
6. **INT gesenkt:** Thalion 27 → 20 und Valdyn 38 → 24. Damit fällt der INT/25-Bonus (+1 SLP pro Level) weg.

### Mögliche nächste Schritte
- **Leonaria:** Für „Alchemie komplett bis Level 50“ bräuchte sie 16 SLP/Lvl (Abschnitt 6).
- **Halbmagier:** Valdyn liegt mit 61 % am höchsten, Gryban mit 45 % am niedrigsten. Abschnitt 6 zeigt die Werte für exakt 50 % der Schule.
- **Frühspiel:** Halbe SLP bei Fehlschlag (Code Amiga + Remake) oder eine höhere Start-R-M für Thalion. Alternativ Licht und Fackel zurück auf 2/5.

Hinweis zum Werkzeug: Die Tabellen werden mit `tools/slp_analysis/slp_report.py` aus den Spieldaten erzeugt. Nach Datenänderungen lässt sich das Dokument neu generieren und vergleichen.

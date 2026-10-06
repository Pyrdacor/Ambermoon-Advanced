
## 7. Einordnung

Stand nach der SLP-Anpassung vom 06.10.2026 (72 Zauber verbilligt, Amiga `DAT_SpellInfos` und Remake `adjustedSLP`).

### Befunde
1. **Schulsummen** (lernbar, Original → Advanced): Heilung 373 → 546, Alchemie 367 → 621, Mystik 235 → 460, Zerstörung 361 → 361. Vor der Anpassung waren es 781, 1010 und 880. Nicht mitgezählt sind Geisterinferno (nur in einer Alchemistenwaffe) und Mystische Imitation (erhält Targor geschenkt).
2. **Vollmagier** werden jetzt alle komplett (Erwartungswert, Start-INT):
   - Sabine bei Level 39.
   - Nelvin bei Level 40, unverändert.
   - Leonaria bei Level 45.
   - Targor als Einziger nicht ganz: bis Level 50 hat er 19 von 20 lernbaren Zaubern, alles nur mit maximalem INT bei Level 52. Für „komplett bis 50“ bräuchte er etwa 12 SLP/Lvl statt 10.
3. **Halbmagier** erreichen bis Level 50 etwa die Hälfte ihrer Schule:
   - Thalion: 315 von 621 SLP (51 %), 21 von 29 Zaubern.
   - Valdyn: 240 von 452 (53 %), 21 von 28.
   - Gryban: 191 von 450 (42 %), 14 von 22. Er tritt mit 90 Start-SLP bei.
   - „Günstigste zuerst“ zählt dabei viele billige Zauber. Die teuren Spitzenzauber (Globus, Wiederbelebung, Element zu X usw.) bekommen Halbmagier nur, wenn sie andere auslassen.
4. **Magische Klassen bleiben nötig:** Kein Halbmagier schafft seine Schule bis Level 55. Mystik und Alchemie haben aber jeweils einen Halbmagier (Valdyn, Thalion), der die meisten Hilfszauber selbst lernen kann. Das ist gewollt, sollte aber bewusst so sein.
5. **Früher Spielverlauf und R-M** bleiben unverändert. Thalion startet mit R-M 23 %, ein Fehlschlag kostet SLP und Rolle, effektiv also etwa das 4,3-Fache. Licht (5) und Fackel (10) sind weiterhin teurer als im Original (2/5).
6. **INT gesenkt:** Thalion 27 → 20 und Valdyn 38 → 24. Damit fällt der INT/25-Bonus (+1 SLP pro Level) weg.

### Mögliche nächste Schritte
- **Targor:** SLP/Lvl 10 → 12, damit Mystik bis Level 50 komplett ist. Alternativ Mystik um etwa 40–50 SLP verbilligen.
- **Halbmagier:** Wenn sie weniger bekommen sollen, Thalion/Valdyn/Gryban um 1–2 SLP/Lvl senken. Abschnitt 6 zeigt die Werte für exakt 50 % der Schule.
- **Frühspiel:** Halbe SLP bei Fehlschlag (Code Amiga + Remake) oder eine höhere Start-R-M für Thalion. Alternativ Licht und Fackel zurück auf 2/5.

Hinweis zum Werkzeug: Die Tabellen werden mit `tools/slp_analysis/slp_report.py` aus den Spieldaten erzeugt. Nach Datenänderungen lässt sich das Dokument neu generieren und vergleichen.

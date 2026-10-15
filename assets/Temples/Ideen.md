# Ratsechsen-Tempel – Ideensammlung

Stand 14.10.2026. Die Liste ergänzt `Tempelanalyse.md`, `Tempel.md` und `Tempel 1 - Labyrinth.md`, die Ideen von dort wiederhole ich nicht.

Ausgangslage:
- Die sieben Paläste sind die Maps 444–450. Alle sind 3D, mit 11×11 bis 25×25 sehr klein, und nutzen dieselbe Labdata 35. Deshalb sehen alle gleich aus.
- S'Riel hat 10 Events, S'Lorwin 13. Fast der ganze Inhalt besteht aus Wachen, Kisten und ein paar Fallen.
- Auf Morag gibt es keine Karte. Orientierung muss also über Optik und Orientierungspunkte laufen.

Aufwand: **[D]** nur Daten und Events, **[G]** braucht neue Grafiken, **[E]** braucht eine Engine-Erweiterung (Remake + Amiga).

---

## Meine Favoriten für morgen

1. **Jeder Tempel bekommt ein eigenes Thema und eine eigene Optik** (eigene Labdata statt 35 für alle). Siehe Abschnitt 1 und 3.
2. **Gemeinsames Grundgerüst „Ring + Sanktum“**, aber in jedem Tempel mit einem anderen Kniff, wie man ins Innere kommt (Abschnitt 2).
3. **Siegel der Ratsechsen:** Jeder besiegte Rat lässt ein Siegel fallen, und spätere Tempel brauchen frühere Siegel. So entsteht eine echte Reihenfolge mit Fortschritt (Abschnitt 5).
4. **S'Ebi als Insider:** Mit S'Ebi in der Gruppe gibt es Kommentare und Abkürzungen über Dienstbotengänge, die er von den Rebellen kennt (Abschnitt 5).
5. **Bewegte Gefahren per Delay + TileChg:** Feuerwalze, Sandflut und einstürzende Decke machen die Gänge spannender (Abschnitt 4).
6. **Schlafgemach mit Tagebuch** in jedem Tempel: Story-Häppchen über die Pläne des Rats, die Luftschiffe und den Krieg gegen Lyramion (Abschnitt 6).

---

## 1. Optik und Atmosphäre

- [D/G] **Eigene Labdata pro Tempel**, als Kopie von 35, aber mit anderen Wand-, Boden- und Deckentexturen. Die grün-gelben Wände nur noch in einem Tempel oder in einem Bereich.
- [G] **Materialien passend zu Morag:** Sandstein, Lehm, Obsidian, Kristall. Die Moraner wohnen laut deiner Notiz in Lehmhäusern; die Tempel könnten als Kontrast prachtvoll mit Kristall und Edelmetall sein.
- [G] **Overlays mit dem Wappen/Siegel des jeweiligen Rats** an Türen, Bannern und Bodenplatten. Gleichzeitig eine Orientierungshilfe.
- [G] **Objekte:** Echsenstatuen, Kohlebecken (Licht), Sandhaufen, Kristallsäulen, Wasserbecken, Teppiche als Bodentextur, Thron im Sanktum.
- [D] **Palette und Licht pro Bereich:** Außenring hell und sandig, Sanktum dunkel mit Kohlebecken. Der Fortschritt wird sichtbar, wie in `Tempel.md` mit „Ebenen mit unterschiedlicher Farbe“.
- [D] **Eigene Musik pro Tempel**, oder zumindest pro Sanktum und Bosskampf.
- [D] **Fenster nach draußen** (Overlay mit Wüste oder Sandsturm) im Außenring. Macht klar, dass man in einem runden Gebäude ist.
- [D] **Kampfhintergründe:** Die unbenutzten 3D-Hintergründe 5 und 13 könnten für die Tempel umgestaltet werden.

## 2. Grundgerüst (für alle Tempel)

- [D] **Außenring + Sanktum**, rund wie das Gebäude von außen. Größe wächst von Tempel zu Tempel, S'Riel klein, S'Lorwin groß.
- [D] **Dreiteilung:** Vorhof/Empfang → Arbeitsbereich mit Thema und Rätsel → Privatgemächer (Schlafgemach, Schatz, Boss).
- [D] **Orientierung ohne Karte:**
  - Echte Türen haben immer 2 Fackeln (deine Idee).
  - Zusätzlich hat jeder Quadrant eine eigene Farbe oder ein eigenes Symbol: Norden Sonne, Osten Mond usw.
  - An Kreuzungen stehen Wegweiser-Statuen, deren Blickrichtung zum Sanktum zeigt.
- [D] **Rücksprung-Teleporter** nach erledigten Abschnitten, damit man nicht alles zurücklaufen muss.
- [D] **Wachen in Stufen:** magische Wache → Tempelwache → Elitewache des jeweiligen Rats. Optisch per Palette unterscheidbar, braucht aber [G] für Varianten.
- [D] **Patrouillen** als sichtbare Monster-Figuren, die nur laufen, wenn sie die Gruppe sehen (Flag „MoveOnlyWhenSeePlayer“ gibt es schon). Man kann sich vorbeischleichen oder sie gezielt angreifen.

## 3. Thema pro Tempel

| Tempel | Thema | Kern-Mechanik |
|---|---|---|
| S'Riel (Verbündeter) | Gelehrter, Bibliothek | Kleine Einführung: Bücherregale mit Augen-Cursor lesen, Hinweise auf die anderen Räte. Karte erlaubt (wie geplant). |
| S'Orel | Kaserne, Waffenkammer | Kampf-Tempel als Ersatz für den fehlenden Boss: Trainingshalle mit Wellen von Wachen, Waffenkammer als Belohnung. |
| S'Arin | Mathematiker, Sternwarte | Zahlen- und Zählrätsel (vorhanden) ausbauen: Sternwarte mit drehbarer Kuppel (Toggle-Schalter), Sternbilder als Zahlencode. |
| S'Endar | Illusionist | Spiegel- und Scheinwände: Illusionswände (vorhanden), dazu ein Raum, in dem Wände nur beim Blick in eine bestimmte Richtung echt sind (Bedingung Richtung). |
| S'Trog | Teleportation | Trickster, der sich wegteleportiert (deine Idee). Dazu Teleporter-Netz mit farbigen Plattformen und einer Legende an der Wand. |
| S'Kat | Labor, Folterkammer | Käfige mit verstärkten Lyramion-Monstern (deine Idee). Dazu Laborgeräte, Gifttanks und Alchemie-Kisten mit Fallen. |
| S'Lorwin | Wasser, Garten, Macht | Oase im Zentrum (deine Idee). Dazu Wasserkanäle: Schleusen öffnen und schließen ändert, welche Gänge geflutet sind (Schwimmen nötig oder nicht). |

## 4. Mechaniken (Engine kann das schon)

- [D] **Feuerwalze / Sandflut:** Eine Reihe aus Flammen- oder Sand-Objekten rückt per Delay + TileChg auf die Gruppe zu. Man muss rechtzeitig einen Schalter oder eine Nische erreichen. Berührung = Falle.
- [D] **Einsturz:** Shake + TileChg schließt den Rückweg hinter der Gruppe, ein neuer Weg öffnet sich woanders.
- [D] **Rotierender Raum:** Ein Toggle-Schalter (Event 29) oder dynamische Tiles (Event 30) drehen Wände im Sanktum um 90°. Vier Stellungen ergeben vier verschiedene Wege.
- [D] **Druckplatten:** Bestimmte Felder müssen in einer Reihenfolge betreten werden (Variablen zählen mit). Ein Fehler setzt zurück und löst einen Kampf aus.
- [D] **Attributs- und Fertigkeits-Proben** (Bedingungen 28/29):
  - Stärke: Statue verschieben.
  - Geschick: Pendel ausweichen.
  - Suchen: verborgener Schalter.
  - Intelligenz: Inschrift entziffern.
- [D] **Klassen-Proben** (Bedingung 25): Magier spürt die Magie einer Illusionswand, Dieb öffnet einen Wandtresor, Paladin bekommt einen Segen am Altar.
- [D] **Nacht** (Bedingung 27): Manche Türen oder Sternbilder sind nur nachts sichtbar. Passt zu S'Arins Sternwarte.
- [D] **Mehrfach-Cursor** (Bedingung 23): Wandreliefs, die man anschauen, berühren oder ansprechen kann, jeweils mit anderem Ergebnis.
- [D] **Licht entziehen:** Ein Buff-Event entfernt das Licht, Kohlebecken geben es kurz zurück (siehe dein Labyrinth-Konzept). Auch als Falle: „Ein kalter Wind löscht alles Licht.“
- [D] **Sprung-Rätsel:** Bodenlöcher (schwarze Bodentextur), die man überspringen muss. Fällt man hinein, landet man in einem Kellerbereich mit Monstern und muss zurücklaufen.
- [D] **Sichtbare Wachen hinter Gittern**, die erst losgelassen werden, wenn man einen Schalter falsch benutzt. Das Rätsel bekommt so eine Konsequenz statt nur „nichts passiert“.
- [D] **Zeitdruck light:** „Die Sanduhr läuft“: Nach X Schritten (Variable zählt über Kacheln mit Events) schließt sich eine Tür wieder.

## 5. Verknüpfung und Fortschritt

- [D] **Siegel der Räte:** Jeder Boss lässt sein Siegel fallen. Das Sanktum von S'Lorwin öffnet sich nur mit allen sechs anderen Siegeln. So entsteht eine klare Reihenfolge, und S'Lorwin wird zum Finale.
- [D] **S'Ebi als Insider:**
  - Mit S'Ebi in der Gruppe (Bedingung Partymitglied anwesend) gibt es Kommentare zu jedem Rat.
  - In 2–3 Tempeln kennt er einen Dienstbotengang als Abkürzung.
  - Ohne S'Ebi geht es auch, nur länger.
- [D] **Rebellen-Aufträge in den Tempeln:** etwa „Bringt uns S'Kats Laborbuch“ oder „Befreit den Gefangenen in S'Orels Kaserne“. Belohnung: Fragmente.
- [D] **Ratsversammlung:** Nach dem 3. besiegten Rat warnen die übrigen per Text bei Tempelbetreten: „Die Räte erwarten euch.“ Die Wachen in den restlichen Tempeln werden stärker (Variable prüfen, andere Monstergruppe).
- [D] **Fragment-Ökonomie:** Kisten in den Tempeln mit 5–30 Fragmenten, wie in `Levelgrenze.md` geplant. Mit sieben Tempeln und je 2–4 Kisten trägt das schon einen guten Teil zu den rund 600 Fragmenten bei.

## 6. Story und Belohnungen

- [D] **Schlafgemach mit Tagebuch** pro Rat. Jedes enthält ein Puzzleteil der Hintergrundgeschichte:
  - Luftschiffe und Hangar,
  - die antike Stadt und die Portale,
  - S'Ebis Gefangennahme,
  - der Plan gegen Lyramion,
  - die Rolle des Weisen.
- [D] **Persönliche Schätze** passend zum Rat:
  - S'Arin: Astrolabium (Item mit Hellsicht-Ladungen),
  - S'Kat: Gifte und Tränke,
  - S'Orel: Waffen mit Mindestlevel 51–53,
  - S'Lorwin: Insignien der Macht.
- [D] **Geheimkammern** pro Tempel mit hoher Suchen-Probe: optional, mit guter Belohnung.
- [D/E] **Boss-Mechaniken:**
  - S'Trog teleportiert sich weg (vorhanden).
  - S'Kat ruft Verstärkung aus den Käfigen.
  - S'Lorwin heilt sich am Wasserbecken, bis man die Schleuse schließt.
  - Die Kampf-Logik dafür ist teils [E].

## 7. Ideen mit Engine-Aufwand

- [E] **Auge der Wahrheit** (deine Idee): Ein Item macht Illusionswände sichtbar. Ginge auch mit [D] als Item-benutzen-Bedingung an festen Stellen, ohne Engine-Änderung.
- [E] **Bewegliche Plattformen/Aufzüge** zwischen zwei Ebenen eines Tempels (Teleport + Sequenz wäre [D], ein echter Aufzug [E]).
- [E] **Wachen, die Alarm schlagen:** Eine Patrouille sieht die Gruppe, und alle Wachen im Bereich werden aktiv (Figuren einblenden).
- [G] **Neue Monstergrafiken** für Tempel- und Elitewachen, damit nicht überall dieselbe magische Wache steht.

## 8. Rahmenbedingungen

- Neue Maps (z. B. Keller oder Sanktum als eigene Map) nur auf freien Indizes 487–512 (Amiga-Archivlimit 530).
- Die bestehenden Maps 444–450 können größer werden; die Map-Größe ist frei wählbar.
- Eigene Labdata pro Tempel heißt bis zu 7 neue Labdata-Einträge.
- Ratsechsen und ihre Diener sollen sehr stark sein (`Ratsechsen.md`). Die Tempel dürfen deshalb nicht zu lang sein, sonst wird es zäh. Lieber dichte, abwechslungsreiche Abschnitte mit Rastplätzen (sicherer Raum ohne Zufallskämpfe).

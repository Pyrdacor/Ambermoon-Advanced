"""SLP analysis: original (german 1.20) vs. Ambermoon Advanced (current german data).

Usage: python slp_report.py <output.md> [--work <dir>] [--original-zip <extracted zip>]

Builds the Advanced test data (tools/ambtools/make_testdata.py), extracts the original,
dumps party members / spells / scrolls with SlpAnalysis (C#, uses Ambermoon.net next to
this repo) and takes the Advanced spell costs from code_changes/AM2_CPU.s.
"""
import argparse
import csv
import os
import re
import subprocess
import sys
import tempfile
import zipfile

S = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(S, '..', '..'))
ap = argparse.ArgumentParser()
ap.add_argument('output')
ap.add_argument('--work', default=os.path.join(tempfile.gettempdir(), 'slp_analysis'))
ap.add_argument('--original-zip', default=r'C:\Users\Robert\source\repos\Ambermoon\Disks\German\ambermoon_german_1.20_extracted.zip')
args = ap.parse_args()
OUT = args.output
O = os.path.join(args.work, 'out')
os.makedirs(O, exist_ok=True)

original_dir = os.path.join(args.work, 'original')
if not os.path.exists(os.path.join(original_dir, 'Amberfiles')):
    with zipfile.ZipFile(args.original_zip) as z:
        z.extractall(original_dir)
advanced_dir = os.path.join(args.work, 'advanced')
subprocess.run([sys.executable, os.path.join(REPO, 'tools', 'ambtools', 'make_testdata.py'), advanced_dir], check=True)
subprocess.run(['dotnet', 'run', '-c', 'Release', '--project', os.path.join(S, 'SlpAnalysis.csproj'), '--',
                O, os.path.join(original_dir, 'Amberfiles'), os.path.join(advanced_dir, 'Amberfiles')], check=True)

# Advanced spell table from the Amiga source (5 bytes per spell: conditions, SP, SLP, target, element)
lines = open(os.path.join(REPO, 'code_changes', 'AM2_CPU.s'), encoding='latin1').read().split('\n')
start = next(k for k, l in enumerate(lines) if l.startswith('DAT_SpellInfos:')) + 2
amiga_rows, values, name = [], [], None
for l in lines[start:]:
    t = l.strip()
    if not t:
        continue
    if t.startswith(';'):
        name, values = t[1:].strip(), []
        continue
    m = re.match(r'dc\.b \$([0-9a-fA-F]+)', t)
    if not m:
        break
    values.append(int(m.group(1), 16))
    if len(values) == 5:
        amiga_rows.append(values)
        values = []
        if len(amiga_rows) == 120:
            break

SCHOOL_OF_CLASS = {'Adventurer': 'Alchemistic', 'Paladin': 'Healing', 'Ranger': 'Mystic', 'Healer': 'Healing',
                   'Alchemist': 'Alchemistic', 'Mystic': 'Mystic', 'Mage': 'Destruction'}
SCHOOL_DE = {'Healing': 'Heilung (weiß)', 'Alchemistic': 'Alchemie (blau)', 'Mystic': 'Mystik (grün)', 'Destruction': 'Zerstörung (schwarz)'}
CLASS_DE = {'Adventurer': 'Abenteurer', 'Paladin': 'Paladin', 'Ranger': 'Ranger', 'Healer': 'Heiler',
            'Alchemist': 'Alchemist', 'Mystic': 'Mystiker', 'Mage': 'Magier'}
HALF = {'Adventurer', 'Paladin', 'Ranger'}
PLAYABLE = ['THALION', 'NELVIN', 'SABINE', 'VALDYN', 'TARGOR', 'LEONARIA', 'GRYBAN']
SCHOOL_RANGE = {'Healing': range(1, 31), 'Alchemistic': range(31, 61), 'Mystic': range(61, 91), 'Destruction': range(91, 121)}
LEVELS = [10, 20, 30, 40, 50]


def tsv(name):
    return list(csv.DictReader(open(os.path.join(O, name), encoding='utf-8'), delimiter='\t'))


def spell_name(i):
    p = os.path.join(REPO, 'german', 'Amberfiles', 'AllTexts', 'Text.amb', 'SpellNames', '%03d.txt' % (i - 1))
    return open(p, encoding='utf-8-sig').read().strip() if os.path.exists(p) else f'#{i}'


# Advanced SLP/SP from the Amiga source table (authoritative), original from the remake tables
amiga = {i: (v[1], v[2]) for i, v in enumerate(amiga_rows, 1)}
spells_o = {int(r['spell']): (int(r['sp']), int(r['slp'])) for r in tsv('spells_original.tsv')}
spells_a = {i: amiga[i] for i in range(1, 121)}
remake_a = {int(r['spell']): int(r['slp']) for r in tsv('spells_advanced.tsv')}

party = {}
for ds in ('original', 'advanced'):
    party[ds] = {r['name']: r for r in tsv(f'party_{ds}.tsv') if r['name'] in PLAYABLE}

scrolls = {ds: set(int(r['spell']) for r in tsv(f'scrolls_{ds}.tsv') if 'SPRUCH -' not in r['name']) for ds in ('original', 'advanced')}
known = {ds: set(int(x) for r in party[ds].values() for x in r['learned'].split(',') if x) for ds in party}
exists = {ds: scrolls[ds] | known[ds] for ds in party}
# not learned via scrolls in Advanced (not counted for the learning demand)
EXCLUDED_ADVANCED = {60: 'nur in Alchemistenwaffe', 90: 'erhält Targor geschenkt'}
learnable = {'original': scrolls['original'], 'advanced': scrolls['advanced'] - set(EXCLUDED_ADVANCED)}
cost = {'original': spells_o, 'advanced': spells_a}


def per_level(p, intel):
    vals = [p * r // 100 for r in range(50, 101)]
    bonus = intel // 25
    return min(vals) + bonus, sum(vals) / len(vals) + bonus, max(vals) + bonus


def slp_at(pm, level, intel):
    join = int(pm['level'])
    if level < join:
        return None
    _, e, _ = per_level(int(pm['slp_per_level']), intel)
    return int(pm['slp']) + e * (level - join)


def level_for(pm, needed, intel, max_level):
    join = int(pm['level'])
    _, e, _ = per_level(int(pm['slp_per_level']), intel)
    have = int(pm['slp'])
    if have >= needed:
        return join
    if e <= 0:
        return None
    lvl = join + -(-(needed - have) // e)
    return int(lvl) if lvl <= max_level else None


out = []
w = out.append
w('# SLP-Analyse: Original (1.20) vs. Ambermoon Advanced Episode 4')
w('')
w('Stand 06.10.2026. Datenquellen:')
w('')
w('- **Original:** deutsche Version 1.20 (`Ambermoon/Disks/German`), Partymitglieder aus `Initial/Party_char.amb`, Zauberkosten aus der Remake-Tabelle `SpellInfos` (Originalwerte).')
w('- **Advanced Ep4:** `german/Amberfiles/Save.00/Party_char.amb` (Branch episode4), Zauberkosten aus der Amiga-Tabelle `DAT_SpellInfos` in `code_changes/AM2_CPU.s`.')
w('- Schriftrollen aus den Item-Daten beider Versionen.')
w('')
diffs = [i for i in sorted(amiga) if i in remake_a and remake_a[i] != amiga[i][1]]
if diffs:
    w('Abweichungen Remake ↔ Amiga (Advanced, SLP): ' + ', '.join(f'{i} „{spell_name(i)}“ (Remake {remake_a[i]}, Amiga {amiga[i][1]})' for i in diffs) + '.')
else:
    w('Remake und Amiga (Advanced) haben identische SLP-Kosten.')
w('')
w('## 1. Mechanik')
w('')
w('- **SLP pro Levelaufstieg** = `floor(SLP/Level × Zufall(50..100) / 100) + floor(INT / 25)`. Nur magische Klassen (alle außer Krieger, Dieb, Tier).')
w('  - Erwartungswert ≈ 0,75 × SLP/Level + INT/25. Min = halber Wert, Max = voller Wert (jeweils + INT/25).')
w('  - INT steigt beim Levelaufstieg **nicht** von selbst, nur über Tränke, Belohnungen und Ausrüstung. Die Hochrechnungen nutzen den Start-INT (in Klammern: mit maximalem INT).')
w('  - Original Amiga: nur Basis-INT ohne Bonus. Advanced (Amiga laut Todo gefixt, Remake): INT inklusive Ausrüstungsbonus.')
w('- **Lernen** einer Schriftrolle: Die SLP-Kosten werden **immer** abgezogen. Erfolg mit Wahrscheinlichkeit R-M% („Magie lesen“). Bei Misserfolg sind **SLP und Rolle weg**. Effektive Kosten ≈ Kosten / R-M.')
w('- Schriftrollen dürfen alle Klassen der jeweiligen Schule lesen. Halbmagier (Abenteurer, Paladin, Ranger) haben **keine** Einschränkung bei den Zaubern, nur weniger SLP (das 0x80-„Meister“-Flag spielt beim Lernen keine Rolle).')
w('- Advanced: Level 51–55 über Fragmente lösen ebenfalls normale Levelaufstiegs-Effekte aus (also auch SLP).')
w('')
w('## 2. Magische Partymitglieder')
w('')
w('Format: Original → Advanced. Fett = geändert.')
w('')
w('| Name | Klasse | Schule | Beitritt Lvl | Start-SLP | SLP/Lvl | INT (Start/Max) | R-M (Start/Max) | SP/Lvl | Startzauber |')
w('|---|---|---|---|---|---|---|---|---|---|')


def pair(a, b):
    return f'{a}' if a == b else f'**{a} → {b}**'


for n in PLAYABLE:
    o, a = party['original'][n], party['advanced'][n]
    cls = o['class']
    w(f"| {n.title()} | {CLASS_DE[cls]}{' (halb)' if cls in HALF else ''} | {SCHOOL_DE[SCHOOL_OF_CLASS[cls]]} | {o['level']} | "
      f"{pair(o['slp'], a['slp'])} | {pair(o['slp_per_level'], a['slp_per_level'])} | "
      f"{pair(o['int'] + '/' + o['int_max'], a['int'] + '/' + a['int_max'])} | "
      f"{pair(o['read_magic'] + '/' + o['read_magic_max'], a['read_magic'] + '/' + a['read_magic_max'])} | "
      f"{pair(o['sp_per_level'], a['sp_per_level'])} | "
      f"{pair(len([x for x in o['learned'].split(',') if x]), len([x for x in a['learned'].split(',') if x]))} |")
w('')
w('### 2.1 SLP pro Levelaufstieg (Min / Erwartung / Max, mit Start-INT)')
w('')
w('| Name | Original | Advanced |')
w('|---|---|---|')
for n in PLAYABLE:
    row = []
    for ds in ('original', 'advanced'):
        pm = party[ds][n]
        mn, e, mx = per_level(int(pm['slp_per_level']), int(pm['int']))
        row.append(f'{mn} / {e:.1f} / {mx}')
    w(f'| {n.title()} | {row[0]} | {row[1]} |')
w('')
w('### 2.2 Insgesamt erhaltene SLP (Erwartung, Start-SLP + Levelaufstiege; in Klammern mit maximalem INT)')
w('')
w('Spalten vor dem Beitrittslevel bleiben leer.')
w('')
w('| Name | Version | ' + ' | '.join(f'Lvl {l}' for l in LEVELS) + ' | Lvl 55 |')
w('|---|---|' + '---|' * (len(LEVELS) + 1))
for n in PLAYABLE:
    for ds in ('original', 'advanced'):
        pm = party[ds][n]
        cells = []
        for l in LEVELS + [55]:
            if l == 55 and ds == 'original':
                cells.append('–')
                continue
            v = slp_at(pm, l, int(pm['int']))
            vmax = slp_at(pm, l, int(pm['int_max']))
            cells.append('' if v is None else f'{v:.0f} ({vmax:.0f})')
        w(f"| {n.title() if ds == 'original' else ''} | {'Orig' if ds == 'original' else 'Adv'} | " + ' | '.join(cells) + ' |')
w('')

w('## 3. Zauber je Schule')
w('')
w('SLP- und SP-Kosten, Original → Advanced. „–“ = existiert in dieser Version nicht. Zauber mit Anmerkung in Klammern (keine Rolle, nur in Waffe, geschenkt) zählen nicht zum Lernbedarf. Fett = geändert.')
for school, rng in SCHOOL_RANGE.items():
    w('')
    w(f'### {SCHOOL_DE[school]}')
    w('')
    w('| # | Zauber | SLP Orig | SLP Adv | SP Orig | SP Adv |')
    w('|---|---|---|---|---|---|')
    tot = {'original': 0, 'advanced': 0}
    cnt = {'original': 0, 'advanced': 0}
    for i in rng:
        eo, ea = i in exists['original'], i in exists['advanced'] or (i == 90)
        if not eo and not ea:
            continue
        so = spells_o[i] if eo else None
        sa = spells_a[i] if ea else None
        if so and i in learnable['original']:
            tot['original'] += so[1]
            cnt['original'] += 1
        if sa and i in learnable['advanced']:
            tot['advanced'] += sa[1]
            cnt['advanced'] += 1
        def fmt(v, other):
            if v is None:
                return '–'
            return f'**{v}**' if other is not None and other != v else str(v)
        note = '' if (i in learnable['advanced'] or not ea) else f" ({EXCLUDED_ADVANCED.get(i, 'keine Rolle')})"
        w(f"| {i} | {spell_name(i)}{note} | {fmt(so and so[1], sa and sa[1]) if so else '–'} | {fmt(sa and sa[1], so and so[1]) if sa else '–'} | "
          f"{fmt(so and so[0], sa and sa[0]) if so else '–'} | {fmt(sa and sa[0], so and so[0]) if sa else '–'} |")
    w(f"| | **Summe lernbar** | **{tot['original']}** ({cnt['original']} Rollen) | **{tot['advanced']}** ({cnt['advanced']} Rollen) | | |")

w('')
w('## 4. Wer kann was ab welchem Level lernen?')
w('')
w('„Bedarf“ = Summe der SLP aller Zauber der Schule, die der Charakter beim Beitritt noch nicht kann. '
  '„Level alle“ = Level, ab dem die erwarteten SLP für die ganze Schule reichen (Start-INT; in Klammern mit Max-INT). '
  '„Effektiv“ = Bedarf geteilt durch die maximale R-M-Chance (erwartete SLP inklusive Fehlversuchen). '
  'Advanced rechnet bis Level 55, das Original bis 50. „nie“ = innerhalb der Levelgrenze nicht erreichbar.')
w('')
w('| Name | Version | Bedarf SLP | Level alle | Effektiv (R-M max) | Level effektiv | SLP bei Lvl 50 | Bei Lvl 50 lernbar (günstigste zuerst) |')
w('|---|---|---|---|---|---|---|---|')


def affordable_fraction(pm, ds, slp_total, school):
    # cheapest first: how many spells / what share of the remaining spells can be paid with slp_total
    kn = set(int(x) for x in pm['learned'].split(',') if x)
    remaining = sorted(cost[ds][i][1] for i in SCHOOL_RANGE[school] if i in learnable[ds] and i not in kn)
    s = 0
    n = 0
    for c in remaining:
        if s + c > slp_total:
            break
        s += c
        n += 1
    return n, len(remaining)


for n in PLAYABLE:
    for ds in ('original', 'advanced'):
        pm = party[ds][n]
        school = SCHOOL_OF_CLASS[pm['class']]
        kn = set(int(x) for x in pm['learned'].split(',') if x)
        need = sum(cost[ds][i][1] for i in SCHOOL_RANGE[school] if i in learnable[ds] and i not in kn)
        maxl = 55 if ds == 'advanced' else 50
        la = level_for(pm, need, int(pm['int']), maxl)
        lam = level_for(pm, need, int(pm['int_max']), maxl)
        rm = max(1, int(pm['read_magic_max']))
        eff = need * 100 / rm
        le = level_for(pm, eff, int(pm['int_max']), maxl)
        at50 = slp_at(pm, 50, int(pm['int']))
        k, total = affordable_fraction(pm, ds, at50, school)
        w(f"| {n.title() if ds == 'original' else ''} | {'Orig' if ds == 'original' else 'Adv'} | {need} | "
          f"{la if la else 'nie'} ({lam if lam else 'nie'}) | {eff:.0f} | {le if le else 'nie'} | {at50:.0f} | {k} von {total} |")

w('')
w('## 5. Beobachtungen')
w('')
w('Automatisch ermittelt, Bewertung siehe Abschnitt 6.')
w('')
for school, rng in SCHOOL_RANGE.items():
    to = sum(spells_o[i][1] for i in rng if i in learnable['original'])
    ta = sum(spells_a[i][1] for i in rng if i in learnable['advanced'])
    w(f'- {SCHOOL_DE[school]}: alle Zauber kosten zusammen {to} SLP im Original und {ta} SLP in Advanced (Faktor {ta / to:.1f}).')



def required_per_level(pm, need, target):
    join = int(pm['level'])
    levels = target - join
    if levels <= 0:
        return None
    for p in range(0, 200):
        _, e, _ = per_level(p, int(pm['int']))
        if int(pm['slp']) + e * levels >= need:
            return p
    return None


w('')
w('## 6. Benötigte SLP/Level (Advanced, Start-INT, Erwartungswert)')
w('')
w('Welcher Wert „SLP/Level“ wäre nötig, um bei den heutigen Zauberkosten das Ziel zu erreichen? '
  'Vollmagier: ganze Schule bis Level 45 bzw. 50. Halbmagier: die Hälfte der SLP-Summe ihrer Schule bis Level 50. '
  'Ohne Fehlversuche gerechnet (R-M), mit Fehlversuchen ist entsprechend mehr nötig.')
w('')
w('| Name | Klasse | SLP/Lvl heute | Bedarf | nötig für Ziel @45 | nötig für Ziel @50 |')
w('|---|---|---|---|---|---|')
for n in PLAYABLE:
    pm = party['advanced'][n]
    cls = pm['class']
    school = SCHOOL_OF_CLASS[cls]
    kn = set(int(x) for x in pm['learned'].split(',') if x)
    need = sum(cost['advanced'][i][1] for i in SCHOOL_RANGE[school] if i in learnable['advanced'] and i not in kn)
    if cls in HALF:
        need = sum(cost['advanced'][i][1] for i in SCHOOL_RANGE[school] if i in learnable['advanced']) // 2 - sum(cost['advanced'][i][1] for i in kn)
        goal = '50 % der Schule'
    else:
        goal = '100 %'
    r45 = required_per_level(pm, need, 45)
    r50 = required_per_level(pm, need, 50)
    w(f"| {n.title()} | {CLASS_DE[cls]} | {pm['slp_per_level']} | {need} ({goal}) | {r45 if r45 is not None else '–'} | {r50 if r50 is not None else '–'} |")

w(open(os.path.join(S, 'section7.md'), encoding='utf-8').read())

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out) + '\n')
print('written', OUT, len(out), 'lines')

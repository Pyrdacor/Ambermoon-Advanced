"""Check the English AllTexts against the German master texts.

- files only in German (missing translation) or only in English
- placeholders (~LEAD~ ...) that differ
- German leftovers in English (umlauts, common German words)
- form: repeated words, double spaces, missing space after punctuation, odd number of quotes
- possibly outdated: the German file was committed after the English one (git) and they are not identical
- names longer than the longest German name of the same kind (item, monster, NPC, map names ...)

Usage: python textcheck.py [--no-git]
"""
import os
import re
import subprocess
import sys
from collections import defaultdict

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
GER = os.path.join(REPO, 'german', 'Amberfiles', 'AllTexts')
ENG = os.path.join(REPO, 'english', 'Amberfiles', 'AllTexts')
SKIP_DIRS = ('Text.amb - Kopie',)
GERMAN_WORDS = re.compile(r'\b(UND|DER|DIE|DAS|IST|NICHT|IHR|EUCH|EINE?N?|MIT|AUF|SIE|WIR|ICH|DU|ZU|VON|DEN|DEM|SICH|AUCH|NOCH|SCHON|ABER|WENN|DASS)\b')
NAME_KINDS = {'Objects.amb': 'item name', 'Monster_char.amb': 'monster name', 'NPC_char.amb': 'NPC name',
              'Party_texts.amb': None, 'Dict.amb': 'keyword'}


def files(root):
    out = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if ' - Kopie' not in d]
        for f in fn:
            if f.endswith('.txt'):
                rel = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/')
                out[rel] = os.path.join(dp, f)
    return out


def read(path):
    return open(path, encoding='utf-8-sig').read()


def last_commit_times(rel_root):
    """path relative to rel_root -> unix time of the last commit touching it."""
    res = subprocess.run(['git', '-C', REPO, 'log', '--name-only', '--format=@%ct', '--', rel_root],
                         capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
    times, t = {}, 0
    for line in res.splitlines():
        if line.startswith('@'):
            t = int(line[1:])
        elif line.strip():
            p = line.strip().strip('"')
            if p.startswith(rel_root + '/'):
                times.setdefault(p[len(rel_root) + 1:], t)
    return times


def kind_of(rel):
    top = rel.split('/')[0]
    if top in NAME_KINDS:
        return NAME_KINDS[top]
    if top.endswith('Map_texts.amb') and rel.endswith('/000.txt'):
        return 'map name'
    return None


def main():
    use_git = '--no-git' not in sys.argv
    g, e = files(GER), files(ENG)
    findings = defaultdict(list)
    only_g = sorted(set(g) - set(e))
    only_e = sorted(set(e) - set(g))
    if use_git:
        tg = last_commit_times('german/Amberfiles/AllTexts')
        te = last_commit_times('english/Amberfiles/AllTexts')
    stale_candidates = []
    max_len = defaultdict(int)
    for rel in g:
        k = kind_of(rel)
        if k:
            max_len[k] = max(max_len[k], len(read(g[rel]).strip()))
    for rel in sorted(set(g) & set(e)):
        de, en = read(g[rel]), read(e[rel])
        if not en.strip():
            if de.strip():
                findings['empty English text'].append(rel)
            continue
        ph_de, ph_en = sorted(re.findall(r'~[A-Z]+~', de)), sorted(re.findall(r'~[A-Z]+~', en))
        if ph_de != ph_en:
            findings['placeholders differ'].append(f'{rel}: DE {ph_de} / EN {ph_en}')
        if re.search('[ÄÖÜäöüß]', en):
            findings['umlaut in English'].append(f'{rel}: {en.strip()[:90]}')
        elif en == de and len(en.strip()) > 3 and kind_of(rel) is None and GERMAN_WORDS.search(en):
            findings['identical to German'].append(f'{rel}: {en.strip()[:90]}')
        elif len(GERMAN_WORDS.findall(en)) >= 3:
            findings['German words in English'].append(f'{rel}: {en.strip()[:90]}')
        m = re.search(r'\b([A-Z]{2,})\s+\1\b', en)
        if m and m.group(1) not in ('HA', 'HO', 'NO', 'BLA', 'LA'):
            findings['repeated word'].append(f'{rel}: "{m.group(0)}"')
        if '  ' in en.strip():
            findings['double space'].append(rel)
        m = re.search(r'[a-zA-Z][,.!?;:][A-Za-z]', en)
        if m and not re.search(r'\.\.\.|[A-Z]\.[A-Z]\.', en) and '~' not in m.group(0):
            findings['missing space after punctuation'].append(f'{rel}: "...{en[max(0, m.start() - 10):m.end() + 10]}..."')
        if en.count('"') % 2 and not de.count('"') % 2:
            findings['odd number of quotes'].append(rel)
        k = kind_of(rel)
        if k and len(en.strip()) > max_len[k]:
            findings[f'{k} longer than any German {k} ({max_len[k]})'].append(f'{rel}: {en.strip()} ({len(en.strip())})')
        if use_git and de != en and tg.get(rel, 0) > te.get(rel, 0) + 60:
            stale_candidates.append(rel)

    if use_git:
        # outdated: the German text differs from the German text at the time of the last English commit
        for rel in stale_candidates:
            commit = subprocess.run(['git', '-C', REPO, 'log', '-1', '--format=%H', '--',
                                     'english/Amberfiles/AllTexts/' + rel], capture_output=True, text=True).stdout.strip()
            if not commit:
                continue
            old = subprocess.run(['git', '-C', REPO, 'show', f'{commit}:german/Amberfiles/AllTexts/{rel}'],
                                 capture_output=True).stdout.decode('utf-8-sig', 'replace')
            if old and old.split() != read(g[rel]).split():
                findings['German text changed since the last English change (maybe outdated)'].append(rel)
    print(f'German texts: {len(g)}, English texts: {len(e)}')
    print(f'only German ({len(only_g)}): ' + ', '.join(only_g[:60]) + (' ...' if len(only_g) > 60 else ''))
    print(f'only English ({len(only_e)}): ' + ', '.join(only_e[:30]))
    for k, v in findings.items():
        print(f'\n{k} ({len(v)}):')
        for x in v[:80]:
            print('  ' + x)
        if len(v) > 80:
            print(f'  ... {len(v) - 80} more')


if __name__ == '__main__':
    main()

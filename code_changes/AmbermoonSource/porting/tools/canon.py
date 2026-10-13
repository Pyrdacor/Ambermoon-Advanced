"""Canonicalize normalized lines: numbers to decimal, drop branch size suffixes, uppercase registers."""
import re, sys
src, out = sys.argv[1:3]
BR = re.compile(r'^(b(?:ra|sr|eq|ne|cc|cs|hi|ls|pl|mi|ge|gt|le|lt|vc|vs|hs|lo))\.[bws]\b', re.I)
NUM = re.compile(r'(?<![\w.])(-?)\$([0-9a-fA-F]+)\b|(?<![\w.$])(-?)(\d+)\b')
def num(m):
    if m.group(2) is not None:
        v = int(m.group(2), 16); s = m.group(1)
    else:
        v = int(m.group(4)); s = m.group(3)
    return ('-' if s else '') + str(v)
res = []
for t in open(src, encoding='latin1').read().split('\n')[:-1]:
    if t.endswith(':'): res.append(t); continue
    p = t.split(' ', 1)
    op = BR.sub(r'\1', p[0].lower())
    if op in ('dc.b', 'dc.w', 'dc.l', 'dx.b', 'dx.w', 'dx.l') or len(p) == 1:
        res.append(op + (' ' + NUM.sub(num, p[1]) if len(p) > 1 else '')); continue
    a = NUM.sub(num, p[1])
    a = re.sub(r'\b([dDaA][0-7])\b', lambda m: m.group(1).upper(), a)
    a = re.sub(r'\b(sp|SP)\b', 'SP', a)
    a = a.replace('.w,', ',').replace('.W,', ',') if False else a
    res.append(op + ' ' + a)
open(out, 'w', encoding='latin1').write('\n'.join(res) + '\n')

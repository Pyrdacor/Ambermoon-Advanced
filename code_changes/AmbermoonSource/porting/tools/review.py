"""Review the differences between the old Advanced build and the ported build.

A difference is 'known' if the same change (removed and added tokens) also appears between
the old base and the unchanged AmbermoonSource build (= an original fix since 62823505)."""
import os, re, sys

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(W, 'cmp')


def hunks(prefix):
    a = open(os.path.join(C, prefix + '.A.tok'), encoding='latin1').read().split('\n')
    b = open(os.path.join(C, prefix + '.B.tok'), encoding='latin1').read().split('\n')
    res = []
    for line in open(os.path.join(C, prefix + '.diff')):
        h = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
        if not h:
            continue
        a1 = int(h.group(1)); an = int(h.group(2) or 1) if h.group(2) != '0' else 0
        b1 = int(h.group(3)); bn = int(h.group(4) or 1) if h.group(4) != '0' else 0
        ta = a[a1 - 1:a1 - 1 + an] if an else []
        tb = b[b1 - 1:b1 - 1 + bn] if bn else []
        res.append((ta, tb, a[max(0, a1 - 2)] if a1 > 1 else '', b[max(0, b1 - 2)] if b1 > 1 else ''))
    return res


def key(ta, tb):
    return (tuple(t.split('|')[1] for t in ta), tuple(t.split('|')[1] for t in tb))


def origins(ts):
    seen = []
    for t in ts:
        o = t.split('|')[2]
        if o not in seen:
            seen.append(o)
    return seen


known = {key(ta, tb) for ta, tb, _, _ in hunks('basepristine')}
unknown = 0
for ta, tb, ca, cb in hunks('advwork'):
    k = key(ta, tb)
    if k in known:
        continue
    unknown += 1
    print('-' * 70)
    print('ADV  %s: %s' % (','.join(origins(ta)[:4]) or ('after ' + ca.split('|')[2]), ' '.join(t.split('|')[1] for t in ta)[:150]))
    print('WORK %s: %s' % (','.join(origins(tb)[:4]) or ('after ' + cb.split('|')[2]), ' '.join(t.split('|')[1] for t in tb)[:150]))
print('unknown differences:', unknown)

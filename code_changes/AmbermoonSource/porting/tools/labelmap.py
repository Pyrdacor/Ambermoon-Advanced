"""Derive a label mapping adv-name -> base-name by aligning the two normalized files.
usage: labelmap.py <base prefix> <adv prefix> <out tsv>"""
import re, sys, subprocess, collections, os, tempfile
bp, ap, out = sys.argv[1:4]
IDENT = re.compile(r'(?<![\w$#.])([A-Za-z_.][\w.]*)')
def load(p):
    return (open(p + '.lines', encoding='latin1').read().split('\n')[:-1],
            set(open(p + '.labels').read().split('\n')))
bl, blab = load(bp); al, alab = load(ap)
def anchor_set(common):
    return set(common)
mapping = {}
# Advanced labels which already use the name of the original source for a renamed base label
symfile = os.path.join(os.path.dirname(os.path.abspath(bp)), '..', 'src121', 'AmbermoonSource', 'SYMBOLS.txt')
if os.path.exists(symfile):
    by_name = {}
    for l in open(symfile, encoding='latin1'):
        if l.startswith('#'):
            continue
        p = l.rstrip('\n').split('\t')
        if len(p) >= 2:
            by_name.setdefault(p[1], []).append(p[0])
    used = set()
    extra = 0
    for y in sorted(alab - blab - set(mapping)):
        for x in by_name.get(y, []):
            if x in blab and x not in alab and x not in used:
                mapping[y] = x; used.add(x); extra += 1
                break
    print('mapped by original source names:', extra)
fixed = set(mapping)
for it in range(3):
    anchors = anchor_set(blab & alab) | set(mapping.values())
    inv = {v: k for k, v in mapping.items()}
    def semi(lines, labs, is_adv):
        res = []
        for t in lines:
            def rep(m):
                n = m.group(1)
                if is_adv and n in mapping: n = mapping[n]
                if n in anchors: return n
                return '@' if (m.group(1) in labs) else m.group(1)
            if t.endswith(':'):
                n = t[:-1]
                if is_adv and n in mapping: n = mapping[n]
                res.append(n + ':' if n in anchors else '@:')
            else:
                p = t.split(' ', 1)
                res.append(p[0] + (' ' + IDENT.sub(rep, p[1]) if len(p) > 1 else ''))
        return res
    sb, sa = semi(bl, blab, False), semi(al, alab, True)
    d = tempfile.mkdtemp()
    fb, fa = os.path.join(d, 'b'), os.path.join(d, 'a')
    open(fb, 'w', encoding='latin1').write('\n'.join(sb) + '\n'); open(fa, 'w', encoding='latin1').write('\n'.join(sa) + '\n')
    r = subprocess.run(['git', 'diff', '--no-index', '--histogram', '-U0', fb, fa], capture_output=True, text=True, encoding='latin1')
    # equal segments
    eq = []; pb = pa = 0
    nchg = 0
    for line in r.stdout.split('\n'):
        m = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
        if not m: continue
        b1, bn, a1, an = int(m.group(1)), int(m.group(2) or 1), int(m.group(3)), int(m.group(4) or 1)
        bs = b1 - 1 if bn else b1; as_ = a1 - 1 if an else a1
        eq.append((pb, bs, pa, as_)); pb, pa = bs + bn, as_ + an; nchg += bn + an
    eq.append((pb, len(sb), pa, len(sa)))
    votes = collections.defaultdict(collections.Counter)
    for b0, b1, a0, a1 in eq:
        for i in range(b1 - b0):
            tb, ta = bl[b0 + i], al[a0 + i]
            if tb == ta: continue
            if tb.endswith(':') and ta.endswith(':'):
                x, y = tb[:-1], ta[:-1]
                if x in blab and y in alab: votes[y][x] += 1  # definition at the same place (weak: a new routine may be inserted right before)
                continue
            nb = [m.group(1) for m in IDENT.finditer(tb.rstrip(':'))]; na = [m.group(1) for m in IDENT.finditer(ta.rstrip(':'))]
            if len(nb) != len(na): continue
            for x, y in zip(nb, na):
                if x != y and x in blab and y in alab :
                    votes[y][x] += 2
    new = {}
    # one-to-one: process the strongest votes first
    cand = []
    for y, c in votes.items():
        for x, n in c.items(): cand.append((n, y, x))
    used_x = set(mapping.values()); used_y = set(mapping)
    for n, y, x in sorted(cand, reverse=True):
        if y in used_y or x in used_x or y in blab or x in alab: continue
        new[y] = x; used_x.add(x); used_y.add(y)
    votes = {}
    for y, c in votes.items():
        x, n = c.most_common(1)[0]
        if len(c) > 1 and c.most_common(2)[1][1] * 2 > n: continue  # ambiguous
        if y not in blab and x not in alab and n >= 1: new[y] = x
    added = len(set(new) - set(mapping))
    mapping.update(new)
    print('iteration', it, 'changed lines', nchg, 'mapping size', len(mapping), 'new', added)
    if not added: break
# validation: the Advanced definition must be aligned with the base definition, or both must be
# inside the same changed hunk. Otherwise the pair is a coincidence (e.g. a new routine).
def validate(mapping):
    renamed = []
    for t in al:
        if t.endswith(':'):
            n = t[:-1]
            renamed.append(mapping.get(n, n) + ':')
        else:
            renamed.append(re.sub(r'(?<![\w$#.])([A-Za-z_.][\w.]*)', lambda m: mapping.get(m.group(1), m.group(1)), t))
    d = tempfile.mkdtemp()
    fb, fa = os.path.join(d, 'b'), os.path.join(d, 'a')
    open(fb, 'w', encoding='latin1').write('\n'.join(bl) + '\n')
    open(fa, 'w', encoding='latin1').write('\n'.join(renamed) + '\n')
    r = subprocess.run(['git', 'diff', '--no-index', '--histogram', '-U0', fb, fa], capture_output=True, text=True, encoding='latin1')
    eq, hunks = {}, []
    pa = pb = 0
    for line in r.stdout.split('\n'):
        h = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
        if not h:
            continue
        b1 = int(h.group(1)); bn = int(h.group(2) or 1) if h.group(2) != '0' else 0
        a1 = int(h.group(3)); an = int(h.group(4) or 1) if h.group(4) != '0' else 0
        bs = b1 - 1 if bn else b1
        as_ = a1 - 1 if an else a1
        while pa < as_:
            eq[pa + 1] = pb + 1; pa += 1; pb += 1
        hunks.append((as_ + 1, as_ + an, bs + 1, bs + bn)); pa, pb = as_ + an, bs + bn
    while pa < len(al):
        eq[pa + 1] = pb + 1; pa += 1; pb += 1
    adef = {t[:-1]: i + 1 for i, t in enumerate(al) if t.endswith(':')}
    bdef = {t[:-1]: i + 1 for i, t in enumerate(bl) if t.endswith(':')}
    bad = []
    for y, x in mapping.items():
        ay, bx = adef.get(y), bdef.get(x)
        if ay is None or bx is None:
            continue
        if ay in eq:
            ok = abs(eq[ay] - bx) <= 3
        else:
            h = next((h for h in hunks if h[0] <= ay <= h[1]), None)
            ok = h is not None and h[2] <= bx <= h[3]
        if not ok:
            bad.append((y, x))
    return bad
for it in range(3):
    bad = validate(mapping)
    if not bad:
        break
    for y, x in bad:
        print('dropped suspicious mapping %s -> %s' % (y, x))
        del mapping[y]
with open(out, 'w') as f:
    for k, v in sorted(mapping.items()): f.write('%s\t%s\n' % (k, v))

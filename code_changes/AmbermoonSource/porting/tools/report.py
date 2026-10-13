import re, sys, collections
base, adv, diff, out = sys.argv[1:5]   # base prefix, adv prefix, diff file, out tsv
bs = open(base + '.s', encoding='latin1').read().split('\n'); as_ = open(adv + '.s', encoding='latin1').read().split('\n')
ib = [int(x) for x in open(base + '.idx')]; ia = [int(x) for x in open(adv + '.idx')]
bl = open(base + '.lines', encoding='latin1').read().split('\n')
GL = re.compile(r'^([A-Za-z_][\w]*):')
def func_at(src, line):
    for i in range(line - 1, -1, -1):
        m = GL.match(src[i])
        if m and not m.group(1).startswith(('LAB_', '.')): return m.group(1)
    return '?'
def tags(src, l1, l2):
    t = ' '.join(src[l1 - 1:l2])
    found = [k for k in ('ADVANCED', 'FIX', 'BUG', 'TODO', 'NEW', 'Advanced') if k in t]
    return ','.join(found)
rows = []
for l in open(diff, encoding='latin1'):
    m = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', l)
    if not m: continue
    b1, bn, a1, an = int(m.group(1)), int(m.group(2) or 1), int(m.group(3)), int(m.group(4) or 1)
    bsl = ib[b1 - 1] if bn else (ib[b1 - 1] if b1 >= 1 else 1)
    bel = ib[b1 + bn - 2] if bn else bsl
    asl = ia[a1 - 1] if an else (ia[a1 - 1] if a1 >= 1 else 1)
    ael = ia[a1 + an - 2] if an else asl
    rows.append((bsl, bn, asl, an, func_at(bs, bsl), func_at(as_, asl), tags(bs, bsl, bel + 1) if bn else '', tags(as_, max(1, asl - 2), ael + 1) if an else ''))
with open(out, 'w') as f:
    f.write('base_line\tbase_n\tadv_line\tadv_n\tbase_func\tadv_func\tbase_tags\tadv_tags\n')
    for r in rows: f.write('\t'.join(map(str, r)) + '\n')
c = collections.Counter('adv-tagged' if r[7] else ('base-tagged' if r[6] else 'untagged') for r in rows)
print(len(rows), 'hunks', dict(c))

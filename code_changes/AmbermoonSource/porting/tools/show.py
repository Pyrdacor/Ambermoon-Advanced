"""Show a hunk: Advanced text, base text and the target region of the 1.21 source.
usage: show.py <hunk id> [<hunk id> ...]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import srcmodel
W = srcmodel.W
H = json.load(open(os.path.join(W, 'plan.json')))
M = srcmodel.load()
adv = open(os.path.join(W, 'adv.s'), encoding='latin1').read().split('\n')
base = open(os.path.join(W, 'base', '62823505.s'), encoding='latin1').read().split('\n')
ia = [int(x) for x in open(os.path.join(W, 'adv.idx'))]
for hid in map(int, sys.argv[1:]):
    h = H[hid]
    print('=' * 30, 'hunk', hid, h.get('kind'), 'target', h.get('target'), 'addr', h.get('addr_range'))
    b1, b2 = h['base_lines']
    print('--- base %d-%d' % (b1, b2))
    for i in range(max(1, b1 - 2), b2 + 2):
        print('   %s%s' % ('-' if b1 <= i <= b2 else ' ', base[i - 1]))
    if h['an']:
        a_first = ia[h['a1'] - 2] + 1 if h['a1'] >= 2 else 1
        a_last = ia[h['a1'] + h['an'] - 2]
        print('--- adv %d-%d' % (a_first, a_last))
        for i in range(a_first, a_last + 1):
            print('   +%s' % adv[i - 1])
    t = h.get('src121') or h.get('target')
    if h.get('src_range'):
        f = h['src_range'][0][0]
        lns = [ln for _, ln in h['src_range']]
        lo, hi = min(lns), max(lns)
    elif t:
        f, lo = t[0], t[1]
        hi = lo
    else:
        continue
    src = M.src_lines(f)
    print('--- source 1.21 %s %d-%d' % (f, lo, hi))
    for i in range(max(1, lo - 3), min(len(src), hi + 3) + 1):
        print('   %s%d: %s' % ('*' if lo <= i <= hi else ' ', i, src[i - 1]))

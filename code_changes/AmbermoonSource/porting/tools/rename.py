import re, sys
lines_in, mapfile, out = sys.argv[1:4]
IDENT = re.compile(r'(?<![\w$#.])([A-Za-z_.][\w.]*)')
mp = dict(l.split('\t') for l in open(mapfile).read().split('\n') if l)
res = []
for t in open(lines_in, encoding='latin1').read().split('\n')[:-1]:
    if t.endswith(':'): res.append(mp.get(t[:-1], t[:-1]) + ':'); continue
    p = t.split(' ', 1)
    res.append(p[0] + (' ' + IDENT.sub(lambda m: mp.get(m.group(1), m.group(1)), p[1]) if len(p) > 1 else ''))
open(out, 'w', encoding='latin1').write('\n'.join(res) + '\n')

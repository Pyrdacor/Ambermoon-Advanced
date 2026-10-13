"""Normalize an AM2_CPU.s disassembly: strip comments, one statement per line.
Writes <out>.lines (normalized text with label names) and <out>.mask (label names replaced by @).
Each output line is prefixed with the source line number in <out>.idx."""
import re, sys
src, out = sys.argv[1], sys.argv[2]
LABEL_DEF = re.compile(r'^([A-Za-z_.][\w.]*):(.*)$')
IDENT = re.compile(r'(?<![\w$#.])([A-Za-z_.][\w.]*)')
def strip_comment(s):
    q = None; r = []
    for ch in s:
        if q:
            r.append(ch)
            if ch == q: q = None
        elif ch in '"\'':
            q = ch; r.append(ch)
        elif ch == ';':
            break
        else:
            r.append(ch)
    return ''.join(r)
lines = open(src, encoding='latin1').read().split('\n')
labels = set(); stmts = []
scope = ''
def qual(t):
    # qualify local labels (.x) with the enclosing global label
    return re.sub(r'(?<![\w$#])(\.[A-Za-z_][\w]*)', lambda mm: scope + mm.group(1), t)
for no, raw in enumerate(lines, 1):
    s = raw.rstrip('\r')
    if s.startswith('*'): continue
    s = strip_comment(s).rstrip()
    if not s.strip(): continue
    m = LABEL_DEF.match(s)
    if m:
        name = m.group(1)
        if name.startswith('.'): name = scope + name
        else: scope = name
        labels.add(name); stmts.append((no, name + ':'))
        s = m.group(2)
        if not s.strip(): continue
    s = ' '.join(s.split())
    p = s.split(' ', 1)
    if len(p) > 1: s = p[0] + ' ' + qual(p[1])
    stmts.append((no, s))
OPS = {'dc.b','dc.w','dc.l','dx.b','dx.w','dx.l','ds.b','ds.w','ds.l','section','even','cnop'}
def mask(t):
    if t.endswith(':') and t[:-1] in labels: return '@:'
    parts = t.split(' ', 1)
    if len(parts) == 1: return t
    ops = IDENT.sub(lambda mm: '@' if mm.group(1) in labels else mm.group(1), parts[1])
    return parts[0] + ' ' + ops
with open(out + '.lines', 'w', encoding='latin1') as f1, open(out + '.mask', 'w', encoding='latin1') as f2, open(out + '.idx', 'w') as f3:
    for no, t in stmts:
        f1.write(t + '\n'); f2.write(mask(t) + '\n'); f3.write('%d\n' % no)
open(out + '.labels', 'w').write('\n'.join(sorted(labels)))
print(src, len(stmts), 'statements', len(labels), 'labels')

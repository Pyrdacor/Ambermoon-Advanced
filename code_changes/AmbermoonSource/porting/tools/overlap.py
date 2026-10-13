"""List applied hunks whose base lines are near lines changed between 62823505 and 382eaeda,
or whose target lines are near lines changed between AmbermoonSource 1.21 and HEAD.
Such places may contain an original fix which Advanced made independently (double fix)."""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan import W, AMB
NEAR = 4

def changed_lines(a, b):
    r = subprocess.run(['git', 'diff', '--no-index', '--histogram', '-U0', a, b], capture_output=True, text=True, encoding='latin1')
    res = set()
    for line in r.stdout.split('\n'):
        h = re.match(r'^@@ -(\d+)(?:,(\d+))? \+', line)
        if h:
            a1, an = int(h.group(1)), int(h.group(2) or 1) if h.group(2) != '0' else 0
            res.update(range(a1, a1 + max(an, 1)))
    return res

ch62 = changed_lines(os.path.join(W, 'base', '62823505.s'), os.path.join(W, 'base', '382eaeda.s'))
plan = json.load(open(os.path.join(W, 'plan.json')))
applied = {}
for l in open(os.path.join(W, 'port_log.txt')):
    p = l.rstrip('\n').split('\t')
    if len(p) > 2 and p[1] == 'applied':
        applied[int(p[0])] = (p[2], int(p[3]))
src121 = os.path.join(W, 'src121', 'AmbermoonSource', 'src')
chhead = {}
for hid, h in enumerate(plan):
    if hid not in applied:
        continue
    b0, b1 = h['base_lines']
    near62 = sorted(x for x in ch62 if b0 - NEAR <= x <= max(b0, b1) + NEAR)
    reason = []
    if near62:
        reason.append('62->382 lines %s' % near62[:6])
    t = h.get('src121')
    if t:
        f, ln, _ = t
        if f not in chhead:
            chhead[f] = changed_lines(os.path.join(src121, f), os.path.join(AMB, 'AmbermoonSource', 'src', f))
        nh = sorted(x for x in chhead[f] if ln - NEAR <= x <= ln + NEAR + max(0, b1 - b0))
        if nh:
            reason.append('1.21->HEAD %s:%s' % (f, nh[:6]))
    if reason:
        print(hid, applied[hid], 'base', h['base_lines'], '|', '; '.join(reason))

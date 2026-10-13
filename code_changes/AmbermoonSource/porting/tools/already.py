"""Mark hunks which are already contained in the 1.21 source (no difference against 382eaeda)."""
import json, os, re
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def adv_ranges(path):
    s = set()
    for l in open(path, encoding='latin1'):
        m = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', l)
        if m:
            a1 = int(m.group(3)); an = int(m.group(4) or 1) if m.group(4) != '0' else 0
            if an:
                s.update(range(a1, a1 + an))
            else:
                s.add(('ins', a1))
    return s
r382 = adv_ranges(os.path.join(W, 'canon382.diff'))
H = json.load(open(os.path.join(W, 'plan.json')))
n = 0
for h in H:
    if h['an']:
        present = not any(k in r382 for k in range(h['a1'], h['a1'] + h['an']))
    else:
        present = ('ins', h['a1']) not in r382 and not any(k in r382 for k in (h['a1'], h['a1'] + 1))
    h['already'] = present
    n += present
json.dump(H, open(os.path.join(W, 'plan.json'), 'w'), indent=0)
print('already in 1.21 source:', n, 'of', len(H))

"""Classify the hunks of plan.json by how they can be applied to AmbermoonSource."""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import srcmodel
from plan import git_diff_linemap

W = srcmodel.W


def main():
    M = srcmodel.load()
    base62 = open(os.path.join(W, 'base', '62823505.s'), encoding='latin1').read().split('\n')
    base382 = open(os.path.join(W, 'base', '382eaeda.s'), encoding='latin1').read().split('\n')
    m = git_diff_linemap(base62, base382)
    H = json.load(open(os.path.join(W, 'plan.json')))
    cats = collections.Counter()
    for h in H:
        if h.get('already'):
            h['kind'] = 'already'; cats['already'] += 1; continue
        if all(x.endswith(':') for x in h['minus'] + h['plus']):
            h['kind'] = 'labels-only'; cats['labels-only'] += 1; continue
        first, last = h['base_lines']
        l1 = m.get(first)
        if h['bn']:
            l2 = m.get(last)
            a, e = M.b_addr(l1), M.b_end(l2)
            if a is None or e is None or a[0] != e[0]:
                h['kind'] = 'manual-range'; cats['manual-range'] += 1; continue
            lines, exact = M.s_covering(a[0], a[1], e[1])
            files = {f for f, ln in lines}
            h['src_range'] = lines
            h['addr_range'] = [a[0], a[1], e[1]]
            if not lines:
                kind = 'replace-empty'
            elif len(files) > 1:
                kind = 'replace-multifile'
            elif exact:
                kind = 'replace-exact'
            else:
                kind = 'replace-partial'
        else:
            a = M.b_addr(l1)
            h['addr_range'] = [a[0], a[1], a[1]] if a else None
            at = M.s_at(*a) if a else []
            h['src_at'] = at
            kind = 'insert' if at else 'insert-inside'
        h['kind'] = kind
        cats[kind] += 1
    json.dump(H, open(os.path.join(W, 'plan.json'), 'w'), indent=0)
    for k, v in cats.most_common():
        print(v, k)


if __name__ == '__main__':
    main()

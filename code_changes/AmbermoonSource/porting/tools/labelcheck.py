"""Check that every label points to the same code/data in the old Advanced build and the ported
build: compare the bytes behind each label pair (relocated longwords masked)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relcheck, srcmodel, symbols
C = relcheck.C
N = 12

def main():
    M = srcmodel.load()
    R = symbols.Resolver(M)
    import port
    la = relcheck.labels(os.path.join(C, 'adv.lst'))
    lw = relcheck.labels(os.path.join(C, 'work.lst'))
    ha = relcheck.read_relocs(os.path.join(C, 'adv.bin'))
    hw = relcheck.read_relocs(os.path.join(C, 'work.bin'))
    def canon(name):
        if name in port.EQUIV:
            return port.EQUIV[name]
        b = R.adv2base.get(name, name if name in R.base_labels else None)
        if b is None:
            return name
        b = R._b62_to_382().get(b, b)
        sym = R.symbols.get(b)
        if sym and sym[1] and not sym[0].startswith('Lbl_'):
            return sym[0]
        n, why = R.base_to_src(b, '', '')
        return n if n else b
    def window(hunks, h, o):
        d = hunks[h]['data']
        if not d:
            return None
        rel = hunks[h]['rel']
        out = []
        for i in range(o, min(o + N, len(d))):
            masked = any(r <= i < r + 4 for r in rel if r <= i)
            out.append(None if masked else d[i])
        return out
    bad = []
    checked = 0
    for n, (h, o) in la.items():
        c = canon(n)
        if '+' in c or c not in lw:
            continue
        wa, ww = window(ha, h, o), window(hw, *lw[c])
        if wa is None or ww is None:
            continue
        checked += 1
        k = min(len(wa), len(ww))
        if any(a is not None and b is not None and a != b for a, b in zip(wa[:k], ww[:k])):
            bad.append((n, c, (h, o), lw[c], bytes(x or 0 for x in wa[:8]).hex(), bytes(x or 0 for x in ww[:8]).hex()))
    print('checked', checked, 'labels, different bytes behind', len(bad))
    for b in bad:
        print(b)

if __name__ == '__main__':
    main()

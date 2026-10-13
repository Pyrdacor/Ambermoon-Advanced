"""Check that relocated references point to the same symbols in the old Advanced build and the
ported build.

For both builds: symbol table from the listing (global labels -> hunk/offset), relocation targets
from the hunk file. Every relocation of an aligned (unchanged) token pair is resolved to
'nearest global label + delta'. Advanced names are translated to source names like port.py does.
"""
import bisect, json, os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bincmp, srcmodel, symbols

W = srcmodel.W
C = os.path.join(W, 'cmp')
LBL = re.compile(r'^(?:([0-9A-F]{2}):([0-9A-F]{8}) \S*)?\s*\t\s*(\d+)([:MR])\s?([A-Za-z_][\w]*)(:|\s|$)')
LOCAL_LBL = re.compile(r'^(?:[0-9A-F]{2}:[0-9A-F]{8} \S*)?\s*\t\s*\d+[:MR]\s?(\.?[A-Za-z_][\w]*):')
ADDR = re.compile(r'^([0-9A-F]{2}):([0-9A-F]{8}) ')


def labels(listing):
    """global label -> (hunk, offset): a label gets the address of the next address line."""
    res = {}
    pending = []
    for l in open(listing, encoding='latin1'):
        m = LBL.match(l.rstrip('\n'))
        a = ADDR.match(l)
        if m and m.group(4) == ':' and not re.match(r'^\s*(equ|set|=|macro|rs)\b', l.split(m.group(5), 1)[1].lstrip(':'), re.I):
            pending.append(m.group(5))
        if a:
            for n in pending:
                res.setdefault(n, (int(a.group(1), 16), int(a.group(2), 16)))
            pending = []
    return res


def read_relocs(path):
    d = open(path, 'rb').read()
    p = 0
    def L():
        nonlocal p
        v = struct.unpack('>I', d[p:p + 4])[0]; p += 4; return v
    assert L() == 0x3F3
    while L():
        pass
    count = L(); first = L(); last = L()
    for _ in range(last - first + 1):
        L()
    hunks = []
    cur = None
    while p < len(d):
        t = L() & 0x3FFFFFFF
        if t in (0x3E9, 0x3EA):
            n = L() * 4
            cur = {'data': d[p:p + n], 'rel': {}}
            p += n
            hunks.append(cur)
        elif t == 0x3EB:
            L(); cur = {'data': b'', 'rel': {}}; hunks.append(cur)
        elif t == 0x3EC:
            while True:
                n = L()
                if not n:
                    break
                th = L()
                for _ in range(n):
                    o = L()
                    cur['rel'][o] = (th, struct.unpack('>I', cur['data'][o:o + 4])[0])
        elif t == 0x3F2:
            pass
    return hunks


def nearest(table, hunk, off):
    lst = table.get(hunk)
    if not lst:
        return None
    i = bisect.bisect_right(lst[0], off) - 1
    if i < 0:
        return None
    return lst[1][i], off - lst[0][i]


def index(labs):
    t = {}
    for n, (h, o) in labs.items():
        t.setdefault(h, []).append((o, n))
    res = {}
    for h, v in t.items():
        v.sort()
        res[h] = ([o for o, _ in v], [n for _, n in v])
    return res


def main():
    M = srcmodel.load()
    R = symbols.Resolver(M)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import port
    port_grename = {}
    la = labels(os.path.join(C, 'adv.lst'))
    lw = labels(os.path.join(C, 'work.lst'))
    ia_, iw_ = index(la), index(lw)
    ra, rw = read_relocs(os.path.join(C, 'adv.bin')), read_relocs(os.path.join(C, 'work.bin'))
    # translate an Advanced global name to the source name
    def canon(name):
        if name in port.EQUIV:
            return port.EQUIV[name]
        b = R.adv2base.get(name, name if name in R.base_labels else None)
        if b is None:
            return port_grename.get(name, name)
        b = R._b62_to_382().get(b, b)
        sym = R.symbols.get(b)
        if sym and sym[1] and not sym[0].startswith('Lbl_'):
            return sym[0]
        n, why = R.base_to_src(b, '', '')
        return n if n else b
    # aligned token pairs from the byte-token diff
    ta = open(os.path.join(C, 'advwork.A.tok'), encoding='latin1').read().split('\n')
    tw = open(os.path.join(C, 'advwork.B.tok'), encoding='latin1').read().split('\n')
    eq = []
    pa = pb = 0
    for line in open(os.path.join(C, 'advwork.diff')):
        h = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
        if not h:
            continue
        a1 = int(h.group(1)); an = int(h.group(2) or 1) if h.group(2) != '0' else 0
        b1 = int(h.group(3)); bn = int(h.group(4) or 1) if h.group(4) != '0' else 0
        as_ = a1 - 1 if an else a1
        bs = b1 - 1 if bn else b1
        while pa < as_:
            eq.append((pa, pb)); pa += 1; pb += 1
        pa, pb = as_ + an, bs + bn
    while pa < len(ta) - 1 and pb < len(tw) - 1:
        eq.append((pa, pb)); pa += 1; pb += 1
    # byte offsets of the tokens: recompute from the token streams
    def offsets(toks):
        res = []
        off = {}
        for t in toks:
            if not t:
                res.append(None); continue
            sec, tok, _ = t.split('|')
            sec = int(sec)
            o = off.get(sec, 0)
            res.append((sec, o))
            if tok == 'RRRR':
                off[sec] = o + 4
            elif tok.startswith('B'):
                off[sec] = o  # branch tokens: length unknown, fixed below
            else:
                off[sec] = o + len(tok) // 2
        return res
    # branch tokens break the offset bookkeeping; use relocation positions directly instead:
    # collect reloc positions per hunk in order and pair them through the aligned RRRR tokens
    def reloc_seq(hunks):
        seq = []
        for hi, h in enumerate(hunks):
            for o in sorted(h['rel']):
                seq.append((hi, o, h['rel'][o]))
        return seq
    sa, sw = reloc_seq(ra), reloc_seq(rw)
    # the n-th RRRR token of a hunk is the n-th relocation of that hunk
    def rr_index(toks):
        res = {}
        cnt = {}
        for i, t in enumerate(toks):
            if not t:
                continue
            sec, tok, _ = t.split('|')
            if tok == 'RRRR':
                sec = int(sec)
                res[i] = (sec, cnt.get(sec, 0))
                cnt[sec] = cnt.get(sec, 0) + 1
        return res
    rra, rrw = rr_index(ta), rr_index(tw)
    by_hunk_a, by_hunk_w = {}, {}
    for hi, o, tgt in sa:
        by_hunk_a.setdefault(hi, []).append((o, tgt))
    for hi, o, tgt in sw:
        by_hunk_w.setdefault(hi, []).append((o, tgt))
    bad, total, unresolved, unres, unresolved_bad = [], 0, 0, [], []
    anchor_name = {}
    for n in la:
        c = canon(n)
        if '+' not in c and c in lw:
            anchor_name[n] = c
    anchors = index({n: la[n] for n in anchor_name})
    names_w = {}
    pending = []
    for l in open(os.path.join(C, 'work.lst'), encoding='latin1'):
        m = LOCAL_LBL.match(l.rstrip(chr(10)))
        ad = ADDR.match(l)
        if m:
            pending.append(m.group(1))
        if ad:
            for n in pending:
                names_w.setdefault((int(ad.group(1), 16), int(ad.group(2), 16)), set()).add(n)
            pending = []
    for a, b in eq:
        if a not in rra or b not in rrw:
            continue
        ha, na = rra[a]; hw, nw = rrw[b]
        oa, (tha, va) = by_hunk_a[ha][na]
        ow, (thw, vw) = by_hunk_w[hw][nw]
        sa_ = nearest(ia_, tha, va)
        sw_ = nearest(iw_, thw, vw)
        total += 1
        if not sa_ or not sw_:
            continue
        # expected target in the ported build: address of the translated label + delta
        cname = canon(sa_[0])
        base = cname.split('+')[0]
        extra = int(cname.split('+')[1]) if '+' in cname else 0
        if base not in lw:
            # fall back to the nearest preceding adv label which has a counterpart in the ported build
            an_ = nearest(anchors, tha, va)
            if an_:
                aname, adelta = an_
                exp = (lw[anchor_name[aname]][0], lw[anchor_name[aname]][1] + adelta)
                if exp == (thw, vw):
                    unresolved += 1
                    continue
            # a new Advanced label which became local in the ported source (or carries a source alias)
            here = names_w.get((thw, vw), set())
            if sa_[1] == 0 and ({'.' + sa_[0], sa_[0], '.' + cname, sa_[0] + '_Adv'} & here):
                unresolved += 1
                continue
            unresolved_bad.append((ta[a].split('|')[2], tw[b].split('|')[2], sa_, cname, an_, sw_, sorted(here)))
            continue
        exp = (lw[base][0], lw[base][1] + extra + sa_[1])
        if exp != (thw, vw):
            bad.append((ta[a].split('|')[2], tw[b].split('|')[2], sa_, cname, sw_))
    print('checked', total, 'relocations of unchanged code, mismatches:', len(bad),
          'resolved via preceding anchor:', unresolved, 'anchor mismatches:', len(unresolved_bad))
    for x in unresolved_bad[:int(os.environ.get("NUNRES", 40))]:
        print('  anchor mismatch', x)
    json.dump(bad, open(os.path.join(C, 'relcheck.json'), 'w'), indent=0)
    for x in bad[:40]:
        print(x)


if __name__ == '__main__':
    main()

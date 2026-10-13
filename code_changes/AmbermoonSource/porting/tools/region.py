"""Region rewrite for hunks which cover source lines only partially (data lines with several
values, macro invocations): replace the whole source lines by the Advanced text of the same
address range."""
import bisect, os, re
import srcmodel, symbols

W = srcmodel.W


def equal_maps():
    """base62 statement -> adv statement and back for unchanged statements (1-based)."""
    b2a, a2b = {}, {}
    hunks = []
    pa = pb = 0
    alen = len(open(os.path.join(W, 'adv.canon'), encoding='latin1').read().split('\n')) - 1
    for line in open(os.path.join(W, 'canon62.diff'), encoding='latin1'):
        h = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
        if not h:
            continue
        b1 = int(h.group(1)); bn = int(h.group(2) or 1) if h.group(2) != '0' else 0
        a1 = int(h.group(3)); an = int(h.group(4) or 1) if h.group(4) != '0' else 0
        bs = b1 - 1 if bn else b1
        as_ = a1 - 1 if an else a1
        while pa < as_:
            b2a[pb + 1] = pa + 1; a2b[pa + 1] = pb + 1; pa += 1; pb += 1
        hunks.append((bs + 1, bn, as_ + 1, an))
        pa, pb = as_ + an, bs + bn
    while pa < alen:
        b2a[pb + 1] = pa + 1; a2b[pa + 1] = pb + 1; pa += 1; pb += 1
    return b2a, a2b, hunks


class Regions:
    def __init__(self, M, m62_382):
        self.M = M
        self.b2a, self.a2b, self.hunks = equal_maps()
        self.ib = [int(x) for x in open(os.path.join(W, 'base', '62823505.idx'))]
        self.ia = [int(x) for x in open(os.path.join(W, 'adv.idx'))]
        # base62 statement -> address (via base382 line)
        self.m62_382 = m62_382
        inv = {}
        for a, b in m62_382.items():
            inv.setdefault(b, a)
        self.m382_62 = inv
        lines62 = open(os.path.join(W, 'base', '62823505.lines'), encoding='latin1').read().split('\n')
        self.addr_first = {}       # address -> first statement (labels included)
        self.addr_first_code = {}  # address -> first statement which is not a label definition
        for k in range(1, len(self.ib) + 1):
            a = self.b_stmt_addr(k)
            if a is None:
                continue
            self.addr_first.setdefault(a, k)
            if not lines62[k - 1].endswith(':'):
                self.addr_first_code.setdefault(a, k)

    def b_stmt_addr(self, k):
        l382 = self.m62_382.get(self.ib[k - 1])
        return self.M.b_addr(l382) if l382 else None

    def next_src_addr(self, f, ln):
        """Address of the first byte behind source line ln of file f (start of the next emitting line)."""
        sec, off = self.M.s_emit[(f, ln)]
        o = self.M.s_offs[sec]
        i = bisect.bisect_right(o, off)
        return (sec, o[i]) if i < len(o) else None

    def adv_stmt_for_base(self, k):
        """Adv statement corresponding to base statement k (start of a hunk if k is changed)."""
        if k in self.b2a:
            return self.b2a[k]
        for bs, bn, as_, an in self.hunks:
            if bs <= k < bs + max(bn, 1):
                return as_
        return None

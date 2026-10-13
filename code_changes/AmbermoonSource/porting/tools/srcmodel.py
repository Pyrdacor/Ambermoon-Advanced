"""Address model of the AmbermoonSource 1.21 build and the 382eaeda disassembly.

src: (file, line) -> (sec, off) of the first byte the line emits; label definitions per address.
base382: line -> (sec, off), plus the end offset (start of the next emitting line).
"""
import bisect, os, pickle, re

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABEL = re.compile(r'^([A-Za-z_.][\w.]*):?(?=\s|$|:)')


class Model:
    def __init__(self):
        blst, slst = pickle.load(open(os.path.join(W, 'lst.pkl'), 'rb'))
        # base382: ordered emitting lines
        self.b_emit = {}
        for f, ln, sec, off in blst:
            self.b_emit.setdefault(ln, (sec, off))
        self.b_lines = sorted(self.b_emit)
        # src: per file ordered emitting lines, and global offset index
        self.s_emit = {}
        for f, ln, sec, off in slst:
            self.s_emit.setdefault((f, ln), (sec, off))
        self.s_by_file = {}
        for (f, ln), v in self.s_emit.items():
            self.s_by_file.setdefault(f, []).append(ln)
        for v in self.s_by_file.values():
            v.sort()
        self.s_by_addr = {}
        for (f, ln), (sec, off) in self.s_emit.items():
            self.s_by_addr.setdefault(sec, []).append((off, f, ln))
        for v in self.s_by_addr.values():
            v.sort()
        self.s_offs = {s: [x[0] for x in v] for s, v in self.s_by_addr.items()}
        self.src_dir = os.path.join(W, 'src121', 'AmbermoonSource', 'src')
        self._files = {}

    def src_lines(self, f):
        if f not in self._files:
            self._files[f] = open(os.path.join(self.src_dir, f), encoding='latin1').read().split('\n')
        return self._files[f]

    # ---- base382 ----
    def b_addr(self, ln):
        """Address of base382 line ln (the next emitting line if ln emits nothing)."""
        i = bisect.bisect_left(self.b_lines, ln)
        return self.b_emit[self.b_lines[i]] if i < len(self.b_lines) else None

    def b_end(self, ln):
        """Address just behind base382 line ln (start of the next emitting line after ln)."""
        i = bisect.bisect_right(self.b_lines, ln)
        return self.b_emit[self.b_lines[i]] if i < len(self.b_lines) else None

    # ---- source ----
    def s_at(self, sec, off):
        """All source lines that start emitting exactly at sec:off."""
        v = self.s_by_addr.get(sec, [])
        i = bisect.bisect_left(self.s_offs[sec], off)
        res = []
        while i < len(v) and v[i][0] == off:
            res.append((v[i][1], v[i][2])); i += 1
        return res

    def s_covering(self, sec, start, end):
        """Source lines emitting in [start, end). Returns (lines, exact) where exact means the
        range starts and ends on line boundaries."""
        v = self.s_by_addr.get(sec, [])
        o = self.s_offs[sec]
        i = bisect.bisect_left(o, start)
        exact_start = i < len(v) and o[i] == start
        j = bisect.bisect_left(o, end)
        exact_end = j >= len(v) or o[j] == end
        if not exact_start and i > 0:
            i -= 1
        return [(v[k][1], v[k][2]) for k in range(i, j)], exact_start and exact_end


def load():
    return Model()

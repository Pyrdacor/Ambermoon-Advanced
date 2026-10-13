"""Build the porting plan: for every hunk of canon62.diff find the target location in the
current AmbermoonSource (HEAD of the Ambermoon repo).

Chain: base 62823505 line -> base 382eaeda line (diff) -> section/offset (listing)
       -> AmbermoonSource 1.21 file/line (listing) -> AmbermoonSource HEAD file/line (diff per file)
"""
import bisect, json, os, pickle, re, subprocess, sys

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AMB = r'C:\Users\Robert\source\repos\Ambermoon'


def git_diff_linemap(a_lines, b_lines):
    """Map line numbers of a to b (1-based) for unchanged lines; changed lines map to the next mapped line."""
    import tempfile
    d = tempfile.mkdtemp()
    fa, fb = os.path.join(d, 'a'), os.path.join(d, 'b')
    open(fa, 'w', encoding='latin1').write('\n'.join(a_lines) + '\n')
    open(fb, 'w', encoding='latin1').write('\n'.join(b_lines) + '\n')
    r = subprocess.run(['git', 'diff', '--no-index', '--histogram', '-U0', fa, fb],
                       capture_output=True, text=True, encoding='latin1')
    m = {}
    pa = pb = 1
    for line in r.stdout.split('\n'):
        h = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
        if not h:
            continue
        a1, an = int(h.group(1)), int(h.group(2) or 1) if h.group(2) != '0' else 0
        b1, bn = int(h.group(3)), int(h.group(4) or 1) if h.group(4) != '0' else 0
        a_start = a1 if an else a1 + 1
        b_start = b1 if bn else b1 + 1
        while pa < a_start:
            m[pa] = pb; pa += 1; pb += 1
        for k in range(an):
            # changed line: map positionally into the replacement (same size: line by line)
            m[pa + k] = b_start + min(k, max(bn - 1, 0))
        pa = a_start + an
        pb = b_start + bn
    while pa <= len(a_lines):
        m[pa] = pb; pa += 1; pb += 1
    return m


def main():
    base62 = open(os.path.join(W, 'base', '62823505.s'), encoding='latin1').read().split('\n')
    base382 = open(os.path.join(W, 'base', '382eaeda.s'), encoding='latin1').read().split('\n')
    m62_382 = git_diff_linemap(base62, base382)
    blst, slst = pickle.load(open(os.path.join(W, 'lst.pkl'), 'rb'))
    # base382 line -> (sec, off); for non-emitting lines use the next emitting line
    emit = {}
    for f, ln, sec, off in blst:
        emit.setdefault(ln, (sec, off))
    lines_sorted = sorted(emit)
    def addr_of(ln382):
        i = bisect.bisect_left(lines_sorted, ln382)
        if i >= len(lines_sorted):
            return None
        return emit[lines_sorted[i]]
    # source: (sec, off) -> list of (file, line), sorted by offset per section
    per_sec = {}
    for f, ln, sec, off in slst:
        per_sec.setdefault(sec, []).append((off, f, ln))
    for v in per_sec.values():
        v.sort()
    offs = {s: [x[0] for x in v] for s, v in per_sec.items()}
    def src_of(sec, off):
        v = per_sec.get(sec)
        if not v:
            return None
        i = bisect.bisect_right(offs[sec], off) - 1
        if i < 0:
            return None
        o, f, ln = v[i]
        return f, ln, off - o   # delta > 0: inside a multi-byte line (data or macro)
    # AmbermoonSource 1.21 file -> HEAD file line maps
    src121 = os.path.join(W, 'src121', 'AmbermoonSource', 'src')
    head_maps = {}
    def head_line(f, ln):
        if f not in head_maps:
            old = open(os.path.join(src121, f), encoding='latin1').read().split('\n')
            newp = os.path.join(AMB, 'AmbermoonSource', 'src', f)
            new = open(newp, encoding='latin1').read().split('\n') if os.path.exists(newp) else []
            head_maps[f] = git_diff_linemap(old, new)
        return head_maps[f].get(ln)
    ib = [int(x) for x in open(os.path.join(W, 'base', '62823505.idx'))]
    ia = [int(x) for x in open(os.path.join(W, 'adv.idx'))]
    hunks = []
    cur = None
    for line in open(os.path.join(W, 'canon62.diff'), encoding='latin1'):
        h = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
        if h:
            b1 = int(h.group(1)); bn = int(h.group(2) or 1) if h.group(2) != '0' else 0
            a1 = int(h.group(3)); an = int(h.group(4) or 1) if h.group(4) != '0' else 0
            cur = {'b1': b1, 'bn': bn, 'a1': a1, 'an': an, 'minus': [], 'plus': []}
            hunks.append(cur)
        elif cur is not None and line[:1] in '+-' and not line.startswith(('+++', '---')):
            (cur['minus'] if line[0] == '-' else cur['plus']).append(line[1:].rstrip('\n'))
    for h in hunks:
        # base source lines (62823505) of the hunk; for pure insertions the line after the insertion point
        if h['bn']:
            first, last = ib[h['b1'] - 1], ib[h['b1'] + h['bn'] - 2]
        else:
            first = ib[h['b1']] if h['b1'] < len(ib) else ib[-1]
            last = first - 1
        h['base_lines'] = [first, last]
        h['adv_lines'] = [ia[h['a1'] - 1], ia[h['a1'] + h['an'] - 2]] if h['an'] else [ia[h['a1'] - 1] + 1, ia[h['a1'] - 1]]
        l382 = m62_382.get(first)
        a = addr_of(l382) if l382 else None
        h['addr'] = a
        if a:
            s = src_of(*a)
            if s:
                f, ln, delta = s
                h['src121'] = [f, ln, delta]
                h['target'] = [f, head_line(f, ln), delta]
    json.dump(hunks, open(os.path.join(W, 'plan.json'), 'w'), indent=0)
    ok = sum(1 for h in hunks if h.get('target') and h['target'][1])
    inside = sum(1 for h in hunks if h.get('target') and h['target'][2])
    print(len(hunks), 'hunks,', ok, 'with target,', inside, 'inside a multi-byte line')


if __name__ == '__main__':
    main()

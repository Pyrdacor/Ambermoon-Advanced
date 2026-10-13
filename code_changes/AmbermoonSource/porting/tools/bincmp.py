"""Compare two Amiga hunk executables instruction by instruction.

Instruction boundaries come from the vasm listings. Relocated longwords and branch
displacements are masked, so layout changes do not count as differences.

usage: bincmp.py <exe A> <listing A> <exe B> <listing B> <out prefix>
Writes <out>.A.tok, <out>.B.tok (one token per line: sec|tokens|origin) and prints a summary.
"""
import os, re, struct, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lstmap

HUNK_CODE, HUNK_DATA, HUNK_BSS, HUNK_RELOC32, HUNK_END, HUNK_HEADER = 0x3E9, 0x3EA, 0x3EB, 0x3EC, 0x3F2, 0x3F3


def read_hunks(path):
    d = open(path, 'rb').read()
    p = 0
    def L():
        nonlocal p
        v = struct.unpack('>I', d[p:p + 4])[0]; p += 4; return v
    assert L() == HUNK_HEADER
    while L():
        pass
    count = L(); first = L(); last = L()
    for _ in range(last - first + 1):
        L()
    hunks = []
    cur = None
    while p < len(d):
        t = L() & 0x3FFFFFFF
        if t in (HUNK_CODE, HUNK_DATA):
            n = L() * 4
            cur = {'type': t, 'data': d[p:p + n], 'relocs': set()}
            p += n
            hunks.append(cur)
        elif t == HUNK_BSS:
            n = L() * 4
            cur = {'type': t, 'data': b'', 'size': n, 'relocs': set()}
            hunks.append(cur)
        elif t == HUNK_RELOC32:
            while True:
                n = L()
                if not n:
                    break
                L()  # target hunk
                for _ in range(n):
                    cur['relocs'].add(L())
        elif t == HUNK_END:
            pass
        else:
            raise ValueError('unknown hunk type %x at %d' % (t, p))
    return hunks


ADDR = re.compile(r'^([0-9A-F]{2}):([0-9A-F]{8}) ')


def tokens(hunks, listing):
    entries = lstmap.parse(listing)
    starts = {}
    origin = {}
    for f, ln, sec, off in entries:
        starts.setdefault(sec, set()).add(off)
        origin.setdefault((sec, off), (f, ln))
    # every address line of the listing is a boundary (macro expansions, data continuation lines)
    for l in open(listing, encoding='latin1'):
        m = ADDR.match(l)
        if m:
            starts.setdefault(int(m.group(1), 16), set()).add(int(m.group(2), 16))
    out = []
    for sec, h in enumerate(hunks):
        if h['type'] == HUNK_BSS or not h['data']:
            continue
        data = h['data']
        offs = sorted(o for o in starts.get(sec, ()) if o < len(data))
        if not offs or offs[0] != 0:
            offs = [0] + offs
        code = h['type'] == HUNK_CODE
        relocs = sorted(h['relocs'])
        for i, o in enumerate(offs):
            e = offs[i + 1] if i + 1 < len(offs) else len(data)
            b = data[o:e]
            tok = None
            if code and len(b) >= 2:
                w = (b[0] << 8) | b[1]
                if (w & 0xF000) == 0x6000:          # Bcc/BRA/BSR: keep only the condition
                    tok = 'B%02x' % (w >> 8)
                elif (w & 0xF0F8) == 0x50C8:        # DBcc: mask the displacement
                    tok = b[:2].hex() + 'DDDD'
            f, ln = origin.get((sec, o), ('?', 0))
            if tok is not None:
                out.append('%d|%s|%s:%d' % (sec, tok, f, ln))
                continue
            # byte tokens, relocated longwords as one token
            k = 0
            while k < len(b):
                if (o + k) in h['relocs']:
                    out.append('%d|RRRR|%s:%d' % (sec, f, ln)); k += 4
                else:
                    out.append('%d|%02x|%s:%d' % (sec, b[k], f, ln)); k += 1
    return out


def main():
    ea, la, eb, lb, out = sys.argv[1:6]
    ta = tokens(read_hunks(ea), la)
    tb = tokens(read_hunks(eb), lb)
    open(out + '.A.tok', 'w', encoding='latin1').write('\n'.join(ta) + '\n')
    open(out + '.B.tok', 'w', encoding='latin1').write('\n'.join(tb) + '\n')
    # token text without origin for the diff
    open(out + '.A.cmp', 'w').write('\n'.join(t.rsplit('|', 1)[0] for t in ta) + '\n')
    open(out + '.B.cmp', 'w').write('\n'.join(t.rsplit('|', 1)[0] for t in tb) + '\n')
    r = subprocess.run(['git', 'diff', '--no-index', '--histogram', '-U0', out + '.A.cmp', out + '.B.cmp'],
                       capture_output=True, text=True)
    open(out + '.diff', 'w').write(r.stdout)
    hunks = sum(1 for l in r.stdout.split('\n') if l.startswith('@@'))
    lines = sum(1 for l in r.stdout.split('\n') if l[:1] in '+-' and not l.startswith(('+++', '---')))
    print('%s: %d tokens vs %d, %d diff hunks, %d changed tokens' % (os.path.basename(out), len(ta), len(tb), hunks, lines))


if __name__ == '__main__':
    main()

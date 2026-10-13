"""Build the AmbermoonSource copy; widen short branches which are out of range and retry.

usage: build.py <src dir> <output binary> [--no-widen]
"""
import os, re, subprocess, sys

VASM = r'C:\Users\Robert\source\repos\Ambermoon-Advanced\code_changes\vasmm68k_mot.exe'
ERR = re.compile(r'^error (\d+) in line (\d+) of "([^"]+)": (.*)$')


def build(src, out):
    r = subprocess.run([VASM, '-m68030', '-Fhunkexe', '-o', out, '-nosym', '-kick1hunks', '-keepempty',
                        '-no-opt', '-align', '-maxerrors=0', 'AMBERMOON.S'],
                       cwd=src, capture_output=True, text=True, encoding='latin1')
    errors = []
    for line in (r.stdout + r.stderr).split('\n'):
        m = ERR.match(line)
        if m:
            errors.append((int(m.group(1)), m.group(3).replace(chr(92), '/'), int(m.group(2)), m.group(4)))
    return r.returncode, errors, r.stdout + r.stderr


def widen(src, errors):
    by_file = {}
    for code, f, ln, msg in errors:
        if code == 2029:
            by_file.setdefault(f, set()).add(ln)
    n = 0
    for f, lns in by_file.items():
        p = os.path.join(src, f)
        raw = open(p, 'rb').read()
        nl = b'\r\n' if b'\r\n' in raw else b'\n'
        lines = raw.split(nl)
        for ln in lns:
            s = lines[ln - 1].decode('latin1')
            t = re.sub(r'(\b(?:b(?:ra|sr|eq|ne|cc|cs|hi|ls|pl|mi|ge|gt|le|lt|vc|vs|hs|lo)))\.[sb]\b', r'\1.w', s, count=1, flags=re.I)
            if t == s:
                # no size given: add .w
                t = re.sub(r'(\b(?:b(?:ra|sr|eq|ne|cc|cs|hi|ls|pl|mi|ge|gt|le|lt|vc|vs|hs|lo)))(\s)', r'\1.w\2', s, count=1, flags=re.I)
            if t != s:
                lines[ln - 1] = t.encode('latin1'); n += 1
        open(p, 'wb').write(nl.join(lines))
    return n


def main():
    src, out = sys.argv[1], sys.argv[2]
    for it in range(30):
        rc, errors, text = build(src, out)
        if rc == 0 and not errors:
            print('build ok after %d widening rounds' % it)
            return 0
        if '--no-widen' in sys.argv or not any(e[0] == 2029 for e in errors):
            break
        print('round %d: widened %d branches' % (it, widen(src, errors)))
    for e in errors[:60]:
        print('error %d %s:%d %s' % e)
    print(len(errors), 'errors')
    return 1


if __name__ == '__main__':
    sys.exit(main())

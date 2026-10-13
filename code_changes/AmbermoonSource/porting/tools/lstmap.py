"""Parse a vasm listing: list of (file, line, section, offset) for lines that emit code or data.

Macro expansion lines ("12M") are attributed to the source line which invoked the macro,
repetition lines ("1R") to the line with the rept directive.
"""
import re

LINE = re.compile(r'^(?:([0-9A-F]{2}):([0-9A-F]{8}) \S*)?\s*\t\s*(\d+)([:MR])(.*)$')
SOURCE = re.compile(r'^Source: "(.*)"')
REPT = re.compile(r'^\s+rept\b', re.I)


def parse(path):
    res = []
    cur = None
    last = None          # (file, line) of the last normal source line
    last_has_addr = False
    rept = None          # [(file, line), has_addr] of the last rept directive
    for l in open(path, encoding='latin1'):
        m = SOURCE.match(l)
        if m:
            cur = m.group(1).replace(chr(92), '/')
            continue
        m = LINE.match(l.rstrip('\n'))
        if not m:
            continue
        kind = m.group(4)
        if kind == ':':
            last = (cur, int(m.group(3)))
            last_has_addr = m.group(1) is not None
            if REPT.match(m.group(5)):
                rept = [last, False]
            if m.group(1) is not None:
                res.append((cur, int(m.group(3)), int(m.group(1), 16), int(m.group(2), 16)))
        elif m.group(1) is None:
            continue
        elif kind == 'R' and rept is not None:
            if not rept[1]:
                res.append((rept[0][0], rept[0][1], int(m.group(1), 16), int(m.group(2), 16)))
                rept[1] = True
        elif last is not None and not last_has_addr:
            # first emitting line of a macro expansion: address of the invoking line
            res.append((last[0], last[1], int(m.group(1), 16), int(m.group(2), 16)))
            last_has_addr = True
    return res

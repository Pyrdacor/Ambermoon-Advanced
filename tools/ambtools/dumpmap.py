"""Print a readable dump of a map's event chains, characters and layout.

Usage: python dumpmap.py <map index> [--data <Amberfiles dir>] [--chains 1,2,3] [--layout]
"""
import argparse
import os

import ambcontainer as amb
import mapmodel as mm

DEFAULT_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'german', 'Amberfiles')
CHAR_TYPES = ('PartyMember', 'NPC', 'Monster', 'Object')


def load_map(data, index):
    for n in (1, 2, 3):
        raw = amb.read_container(os.path.join(data, f'{n}Map_data.amb')).get(index)
        if raw:
            return mm.parse(raw)
    raise SystemExit(f'Map {index} not found')


def layout(m):
    lines = ['    ' + ''.join('%-3d' % x for x in range(1, m.w + 1))]
    for y in range(1, m.h + 1):
        row = ''
        for x in range(1, m.w + 1):
            i = ((y - 1) * m.w + (x - 1)) * (2 if m.type == 1 else 4)
            b, ev = m.tiles[i], m.tiles[i + 1]
            if m.type == 1:
                cell = '##' if 100 < b < 255 else ('XX' if b == 255 else ('  ' if b == 0 else 'o%d' % b if b < 10 else '%2d' % b))
            else:
                cell = '%02x' % b
            row += (cell if not ev else cell[0] + '*') + ' '
        lines.append('%3d ' % y + row)
    return '\n'.join(lines) + '\n(## wall, oN object, * tile has an event chain)'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('map', type=int)
    ap.add_argument('--data', default=DEFAULT_DATA)
    ap.add_argument('--chains', default='')
    ap.add_argument('--layout', action='store_true')
    args = ap.parse_args()
    m = load_map(args.data, args.map)
    print(f'Map {args.map}: {"3D" if m.type == 1 else "2D"} {m.w}x{m.h}, flags {m.flags:#06x}, '
          f'{len(m.heads)} chains, {len(m.events)} events')
    for i, c in enumerate(m.chars):
        if c[0]:
            pos = m.positions[i][:2]
            print(f'  char {i}: {CHAR_TYPES[c[2] & 3]} index {c[0]} flags {c[2] >> 2:#04x} '
                  f'event chain {c[3]} gfx {int.from_bytes(c[4:6], "big")} start ({pos[0]},{pos[1]})')
    for g in m.gotos:
        print(f'  goto ({g[0]},{g[1]}) idx {g[3]} {g[4:].split(b"\0")[0].decode("latin1")}')
    if args.layout:
        print(layout(m))
    chains = set(int(c) for c in args.chains.split(',') if c)
    text, orphans = mm.dump(m, chains or None)
    print(text)
    if orphans and not chains:
        print('Events not reachable from any chain:', orphans)


if __name__ == '__main__':
    main()

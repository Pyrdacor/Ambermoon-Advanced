"""Make the sandstone temple walls from textures/Pixel-Art-Sandsteinwand mit Tempelfriesen.png.

- 193 frieze wall with two lotus columns (the picture)
- 194 frieze wall without columns (middle section repeated, separated by a joint)
- 195 gateway: dark passage between the columns, through the lower frieze down to the floor

Writes textures/generated/sandstone_<n>.tex (Texture4Bit 128x80), preview PNGs and wuestentempel.pal
(palette 60: stone colours 1-6/12/13 matched to the picture, the rest like palette 6).
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools', 'ambtools'))
import ambcontainer as amb  # noqa: E402
import textures as tx  # noqa: E402

DATA = os.path.join(HERE, '..', '..', '..', 'german', 'Amberfiles')
SRC = os.path.join(HERE, '..', 'textures', 'Pixel-Art-Sandsteinwand mit Tempelfriesen.png')
OUT = os.path.join(HERE, '..', 'textures', 'generated')
STONE = {1: 'eb7', 2: 'd94', 3: 'b73', 4: '863', 5: '642', 6: '421', 12: 'c84', 13: 'a63'}

WALL_TOP, WALL_BOTTOM = 11, 68          # rows between the friezes
MID = (36, 91)                          # stone section between the columns
JOINT_X = 35                            # column frame edge, used as a vertical joint


def palette():
    pal = tx.decode_palette(amb.read_container(os.path.join(DATA, 'Palettes.amb'))[6])
    for i, hx in STONE.items():
        pal[i] = tuple(int(c, 16) * 17 for c in hx)
    return pal


def pal_bytes(pal):
    return b''.join(struct.pack('>H', (r // 17) << 8 | (g // 17) << 4 | (b // 17)) for r, g, b in pal)


def plain(cols):
    rows = [list(r) for r in cols]
    a, b = MID
    seg = list(range(a, b + 1))
    xs = (seg + [JOINT_X]) * 3
    for y in range(WALL_TOP, WALL_BOTTOM + 1):
        src = cols[y]
        rows[y] = [src[x] for x in xs[:128]]
    return rows


def gateway(cols):
    rows = [list(r) for r in cols]
    x0, x1, top = 44, 83, 22
    for y in range(top - 3, 80):
        for x in range(x0 - 3, x1 + 4):
            edge = x < x0 or x > x1 or y < top
            if y < top - 1 and (x0 - 3 <= x <= x1 + 3):
                rows[y][x] = 5 if y == top - 3 else 4            # lintel
            elif edge:
                rows[y][x] = 6 if (x in (x0 - 1, x1 + 1) or y == top - 1) else 3   # frame
            else:
                # dark passage, a little lighter towards the floor
                rows[y][x] = 0 if y < 66 else 6
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    pal = palette()
    w, h, src = tx.read_png(SRC)
    idx = tx.quantize(tx.downscale(src, 128, 80), pal, [1, 2, 3, 4, 5, 6, 12, 13])
    walls = {193: idx, 194: plain(idx), 195: gateway(idx)}
    for n, rows in walls.items():
        open(os.path.join(OUT, f'sandstone_{n}.tex'), 'wb').write(tx.encode_texture(rows, 128))
        tx.write_png(os.path.join(OUT, f'sandstone_{n}_x4.png'), rows, pal, 4)
    open(os.path.join(OUT, 'wuestentempel.pal'), 'wb').write(pal_bytes(pal))
    print('written', ', '.join(str(n) for n in walls))


if __name__ == '__main__':
    main()

"""Make the sandstone temple walls from textures/Pixelart-Sandsteinmauer mit ägyptischen Säulen.png
(or the picture given in the environment variable SANDSTONE_SRC).

- 193 frieze wall with two lotus columns (the picture)
- 194 frieze wall without columns (middle section repeated, courses staggered)
- 195 gateway: dark passage between the columns, through the lower frieze down to the floor

Usage: python make_sandstone_walls.py [sharpen contrast [out dir [threshold]]]

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
SRC = os.path.join(HERE, '..', 'textures', os.environ.get('SANDSTONE_SRC', 'Pixelart-Sandsteinmauer mit ägyptischen Säulen.png'))
OUT = os.path.join(HERE, '..', 'textures', 'generated')
STONE = {1: 'eb7', 2: 'd94', 3: 'b73', 4: '863', 5: '642', 6: '421', 12: 'c84', 13: 'a63'}

WALL_TOP, WALL_BOTTOM = 11, 68          # rows between the friezes
SHARPEN, CONTRAST, THRESHOLD = 1.0, 1.05, 8   # see sharpen()
MID = (37, 88)                          # stone section between the columns (joint at 36)


def sharpen(img, amount=1.5, contrast=1.15, threshold=THRESHOLD):
    """Unsharp mask (3x3) plus a contrast stretch around the mean brightness, so joints and stone edges
    survive the downscaling. Only details stronger than the threshold (brightness) are amplified; everything
    else is smoothed, so the speckles on the stone surfaces don't turn into noise."""
    h, w = len(img), len(img[0])
    out = []
    mean = [sum(p[k] for row in img for p in row) / (w * h) for k in range(3)]
    for y in range(h):
        row = []
        for x in range(w):
            acc = [0.0, 0.0, 0.0]
            n = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = min(h - 1, max(0, y + dy)), min(w - 1, max(0, x + dx))
                    for k in range(3):
                        acc[k] += img[yy][xx][k]
                    n += 1
            p = []
            detail = [img[y][x][k] - acc[k] / n for k in range(3)]
            strong = abs(0.3 * detail[0] + 0.59 * detail[1] + 0.11 * detail[2]) >= threshold
            for k in range(3):
                # edges are amplified, surfaces smoothed (3x3 average) so they quantize to calm areas
                v = img[y][x][k] + amount * detail[k] if strong else acc[k] / n
                v = mean[k] + (v - mean[k]) * contrast
                p.append(max(0.0, min(255.0, v)))
            row.append(tuple(p))
        out.append(row)
    return out


def palette():
    pal = tx.decode_palette(amb.read_container(os.path.join(DATA, 'Palettes.amb'))[6])
    for i, hx in STONE.items():
        pal[i] = tuple(int(c, 16) * 17 for c in hx)
    return pal


def pal_bytes(pal):
    return b''.join(struct.pack('>H', (r // 17) << 8 | (g // 17) << 4 | (b // 17)) for r, g, b in pal)


def plain(cols):
    """The stone section between the columns (with its left joint) is repeated over the whole width. Each
    course (found by its horizontal joints) gets its own offset, so the vertical joints are staggered like
    in real masonry instead of running through the whole height."""
    rows = [list(r) for r in cols]
    seq = [MID[0] - 1] + list(range(MID[0], MID[1] + 1))       # joint + stone section
    period = len(seq)
    dark = (5, 6)
    joints = [y for y in range(WALL_TOP, WALL_BOTTOM + 1)
              if sum(cols[y][x] in dark for x in seq) > 0.6 * period]
    course, last = 0, None
    for y in range(WALL_TOP, WALL_BOTTOM + 1):
        if y in joints:
            if last is not None and y != last + 1:
                course += 1
            last = y
        phase = (course * 23) % period
        rows[y] = [cols[y][seq[(x + phase) % period]] for x in range(128)]
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
    out = sys.argv[3] if len(sys.argv) > 3 else OUT
    os.makedirs(out, exist_ok=True)
    pal = palette()
    w, h, src = tx.read_png(SRC)
    amount = float(sys.argv[1]) if len(sys.argv) > 1 else SHARPEN
    contrast = float(sys.argv[2]) if len(sys.argv) > 2 else CONTRAST
    threshold = float(sys.argv[4]) if len(sys.argv) > 4 else THRESHOLD
    idx = tx.quantize(sharpen(tx.downscale(src, 128, 80), amount, contrast, threshold), pal, [1, 2, 3, 4, 5, 6, 12, 13])
    walls = {193: idx, 194: plain(idx), 195: gateway(idx)}
    for n, rows in walls.items():
        open(os.path.join(out, f'sandstone_{n}.tex'), 'wb').write(tx.encode_texture(rows, 128))
        tx.write_png(os.path.join(out, f'sandstone_{n}_x4.png'), rows, pal, 4)
    open(os.path.join(out, 'wuestentempel.pal'), 'wb').write(pal_bytes(pal))
    print('written', ', '.join(str(n) for n in walls), 'sharpen', amount, 'contrast', contrast)


if __name__ == '__main__':
    main()

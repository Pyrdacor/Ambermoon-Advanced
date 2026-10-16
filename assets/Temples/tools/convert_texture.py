"""Convert a true colour picture (16:10) into a 128x80 wall texture with 16 colours.

- area average down to 128x80
- palette: an existing one (e.g. 59) or one derived from the picture: the stone colours 1-6 and 12/13 are
  taken from the picture (k-means, sorted by brightness), the rest (0, 7-11 wood/gold, 14/15 red) stays
- quantize to the allowed colour indices, optionally with Floyd-Steinberg dithering

Usage: python convert_texture.py <picture.png> <out prefix> [--palette 59] [--derive] [--colors 1=fc8,...] [--allowed 1-6,12-13] [--dither 0.4]
Writes <prefix>.png (preview 128x80), <prefix>_x4.png, <prefix>.tex (Texture4Bit) and with --derive <prefix>.pal.
"""
import argparse
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools', 'ambtools'))
import ambcontainer as amb  # noqa: E402
import textures as tx  # noqa: E402

DATA = os.path.join(HERE, '..', '..', '..', 'german', 'Amberfiles')
STONE = [1, 2, 3, 4, 5, 6, 12, 13]


def to12(c):
    return tuple(max(0, min(15, round(v / 17))) * 17 for v in c)


def kmeans(pixels, k, rounds=20, seed=1):
    rnd = random.Random(seed)
    centers = rnd.sample(pixels, k)
    for _ in range(rounds):
        groups = [[] for _ in range(k)]
        for p in pixels:
            i = min(range(k), key=lambda j: sum((p[t] - centers[j][t]) ** 2 for t in range(3)))
            groups[i].append(p)
        centers = [tuple(sum(p[t] for p in g) / len(g) for t in range(3)) if g else centers[i]
                   for i, g in enumerate(groups)]
    return centers


def lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


# brightness quantiles of the picture for the stone colours: highlight, light, base (12), base, shade (13),
# shadow, joint, deep joint
QUANTILES = {1: 0.995, 2: 0.93, 12: 0.7, 3: 0.45, 13: 0.22, 4: 0.09, 5: 0.03, 6: 0.005}


def derive_palette(base, img):
    """Stone colours 1-6 and 12/13 from brightness quantiles of the picture, all distinct in 12 bit."""
    pixels = sorted((p for row in img for p in row), key=lum)
    n = len(pixels)
    pal = list(base)
    used = set()
    for i, q in sorted(QUANTILES.items(), key=lambda t: -t[1]):
        k = int(q * (n - 1))
        lo, hi = max(0, k - n // 40), min(n, k + n // 40 + 1)
        avg = tuple(sum(p[t] for p in pixels[lo:hi]) / (hi - lo) for t in range(3))
        c = to12(avg)
        while c in used:                    # keep the colours distinct: nudge darker
            c = tuple(max(0, v - 17) for v in c)
        used.add(c)
        pal[i] = c
    return pal


def pal_bytes(pal):
    return b''.join(struct.pack('>H', (r // 17) << 8 | (g // 17) << 4 | (b // 17)) for r, g, b in pal)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('picture')
    ap.add_argument('out')
    ap.add_argument('--palette', type=int, default=59)
    ap.add_argument('--derive', action='store_true')
    ap.add_argument('--allowed', default='1-15')
    ap.add_argument('--dither', type=float, default=0.0)
    ap.add_argument('--colors', default='', help='override colours, e.g. "1=fc8,2=eb6"')
    a = ap.parse_args()
    w, h, rows = tx.read_png(a.picture)
    small = tx.downscale(rows, 128, 80)
    base = tx.decode_palette(amb.read_container(os.path.join(DATA, 'Palettes.amb'))[a.palette])
    pal = derive_palette(base, small) if a.derive else list(base)
    for item in filter(None, a.colors.split(',')):
        i, _, hx = item.partition('=')
        pal[int(i)] = tuple(int(c, 16) * 17 for c in hx)
    allowed = []
    for part in a.allowed.split(','):
        lo, _, hi = part.partition('-')
        allowed += list(range(int(lo), int(hi or lo) + 1))
    idx = tx.quantize(small, pal, allowed, a.dither)
    tx.write_png(a.out + '.png', idx, pal)
    tx.write_png(a.out + '_x4.png', idx, pal, 4)
    open(a.out + '.tex', 'wb').write(tx.encode_texture(idx, 128))
    if a.derive or a.colors:
        open(a.out + '.pal', 'wb').write(pal_bytes(pal))
        print('palette:', ' '.join('%x%x%x' % (r // 17, g // 17, b // 17) for r, g, b in pal[:16]))
    print('written', a.out)


if __name__ == '__main__':
    main()

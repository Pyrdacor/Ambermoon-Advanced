"""Render the 3D textures (walls, objects, overlays, floors) and labdata as PNG contact sheets.

Usage: python render3d.py <output dir> [--palette N] [--data <Amberfiles dir>] [--labdata 2:35 ...]

- walls.png, objects.png, overlays.png, floors.png: all textures with their index, drawn with the
  given palette (default 12, used by the council temples).
- labdata_<world>_<index>.png: the walls of a labdata with their overlays and the objects.
- palettes.png: all palettes (32 colours each, the 3D colours are 0-15).

No dependencies (PNG is written with zlib).
"""
import argparse
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ambcontainer as amb  # noqa: E402
import labdata as ld  # noqa: E402

DEFAULT_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'german', 'Amberfiles')
FALLBACK_DATA = r'C:\Users\Robert\source\repos\Ambermoon\Disks\Bugfixing\German\Amberfiles'

# 3x5 digit font
FONT = {
    '0': '111101101101111', '1': '010110010010111', '2': '111001111100111', '3': '111001111001111',
    '4': '101101111001001', '5': '111100111001111', '6': '111100111101111', '7': '111001001001001',
    '8': '111101111101111', '9': '111101111001111', ':': '000010000010000', '-': '000000111000000',
}


def write_png(path, w, h, rgb):
    raw = b''.join(b'\0' + bytes(rgb[y * w * 3:(y + 1) * w * 3]) for y in range(h))

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    open(path, 'wb').write(png)


class Canvas:
    def __init__(self, w, h, bg=(40, 40, 48)):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def text(self, x, y, s, c=(255, 255, 0), scale=2):
        for ch in s:
            g = FONT.get(ch)
            if g:
                for k, bit in enumerate(g):
                    if bit == '1':
                        for sy in range(scale):
                            for sx in range(scale):
                                self.put(x + (k % 3) * scale + sx, y + (k // 3) * scale + sy, c)
            x += 4 * scale

    def blit(self, x0, y0, img, w, h, pal, transparent=True, scale=1):
        for y in range(h):
            for x in range(w):
                v = img[y * w + x]
                if transparent and v == 0:
                    continue
                for sy in range(scale):
                    for sx in range(scale):
                        self.put(x0 + x * scale + sx, y0 + y * scale + sy, pal[v])

    def save(self, path):
        write_png(path, self.w, self.h, self.px)


def texture4(data, w, h):
    """Texture4Bit: per 8 pixels one byte per plane (4 planes)."""
    out = bytearray(w * h)
    chunks = (w + 7) // 8
    o = 0
    for y in range(h):
        for n in range(chunks):
            planes = data[o:o + 4]
            o += 4
            for x in range(8):
                mx = n * 8 + x
                if mx >= w or len(planes) < 4:
                    continue
                v = 0
                for p in range(4):
                    if planes[p] & (0x80 >> x):
                        v |= 1 << p
                out[y * w + mx] = v
    return out


def planar4(data, w, h):
    """Palette4Bit: per row 4 planes of w/8 bytes."""
    out = bytearray(w * h)
    bpr = (w + 7) // 8
    o = 0
    for y in range(h):
        for x in range(w):
            v = 0
            for p in range(4):
                b = data[o + p * bpr + x // 8] if o + p * bpr + x // 8 < len(data) else 0
                if b & (0x80 >> (x % 8)):
                    v |= 1 << p
            out[y * w + x] = v
        o += 4 * bpr
    return out


def load(data, name):
    for d in (data, FALLBACK_DATA):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return amb.read_container(p)
    return {}


def merged(data, kind):
    """2<kind>.amb, completed by 3<kind>.amb (like the remake)."""
    files = dict(load(data, '2' + kind))
    for k, v in load(data, '3' + kind).items():
        if k not in files or not files[k]:
            files[k] = v
    return files


def palettes(data):
    res = {}
    for k, raw in load(data, 'Palettes.amb').items():
        cols = []
        for i in range(32):
            c = struct.unpack('>H', raw[i * 2:i * 2 + 2])[0] if len(raw) >= i * 2 + 2 else 0
            cols.append((((c >> 8) & 15) * 17, ((c >> 4) & 15) * 17, (c & 15) * 17))
        res[k] = cols
    return res


def labdatas(data):
    res = {}
    for n in (2, 3):
        for k, raw in load(data, f'{n}Lab_data.amb').items():
            if raw:
                res[(n, k)] = ld.parse(raw)
    return res


def grid(items, cell_w, cell_h, cols, draw, path, scale=1):
    rows = (len(items) + cols - 1) // cols
    cw, ch = cell_w * scale + 8, cell_h * scale + 22
    cv = Canvas(cols * cw + 8, rows * ch + 8)
    for i, it in enumerate(items):
        x, y = 8 + (i % cols) * cw, 8 + (i // cols) * ch
        draw(cv, x, y + 14, it)
        cv.text(x, y, str(it[0]))
    cv.save(path)


def paged(items, per_page, cols, pal, pattern):
    """Sprite sheets split into pages, each with a cell size fitting its items (scaled up if small)."""
    for page in range(0, len(items), per_page):
        part = items[page:page + per_page]
        mw = max(i[2] for i in part); mh = max(i[3] for i in part)
        scale = 2 if max(mw, mh) <= 64 else 1
        grid(part, mw, mh, cols, lambda cv, x, y, it: cv.blit(x, y, it[1], it[2], it[3], pal, scale=scale),
             pattern % (page // per_page + 1), scale)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--palette', type=int, default=12)
    ap.add_argument('--data', default=DEFAULT_DATA)
    ap.add_argument('--labdata', nargs='*', default=['2:35'])
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    pals = palettes(args.data)
    pal = pals[args.palette]
    labs = labdatas(args.data)

    # texture sizes from the labdata (objects and overlays have individual sizes)
    obj_size, ovl_size = {}, {}
    for lab in labs.values():
        for o in lab.objects:
            tex = struct.unpack('>H', o[4:6])[0]
            obj_size.setdefault(tex, (o[8], o[9], max(1, o[6])))
        for header, overlays in lab.walls:
            for ov in overlays:
                ovl_size.setdefault(ov[1], (ov[4], ov[5]))

    walls = merged(args.data, 'Wall3D.amb')
    items = [(k, texture4(v, 128, 80)) for k, v in sorted(walls.items()) if v]
    grid(items, 128, 80, 8, lambda cv, x, y, it: cv.blit(x, y, it[1], 128, 80, pal, False), os.path.join(args.out, 'walls.png'))

    objects = merged(args.data, 'Object3D.amb')
    items = []
    for k, v in sorted(objects.items()):
        if v and k in obj_size:
            w, h, frames = obj_size[k]
            items.append((k, texture4(v, w, h), w, h))
    paged(items, 50, 10, pal, os.path.join(args.out, 'objects_%d.png'))

    overlays = merged(args.data, 'Overlay3D.amb')
    items = []
    for k, v in sorted(overlays.items()):
        if v and k in ovl_size:
            w, h = ovl_size[k]
            items.append((k, texture4(v, w, h), w, h))
    paged(items, 60, 12, pal, os.path.join(args.out, 'overlays_%d.png'))

    floors = load(args.data, 'Floors.amb')
    items = [(k, planar4(v, 64, 64)) for k, v in sorted(floors.items()) if v]
    grid(items, 64, 64, 12, lambda cv, x, y, it: cv.blit(x, y, it[1], 64, 64, pal, False), os.path.join(args.out, 'floors.png'))

    # palettes: one row per palette, 32 colours (the 3D part 0-15 first)
    keys = sorted(pals)
    cv = Canvas(8 + 40 + 32 * 14, 8 + len(keys) * 16)
    for r, k in enumerate(keys):
        cv.text(8, 8 + r * 16 + 2, str(k))
        for i, c in enumerate(pals[k]):
            for y in range(12):
                for x in range(12):
                    cv.put(48 + i * 14 + x + (6 if i >= 16 else 0), 8 + r * 16 + y, c)
    cv.save(os.path.join(args.out, 'palettes.png'))

    # labdata: composed walls (texture + overlays) and objects
    for spec in args.labdata:
        n, k = map(int, spec.split(':'))
        lab = labs[(n, k)]
        items = []
        for wi, (header, ovs) in enumerate(lab.walls):
            img = bytearray(texture4(walls.get(header[4], b''), 128, 80))
            for ov in ovs:
                w, h = ov[4], ov[5]
                oimg = texture4(overlays.get(ov[1], b''), w, h)
                for y in range(h):
                    for x in range(w):
                        v = oimg[y * w + x]
                        if v and 0 <= ov[2] + x < 128 and 0 <= ov[3] + y < 80:
                            img[(ov[3] + y) * 128 + ov[2] + x] = v
            items.append((101 + wi, img))
        grid(items, 128, 80, 6, lambda cv, x, y, it: cv.blit(x, y, it[1], 128, 80, pal, False),
             os.path.join(args.out, f'labdata_{n}_{k}_walls.png'))
        items = []
        for oi, o in enumerate(lab.objects):
            tex = struct.unpack('>H', o[4:6])[0]
            w, h = o[8], o[9]
            if objects.get(tex):
                items.append((oi + 1, texture4(objects[tex], w, h), w, h))
        if items:
            mw = max(i[2] for i in items); mh = max(i[3] for i in items)
            grid(items, mw, mh, 8, lambda cv, x, y, it: cv.blit(x, y, it[1], it[2], it[3], pal),
                 os.path.join(args.out, f'labdata_{n}_{k}_objects.png'))
    print('written to', args.out)


if __name__ == '__main__':
    main()

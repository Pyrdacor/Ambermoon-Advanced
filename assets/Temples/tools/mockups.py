"""Palette and wall mockups for the council temples.

Renders candidate walls and objects with the original temple palette (6) and with proposed new
palettes, plus walls composed from existing textures and overlays (no new graphics needed).

Usage: python mockups.py   (writes into ../mockups)
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools', 'ambtools'))
import render3d as r  # noqa: E402

OUT = os.path.join(HERE, '..', 'mockups')


def pal16(hexes):
    return [(int(h[0], 16) * 17, int(h[1], 16) * 17, int(h[2], 16) * 17) for h in hexes]


BASE6 = ['000', 'bba', '997', '876', '654', '432', '311', 'a74', '853', '632', 'c82', 'ea4', '672', '452', '900', 'c40']
# Only the stone ramp (1-6) and the accent colours (12-13) are changed, orange (7-11) and red (14-15) stay,
# so wood, fire and monsters keep looking normal.
PALETTES = {
    'P6 original': BASE6,
    'Sandstein + Gold': ['000', 'eda', 'cb8', 'a96', '875', '653', '431'] + BASE6[7:12] + ['fc5', 'c93'] + BASE6[14:],
    'Marmor + Tuerkis': ['000', 'eef', 'ccd', 'aab', '889', '667', '445'] + BASE6[7:12] + ['4bb', '288'] + BASE6[14:],
    'Obsidian + Glut': ['000', '889', '667', '556', '434', '323', '212'] + BASE6[7:12] + ['f60', 'c30'] + BASE6[14:],
    'Jade + Gold': ['000', '9db', '7b9', '597', '476', '354', '232'] + BASE6[7:12] + ['fd7', 'ba4'] + BASE6[14:],
    'Rotstein + Blau': ['000', 'dba', 'b87', '966', '744', '533', '311'] + BASE6[7:12] + ['6ad', '359'] + BASE6[14:],
}

WALLS = [97, 99, 100, 104, 106, 144, 145, 148, 171, 187, 191, 69]
OBJECTS = [100, 101, 102, 103, 133, 143, 121, 141, 108, 117, 28, 30, 96, 98, 227, 379]


def walls_sheet(walls):
    cell_w, cell_h = 128, 80
    cols = len(WALLS)
    rows = len(PALETTES)
    cv = r.Canvas(8 + cols * (cell_w + 6), 8 + rows * (cell_h + 20))
    for ri, (name, hexes) in enumerate(PALETTES.items()):
        pal = pal16(hexes) + [(0, 0, 0)] * 16
        y = 8 + ri * (cell_h + 20)
        for ci, t in enumerate(WALLS):
            x = 8 + ci * (cell_w + 6)
            cv.blit(x, y + 14, r.texture4(walls[t], 128, 80), 128, 80, pal, False)
            cv.text(x, y, str(t))
        cv.text(8 + cols * (cell_w + 6) - 60, y, str(ri), (255, 128, 0))
    cv.save(os.path.join(OUT, 'walls_palettes.png'))


def objects_sheet(objects, sizes):
    items = [(t, sizes[t]) for t in OBJECTS if t in sizes and objects.get(t)]
    mw = max(s[0] for _, s in items); mh = max(s[1] for _, s in items)
    cv = r.Canvas(8 + len(items) * (mw + 6), 8 + len(PALETTES) * (mh + 20))
    for ri, (name, hexes) in enumerate(PALETTES.items()):
        pal = pal16(hexes) + [(0, 0, 0)] * 16
        y = 8 + ri * (mh + 20)
        for ci, (t, (w, h, _)) in enumerate(items):
            x = 8 + ci * (mw + 6)
            cv.blit(x, y + 14, r.texture4(objects[t], w, h), w, h, pal)
            cv.text(x, y, str(t))
    cv.save(os.path.join(OUT, 'objects_palettes.png'))


def compose(walls, overlays, ovl_size, base, parts):
    img = bytearray(r.texture4(walls[base], 128, 80))
    for ov, px, py in parts:
        w, h = ovl_size[ov]
        o = r.texture4(overlays[ov], w, h)
        if px == 'r':
            px = 128 - w
        if px == 'c':
            px = (128 - w) // 2
        for y in range(h):
            for x in range(w):
                v = o[y * w + x]
                if v and 0 <= px + x < 128 and 0 <= py + y < 80:
                    img[(py + y) * 128 + px + x] = v
    return img


def composed_sheet(walls, overlays, ovl_size):
    # (title, base wall, [(overlay, x, y)])
    designs = [
        ('171', 171, []),
        ('171+96/97', 171, [(96, 0, 0), (97, 'r', 0)]),
        ('171+71', 171, [(96, 0, 0), (97, 'r', 0), (71, 'c', 8)]),
        ('148+74', 148, [(74, 'c', 10)]),
        ('144+15/16', 144, [(15, 0, 0), (16, 'r', 0)]),
        ('171+72', 171, [(72, 'c', 6)]),
        ('99+40', 99, [(40, 'c', 30)]),
        ('148+86', 148, [(86, 'c', 0)]),
    ]
    cell_w, cell_h = 128, 80
    cv = r.Canvas(8 + len(designs) * (cell_w + 6), 8 + len(PALETTES) * (cell_h + 20))
    for ri, (name, hexes) in enumerate(PALETTES.items()):
        pal = pal16(hexes) + [(0, 0, 0)] * 16
        y = 8 + ri * (cell_h + 20)
        for ci, (title, base, parts) in enumerate(designs):
            if any(ov not in ovl_size or not overlays.get(ov) for ov, _, _ in parts):
                continue
            x = 8 + ci * (cell_w + 6)
            cv.blit(x, y + 14, compose(walls, overlays, ovl_size, base, parts), 128, 80, pal, False)
            cv.text(x, y, str(ci + 1))
    cv.save(os.path.join(OUT, 'composed_walls.png'))
    return designs


def main():
    os.makedirs(OUT, exist_ok=True)
    data = r.DEFAULT_DATA
    walls = r.merged(data, 'Wall3D.amb')
    objects = r.merged(data, 'Object3D.amb')
    overlays = r.merged(data, 'Overlay3D.amb')
    labs = r.labdatas(data)
    obj_size, ovl_size = {}, {}
    for lab in labs.values():
        for o in lab.objects:
            obj_size.setdefault(struct.unpack('>H', o[4:6])[0], (o[8], o[9], max(1, o[6])))
        for header, ovs in lab.walls:
            for ov in ovs:
                ovl_size.setdefault(ov[1], (ov[4], ov[5]))
    walls_sheet(walls)
    objects_sheet(objects, obj_size)
    designs = composed_sheet(walls, overlays, ovl_size)
    with open(os.path.join(OUT, 'legend.txt'), 'w', encoding='utf-8') as f:
        f.write('Palettes (rows, top to bottom):\n')
        for i, (name, hexes) in enumerate(PALETTES.items()):
            f.write(f'  {i}: {name}: {" ".join(hexes)}\n')
        f.write('\nComposed walls (columns):\n')
        for i, (title, base, parts) in enumerate(designs):
            f.write(f'  {i + 1}: wall {base} + overlays {[p[0] for p in parts]}\n')
    print('written to', OUT)


if __name__ == '__main__':
    main()

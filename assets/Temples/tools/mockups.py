"""3D mockups for the council temples.

Only the detailed temple textures (Gala/Sansri family: walls 96-109, overlays 24/25, 39, 67-74, 96/97,
133-137) are used, combined the way the original designers did it (labdata 2:5 and 2:32), plus a few new
combinations in the same style. Each temple gets its own palette. In these walls the colours 12/13 are
part of the stone (about 20% of the pixels), so the palettes tint 1-6 and 12/13 together instead of
using 12/13 as accent colours.

Usage: python mockups.py   (writes into ../mockups)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scene3d as s  # noqa: E402
import render3d as r  # noqa: E402

OUT = os.path.join(HERE, '..', 'mockups')
GALA, SANSRI = (2, 5), (2, 32)

BASE6 = ['000', 'bba', '997', '876', '654', '432', '311', 'a74', '853', '632', 'c82', 'ea4', '672', '452', '900', 'c40']


def tinted(ramp, accents):
    """Stone ramp 1-6 and the stone tint 12/13 change, wood/gold 7-11 and red 14/15 stay."""
    return ['000'] + ramp + BASE6[7:12] + accents + BASE6[14:]


PALETTES = {
    'original': BASE6,
    'sandstein': tinted(['fed', 'dca', 'ba8', '986', '764', '542'], ['cb7', 'a95']),
    'rotstein': tinted(['edc', 'cb9', 'a97', '865', '644', '422'], ['c86', 'a64']),
    'lapis': tinted(['cde', 'abc', '89a', '789', '567', '345'], ['79b', '579']),
    'amethyst': tinted(['dcd', 'bac', '98a', '879', '657', '435'], ['97a', '768']),
    'basalt': tinted(['bbb', '999', '777', '666', '444', '333'], ['887', '665']),
    'moder': tinted(['aa9', '887', '665', '554', '433', '211'], ['774', '552']),
    'jade': tinted(['cec', 'aca', '8a8', '687', '465', '243'], ['9c9', '7a8']),
}


def pal(name):
    return [(int(h[0], 16) * 17, int(h[1], 16) * 17, int(h[2], 16) * 17) for h in PALETTES[name]] + [(0, 0, 0)] * 16


def temples(a):
    """(name, palette, floor, ceiling, grid, legend, objects, cameras, description)"""
    W = a.wall
    G = lambda n: a.lab_wall(GALA, n)       # noqa: E731
    Sa = lambda n: a.lab_wall(SANSRI, n)    # noqa: E731
    O = a.obj_tex
    cols = [(1.5, 2.5, 0, O(100)), (3.5, 2.5, 0, O(100)), (1.5, 4.5, 0, O(100)), (3.5, 4.5, 0, O(100))]
    res = []

    res.append(('S\'Riel', 'sandstein', 20, 8,
                ['#####', '#PDP#', 'B...B', 'C...C', 'B...B', '#...#'],
                {'#': G(116), 'P': G(102), 'D': G(126), 'B': W(167), 'C': W(168)},
                [(2.5, 3.5, 0, O(97)), (1.5, 2.3, 0, O(142)), (3.5, 2.3, 0, O(142)), (2.5, 4.4, 0, O(156))],
                [(2.5, 4.7, 0), (2.1, 4.5, 40)],
                'Bibliothek: Bücherregale 167/168 zwischen Bogenwänden 98, Prunktür 96 mit Säulenrahmen 96/97, '
                'Bodenmosaik, Kerzenständer, Lesetisch'))

    res.append(('S\'Orel', 'rotstein', 20, 8,
                ['#####', '#CGC#', 'A...A', 'K...K', 'A...A', '#...#'],
                {'#': G(116), 'C': G(120), 'G': G(106), 'A': G(130), 'K': W(100, [(137, 32, 10)])},
                [(1.4, 2.6, 0, O(13)), (3.6, 2.6, 0, O(14)), (1.4, 4.0, 0, O(14)), (3.6, 4.0, 0, O(13)),
                 (2.5, 3.5, 0, O(99)), (2.5, 2.4, 0, O(116))],
                [(2.5, 4.7, 0), (2.9, 4.5, -40)],
                'Kaserne/Waffenkammer: Wappen 74/137 auf Quaderwand und Bogenwand, dunkles Tor 104, '
                'Rüstungen als Ehrenwache, Waffenständer'))

    res.append(('S\'Arin', 'lapis', 20, None,
                ['#####', '#WRW#', 'X...X', 'R...R', 'X...X', '#...#'],
                {'#': G(116), 'W': G(111), 'R': W(99, [(24, 0, 0, 0), (25, 96, 0, 0), (71, 32, 8)]),
                 'X': G(113)},
                cols[:2] + [(2.5, 3.5, 0, O(96)), (2.5, 2.6, 0.25, O(124)), (1.7, 3.6, 0.35, O(124)),
                            (3.3, 3.8, 0.3, O(124))],
                [(2.5, 4.7, 0), (2.1, 4.5, 40)],
                'Sternwarte: Rosettenfenster 71 zwischen Säulenrahmen 24/25 (neu), Spitzbogenfenster 72, '
                'Decke offen (Nachthimmel), schwebende Sterne, achteckiges Mosaik'))

    res.append(('S\'Endar', 'amethyst', 20, 8,
                ['#####', '#HFH#', 'M...M', 'L...L', 'N...N', '#...#'],
                {'#': G(116), 'H': W(103, [(39, 32, 12)]), 'F': G(105), 'M': G(117), 'L': G(118),
                 'N': G(119)},
                [(1.5, 2.5, 0, O(143)), (3.5, 2.5, 0, O(133)), (2.5, 3.2, 0, O(31))],
                [(2.5, 4.7, 0), (2.9, 4.5, -40)],
                'Illusionist: Steinköpfe 39 im Relieffries 103 (neu, Rätselmünder), Gemälde 67-69, '
                'Statuen in Roben, Funkelfeld als Illusion'))

    res.append(('S\'Trog', 'basalt', 14, 8,
                ['#####', '#ZYZ#', 'V...V', 'F...F', 'V...V', '#...#'],
                {'#': G(116), 'Z': G(104), 'Y': G(106), 'V': G(129), 'F': G(105)},
                cols + [(2.5, 3.5, 0, O(395)), (2.5, 3.5, 0, O(31))],
                [(2.5, 4.7, 0), (2.1, 4.5, 40)],
                'Teleportation: Reliefwände 100/103/104, Teleporter-Ring mit Funkeln im Zentrum, Säulen'))

    res.append(('S\'Kat', 'moder', 14, 8,
                ['#####', '#QTQ#', 'U...U', 'Q...Q', 'U...U', '#...#'],
                {'#': Sa(116), 'Q': Sa(120), 'T': Sa(124), 'U': Sa(123)},
                [(1.4, 2.5, 0, O(117)), (3.6, 2.5, 0, O(118)), (1.4, 4.0, 0, O(118)),
                 (2.5, 3.4, 0, O(121)), (3.4, 4.1, 0, O(159))],
                [(2.5, 4.7, 0), (2.1, 4.5, 40)],
                'Labor/Folter: Schlangenreliefs mit Glut 105-109 (Sansri), Käfige, Kohlebecken, Labortisch'))

    res.append(('S\'Lorwin', 'jade', 20, 8,
                ['#####', '#SDS#', 'X...X', 'P...P', 'X...X', '#...#'],
                {'#': G(116), 'S': Sa(119), 'D': G(126), 'X': G(113), 'P': G(102)},
                cols[2:] + [(2.5, 3.0, 0, O(259)), (2.5, 3.0, 0, O(125)), (1.5, 2.5, 0, O(28)), (3.5, 2.5, 0, O(28))],
                [(2.5, 4.7, 0), (2.1, 4.5, 40)],
                'Wasser/Garten/Macht: Teich mit Brunnen, Schlangentotems 28 vor dem Thronportal, Säulen, '
                'Kobra-Reliefs 102 und Fensterbögen'))
    return res


def main():
    os.makedirs(OUT, exist_ok=True)
    for old in ('walls_palettes.png', 'objects_palettes.png', 'composed_walls.png'):
        p = os.path.join(OUT, old)
        if os.path.exists(p):
            os.remove(p)
    a = s.Assets()
    size = (176, 144)
    scale = 2
    vw, vh = size[0] * scale, size[1] * scale
    lines = ['Palettes (3D colours 0-15):']
    for name, hexes in PALETTES.items():
        lines.append(f'  {name}: {" ".join(hexes)}')
    lines.append('')
    lines.append('Temples (temples.png, rows top to bottom, two views each):')

    designs = temples(a)
    cv = s.r.Canvas(8 + 2 * (vw + 8), 8 + len(designs) * (vh + 24))
    for i, (name, palname, floor, ceiling, grid, legend, objects, cams, desc) in enumerate(designs):
        y = 8 + i * (vh + 24)
        cv.text(8, y, str(i + 1))
        for c, cam in enumerate(cams):
            img, w, h = s.render(a, None, grid, legend, cam, objects, floor=floor, ceiling=ceiling,
                                 ceil_col=6, size=size, fov=60)
            cv.blit(8 + c * (vw + 8), y + 16, img, w, h, pal(palname), False, scale=scale)
        lines.append(f'  {i + 1}: {name} (palette {palname}, floor {floor}, ceiling {ceiling or "-"}): {desc}')
    cv.save(os.path.join(OUT, 'temples.png'))

    # the same hall in every palette
    L = GALA
    legend = {'#': a.lab_wall(L, 116), 'B': a.lab_wall(L, 107), 'C': a.lab_wall(L, 108), 'D': a.lab_wall(L, 101),
              'R': a.lab_wall(L, 110), 'X': a.lab_wall(L, 113), 'A': a.lab_wall(L, 103)}
    grid = ['#####', '#BDC#', 'R...R', 'X...X', 'A...A', '#...#']
    objs = [(1.5, 2.5, 0, a.obj(L, 9)), (3.5, 2.5, 0, a.obj(L, 9)), (2.5, 3.0, 0, a.obj(L, 5))]
    img, w, h = s.render(a, None, grid, legend, (2.5, 4.6, 20), objs, floor=20, ceiling=8, size=size, fov=60)
    names = list(PALETTES)
    cv = s.r.Canvas(8 + 4 * (vw + 8), 8 + 2 * (vh + 24))
    for i, name in enumerate(names):
        x, y = 8 + (i % 4) * (vw + 8), 8 + (i // 4) * (vh + 24)
        cv.text(x, y, str(i + 1))
        cv.blit(x, y + 16, img, w, h, pal(name), False, scale=scale)
    cv.save(os.path.join(OUT, 'palettes.png'))
    lines.append('')
    lines.append('palettes.png: the Gala hall (labdata 2:5) in all palettes, ' +
                 ', '.join(f'{i + 1} = {n}' for i, n in enumerate(names)))

    with open(os.path.join(OUT, 'legend.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('written to', OUT)


if __name__ == '__main__':
    main()

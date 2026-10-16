"""Build the temple prototypes into the german Amberfiles (pilot: S'Riel).

Prototype maps live on free map indices (487+) and are only reachable with a teleport cheat.
The real temples 444-450 are not touched.

Writes:
- 2Map_data.amb: prototype map(s)
- 2Lab_data.amb: labdata 46 (copy of the Gala labdata 5 with floor 20 and ceiling 8)
- Palettes.amb: palette 59 ("Sandstein")
- Save.00/Automap.amb: automap entries up to the new map (485 and 486 were missing too)
- AllTexts (german + english) 2Map_texts.amb/<map>, imported into the german 2Map_texts.amb

Usage: python build_prototype.py [--preview-only]
"""
import argparse
import math
import os
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
DATA = os.path.join(REPO, 'german', 'Amberfiles')
EN_TEXTS = os.path.join(REPO, 'english', 'Amberfiles', 'AllTexts')
WORK = os.path.join(os.environ.get('TEMP', HERE), 'temple_prototype_work')
PREVIEW = os.path.join(HERE, '..', 'prototypes')
sys.path.insert(0, os.path.join(REPO, 'tools', 'ambtools'))
sys.path.insert(0, HERE)
import ambcontainer as amb  # noqa: E402
import labdata as ld  # noqa: E402
import mapmodel as mm  # noqa: E402

GALA_LAB = 5
NEW_LAB = 46
NEW_PALETTE = 59
FLOOR_TEX, CEILING_TEX = 20, 8
SANDSTEIN = ['000', 'fed', 'dca', 'ba8', '986', '764', '542', 'a74', '853', '632', 'c82', 'ea4', 'cb7', 'a95', '900', 'c40']

# labdata 5 walls (tile values) and object groups
W_PLAIN, W_DOOR_FRAMED = 103, 126
W_FRAME_L, W_FRAME_R, W_ROSETTE, W_WINDOW = 107, 108, 110, 111
W_PAINT1, W_PAINT2, W_PAINT3, W_CREST = 117, 118, 119, 120
W_SHELF1, W_SHELF2 = 127, 128
G_COLUMN, G_MOSAIC, G_STATUE, G_CANDLE, G_TABLE, G_CHEST, G_ARMOUR, G_BED, G_GUARD = 9, 5, 14, 18, 20, 21, 22, 24, 27

MAGIC_GUARDS = 68           # monster group
GUARD_TILE_FLAGS = 0xc0000111


def run(*args):
    subprocess.run(args, check=True, capture_output=True)


def unpack(rel, fmt):
    dst = os.path.join(WORK, rel.replace('/', '_').replace('.', '_'))
    if os.path.exists(dst):
        shutil.rmtree(dst)
    run('AmbermoonPack', 'UNPACK', os.path.join(DATA, rel), dst)
    run('AmbermoonPack', fmt, dst, dst + '.check')
    assert open(dst + '.check', 'rb').read() == open(os.path.join(DATA, rel), 'rb').read(), rel
    return dst


def pack(rel, fmt, src):
    run('AmbermoonPack', fmt, src, os.path.join(DATA, rel))


def sub(d, i):
    return os.path.join(d, '%03d' % i)


def ev(*b):
    e = bytearray(12)
    e[:len(b)] = bytes(b)
    e[10:12] = b'\xff\xff'
    return e


def word(e, o, v):
    e[o:o + 2] = struct.pack('>H', v)
    return e


# ------------------------------------------------------------------ S'Riel
class Proto:
    """A prototype map: grid of tile values, objects, chains (list of event lists), characters and texts."""

    def __init__(self, index, w, h):
        self.index, self.w, self.h = index, w, h
        self.tiles = [[255] * (w + 1) for _ in range(h + 1)]     # 1-based
        self.events = [[0] * (w + 1) for _ in range(h + 1)]
        self.chains = []        # (automap type, [events])
        self.chars = []         # (index, type flags, gfx, x, y)

    def chain(self, automap, events, *tiles):
        self.chains.append((automap, events))
        n = len(self.chains)
        for x, y in tiles:
            self.events[y][x] = n
        return n

    def event_bit(self, chain):
        return (self.index - 1) * 64 + chain - 1


def sriel():
    p = Proto(487, 17, 17)
    floor = set()

    def rect(x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                floor.add((x, y))
    rect(7, 7, 11, 11)          # reception hall
    rect(3, 4, 4, 13)           # library (west wing)
    rect(14, 4, 15, 13)         # east wing
    rect(3, 13, 15, 14)         # foyer
    rect(7, 3, 11, 4)           # bedchamber
    floor |= {(9, 12), (5, 4), (5, 5)}  # hall exit, passage to the secret wall, reading nook (the cheat map jump lands on 5,5)
    secret = (6, 4)

    for y in range(1, p.h + 1):
        for x in range(1, p.w + 1):
            if (x, y) in floor:
                p.tiles[y][x] = 0
            elif any((x + dx, y + dy) in floor for dx in (-1, 0, 1) for dy in (-1, 0, 1)) or (x, y) == secret:
                p.tiles[y][x] = W_PLAIN
    walls = {
        # hall
        (9, 6): W_ROSETTE, (8, 6): W_FRAME_R, (10, 6): W_FRAME_L, (6, 9): W_CREST, (12, 9): W_CREST,
        (8, 12): W_FRAME_R, (10, 12): W_FRAME_L,
        # bedchamber
        (7, 2): W_WINDOW, (8, 2): W_PAINT2, (9, 2): W_WINDOW, (10, 2): W_PAINT3, (11, 2): W_WINDOW,
        # foyer and exit
        (9, 15): W_DOOR_FRAMED, (6, 15): W_WINDOW, (12, 15): W_WINDOW, (2, 14): W_PAINT1, (16, 14): W_PAINT1,
        # east wing
        (16, 5): W_WINDOW, (16, 7): W_CREST, (16, 9): W_WINDOW, (16, 11): W_CREST, (13, 8): W_FRAME_L, (13, 10): W_FRAME_R,
    }
    for y in range(4, 14):                      # library shelves on both sides
        p.tiles[y][2] = W_SHELF1 if y % 2 else W_SHELF2
        if p.tiles[y][5] == W_PLAIN and y > 4:
            p.tiles[y][5] = W_SHELF2 if y % 2 else W_SHELF1
    for (x, y), t in walls.items():
        p.tiles[y][x] = t
    objects = {
        (7, 7): G_COLUMN, (11, 7): G_COLUMN, (7, 11): G_COLUMN, (11, 11): G_COLUMN, (9, 9): G_MOSAIC,
        (7, 3): G_CHEST, (9, 3): G_BED, (11, 3): G_TABLE,
        (3, 4): G_CANDLE, (3, 9): G_TABLE,
        (15, 4): G_CHEST, (15, 7): G_STATUE, (15, 10): G_ARMOUR,
        (3, 14): G_CANDLE, (15, 14): G_CANDLE,
    }
    for (x, y), g in objects.items():
        p.tiles[y][x] = g

    text = lambda n, trigger=2: ev(0x04, 0xff, trigger, 0, 0, n)    # noqa: E731
    p.chain(14, [word(ev(0x01, 37, 41, 2, 0xff, 0), 6, 520)], (9, 15))                 # 1 exit -> Morag
    arrival = p.chain(0, [text(1, 3), word(ev(0x0e, 0x01, 1), 6, 0)], (9, 10))         # 2 S'Arin appears
    p.chains[-1][1][1] = word(ev(0x0e, 0x01, 1), 6, p.event_bit(arrival))
    p.chain(0, [text(2)], (2, 6))                                                      # 3-6 readable shelves
    p.chain(0, [text(3)], (2, 8))
    p.chain(0, [text(4)], (2, 10))
    p.chain(0, [text(5)], (2, 12))
    lever = p.chain(9, [], (2, 5))                                                     # 7 loose book
    p.chains[-1] = (9, [ev(0x0d, 0x0e, 1, 0, 0, 0, 0, 0, 0xff, 0xff), text(6, 0),
                        word(ev(0x0a, secret[0], secret[1]), 6, 0), word(ev(0x0e, 0x01, 1), 6, p.event_bit(lever))])
    p.chain(0, [text(7)], (11, 3))                                                     # 8 diary
    p.chain(13, [ev(0x03, 75, 0, 0xff, 116 - 1 + 1)], (7, 3))                           # 9 chest 116
    p.chain(13, [ev(0x03, 50, 0, 0xff, 117 - 1 + 1)], (15, 4))                          # 10 chest 117
    p.chars = [(MAGIC_GUARDS, 0x06, G_GUARD, 8, 8), (MAGIC_GUARDS, 0x06, G_GUARD, 10, 8)]
    p.header = dict(flags=0x0899, music=22, labdata=NEW_LAB, palette=NEW_PALETTE, world=2)
    p.texts = SRIEL_TEXTS
    return p


SRIEL_TEXTS = {
    'de': [
        "PALAST DES S'RIEL",
        None,   # 001: arrival text of map 444
        "ZWISCHEN DICKEN BÄNDEN VOLLER ZAHLENKOLONNEN STECKT EIN ZETTEL IN S'RIELS HANDSCHRIFT:^ "
        "\"S'ARIN ZÄHLT ALLES, SOGAR DIE SÄULEN UND KUGELN IN SEINEM EIGENEN PALAST. WER IHN BESUCHT, SOLLTE ES IHM GLEICHTUN.\"",
        "EIN SCHMALES BUCH TRÄGT DEN TITEL \"VOM WESEN DES SCHEINS\". AM RAND HAT S'RIEL NOTIERT:^ "
        "\"S'ENDAR TRAUT NICHT EINMAL SEINEN EIGENEN WÄNDEN. VIELE DAVON GIBT ES GAR NICHT. EIN BEHERZTER SCHRITT VERRÄT MEHR ALS JEDES AUGE.\"",
        "AUF EINEM PERGAMENT STEHT:^ \"S'TROG SPRINGT VON ORT ZU ORT WIE EIN SANDFLOH. WER IHN STELLEN WILL, MUSS IHM ZWEIMAL BEGEGNEN.^ "
        "S'KATS LABOR STINKT NACH GIFT UND ANGST. DIE KREATUREN IN SEINEN KÄFIGEN STAMMEN NICHT VON MORAG.\"",
        "EIN ALTES VERZEICHNIS DER RATSMITGLIEDER. HINTER S'LORWINS NAMEN STEHT:^ "
        "\"DER MÄCHTIGSTE VON UNS. SEIN WASSER HEILT IHN. SOLANGE ES FLIEßT, IST ER KAUM ZU BESIEGEN.\"^ "
        "GANZ OBEN IM REGAL NEBEN DER NORDWAND STEHT EIN BAND WEITER VOR ALS DIE ANDEREN.",
        "IHR ZIEHT AN DEM VORSTEHENDEN BAND. MIT EINEM LEISEN KLICKEN GLEITET IRGENDWO IN DER NÄHE EINE WAND ZUR SEITE.",
        "S'RIELS TAGEBUCH. DIE LETZTEN SEITEN SIND ERST VOR KURZEM GESCHRIEBEN WORDEN:^ "
        "\"DER RAT HAT BESCHLOSSEN, DIE LUFTSCHIFFE GEGEN LYRAMION ZU SCHICKEN. ICH HABE ALS EINZIGER DAGEGEN GESTIMMT. "
        "SEITDEM LÄSST S'ARIN MICH NICHT MEHR AUS DEN AUGEN.^ SOLLTE MIR ETWAS ZUSTOßEN, FINDET IHR IN MEINER TRUHE ALLES, "
        "WAS ICH ÜBER DIE ANDEREN RÄTE GESAMMELT HABE. MÖGEN DIE FREMDEN AUS LYRAMION MEHR ERFOLG HABEN ALS ICH.\"",
    ],
    'en': [
        "PALACE OF S'RIEL",
        None,
        "BETWEEN THICK VOLUMES FULL OF COLUMNS OF NUMBERS THERE IS A NOTE IN S'RIEL'S HANDWRITING:^ "
        "\"S'ARIN COUNTS EVERYTHING, EVEN THE PILLARS AND SPHERES IN HIS OWN PALACE. WHOEVER VISITS HIM SHOULD DO THE SAME.\"",
        "A SLIM BOOK IS TITLED \"ON THE NATURE OF ILLUSION\". IN THE MARGIN S'RIEL HAS WRITTEN:^ "
        "\"S'ENDAR DOES NOT EVEN TRUST HIS OWN WALLS. MANY OF THEM DO NOT EXIST AT ALL. A BOLD STEP REVEALS MORE THAN ANY EYE.\"",
        "A PARCHMENT READS:^ \"S'TROG JUMPS FROM PLACE TO PLACE LIKE A SAND FLEA. WHOEVER WANTS TO CATCH HIM MUST MEET HIM TWICE.^ "
        "S'KAT'S LABORATORY REEKS OF POISON AND FEAR. THE CREATURES IN HIS CAGES ARE NOT FROM MORAG.\"",
        "AN OLD REGISTER OF THE COUNCIL MEMBERS. NEXT TO S'LORWIN'S NAME IT SAYS:^ "
        "\"THE MIGHTIEST OF US. HIS WATER HEALS HIM. AS LONG AS IT FLOWS, HE IS HARDLY TO BE DEFEATED.\"^ "
        "AT THE TOP OF THE SHELF NEXT TO THE NORTH WALL ONE VOLUME STICKS OUT FURTHER THAN THE OTHERS.",
        "YOU PULL THE PROTRUDING VOLUME. WITH A QUIET CLICK A WALL NEARBY SLIDES ASIDE.",
        "S'RIEL'S DIARY. THE LAST PAGES WERE WRITTEN ONLY RECENTLY:^ "
        "\"THE COUNCIL HAS DECIDED TO SEND THE AIRSHIPS AGAINST LYRAMION. I WAS THE ONLY ONE WHO VOTED AGAINST IT. "
        "SINCE THEN S'ARIN HAS NOT LET ME OUT OF HIS SIGHT.^ SHOULD ANYTHING HAPPEN TO ME, YOU WILL FIND EVERYTHING I HAVE GATHERED "
        "ABOUT THE OTHER COUNCILLORS IN MY CHEST. MAY THE STRANGERS FROM LYRAMION BE MORE SUCCESSFUL THAN I WAS.\"",
    ],
}


def build_map(p):
    h = p.header
    m = mm.Map()
    m.header = bytearray(struct.pack('>HBBBBBBBBBB', h['flags'], 1, h['music'], p.w, p.h, h['labdata'], 0, 0,
                                     h['palette'], h['world'], 0))
    m.shared = None
    m.chars = []
    m.positions = []
    for idx, typ, gfx, x, y in p.chars:
        m.chars.append(bytearray(struct.pack('>BBBBHI', idx, 1, typ, 0, gfx, GUARD_TILE_FLAGS)))
        m.positions.append(bytearray([x, y]))
    while len(m.chars) < 32:
        m.chars.append(bytearray(10))
    m.type = 1
    m.tiles = bytearray()
    for y in range(1, p.h + 1):
        for x in range(1, p.w + 1):
            m.tiles += bytes([p.tiles[y][x], p.events[y][x]])
    m.events, m.heads, m.automap = [], [], bytearray()
    for automap, events in p.chains:
        m.heads.append(len(m.events))
        m.automap.append(automap)
        for k, e in enumerate(events):
            mm.set_next(e, len(m.events) + 1 if k + 1 < len(events) else 0xffff)
            m.events.append(e)
    m.gotos = []
    m.tail = b''
    raw = mm.serialize(m)
    assert mm.serialize(mm.parse(raw)) == raw
    return raw


def build_labdata(raw5):
    lab = ld.parse(raw5)
    lab.header[6] = CEILING_TEX
    lab.header[7] = FLOOR_TEX
    return ld.serialize(lab)


def build_palette(base):
    out = bytearray(base)
    for i, hx in enumerate(SANDSTEIN):
        out[i * 2:i * 2 + 2] = struct.pack('>H', int(hx, 16))
    return bytes(out)


def write_texts(p):
    src444 = os.path.join(DATA, 'AllTexts', '2Map_texts.amb', '444', '001.txt')
    for lang, root in (('de', os.path.join(DATA, 'AllTexts')), ('en', EN_TEXTS)):
        d = os.path.join(root, '2Map_texts.amb', str(p.index))
        os.makedirs(d, exist_ok=True)
        for i, t in enumerate(p.texts[lang]):
            if t is None:
                t = open(os.path.join(root, '2Map_texts.amb', '444', '001.txt'), encoding='utf-8-sig').read()
            with open(os.path.join(d, '%03d.txt' % i), 'w', encoding='utf-8-sig', newline='') as f:
                f.write(t)
    assert os.path.exists(src444)


# ------------------------------------------------------------------ preview
def preview(p, lab_raw, pal_raw):
    import scene3d as s
    import render3d as r
    os.makedirs(PREVIEW, exist_ok=True)
    a = s.Assets()
    a.labs[(2, NEW_LAB)] = ld.parse(lab_raw)
    pal = [(((c >> 8) & 15) * 17, ((c >> 4) & 15) * 17, (c & 15) * 17)
           for c in struct.unpack('>32H', pal_raw)]
    lab = a.labs[(2, NEW_LAB)]
    legend, grid, objs = {}, [], []
    chars = {}
    for y in range(1, p.h + 1):
        row = ''
        for x in range(1, p.w + 1):
            t = p.tiles[y][x]
            if t == 255:
                row += '#'
                legend['#'] = a.lab_wall((2, NEW_LAB), W_PLAIN)
            elif t > 100:
                c = chars.setdefault(t, chr(0x100 + t))
                legend[c] = a.lab_wall((2, NEW_LAB), t)
                row += c
            else:
                row += '.'
                if t:
                    g = lab.object_groups[t - 1]
                    for k in range(8):
                        ox, oy, oz, oi = struct.unpack('>HHHH', g[2 + k * 8:10 + k * 8])
                        if oi:
                            oz = oz - 65536 if oz > 32767 else oz
                            objs.append((x - 1 + ox / 512, y - 1 + oy / 512, oz / 512, a.obj((2, NEW_LAB), oi)))
        grid.append(row)
    for idx, typ, gfx, x, y in p.chars:
        g = lab.object_groups[gfx - 1]
        oi = struct.unpack('>H', g[8:10])[0]
        objs.append((x - 0.5, y - 0.5, 0, a.obj((2, NEW_LAB), oi)))
    # grid is 0-based for the renderer: cell (x, y) 1-based -> index (x-1, y-1)
    # (tile x, tile y, direction in degrees) 1-based like the map
    views = [(9, 10, 0, 'Halle, Blick nach Norden'),
             (9, 14, 0, 'Foyer, Blick auf die Halle'),
             (3, 12, 0, 'Bibliothek, Blick nach Norden'),
             (5, 4, 90, 'Geheimgang, Blick ins Schlafgemach'),
             (9, 4, 0, 'Schlafgemach'),
             (14, 12, 0, 'Ostflügel, Blick nach Norden')]
    views = [(x - 0.5, y - 0.5 + (0.45 if ang == 0 else 0), ang, n) for x, y, ang, n in views]
    size, scale = (176, 144), 2
    vw, vh = size[0] * scale, size[1] * scale
    cv = r.Canvas(8 + 3 * (vw + 8), 8 + 2 * (vh + 24))
    open_grid = [list(rw) for rw in grid]
    sx, sy = 6 - 1, 4 - 1                                   # show the secret passage open
    open_grid[sy][sx] = '.'
    for i, (cx, cy, ang, _) in enumerate(views):
        g = [''.join(rw) for rw in open_grid] if i >= 3 else grid
        img, w, h = s.render(a, None, g, legend, (cx, cy, ang), objs, floor=FLOOR_TEX, ceiling=CEILING_TEX,
                             size=size, fov=60)
        x0, y0 = 8 + (i % 3) * (vw + 8), 8 + (i // 3) * (vh + 24)
        cv.text(x0, y0, str(i + 1))
        cv.blit(x0, y0 + 16, img, w, h, pal, False, scale=scale)
    cv.save(os.path.join(PREVIEW, f'{p.index}_views.png'))
    # top-down plan
    cell = 16
    cv = r.Canvas(p.w * cell + 16, p.h * cell + 16)
    colours = {0: (200, 190, 160), 255: (30, 30, 36)}
    for y in range(1, p.h + 1):
        for x in range(1, p.w + 1):
            t = p.tiles[y][x]
            c = colours.get(t, (110, 90, 70) if t > 100 else (200, 190, 160))
            if t in (W_SHELF1, W_SHELF2):
                c = (150, 90, 40)
            elif t in (W_WINDOW, W_ROSETTE):
                c = (90, 140, 200)
            elif t in (W_DOOR_FRAMED,):
                c = (220, 160, 40)
            elif t == W_CREST:
                c = (180, 60, 60)
            for yy in range(cell - 1):
                for xx in range(cell - 1):
                    cv.put(8 + (x - 1) * cell + xx, 8 + (y - 1) * cell + yy, c)
            if 0 < t <= 100:
                for yy in range(4, cell - 5):
                    for xx in range(4, cell - 5):
                        cv.put(8 + (x - 1) * cell + xx, 8 + (y - 1) * cell + yy, (70, 70, 70))
            if p.events[y][x]:
                cv.text(8 + (x - 1) * cell + 2, 8 + (y - 1) * cell + 4, str(p.events[y][x]), (255, 255, 255), 1)
    for idx, typ, gfx, x, y in p.chars:
        for yy in range(4, cell - 5):
            for xx in range(4, cell - 5):
                cv.put(8 + (x - 1) * cell + xx, 8 + (y - 1) * cell + yy, (220, 40, 40))
    cv.save(os.path.join(PREVIEW, f'{p.index}_plan.png'))
    return [v[3] for v in views]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview-only', action='store_true')
    args = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    p = sriel()
    lab_raw = build_labdata(amb.read_container(os.path.join(DATA, '2Lab_data.amb'))[GALA_LAB])
    pal_raw = build_palette(amb.read_container(os.path.join(DATA, 'Palettes.amb'))[6])
    names = preview(p, lab_raw, pal_raw)
    print('preview:', ', '.join(names))
    if args.preview_only:
        return

    maps = unpack('2Map_data.amb', 'AMPC')
    old = open(sub(maps, p.index), 'rb').read()
    assert not old or old[6] == NEW_LAB, 'map slot not free'      # empty or an earlier prototype build
    open(sub(maps, p.index), 'wb').write(build_map(p))
    pack('2Map_data.amb', 'AMPC', maps)

    labs = unpack('2Lab_data.amb', 'AMPC')
    n = len(os.listdir(labs))
    assert n in (NEW_LAB - 1, NEW_LAB), n
    open(sub(labs, NEW_LAB), 'wb').write(lab_raw)
    pack('2Lab_data.amb', 'AMPC', labs)

    pals = unpack('Palettes.amb', 'AMPC')
    n = len(os.listdir(pals))
    assert n in (NEW_PALETTE - 1, NEW_PALETTE), n
    open(sub(pals, NEW_PALETTE), 'wb').write(pal_raw)
    pack('Palettes.amb', 'AMPC', pals)

    autos = unpack('Save.00/Automap.amb', 'AMBR')
    m2 = amb.read_container(os.path.join(DATA, '2Map_data.amb'))
    for k in range(1, p.index + 1):
        f = sub(autos, k)
        if not os.path.exists(f):
            d = m2.get(k, b'')
            size = math.ceil(d[4] * d[5] / 8) if d and d[2] == 1 else 0
            open(f, 'wb').write(bytes(size))
    pack('Save.00/Automap.amb', 'AMBR', autos)

    write_texts(p)
    run('AmbermoonTextManager', '-i', DATA, os.path.join(DATA, 'AllTexts'), '-f', '2Map_texts.amb')
    print('built map', p.index)


if __name__ == '__main__':
    main()

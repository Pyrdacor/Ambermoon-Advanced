"""Build the temple prototypes into the german Amberfiles (S'Riel 487, S'Orel 488).

Prototype maps live on free map indices (487+) and are only reachable with a teleport cheat.
The real temples 444-450 are not touched.

Writes:
- 2Map_data.amb: prototype map(s)
- 2Lab_data.amb: labdata 46, the temple base (copy of the Gala labdata 5 with floor 20, ceiling 8, extra walls
  and the serpent totem), see "Labdata 46.md"
- Monster_groups.amb: group 172 (6 magic guards)
- Palettes.amb: palette 59 ("Wüstentempel", S'Riel) and 60 ("Kaserne", S'Orel): the stone colours of palette 6 replaced by sandstone colours with
  the same meaning (1 brightest ... 6 darkest, 12/13 between), so all Gala walls, overlays and objects turn
  into sandstone without new graphics
- 3Lab_data.amb: the same labdata 46 (2Lab_data and 3Lab_data must stay identical)
- 2Object3D.amb 413-416: fire bowl halves (from textures/sketches) and the crystal stool and table
- 2Overlay3D.amb 156/157: the switch overlays 133/134 with a blue-green knob
- 2Wall3D.amb 193-200 / 2Overlay3D.amb 151-155: copies of the stone walls and overlays without the colours
  12/13, which are blue-green accents in palette 59
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
FLOOR_TEX, CEILING_TEX = 20, 8
BASE_PALETTE = 6
# palette 59: stone colours with the meaning of palette 6 (histogram match of wall 99 against the sandstone picture)
SANDSTONE = {1: 'ffe', 2: 'eda', 3: 'cb8', 4: 'c73', 5: '653', 6: '323', 12: '5a9', 13: '367'}
KASERNE = {1: 'eed', 2: 'dcb', 3: 'ba8', 4: 'a76', 5: '654', 6: '322', 12: '69b', 13: '357'}   # S'Orel: darker brownish sandstone, steel blue
PALETTES = {59: SANDSTONE, 60: KASERNE}
# 12/13 are the moss/glass tones of palette 6. In the temple they are blue-green accents (glass, mosaics,
# marble, books, paintings). The stone graphics that use 12/13 as stone colour get copies without them.
STONE_REMAP = {12: 3, 13: 5}
RECOLOURED_WALLS = (96, 98, 99, 100, 103, 104, 125, 126)        # -> 2Wall3D.amb 193...
RECOLOURED_OVERLAYS = (24, 25, 39, 96, 97)                      # -> 2Overlay3D.amb 151...
FIRST_WALL_COPY, FIRST_OVERLAY_COPY = 193, 151

# extra walls of labdata 46 (appended to the 30 walls of labdata 5): (texture, flags, automap, colour, overlays)
SOLID, PASSABLE = 0x40000082, 0x40000102
FRAMES = [(0, 24, 0, 0, 32, 80), (0, 25, 96, 0, 32, 80)]       # column frames left and right (no blending)
W_FRAMES, W_FRAMES_ROSETTE, W_FRAMES_WINDOW, W_FRAMES_CREST = range(131, 135)
NEW_WALLS = [
    (99, SOLID, 1, 4, FRAMES),
    (99, SOLID, 1, 4, FRAMES + [(1, 71, 32, 8, 64, 64)]),
    (99, SOLID, 1, 4, FRAMES + [(1, 72, 48, 10, 32, 58)]),
    (99, SOLID, 1, 4, FRAMES + [(1, 74, 32, 10, 64, 52)]),
    (99, SOLID, 1, 4, [(1, 156, 40, 16, 40, 32)]),     # 135: plain wall with switch (off), behind the painting
    (99, SOLID, 1, 4, [(1, 157, 40, 16, 40, 32)]),     # 136: plain wall with switch (on)
]
# 2Overlay3D.amb 156/157: copies of the switch overlays 133/134 with a blue-green knob (the sandstone plate made the
# golden knob hard to see)
SWITCH_OVERLAYS = {156: 133, 157: 134}
SWITCH_KNOB = {0xb: 12, 0xa: 12, 0x7: 13, 0x8: 13}         # only inside the knob area x 17-28, y 10-20
W_PLAIN_SWITCH_OFF, W_PLAIN_SWITCH_ON = 135, 136

# labdata 5 walls (tile values) and object groups
W_DOOR, W_ARCHES, W_PLAIN, W_PILLAR, W_FRIEZE, W_GATE = 101, 102, 103, 104, 105, 106
W_FRAME_L, W_FRAME_R, W_HEAD, W_ROSETTE, W_WINDOW, W_WINDOWS2, W_ARCH_WINDOWS = 107, 108, 109, 110, 111, 112, 113
W_STAIRS_UP, W_STAIRS_DOWN, W_ILLUSION = 114, 115, 116
W_PAINT1, W_PAINT2, W_PAINT3, W_CREST = 117, 118, 119, 120
W_SWITCH1, W_SWITCH2, W_DOOR_FRAMED, W_ARCHES_CREST = 122, 123, 126, 130
W_SHELF1, W_SHELF2 = 127, 128
G_COLUMN, G_MOSAIC, G_STATUE, G_CANDLE, G_TABLE, G_CHEST, G_ARMOUR, G_BED, G_GUARD = 9, 5, 14, 18, 20, 21, 22, 24, 27
G_MOSAIC_ORANGE = 8
G_MOSAIC_GREEN = 6         # round mosaic with blue-green inlay (colours 12/13)
G_SPIKES = 41               # new object group: three floor spikes (object 39, texture 10, like the spikes in 445)
G_WEAPONS, G_TABLET, G_GOLEM, G_ROBE = 34, 38, 1, 14
G_TOTEM = 40                # new object group: serpent totem from Sansri's temple (labdata 32, texture 28)
TOTEM_OBJECT = bytes.fromhex('40000080001c0100605001200155')
# new object group: fire bowl hanging from the ceiling (layers of textures/sketches/merged.pdn, the two bowl halves
# exported as fire-bowl-back-v2.png and fire-bowl-front-v2.png). Sub-objects at the block centre, all scaled 3x like
# the chain: bowl front (new texture), chain (object 27, texture 147) and a second chain piece above it up to the
# ceiling, flame (texture 144 frame 0 like in merged.pdn, 8 frames), bowl back (new texture). The first sub-object
# is drawn in front of the others.
G_FIRE_BOWL = 42
FIRE_BOWL_BACK_TEX, FIRE_BOWL_FRONT_TEX = 413, 414     # 2Object3D.amb
FIRE_BOWL_SKETCHES = os.path.join(HERE, '..', 'textures', 'sketches')
FIRE_BOWL_OBJECTS = [                                   # (texture, frames, width, height), appended as objects 43-45
    (FIRE_BOWL_FRONT_TEX, 1, 32, 11),
    (144, 8, 16, 36),
    (FIRE_BOWL_BACK_TEX, 1, 32, 4),
]
CHAIN_OBJECT = 27
# z of the lower edge (wall height 341, 3 units per pixel). merged.pdn row 0 (top of the flame) is the ceiling:
# flame rows 0-35, chain rows 10-35 plus a second piece for rows -16-9 (its upper part is hidden in the ceiling),
# back rows 32-35, front rows 33-43
FIRE_BOWL_Z = {'front': 341 - 3 * 44, 'chain': 341 - 3 * 36, 'chain_top': 341 - 3 * 10, 'flame': 341 - 3 * 36,
               'back': 341 - 3 * 36}
# new object groups: crystal stool (from the stool 255) and crystal table (top 250 squashed on the column 254),
# the wood/stone colours replaced by the blue-green accents 12/13 with highlights 1/2
G_CRYSTAL_STOOL, G_CRYSTAL_TABLE = 43, 44
CRYSTAL_STOOL_TEX, CRYSTAL_TABLE_TEX = 415, 416      # 2Object3D.amb
CRYSTAL_WOOD = {0x1: 1, 0xb: 2, 0xa: 12, 0x7: 12, 0x8: 13}
CRYSTAL_STONE = {1: 1, 2: 2, 3: 12, 4: 13, 5: 13, 6: 6}
G_MORANIAN = 45            # new object group: a single Moranian in a robe (object 30 of group 28 without the guards)
VAR_PAINTING_REMOVED, VAR_SWITCH_USED = 478, 479       # global variables (S'Riel: painting taken down, switch used)

MAGIC_GUARDS = 68           # monster group: 4 magic guards
TWO_GUARDS = 67             # 2 magic guards
SIX_GUARDS = 172            # new: 6 magic guards
SIX_GUARDS_DATA = struct.pack('>18H', 0, 0, 0, 0, 0, 0, 0, 42, 0, 0, 42, 0, 42, 42, 0, 0, 42, 42)
GUARD_TILE_FLAGS = 0xc0000111
GUARD_STAY = 0x86           # monster (2) + moving (bit 2) + only move when they see the party (bit 7)


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
    """S'Riel (sketch of 2026-11-13): round 13x13 temple, ring corridor around a central chamber.
    The painting above the entrance tile hides a switch which opens the secret wall to the chamber's north side."""
    p = Proto(487, 13, 13)
    floor = set()
    for x in range(4, 11):
        floor |= {(x, 3), (x, 11)}                  # ring corridor north and south
    for y in range(4, 11):
        floor |= {(3, y), (11, y)}                  # west and east
    floor |= {(4, 4), (10, 4), (4, 10), (10, 10)}   # rounded inner corners of the ring
    floor |= {(6, 5), (7, 5), (8, 5), (6, 9), (7, 9), (8, 9)}       # central chamber
    for y in range(6, 9):
        for x in range(5, 10):
            floor.add((x, y))
    painting, secret, exit_ = (7, 10), (7, 4), (7, 12)
    for y in range(1, p.h + 1):
        for x in range(1, p.w + 1):
            if (x, y) in floor:
                p.tiles[y][x] = 0
            elif any((x + dx, y + dy) in floor for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                p.tiles[y][x] = W_PLAIN
    walls = {
        # outer wall
        exit_: W_DOOR_FRAMED, (6, 12): W_FRIEZE, (8, 12): W_FRIEZE, (5, 12): W_FRAMES_WINDOW, (9, 12): W_FRAMES_WINDOW,
        (7, 2): W_FRAMES_ROSETTE, (5, 2): W_FRAMES_WINDOW, (9, 2): W_FRAMES_WINDOW,
        (2, 7): W_FRAMES_CREST, (2, 5): W_FRAMES_WINDOW, (2, 9): W_FRAMES_WINDOW,
        (12, 7): W_FRAMES_CREST, (12, 5): W_FRAMES_WINDOW, (12, 9): W_FRAMES_WINDOW,
        (3, 3): W_PILLAR, (11, 3): W_PILLAR, (3, 11): W_PILLAR, (11, 11): W_PILLAR,
        # central block (seen from the corridor and from the chamber)
        painting: W_PAINT1, (6, 10): W_FRAMES, (8, 10): W_FRAMES, (5, 10): W_FRIEZE, (9, 10): W_FRIEZE,
        (6, 4): W_FRAMES, (8, 4): W_FRAMES, (5, 4): W_FRIEZE, (9, 4): W_FRIEZE,
        (4, 7): W_CREST, (4, 5): W_PILLAR, (4, 9): W_PILLAR,
        (10, 6): W_SHELF1, (10, 7): W_SHELF2, (10, 8): W_SHELF1, (10, 5): W_PILLAR, (10, 9): W_PILLAR,
    }
    for (x, y), t in walls.items():
        p.tiles[y][x] = t
    objects = {xy: G_FIRE_BOWL for xy in ((7, 3), (7, 11), (4, 4), (10, 4), (4, 10), (10, 10), (3, 7), (11, 7),
                                          (6, 6), (8, 6), (6, 8), (8, 8))}
    objects.update({
        (5, 7): G_BED, (5, 8): G_CHEST, (7, 7): G_CRYSTAL_TABLE, (8, 7): G_CRYSTAL_STOOL,
        (7, 6): G_MORANIAN,                         # a Moranian at the table, disappears after the arrival text
        # carpets
        (5, 3): G_MOSAIC_GREEN, (9, 3): G_MOSAIC_GREEN, (5, 11): G_MOSAIC_GREEN, (9, 11): G_MOSAIC_GREEN,
        (3, 5): G_MOSAIC_ORANGE, (3, 9): G_MOSAIC_ORANGE, (11, 5): G_MOSAIC_ORANGE, (11, 9): G_MOSAIC_ORANGE,
        (7, 5): G_MOSAIC, (7, 9): G_MOSAIC,
    })
    for (x, y), g in objects.items():
        p.tiles[y][x] = g

    text = lambda n, trigger=2: ev(0x04, 0xff, trigger, 0, 0, n)    # noqa: E731
    first = lambda: sum(len(c[1]) for c in p.chains)                # map event index of the next chain   # noqa: E731

    def cond(typ, value, obj=0, if_false=0xffff):
        return word(word(ev(0x0d, typ, value), 6, obj), 8, if_false)
    p.chain(14, [word(ev(0x01, 37, 41, 2, 0xff, 0), 6, 520)], exit_)                   # 1 exit -> Morag
    music = lambda song: ev(0x14, 0, song)                          # sound event, b1 = 0: music b2 (255 = map music)   # noqa: E731
    # character bit of the chamber guard (map character 1): 1 = inactive (hidden), 0 = active
    guard = lambda active: word(ev(0x0e, 0x04, 0 if active else 1), 6, (p.index - 1) * 32 + 0)   # noqa: E731
    arrival = p.chain(0, [], (7, 5))           # 2 arrival: guard hidden, dramatic music, delay, text, Moranian vanishes,
    p.chains[-1][1].extend([guard(False), music(30), word(ev(0x19), 6, 500), text(1, 3),   # guard appears, map music
                            word(ev(0x0a, 7, 6), 6, 0), guard(True), music(255),
                            word(ev(0x0e, 0x01, 1), 6, p.event_bit(arrival))])
    # 3 painting: eye -> text, painting taken down (wall with switch), hand (false branch of the eye) -> switch on, secret wall opens
    base = first()
    p.chain(0, [
        cond(0x14, 1, 0, base + 5),                                         # 0 eye? (else hand branch)
        cond(0x00, 0, VAR_PAINTING_REMOVED),                                # 1 painting still hanging?
        text(5, 0),                                                         # 2 "Lyramion and its moons ..."
        word(ev(0x0a, painting[0], painting[1]), 6, W_PLAIN_SWITCH_OFF),   # 3
        word(ev(0x0e, 0x00, 1), 6, VAR_PAINTING_REMOVED),                   # 4
        cond(0x0e, 1),                                                      # 5 hand?
        cond(0x00, 1, VAR_PAINTING_REMOVED),                                # 6 switch visible?
        cond(0x00, 0, VAR_SWITCH_USED),                                     # 7 not used yet?
        text(6, 0),                                                         # 8 "the switch ..."
        word(ev(0x0a, painting[0], painting[1]), 6, W_PLAIN_SWITCH_ON),    # 9
        word(ev(0x0a, secret[0], secret[1]), 6, 0),                         # 10 secret wall opens
        word(ev(0x0e, 0x00, 1), 6, VAR_SWITCH_USED),                        # 11
    ], painting)
    p.chain(0, [text(2)], (10, 6))                                                     # 4-6 readable shelves
    p.chain(0, [text(3)], (10, 7))
    p.chain(0, [text(4)], (10, 8))
    p.chain(0, [text(7)], (7, 7))                                                      # 7 diary on the table
    p.chain(13, [ev(0x03, 50, 0, 0xff, 117)], (5, 8))                                  # 8 chest 117 (key 388 for S'Orel)
    p.chars = [(TWO_GUARDS, GUARD_STAY, G_GUARD, 7, 6), (TWO_GUARDS, GUARD_STAY, G_GUARD, 7, 11)]
    p.header = dict(flags=0x0899, music=22, labdata=NEW_LAB, palette=59, world=2)
    p.texts = SRIEL_TEXTS
    p.open_tiles = [secret]
    p.views = [(7, 11, 0, 'Eingang, Blick auf das Gemaelde', False), (3, 10, 0, 'Westgang, Blick nach Norden', False),
               (7, 3, 180, 'Nordgang, Blick auf die Geheimwand', False), (7, 9, 0, 'Zentralraum, Blick nach Norden', True),
               (9, 7, 270, 'Zentralraum, Blick nach Westen', False), (11, 4, 180, 'Ostgang, Blick nach Sueden', False)]
    return p


def sorel():
    """S'Orel (barracks): outer corridor with guards and a spike trap (switched off by a hidden button),
    at the far end the gate to the inner part (key 388 from S'Riel's chest 117). Inside: armoury with weapon
    racks and chest 118, then the training hall with the big guard group and chest 119 (key 389 for S'Arin)."""
    p = Proto(488, 21, 21)
    floor = set()

    def rect(x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                floor.add((x, y))
    rect(4, 4, 5, 18)           # outer corridor west
    rect(17, 4, 18, 18)         # east
    rect(4, 4, 18, 5)           # north
    rect(4, 17, 18, 18)         # south
    rect(7, 7, 15, 8)           # armoury
    rect(7, 10, 15, 15)         # training hall
    floor.add((11, 9))          # arch between armoury and hall
    gate, button = (11, 6), (19, 9)
    spikes = [(4, 9), (5, 11), (4, 13)]
    for y in range(1, p.h + 1):
        for x in range(1, p.w + 1):
            if (x, y) in floor:
                p.tiles[y][x] = 0
            elif any((x + dx, y + dy) in floor for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                p.tiles[y][x] = W_PLAIN
    walls = {
        # outer wall
        (11, 3): W_FRAMES_WINDOW, (7, 3): W_FRAMES_CREST, (15, 3): W_FRAMES_CREST,
        (3, 11): W_FRAMES_WINDOW, (3, 7): W_FRAMES_CREST, (3, 15): W_FRAMES_CREST,
        (19, 11): W_FRAMES_WINDOW, (19, 7): W_FRAMES_CREST, (19, 15): W_FRAMES_CREST, button: W_SWITCH1,
        (11, 19): W_DOOR_FRAMED, (10, 19): W_FRIEZE, (12, 19): W_FRIEZE, (7, 19): W_FRAMES_WINDOW, (15, 19): W_FRAMES_WINDOW,
        # inner building, outside
        gate: W_GATE, (10, 6): W_FRAME_R, (12, 6): W_FRAME_L, (6, 11): W_PILLAR, (16, 11): W_PILLAR,
        (11, 16): W_ARCHES_CREST, (8, 16): W_CREST, (14, 16): W_CREST, (6, 8): W_FRIEZE, (16, 8): W_FRIEZE,
        # inside: wall between armoury and hall
        (10, 9): W_FRAME_R, (12, 9): W_FRAME_L, (8, 9): W_ARCHES, (14, 9): W_ARCHES,
    }
    for (x, y), tl in walls.items():
        p.tiles[y][x] = tl
    objects = {
        (4, 4): G_ROBE, (18, 4): G_ROBE, (4, 18): G_ROBE, (18, 18): G_ROBE,
        (7, 7): G_TABLET, (8, 7): G_WEAPONS, (10, 7): G_WEAPONS, (12, 7): G_WEAPONS, (14, 7): G_WEAPONS, (15, 7): G_CHEST,
        (8, 11): G_COLUMN, (14, 11): G_COLUMN, (8, 14): G_COLUMN, (14, 14): G_COLUMN, (11, 15): G_CHEST,
        (7, 10): G_GOLEM, (15, 10): G_GOLEM, (11, 12): G_MOSAIC_ORANGE,
    }
    for xy in spikes:
        objects[xy] = G_SPIKES
    for (x, y), g in objects.items():
        p.tiles[y][x] = g

    text = lambda n, trigger=2: ev(0x04, 0xff, trigger, 0, 0, n)    # noqa: E731
    hand = lambda: ev(0x0d, 0x0e, 1, 0, 0, 0, 0, 0, 0xff, 0xff)    # noqa: E731
    p.chain(14, [word(ev(0x01, 33, 28, 2, 0xff, 0), 6, 525)], (11, 19))                # 1 exit -> Morag (like 445)
    trap = p.chain(5, [text(1, 1), ev(0x06, 0x09, 1, 3, 0xff)], *spikes)                # 2 spikes (text and trap of 445)
    btn = p.chain(7, [], button)                                                       # 3 hidden button
    p.chains[-1] = (7, [hand(), text(2, 0), word(ev(0x0a, button[0], button[1]), 6, W_SWITCH2),
                        word(ev(0x0e, 0x01, 1), 6, p.event_bit(btn))]
                   + [word(ev(0x0a, x, y), 6, 0) for x, y in spikes] + [word(ev(0x0e, 0x01, 1), 6, p.event_bit(trap))])
    door = p.chain(9, [], gate)                                                        # 4 gate, key 388 (door 33 like 445)
    p.chains[-1] = (9, [hand(), bytearray.fromhex('026421ffff000184ffffffff'), ev(0x0d, 0x09, 1, 0, 0, 0, 0, 0, 0xff, 0xff),
                        word(ev(0x0e, 0x01, 1), 6, p.event_bit(door)), word(ev(0x0a, gate[0], gate[1]), 6, 0)])
    p.chain(0, [text(3)], (7, 7))                                                      # 5 duty roster
    p.chain(13, [ev(0x03, 85, 0, 0xff, 118)], (15, 7))                                 # 6 chest 118 (armoury)
    p.chain(13, [ev(0x03, 50, 0, 0xff, 119)], (11, 15))                                # 7 chest 119 (key 389)
    # monsters that only move when they see the party (flag 0x80), so they don't wander into corners
    p.chars = [(TWO_GUARDS, GUARD_STAY, G_GUARD, 18, 12), (MAGIC_GUARDS, GUARD_STAY, G_GUARD, 11, 5),
               (MAGIC_GUARDS, GUARD_STAY, G_GUARD, 5, 7), (SIX_GUARDS, GUARD_STAY, G_GUARD, 11, 13),
               (TWO_GUARDS, GUARD_STAY, G_GUARD, 9, 8)]
    p.header = dict(flags=0x0891, music=18, labdata=NEW_LAB, palette=60, world=2)    # lit, no map (445 was dark)
    p.texts = SOREL_TEXTS
    p.open_tiles = [gate]
    p.views = [(11, 18, 0, 'Suedgang, Blick auf das Hallengebaeude', False), (4, 17, 0, 'Westgang mit Spiessfalle', False),
               (18, 9, 90, 'Ostgang, versteckter Schalter', False), (11, 5, 180, 'Tor zum Innenbereich', False),
               (7, 8, 90, 'Waffenkammer', True), (11, 10, 180, 'Uebungshalle mit Wachen und Truhe', True)]
    return p


SOREL_TEXTS = {
    'de': [
        (445, 0),
        (445, 1),
        (445, 2),
        "AUF EINER STEINTAFEL STEHT DER DIENSTPLAN DER PALASTWACHE. DARUNTER HAT JEMAND IN EILIGER SCHRIFT ERGÄNZT:^ "
        "\"SEIT S'OREL AUF LYRAMION GEFALLEN IST, ERHALTEN DIE WACHEN IHRE BEFEHLE VON S'ARIN. DEN SCHLÜSSEL ZU SEINEM "
        "PALAST VERWAHRT DER HAUPTMANN IN DER TRUHE DER ÜBUNGSHALLE.\"",
    ],
    'en': [
        (445, 0),
        (445, 1),
        (445, 2),
        "THE DUTY ROSTER OF THE PALACE GUARD IS WRITTEN ON A STONE TABLET. BELOW IT SOMEONE HAS ADDED IN HASTY LETTERS:^ "
        "\"SINCE S'OREL FELL ON LYRAMION, THE GUARDS RECEIVE THEIR ORDERS FROM S'ARIN. THE CAPTAIN KEEPS THE KEY TO HIS "
        "PALACE IN THE CHEST OF THE TRAINING HALL.\"",
    ],
}


SRIEL_TEXTS = {
    'de': [
        "PALAST DES S'RIEL",
        None,   # 001: arrival text of map 444
        "ZWISCHEN DICKEN BÄNDEN VOLLER ZAHLENKOLONNEN STECKT EIN ZETTEL IN S'RIELS HANDSCHRIFT:^ "
        "\"S'ARIN ZÄHLT ALLES, SOGAR DIE SÄULEN UND KUGELN IN SEINEM EIGENEN PALAST. WER IHN BESUCHT, SOLLTE ES IHM GLEICHTUN.\"",
        "EIN SCHMALES BUCH TRÄGT DEN TITEL \"VOM WESEN DES SCHEINS\". AM RAND HAT S'RIEL NOTIERT:^ "
        "\"S'ENDAR TRAUT NICHT EINMAL SEINEN EIGENEN WÄNDEN. VIELE DAVON GIBT ES GAR NICHT. EIN BEHERZTER SCHRITT VERRÄT MEHR ALS JEDES AUGE.\"",
        "EIN ALTES VERZEICHNIS DER RATSMITGLIEDER. NEBEN EINIGE NAMEN HAT S'RIEL NOTIZEN GESCHRIEBEN:^ "
        "S'TROG: \"SPRINGT VON ORT ZU ORT WIE EIN SANDFLOH. WER IHN STELLEN WILL, MUSS IHM ZWEIMAL BEGEGNEN.\"^ "
        "S'KAT: \"SEIN LABOR STINKT NACH GIFT UND ANGST. DIE KREATUREN IN SEINEN KÄFIGEN STAMMEN NICHT VON MORAG.\"^ "
        "S'LORWIN: \"DER MÄCHTIGSTE VON UNS. SEIN WASSER HEILT IHN. SOLANGE ES FLIEßT, IST ER KAUM ZU BESIEGEN.\"",
        "~LEAD~ BETRACHTET DAS GEMÄLDE: \"DAS IST DOCH LYRAMION MIT SEINEN MONDEN! EIN SELTSAMES BILD FÜR EIN RATSMITGLIED.\"^ "
        "IHR BESCHLIESST, DAS GEMÄLDE VON DER WAND ZU NEHMEN. DAHINTER KOMMT EIN SCHALTER ZUM VORSCHEIN.",
        "IHR LEGT DEN SCHALTER UM. MIT EINEM DUMPFEN KNIRSCHEN GLEITET IRGENDWO IM NORDEN EINE WAND ZUR SEITE.",
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
        "AN OLD REGISTER OF THE COUNCIL MEMBERS. S'RIEL HAS WRITTEN NOTES NEXT TO SOME OF THE NAMES:^ "
        "S'TROG: \"JUMPS FROM PLACE TO PLACE LIKE A SAND FLEA. WHOEVER WANTS TO CATCH HIM MUST MEET HIM TWICE.\"^ "
        "S'KAT: \"HIS LABORATORY REEKS OF POISON AND FEAR. THE CREATURES IN HIS CAGES ARE NOT FROM MORAG.\"^ "
        "S'LORWIN: \"THE MIGHTIEST OF US. HIS WATER HEALS HIM. AS LONG AS IT FLOWS, HE IS HARDLY TO BE DEFEATED.\"",
        "~LEAD~ LOOKS AT THE PAINTING: \"THAT'S LYRAMION WITH ITS MOONS! A STRANGE PICTURE FOR A COUNCIL MEMBER.\"^ "
        "YOU DECIDE TO TAKE THE PAINTING OFF THE WALL. BEHIND IT A SWITCH COMES TO LIGHT.",
        "YOU FLIP THE SWITCH. WITH A DULL GRINDING SOUND A WALL SOMEWHERE TO THE NORTH SLIDES ASIDE.",
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


def recoloured_graphics(lab):
    """Copies of the stone walls/overlays with 12/13 replaced by stone colours.
    Returns ({wall copy index: data}, {overlay copy index: data}, wall map, overlay map)."""
    sys.path.insert(0, os.path.join(REPO, 'tools', 'ambtools'))
    import textures as tx
    walls = amb.read_container(os.path.join(DATA, '2Wall3D.amb'))
    overlays = amb.read_container(os.path.join(DATA, '2Overlay3D.amb'))
    sizes = {}
    for header, ovs in lab.walls:
        for ov in ovs:
            sizes.setdefault(ov[1], (ov[4], ov[5]))

    def remap(data, w, h):
        rows = tx.decode_texture(data, w, h)
        rows = [[STONE_REMAP.get(v, v) for v in row] for row in rows]
        return tx.encode_texture(rows, w)
    wall_files, ovl_files, wall_map, ovl_map = {}, {}, {}, {}
    for k, n in enumerate(RECOLOURED_WALLS):
        wall_map[n] = FIRST_WALL_COPY + k
        wall_files[wall_map[n]] = remap(walls[n], 128, 80)
    for k, n in enumerate(RECOLOURED_OVERLAYS):
        w, h = sizes[n]
        ovl_map[n] = FIRST_OVERLAY_COPY + k
        ovl_files[ovl_map[n]] = remap(overlays[n], w, h)
    for copy, n in SWITCH_OVERLAYS.items():
        rows = tx.decode_texture(overlays[n], 40, 32)
        rows = [[SWITCH_KNOB.get(v, v) if 17 <= x <= 28 and 10 <= y <= 20 else v for x, v in enumerate(row)]
                for y, row in enumerate(rows)]
        ovl_files[copy] = tx.encode_texture(rows, 40)
    return wall_files, ovl_files, wall_map, ovl_map


def build_labdata(raw5, wall_map=None, ovl_map=None):
    lab = ld.parse(raw5)
    lab.header[6] = CEILING_TEX
    lab.header[7] = FLOOR_TEX
    assert len(lab.walls) == 30 and len(lab.object_groups) == G_TOTEM - 1
    lab.objects.append(bytearray(TOTEM_OBJECT))
    group = bytearray(66)
    group[2:10] = struct.pack('>HHHH', 255, 255, 0, len(lab.objects))
    lab.object_groups.append(group)
    spikes = bytearray(66)
    for k, (x, y) in enumerate(((150, 150), (370, 210), (240, 390))):
        spikes[2 + k * 8:10 + k * 8] = struct.pack('>HHHH', x, y, 0, 39)
    lab.object_groups.append(spikes)
    assert len(lab.object_groups) == G_SPIKES
    first = len(lab.objects) + 1
    for tex, frames, w, h in FIRE_BOWL_OBJECTS:
        lab.objects.append(bytearray(struct.pack('>IHBBBBHH', 0x40000300, tex, frames, 0, w, h, w * 3, h * 3)))
    bowl = bytearray(66)
    for k, (z, obj) in enumerate(((FIRE_BOWL_Z['front'], first), (FIRE_BOWL_Z['chain'], CHAIN_OBJECT),
                                  (FIRE_BOWL_Z['chain_top'], CHAIN_OBJECT), (FIRE_BOWL_Z['flame'], first + 1),
                                  (FIRE_BOWL_Z['back'], first + 2))):
        bowl[2 + k * 8:10 + k * 8] = struct.pack('>HHHH', 255, 255, z, obj)
    lab.object_groups.append(bowl)
    assert len(lab.object_groups) == G_FIRE_BOWL
    for tex, w, h, x in ((CRYSTAL_STOOL_TEX, 32, 30, 0), (CRYSTAL_TABLE_TEX, 48, 41, 384)):    # stool at the left edge
        lab.objects.append(bytearray(struct.pack('>IHBBBBHH', 0x40000080, tex, 1, 0, w, h, w * 3, h * 3)))
        group = bytearray(66)
        group[2:10] = struct.pack('>HHHH', x, 255, 0, len(lab.objects))
        lab.object_groups.append(group)
    assert len(lab.object_groups) == G_CRYSTAL_TABLE
    group = bytearray(66)
    group[2:10] = struct.pack('>HHHH', 255, 255, 0, 30)
    lab.object_groups.append(group)
    assert len(lab.object_groups) == G_MORANIAN
    for tex, flags, automap, colour, overlays in NEW_WALLS:
        header = bytearray(struct.pack('>IBBBB', flags, tex, automap, colour, len(overlays)))
        lab.walls.append((header, [bytearray(o) for o in overlays]))
    for header, ovs in lab.walls:                  # use the recoloured copies
        header[4] = (wall_map or {}).get(header[4], header[4])
        for ov in ovs:
            ov[1] = (ovl_map or {}).get(ov[1], ov[1])
    return ld.serialize(lab)


def fire_bowl_textures():
    """The two bowl halves (palette 6 colours, which are the same indices in the temple palettes), 32 pixels wide
    like merged.pdn."""
    from PIL import Image
    sys.path.insert(0, os.path.join(REPO, 'tools', 'ambtools'))
    import textures as tx
    pal6 = amb.read_container(os.path.join(DATA, 'Palettes.amb'))[BASE_PALETTE]
    pal6 = [struct.unpack('>H', pal6[i * 2:i * 2 + 2])[0] for i in range(16)]

    def load(name):
        im = Image.open(os.path.join(FIRE_BOWL_SKETCHES, name))
        pal, px, transparent = im.getpalette(), im.load(), im.info['transparency']
        rows = []
        for y in range(im.height):
            row = [0] * im.width
            for x in range(im.width):
                v = px[x, y]
                if v != transparent:
                    r, g, b = pal[v * 3:v * 3 + 3]
                    row[x] = pal6.index(((r // 17) << 8) | ((g // 17) << 4) | (b // 17), 1)
            rows.append(row)
        return tx.encode_texture(rows, im.width)
    return {FIRE_BOWL_BACK_TEX: load('fire-bowl-back-v2.png'), FIRE_BOWL_FRONT_TEX: load('fire-bowl-front-v2.png')}


def crystal_textures():
    """Crystal stool and table from the wooden stool 255, the round top 250 and the column 254."""
    sys.path.insert(0, os.path.join(REPO, 'tools', 'ambtools'))
    import textures as tx
    objects = amb.read_container(os.path.join(DATA, '3Object3D.amb'))     # 250, 254 and 255 are only there
    stool = tx.decode_texture(objects[255], 32, 30)
    top = tx.decode_texture(objects[250], 48, 48)
    leg = tx.decode_texture(objects[254], 16, 41)
    stool = [[CRYSTAL_WOOD.get(v, v) for v in row] for row in stool]
    w, top_h, leg_h = 48, 16, 26
    h = top_h - 4 + leg_h + 3
    table = [[0] * w for _ in range(h)]
    for y in range(h - 7, h):                       # floor shadow like the one of the stool (5 rim, 6 inside)
        for x in range(w):
            d = ((x - 24) / 16) ** 2 + ((y - (h - 3.5)) / 3.2) ** 2
            if d <= 1:
                table[y][x] = 6 if d < 0.75 else 5
    for y in range(leg_h):                          # lower part of the column with the rounded foot
        for x in range(16):
            v = leg[y + 41 - leg_h][x]
            if v:
                table[top_h - 4 + y][16 + x] = CRYSTAL_STONE.get(v, v)
    for y in range(top_h):                          # the round top squashed to an ellipse (every third row)
        for x in range(w):
            v = top[min(47, y * 3 + 1)][x]
            if v:
                table[y][x] = CRYSTAL_STONE.get(v, v)
    return {CRYSTAL_STOOL_TEX: tx.encode_texture(stool, 32), CRYSTAL_TABLE_TEX: tx.encode_texture(table, w)}


def build_palette(stone):
    out = bytearray(amb.read_container(os.path.join(DATA, 'Palettes.amb'))[BASE_PALETTE])
    for i, hx in stone.items():
        out[i * 2:i * 2 + 2] = struct.pack('>H', int(hx, 16))
    return bytes(out)


def amnp_remove(rel, indices):
    """Remove trailing entries of an AMNP container (all other entries stay byte-identical)."""
    path = os.path.join(DATA, rel)
    entries = amnp_entries(open(path, 'rb').read())
    keep = len(entries)
    while keep and keep in indices:
        keep -= 1
    if keep == len(entries):
        return
    entries = entries[:keep]
    out = b'AMNP' + struct.pack('>H', len(entries)) + b''.join(struct.pack('>I', len(e)) for e in entries) + b''.join(entries)
    open(path, 'wb').write(out)


def amnp_entries(d):
    assert d[:4] == b'AMNP'
    n = struct.unpack('>H', d[4:6])[0]
    assert n >> 14 == 0
    sizes = struct.unpack('>%dI' % n, d[6:6 + 4 * n])
    off, out = 6 + 4 * n, []
    for s in sizes:
        out.append(d[off:off + s])
        off += s
    return out


def amnp_set(rel, files):
    """Add or replace entries of an AMNP container. All other entries stay byte-identical (packing the whole
    container again with AmbermoonPack changes some original entries by 2 bytes)."""
    path = os.path.join(DATA, rel)
    entries = amnp_entries(open(path, 'rb').read())
    tmp = os.path.join(WORK, 'amnp_' + os.path.basename(rel))
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    run('AmbermoonPack', 'UNPACK', path, tmp)
    for i, data in files.items():
        open(sub(tmp, i), 'wb').write(data)
    for i in range(1, max(files) + 1):          # gaps as empty entries
        if not os.path.exists(sub(tmp, i)):
            open(sub(tmp, i), 'wb').write(b'')
    run('AmbermoonPack', 'AMNP', tmp, tmp + '.amb')
    packed = amnp_entries(open(tmp + '.amb', 'rb').read())
    entries += [b''] * (max(files) - len(entries))
    for i in files:
        entries[i - 1] = packed[i - 1]
    out = b'AMNP' + struct.pack('>H', len(entries)) + b''.join(struct.pack('>I', len(e)) for e in entries) + b''.join(entries)
    open(path, 'wb').write(out)
    check = amb.read_container(path)
    for i, data in files.items():
        assert check[i] == data, i


def write_texts(p):
    src444 = os.path.join(DATA, 'AllTexts', '2Map_texts.amb', '444', '001.txt')
    for lang, root in (('de', os.path.join(DATA, 'AllTexts')), ('en', EN_TEXTS)):
        d = os.path.join(root, '2Map_texts.amb', str(p.index))
        os.makedirs(d, exist_ok=True)
        for i, t in enumerate(p.texts[lang]):
            if t is None:
                t = open(os.path.join(root, '2Map_texts.amb', '444', '001.txt'), encoding='utf-8-sig').read()
            elif isinstance(t, tuple):                      # (map, text) copied from the original temple
                t = open(os.path.join(root, '2Map_texts.amb', str(t[0]), '%03d.txt' % t[1]), encoding='utf-8-sig').read()
            with open(os.path.join(d, '%03d.txt' % i), 'w', encoding='utf-8-sig', newline='') as f:
                f.write(t)
    assert os.path.exists(src444)


# ------------------------------------------------------------------ preview
def preview(p, lab_raw, pal_raw, wall_files, ovl_files):
    import scene3d as s
    import render3d as r
    os.makedirs(PREVIEW, exist_ok=True)
    a = s.Assets()
    a.labs[(2, NEW_LAB)] = ld.parse(lab_raw)
    a.walls.update(wall_files)
    a.overlays.update(ovl_files)
    a.objects.update({**fire_bowl_textures(), **crystal_textures()})
    for header, ovs in a.labs[(2, NEW_LAB)].walls:
        for ov in ovs:
            a.ovl_size.setdefault(ov[1], (ov[4], ov[5]))
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
    views = [(x - 0.5, y - 0.5 + (0.45 if ang == 0 else 0), ang, n, o) for x, y, ang, n, o in p.views]
    size, scale = (176, 144), 2
    vw, vh = size[0] * scale, size[1] * scale
    cv = r.Canvas(8 + 3 * (vw + 8), 8 + 2 * (vh + 24))
    open_grid = [list(rw) for rw in grid]
    for sx, sy in p.open_tiles:                             # show secret passages / doors open
        open_grid[sy - 1][sx - 1] = '.'
    for i, (cx, cy, ang, _, use_open) in enumerate(views):
        g = [''.join(rw) for rw in open_grid] if use_open else grid
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
            elif t in (W_WINDOW, W_ROSETTE, W_WINDOWS2, W_ARCH_WINDOWS, W_FRAMES_WINDOW, W_FRAMES_ROSETTE):
                c = (90, 140, 200)
            elif t in (W_DOOR, W_DOOR_FRAMED):
                c = (220, 160, 40)
            elif t in (W_CREST, W_FRAMES_CREST):
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
    protos = [sriel(), sorel()]
    raw5 = amb.read_container(os.path.join(DATA, '2Lab_data.amb'))[GALA_LAB]
    wall_files, ovl_files, wall_map, ovl_map = recoloured_graphics(ld.parse(raw5))
    lab_raw = build_labdata(raw5, wall_map, ovl_map)
    pal_raws = {i: build_palette(stone) for i, stone in PALETTES.items()}
    for p in protos:
        names = preview(p, lab_raw, pal_raws[p.header['palette']], wall_files, ovl_files)
        print('preview', p.index, ':', ', '.join(names))
    if args.preview_only:
        return

    maps = unpack('2Map_data.amb', 'AMPC')
    for p in protos:
        old = open(sub(maps, p.index), 'rb').read()
        assert not old or old[6] == NEW_LAB, 'map slot not free'      # empty or an earlier prototype build
        open(sub(maps, p.index), 'wb').write(build_map(p))
    pack('2Map_data.amb', 'AMPC', maps)

    amnp_set('2Wall3D.amb', wall_files)
    amnp_set('2Overlay3D.amb', ovl_files)
    amnp_set('2Object3D.amb', {**fire_bowl_textures(), **crystal_textures()})
    amnp_set('Monster_groups.amb', {SIX_GUARDS: SIX_GUARDS_DATA})

    labs = unpack('2Lab_data.amb', 'AMPC')
    n = len(os.listdir(labs))
    assert n in (NEW_LAB - 1, NEW_LAB), n
    open(sub(labs, NEW_LAB), 'wb').write(lab_raw)
    pack('2Lab_data.amb', 'AMPC', labs)
    labs = unpack('3Lab_data.amb', 'AMPC')          # 2Lab_data and 3Lab_data must stay identical
    open(sub(labs, NEW_LAB), 'wb').write(lab_raw)
    pack('3Lab_data.amb', 'AMPC', labs)

    pals = unpack('Palettes.amb', 'AMPC')
    n = len(os.listdir(pals))
    assert min(PALETTES) - 1 <= n <= max(PALETTES), n
    for i, raw in pal_raws.items():
        open(sub(pals, i), 'wb').write(raw)
    pack('Palettes.amb', 'AMPC', pals)

    autos = unpack('Save.00/Automap.amb', 'AMBR')
    m2 = amb.read_container(os.path.join(DATA, '2Map_data.amb'))
    for k in range(1, max(p.index for p in protos) + 1):
        f = sub(autos, k)
        if not os.path.exists(f) or k in [p.index for p in protos]:     # prototype sizes may change
            d = m2.get(k, b'')
            size = math.ceil(d[4] * d[5] / 8) if d and d[2] == 1 else 0
            open(f, 'wb').write(bytes(size))
    pack('Save.00/Automap.amb', 'AMBR', autos)

    for p in protos:
        write_texts(p)
    run('AmbermoonTextManager', '-i', DATA, os.path.join(DATA, 'AllTexts'), '-f', '2Map_texts.amb')
    print('built maps', ', '.join(str(p.index) for p in protos))


if __name__ == '__main__':
    main()

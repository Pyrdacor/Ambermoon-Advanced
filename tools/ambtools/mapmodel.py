"""Parse and serialize raw (unpacked) Ambermoon map files losslessly."""
import struct

ET = {1: 'Teleport', 2: 'Door', 3: 'Chest', 4: 'Text', 5: 'Spinner', 6: 'Trap', 7: 'Buffs', 8: 'Riddle',
      9: 'Reward', 10: 'TileChg', 11: 'Battle', 12: 'Place', 13: 'Cond', 14: 'Action', 15: 'Dice',
      16: 'Conv', 17: 'Print', 18: 'Create', 19: 'Question', 20: 'Music', 21: 'Exit', 22: 'Spawn',
      23: 'Interact', 24: 'RemPM', 25: 'Delay', 26: 'PMCond', 27: 'Shake', 28: 'ShowMap', 29: 'Toggle',
      30: 'DynTile', 31: 'RectExpl', 32: 'VLine'}
COND = {0: 'GlobVar', 1: 'EventBit', 2: 'Door', 3: 'Chest', 4: 'CharBit', 5: 'PMPresent', 6: 'HasItem',
        7: 'UseItem', 8: 'Keyword', 9: 'Success', 10: 'Option', 11: 'CanSee', 12: 'Dir', 13: 'Ailment',
        14: 'Hand', 15: 'SayWord', 16: 'Number', 17: 'Levitating', 18: 'Gold', 19: 'Food', 20: 'Eye',
        21: 'Mouth', 22: 'Transport', 23: 'MultiCursor', 24: 'TravelType', 25: 'Class', 26: 'Empowered',
        27: 'Night', 28: 'Attr', 29: 'Skill', 30: 'Minute'}
ACT = {0: 'SetGlobVar', 1: 'EventBit', 2: 'Door', 3: 'Chest', 4: 'CharBit', 6: 'Items', 8: 'Keyword',
       10: 'Option', 12: 'Dir', 13: 'Ailment', 18: 'Gold', 19: 'Food'}
NONE = 0xffff


class Map:
    pass


def parse(raw):
    m = Map()
    m.raw = raw
    m.header = bytearray(raw[:12])
    m.flags, m.type, _, m.w, m.h = struct.unpack('>HBBBB', raw[:6])
    p = 12
    m.shared = None
    if m.flags & 0x8000:
        m.shared = raw[12:14]
        p = 14
    m.chars = [bytearray(raw[p + i * 10:p + i * 10 + 10]) for i in range(32)]
    p += 320
    tsz = 0 if m.shared else m.w * m.h * (2 if m.type == 1 else 4)
    m.tiles = bytearray(raw[p:p + tsz])
    p += tsz
    n = struct.unpack('>H', raw[p:p + 2])[0]
    m.heads = list(struct.unpack('>%dH' % n, raw[p + 2:p + 2 + 2 * n]))
    p += 2 + 2 * n
    ne = struct.unpack('>H', raw[p:p + 2])[0]
    p += 2
    m.events = [bytearray(raw[p + i * 12:p + i * 12 + 12]) for i in range(ne)]
    p += 12 * ne
    m.positions = []
    for c in m.chars:
        if c[0] == 0:
            break
        typ, fl = c[2] & 3, c[2] >> 2
        if typ == 2 or fl & 1 or fl & 0x20:
            cnt = 1
        elif fl & 0x10:
            cnt = 12
        else:
            cnt = 288
        m.positions.append(bytearray(raw[p:p + 2 * cnt]))
        p += 2 * cnt
    gc = struct.unpack('>H', raw[p:p + 2])[0]
    m.gotos = [bytearray(raw[p + 2 + i * 20:p + 22 + i * 20]) for i in range(gc)]
    p += 2 + 20 * gc
    if m.type == 1:
        m.automap = bytearray(raw[p:p + n])
        p += n
    else:
        m.automap = bytearray()
    m.tail = raw[p:]
    return m


def serialize(m):
    out = bytearray(m.header)
    if m.shared:
        out += m.shared
    for c in m.chars:
        out += c
    out += m.tiles
    out += struct.pack('>H', len(m.heads)) + struct.pack('>%dH' % len(m.heads), *m.heads)
    out += struct.pack('>H', len(m.events))
    for e in m.events:
        out += e
    for pos in m.positions:
        out += pos
    out += struct.pack('>H', len(m.gotos))
    for g in m.gotos:
        out += g
    if m.type == 1:
        assert len(m.automap) == len(m.heads)
        out += m.automap
    out += m.tail
    return bytes(out)


def nxt(e):
    return struct.unpack('>H', e[10:12])[0]


def set_next(e, i):
    e[10:12] = struct.pack('>H', i)


def w(e, o):
    return struct.unpack('>H', e[o:o + 2])[0]


def tile_event(m, x, y):
    """1-based coords -> chain index (1-based) or 0."""
    i = (y - 1) * m.w + (x - 1)
    return m.tiles[i * 2 + 1] if m.type == 1 else m.tiles[i * 4 + 1]


def tiles_of_chain(m, chain):
    res = []
    for y in range(1, m.h + 1):
        for x in range(1, m.w + 1):
            if tile_event(m, x, y) == chain:
                res.append((x, y))
    return res


def describe(e):
    t = e[0]
    n = ET.get(t, str(t))
    if t == 1:
        return f'Teleport to ({e[1]},{e[2]}) dir {e[3]} trans {e[5]} map {w(e, 6)}'
    if t == 2:
        return f'Door idx {e[2]} key {w(e, 6)} lock {e[1]} text {e[3]}/{e[4]} fail {w(e, 8)}'
    if t == 3:
        return f'Chest idx {e[4]} flags {e[5]:#x} text {e[3]} lock {e[1]} key {w(e, 6)}'
    if t == 4:
        return f'Text #{e[5]} pic {e[1]} trigger {e[2]}'
    if t == 6:
        return f'Trap ailment {e[1]} target {e[2]} dmg {e[4]}'
    if t == 9:
        return f'Reward type {e[1]} op {e[2]} target {e[4]} what {w(e, 6)} val {w(e, 8)}'
    if t == 10:
        return f'TileChg ({e[1]},{e[2]}) -> {w(e, 6)} map {w(e, 8)}'
    if t == 11:
        return f'Battle group {w(e, 6)}'
    if t == 13:
        return f'Cond {COND.get(e[1], e[1])} val {e[2]} cnt {e[3]} obj {w(e, 6)} else {w(e, 8) if w(e, 8) != NONE else "stop"}'
    if t == 14:
        return f'Action {ACT.get(e[1], e[1])} val {e[2]} cnt {e[3]} obj {w(e, 6)}'
    if t == 15:
        return f'Dice {e[1]}% else {w(e, 8)}'
    if t == 19:
        return f'Question #{e[1]} no-> {w(e, 8) if w(e, 8) != NONE else "stop"}'
    if t == 20:
        return f'Music {e[2]}'
    if t == 25:
        return f'Delay {w(e, 6)}ms'
    if t == 26:
        return f'PMCond type {e[1]} sub {e[2]} target {e[3]} val {w(e, 6)} else {w(e, 8)}'
    if t == 27:
        return f'Shake {w(e, 6)}'
    if t == 28:
        return f'ShowMap opts {e[1]:#x}'
    if t == 29:
        bits = int.from_bytes(e[1:6], 'big')
        vars_ = [(bits >> s) & 0x3ff for s in (30, 20, 10, 0)]
        return f'Toggle vars {[v for v in vars_ if v]} off {w(e, 6)} on {w(e, 8)}'
    if t == 30:
        v = (e[3] << 8) | e[4]
        b = int.from_bytes(e[5:8], 'big')
        return f'DynTile ({e[1]},{e[2]}) var {v} off {b >> 12} on {b & 0xfff} map {w(e, 8)}'
    if t == 31:
        return f'RectExpl ({e[1]},{e[2]}) {e[3]}x{e[4]} type {e[5]} map {w(e, 6)}'
    if t == 32:
        return f'VLine {list(e[1:10])}'
    return f'{n} {e[1:10].hex()}'


def dump(m, chain_filter=None):
    lines = []
    seen = set()
    for ci, head in enumerate(m.heads, 1):
        if chain_filter and ci not in chain_filter:
            continue
        tiles = tiles_of_chain(m, ci)
        chars = [i for i, c in enumerate(m.chars) if c[0] and c[3] == ci]
        lines.append(f'== Chain {ci} tiles {tiles[:8]}{"..." if len(tiles) > 8 else ""} chars {chars} automap {m.automap[ci - 1] if m.automap else "-"}')
        stack = [(head, 1)]
        local = set()
        while stack:
            i, d = stack.pop()
            while i != NONE and i < len(m.events) and i not in local:
                local.add(i)
                seen.add(i)
                e = m.events[i]
                lines.append('  ' * d + f'[{i}] {describe(e)}')
                if e[0] in (13, 26, 19, 15, 2) and w(e, 8) != NONE:
                    stack.append((w(e, 8), d + 1))
                i = nxt(e)
    orphans = [i for i in range(len(m.events)) if i not in seen]
    return '\n'.join(lines), orphans

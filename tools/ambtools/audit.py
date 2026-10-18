"""Deeper data checks than validate.py (which checks event references).

- teleport targets that are blocked (wall, blocking object or tile) or outside the map
- characters (monsters, NPCs, party members, objects) that start on a blocked tile or outside the map
- 3D maps: walkable floor at the map edge or passable walls (without an event) next to the outside
- chests and doors used by more than one map (often intended, listed for review)

Usage: python audit.py [Amberfiles dir] [map ...]
"""
import os
import struct
import sys
from collections import defaultdict

import ambcontainer as amb
import labdata as ld
import mapmodel as mm

A = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'german', 'Amberfiles')
ONLY = set(int(x) for x in sys.argv[2:])
TRAVEL = ['walk', 'horse', 'raft', 'ship', 'disc', 'eagle', 'fly', 'swim', 'broom', 'lizard', 'sandship', 'wasp']

maps = {}
for n in (1, 2, 3):
    for i, raw in amb.read_container(os.path.join(A, f'{n}Map_data.amb')).items():
        if raw:
            maps[i] = mm.parse(raw)
labs = {k: ld.parse(v) for k, v in amb.read_container(os.path.join(A, '2Lab_data.amb')).items() if v}
icon_data = {}
for k, v in amb.read_container(os.path.join(A, 'Icon_data.amb')).items():
    if v:
        n = struct.unpack('>H', v[:2])[0]
        icon_data[k] = [struct.unpack('>I', v[2 + i * 8:6 + i * 8])[0] for i in range(n)]


def allows(flags, travel):
    return not flags & 0x80 and flags & (1 << (8 + travel))


def passable(m, x, y, travel=0):
    """1-based coordinates. Returns (passable, reason)."""
    if not (1 <= x <= m.w and 1 <= y <= m.h):
        return False, 'outside the map'
    if m.shared:
        return True, ''
    i = (y - 1) * m.w + (x - 1)
    if m.type == 1:
        block = m.tiles[i * 2]
        lab = labs.get(m.header[6])
        if block == 0:
            return True, ''
        if block == 255:
            return False, 'map border'
        if lab is None:
            return True, ''
        if block > 100:
            wall = lab.walls[block - 101] if block - 101 < len(lab.walls) else None
            if wall is None:
                return False, f'wall {block} missing in labdata'
            f = struct.unpack('>I', wall[0][:4])[0]
            return bool(allows(f, travel)), f'wall {block}'
        group = lab.object_groups[block - 1] if block - 1 < len(lab.object_groups) else None
        if group is None:
            return False, f'object group {block} missing'
        for k in range(8):
            idx = struct.unpack('>H', group[8 + k * 8:10 + k * 8])[0]
            if idx:
                f = struct.unpack('>I', lab.objects[idx - 1][:4])[0]
                if not allows(f, travel):
                    return False, f'object group {block}'
        return True, ''
    tiles = icon_data.get(m.header[6])
    if tiles is None:
        return True, ''
    back = m.tiles[i * 4]
    front = (m.tiles[i * 4 + 2] << 8) | m.tiles[i * 4 + 3]
    if front and (back == 0 or not tiles[front - 1] & 0x20):
        f, what = tiles[front - 1], f'tile {front}'
    elif back:
        f, what = tiles[back - 1], f'tile {back}'
    else:
        return True, ''
    if f & 0x03800000:                      # chairs and beds: characters sit or sleep there
        return True, ''
    return bool(allows(f, travel)), what


problems = defaultdict(list)
chest_use, door_use = defaultdict(set), defaultdict(set)

# tiles changed by tile change events anywhere: (map, x, y) -> new tile values
tile_changes = defaultdict(set)
for idx, m in maps.items():
    for e in m.events:
        if e[0] == 10:
            target = struct.unpack('>H', e[8:10])[0] or idx
            tile_changes[(target, e[1], e[2])].add(struct.unpack('>H', e[6:8])[0])


def changed(target, x, y):
    c = tile_changes.get((target, x, y))
    return f' (changed by a tile change event to {sorted(c)})' if c else ''


def has_event(m, x, y):
    i = (y - 1) * m.w + (x - 1)
    return m.tiles[i * 2 + 1] if m.type == 1 else m.tiles[i * 4 + 1]

for idx, m in sorted(maps.items()):
    if ONLY and idx not in ONLY:
        continue
    reachable = set()
    for head in m.heads:
        e = head
        while e != 0xffff and e < len(m.events) and e not in reachable:
            reachable.add(e)
            e = mm.nxt(m.events[e])
    for ei in sorted(reachable):
        e = m.events[ei]
        t = e[0]
        if t == 1:
            x, y = e[1], e[2]
            target = struct.unpack('>H', e[6:8])[0] or idx
            tm = maps.get(target)
            if tm and x and y and not tm.shared:
                ok, why = passable(tm, x, y, 0)
                if not ok and not (tm.type == 2 and tm.flags & 0x0100):   # world maps: travel type decides
                    problems[idx].append(f'event {ei}: teleport to map {target} ({x},{y}) lands on {why}{changed(target, x, y)}')
        elif t == 3:
            chest_use[e[4] + (256 if e[5] & 4 else 0)].add(idx)
        elif t == 2:
            door_use[e[2]].add(idx)
    for ci, c in enumerate(m.chars):
        if c[0] == 0 or ci >= len(m.positions):
            continue
        pos = m.positions[ci]
        x, y = pos[0], pos[1]
        typ = c[2] & 3
        if (x == 0 and y == 0) or typ == 3:  # map objects are interaction triggers, often on statues etc.
            continue
        travel = (c[1] if c[1] < 12 else 0) if m.type == 1 else 0   # 2D characters always use walk (remake)
        if travel == 6:                       # flying characters ignore collisions
            continue
        ok, why = passable(m, x, y, travel)
        if not ok:
            kind = ['party member', 'NPC', 'monster group', 'object'][typ]
            problems[idx].append(f'char {ci} ({kind} {c[0]}, {TRAVEL[travel]}) starts at ({x},{y}) on {why}{changed(idx, x, y)}')
    if m.type == 1 and not m.shared:
        for y in range(1, m.h + 1):
            for x in range(1, m.w + 1):
                ok, why = passable(m, x, y)
                if not ok or has_event(m, x, y):    # exits (doors, stairs) have events
                    continue
                edge = x in (1, m.w) or y in (1, m.h)
                if edge:
                    problems[idx].append(f'walkable tile at the map edge ({x},{y}) {why}'.rstrip())
                    continue
                if why.startswith('wall'):
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        b = m.tiles[((y + dy - 1) * m.w + (x + dx - 1)) * 2]
                        if b == 255:
                            problems[idx].append(f'passable {why} at ({x},{y}) next to the map border (exit?)')
                            break

for idx in sorted(problems):
    print(f'map {idx}:')
    for p in problems[idx]:
        print('  ' + p)
print()
print('chests used in more than one map:', {k: sorted(v) for k, v in sorted(chest_use.items()) if len(v) > 1})
print('doors used in more than one map:', {k: sorted(v) for k, v in sorted(door_use.items()) if len(v) > 1})
print(f'checked {len(maps) if not ONLY else len(ONLY)} maps, {sum(len(v) for v in problems.values())} findings')

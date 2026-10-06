"""Static validation of map event references in Ambermoon Advanced data."""
import os
import struct
import sys

import ambcontainer as amb
import mapmodel as mm

A = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\Robert\source\repos\Ambermoon-Advanced\german\Amberfiles'
ONLY = set(int(x) for x in sys.argv[2:])

maps = {}
text_counts = {}
for n in (1, 2, 3):
    texts = amb.read_container(os.path.join(A, f'{n}Map_texts.amb'))
    for i, raw in amb.read_container(os.path.join(A, f'{n}Map_data.amb')).items():
        if raw:
            assert i not in maps, f'map {i} in multiple containers'
            maps[i] = mm.parse(raw)
            t = texts.get(i, b'')
            text_counts[i] = struct.unpack('>H', t[:2])[0] if len(t) >= 2 else 0

groups = amb.read_container(os.path.join(A, 'Monster_groups.amb'))
chests = amb.read_container(os.path.join(A, 'Save.00', 'Chest_data.amb'))
n_items = len(os.listdir(os.path.join(A, 'AllTexts', 'Objects.amb')))

problems = []


def bad(m, ev, msg):
    problems.append(f'map {m} event {ev}: {msg}')


for idx, m in sorted(maps.items()):
    if ONLY and idx not in ONLY:
        continue
    ne = len(m.events)
    texts = text_counts.get(idx)
    # reachable events: chains referenced by tiles or characters
    used_chains = set(c[3] for c in m.chars if c[0] and c[3])
    if not m.shared:
        for y in range(1, m.h + 1):
            for x in range(1, m.w + 1):
                ev = mm.tile_event(m, x, y)
                if ev:
                    used_chains.add(ev)
    reachable = set()
    stack = [m.heads[c - 1] for c in used_chains if c <= len(m.heads)]
    while stack:
        i = stack.pop()
        if i == 0xffff or i >= ne or i in reachable:
            continue
        reachable.add(i)
        e = m.events[i]
        stack.append(mm.nxt(e))
        if e[0] in (13, 26, 19, 15, 2, 3):
            stack.append(mm.w(e, 8))
    for i, e in enumerate(m.events):
        if i not in reachable:
            continue
        t = e[0]
        nx = mm.nxt(e)
        if nx != 0xffff and nx >= ne:
            bad(idx, i, f'next {nx} out of range')
        if t in (13, 26, 19, 15) and mm.w(e, 8) != 0xffff and mm.w(e, 8) >= ne:
            bad(idx, i, f'else {mm.w(e, 8)} out of range')
        if t == 2 and mm.w(e, 8) != 0xffff and mm.w(e, 8) >= ne:
            bad(idx, i, f'door fail event {mm.w(e, 8)} out of range')
        if t == 3 and mm.w(e, 8) != 0xffff and mm.w(e, 8) >= ne:
            bad(idx, i, f'chest fail event {mm.w(e, 8)} out of range')

        def check_text(ti, what):
            if ti != 0xff and texts is not None and ti >= texts:
                bad(idx, i, f'{what} text #{ti} but map has only {texts} texts')

        if t == 4:
            check_text(e[5], 'popup')
        elif t == 19:
            check_text(e[1], 'question')
        elif t == 2:
            check_text(e[3], 'door')
            check_text(e[4], 'door unlock')
        elif t == 3:
            check_text(e[3], 'chest')
            ci = e[4] + (256 if e[5] & 4 else 0) + 1
            if ci not in chests or not chests[ci]:
                bad(idx, i, f'chest data {ci - 1} missing')
        elif t == 12:
            check_text(e[1], 'place closed')
            check_text(e[5], 'place use')
        elif t == 11:
            g = mm.w(e, 6)
            if g not in groups or not groups[g]:
                bad(idx, i, f'monster group {g} missing')
        elif t == 1:
            tm = mm.w(e, 6) or idx
            if tm not in maps:
                bad(idx, i, f'teleport to missing map {tm}')
            else:
                tmap = maps[tm]
                if e[1] > tmap.w or e[2] > tmap.h:
                    bad(idx, i, f'teleport ({e[1]},{e[2]}) outside map {tm} ({tmap.w}x{tmap.h})')
        elif t == 10:
            tm = mm.w(e, 8) or idx
            if tm in maps and (e[1] > maps[tm].w or e[2] > maps[tm].h):
                bad(idx, i, f'tile change ({e[1]},{e[2]}) outside map {tm}')
        elif t in (13, 14) and e[1] in (6, 7):
            it = mm.w(e, 6)
            if it == 0 or it > n_items:
                bad(idx, i, f'item {it} invalid')
    for ci, c in enumerate(m.chars):
        if c[0] and (c[2] & 3) == 2 and (c[0] not in groups or not groups[c[0]]):
            problems.append(f'map {idx} char {ci}: monster group {c[0]} missing')
        if c[0] and c[3] and c[3] > len(m.heads):
            problems.append(f'map {idx} char {ci}: event chain {c[3]} missing')
    for y in range(1, m.h + 1):
        for x in range(1, m.w + 1):
            if m.shared:
                break
            ev = mm.tile_event(m, x, y)
            if ev and ev > len(m.heads):
                problems.append(f'map {idx} tile ({x},{y}): event chain {ev} missing')

print('\n'.join(problems) if problems else 'No problems found.')
print(f'checked {len(ONLY) if ONLY else len(maps)} maps')

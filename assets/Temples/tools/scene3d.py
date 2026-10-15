"""Tiny raycaster for temple mockups: renders a 3D view (walls with overlays, floor and ceiling textures,
billboard objects, floor decals like mosaics) from the original game textures with any palette.

Block size 512x512x341 like the game, so the objects' mapped sizes can be used directly.
"""
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'tools', 'ambtools'))
import render3d as r  # noqa: E402

BLOCK = 512.0
WALL_H = 341.0 / BLOCK
EYE_Z = WALL_H * 0.5


class Assets:
    def __init__(self, data=r.DEFAULT_DATA):
        self.walls = r.merged(data, 'Wall3D.amb')
        self.objects = r.merged(data, 'Object3D.amb')
        self.overlays = r.merged(data, 'Overlay3D.amb')
        self.floors = r.load(data, 'Floors.amb')
        self.palettes = r.palettes(data)
        self.labs = r.labdatas(data)
        self.ovl_size = {}
        for lab in self.labs.values():
            for header, ovs in lab.walls:
                for ov in ovs:
                    self.ovl_size.setdefault(ov[1], (ov[4], ov[5]))
        self._cache = {}

    def wall(self, base, overlays=()):
        """overlays: (overlay index, x, y[, blend]) with x 'l', 'r', 'c' or pixels."""
        key = ('w', base, tuple(overlays))
        if key not in self._cache:
            img = bytearray(r.texture4(self.walls[base], 128, 80))
            for ov in overlays:
                idx, px, py = ov[:3]
                blend = ov[3] if len(ov) > 3 else 1
                w, h = self.ovl_size[idx]
                o = r.texture4(self.overlays[idx], w, h)
                px = {'l': 0, 'r': 128 - w, 'c': (128 - w) // 2}.get(px, px)
                px &= 0xf8          # the Amiga uses 8 pixel boundaries
                for y in range(h):
                    for x in range(w):
                        v = o[y * w + x]
                        if (v or not blend) and 0 <= px + x < 128 and 0 <= py + y < 80:
                            img[(py + y) * 128 + px + x] = v
            self._cache[key] = img
        return self._cache[key]

    def lab_wall(self, lab, index):
        """Wall exactly as a labdata defines it (index 101-based like the sheets)."""
        header, ovs = self.labs[lab].walls[index - 101]
        return self.wall(header[4], [(o[1], o[2], o[3], o[0]) for o in ovs])

    def obj(self, lab, index):
        """Object data (1-based) of a labdata: (pixels, w, h, mapped w, mapped h, flat)."""
        key = ('o', lab, index)
        if key not in self._cache:
            o = self.labs[lab].objects[index - 1]
            flags, tex, frames, _, w, h, mw, mh = struct.unpack('>IHBBBBHH', o)
            self._cache[key] = (r.texture4(self.objects[tex], w, h), w, h, mw / BLOCK, mh / BLOCK, bool(flags & 0x08))
        return self._cache[key]

    def obj_tex(self, tex):
        """Object by texture index, with the sizes of the first labdata that uses it."""
        for lab in sorted(self.labs):
            for i, o in enumerate(self.labs[lab].objects):
                if struct.unpack('>H', o[4:6])[0] == tex:
                    return self.obj(lab, i + 1)
        raise KeyError(tex)

    def floor(self, index):
        key = ('f', index)
        if key not in self._cache:
            self._cache[key] = r.planar4(self.floors[index], 64, 64)
        return self._cache[key]


def render(assets, pal, grid, legend, cam, objects=(), floor=None, ceiling=None, floor_col=4, ceil_col=5,
           size=(208, 144), fov=72):
    """grid: list of strings, '.' is free; legend: char -> wall image (128x80 bytes).
    cam: (x, y, angle in degrees, 0 = north/up). objects: (x, y, z, obj tuple) in block units."""
    W, H = size
    hz = H / 2
    f = (W / 2) / math.tan(math.radians(fov) / 2)
    cx, cy, ang = cam
    dx, dy = math.sin(math.radians(ang)), -math.cos(math.radians(ang))
    px, py = -dy, dx            # camera plane (right)
    out = bytearray(W * H)
    zbuf = [1e9] * W
    flr = assets.floor(floor) if floor else None
    ceil = assets.floor(ceiling) if ceiling else None
    decals = [o for o in objects if o[3][5]]
    sprites = [o for o in objects if not o[3][5]]

    def cell(x, y):
        if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
            return grid[y][x]
        return '#'

    # floor and ceiling
    for y in range(H):
        if y == int(hz):
            continue
        is_floor = y > hz
        dist = (EYE_Z if is_floor else WALL_H - EYE_Z) * f / abs(y + 0.5 - hz)
        for x in range(W):
            k = (x + 0.5 - W / 2) / f
            rx, ry = dx + px * k, dy + py * k
            wx, wy = cx + rx * dist, cy + ry * dist
            v = 0
            if is_floor:
                for ox, oy, oz, (img, w, h, mw, mh, _) in decals:
                    u = (wx - ox) / mw + 0.5
                    t = (wy - oy) / mh + 0.5
                    if 0 <= u < 1 and 0 <= t < 1:
                        v = img[int(t * h) * w + int(u * w)]
                        if v:
                            break
            if not v:
                tex = flr if is_floor else ceil
                if tex:
                    v = tex[int((wy % 1) * 64) * 64 + int((wx % 1) * 64)]
                else:
                    v = floor_col if is_floor else ceil_col
            out[y * W + x] = v

    # walls (DDA)
    for x in range(W):
        k = (x + 0.5 - W / 2) / f
        rx, ry = dx + px * k, dy + py * k
        mx, my = int(cx), int(cy)
        ddx = abs(1 / rx) if rx else 1e30
        ddy = abs(1 / ry) if ry else 1e30
        sx, sdx = (-1, (cx - mx) * ddx) if rx < 0 else (1, (mx + 1 - cx) * ddx)
        sy, sdy = (-1, (cy - my) * ddy) if ry < 0 else (1, (my + 1 - cy) * ddy)
        side = 0
        for _ in range(64):
            if sdx < sdy:
                sdx += ddx; mx += sx; side = 0
            else:
                sdy += ddy; my += sy; side = 1
            if cell(mx, my) != '.':
                break
        ch = cell(mx, my)
        dist = (sdx - ddx) if side == 0 else (sdy - ddy)
        dist = max(dist, 1e-3)
        zbuf[x] = dist
        if side == 0:
            u = cy + dist * ry
            u -= math.floor(u)
            if rx < 0:
                u = 1 - u
        else:
            u = cx + dist * rx
            u -= math.floor(u)
            if ry > 0:
                u = 1 - u
        img = legend.get(ch)
        if img is None:
            continue
        top = hz - (WALL_H - EYE_Z) * f / dist
        bot = hz + EYE_Z * f / dist
        tx = min(127, int(u * 128))
        for y in range(max(0, int(top)), min(H, int(math.ceil(bot)))):
            t = (y + 0.5 - top) / (bot - top)
            if 0 <= t < 1:
                out[y * W + x] = img[int(t * 80) * 128 + tx]

    # sprites, far to near
    def depth(o):
        return (o[0] - cx) * dx + (o[1] - cy) * dy
    for ox, oy, oz, (img, w, h, mw, mh, _) in sorted(sprites, key=depth, reverse=True):
        rel_x, rel_y = ox - cx, oy - cy
        d = rel_x * dx + rel_y * dy
        if d <= 0.05:
            continue
        lat = rel_x * px + rel_y * py
        sxc = W / 2 + lat * f / d
        sw = mw * f / d
        bot = hz + (EYE_Z - oz) * f / d
        top = bot - mh * f / d
        for x in range(max(0, int(sxc - sw / 2)), min(W, int(sxc + sw / 2) + 1)):
            if zbuf[x] <= d:
                continue
            u = (x + 0.5 - (sxc - sw / 2)) / sw
            if not 0 <= u < 1:
                continue
            for y in range(max(0, int(top)), min(H, int(math.ceil(bot)))):
                t = (y + 0.5 - top) / (bot - top)
                if 0 <= t < 1:
                    v = img[int(t * h) * w + int(u * w)]
                    if v:
                        out[y * W + x] = v
    return out, W, H

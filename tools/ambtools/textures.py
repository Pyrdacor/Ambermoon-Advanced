"""4-bit packed 3D textures (walls, objects, overlays), palettes and a tiny PNG writer."""
import math
import struct
import zlib


def decode_texture(data, width, height):
    """Returns rows of palette indices. Data is stored per row in 8 pixel chunks, 4 planes each."""
    chunks = (width + 7) // 8
    rows = []
    p = 0
    for _ in range(height):
        row = []
        for _c in range(chunks):
            planes = data[p:p + 4]
            p += 4
            for x in range(8):
                v = 0
                for k in range(4):
                    v |= ((planes[k] >> (7 - x)) & 1) << k
                row.append(v)
        rows.append(row[:width])
    return rows


def encode_texture(rows, width):
    assert width % 8 == 0
    out = bytearray()
    for row in rows:
        assert len(row) == width
        for c in range(width // 8):
            planes = [0, 0, 0, 0]
            for x in range(8):
                v = row[c * 8 + x]
                assert 0 <= v < 16
                for k in range(4):
                    planes[k] |= ((v >> k) & 1) << (7 - x)
            out += bytes(planes)
    return bytes(out)


def decode_palette(data):
    """32 entries, 2 bytes each: 0R GB (4 bits per channel)."""
    pal = []
    for i in range(32):
        r = data[i * 2] & 0x0f
        g = data[i * 2 + 1] >> 4
        b = data[i * 2 + 1] & 0x0f
        pal.append((r * 17, g * 17, b * 17))
    return pal


def write_png(path, rows, palette, scale=1):
    h = len(rows)
    w = len(rows[0])
    raw = bytearray()
    for row in rows:
        line = bytearray()
        for v in row:
            line += bytes(palette[v]) * scale
        for _ in range(scale):
            raw += b'\0' + line
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', w * scale, h * scale, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


def read_png(path):
    """Minimal PNG reader (8 bit RGB/RGBA, not interlaced). Returns (width, height, rows of (r, g, b))."""
    data = open(path, 'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    p, idat = 8, b''
    while p < len(data):
        n, tag = struct.unpack('>I4s', data[p:p + 8])
        body = data[p + 8:p + 8 + n]
        if tag == b'IHDR':
            w, h, depth, ctype, _, _, interlace = struct.unpack('>IIBBBBB', body)
            assert depth == 8 and ctype in (2, 6) and not interlace, 'only 8 bit RGB/RGBA, not interlaced'
        elif tag == b'IDAT':
            idat += body
        p += 12 + n
    bpp = 3 if ctype == 2 else 4
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows, prev, o = [], bytearray(stride), 0
    for _ in range(h):
        f = raw[o]
        line = bytearray(raw[o + 1:o + 1 + stride])
        o += 1 + stride
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                line[i] = (line[i] + a) & 0xff
            elif f == 2:
                line[i] = (line[i] + b) & 0xff
            elif f == 3:
                line[i] = (line[i] + ((a + b) >> 1)) & 0xff
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 0xff
        rows.append([tuple(line[x * bpp:x * bpp + 3]) for x in range(w)])
        prev = line
    return w, h, rows


def downscale(rows, w, h):
    """Area average (box filter with fractional coverage) to w x h. Returns rows of float (r, g, b)."""
    sh, sw = len(rows), len(rows[0])
    fx, fy = sw / w, sh / h
    # first horizontally, then vertically
    def weights(n_src, n_dst, f):
        res = []
        for d in range(n_dst):
            a, b = d * f, (d + 1) * f
            ws = []
            for s in range(int(a), min(n_src, int(math.ceil(b)))):
                cov = min(b, s + 1) - max(a, s)
                if cov > 0:
                    ws.append((s, cov))
            res.append(ws)
        return res
    wx, wy = weights(sw, w, fx), weights(sh, h, fy)
    tmp = []
    for row in rows:
        out = []
        for ws in wx:
            t = sum(c for _, c in ws)
            out.append(tuple(sum(row[s][k] * c for s, c in ws) / t for k in range(3)))
        tmp.append(out)
    res = []
    for ws in wy:
        t = sum(c for _, c in ws)
        res.append([tuple(sum(tmp[s][x][k] * c for s, c in ws) / t for k in range(3)) for x in range(w)])
    return res


def quantize(rows, palette, allowed, dither=0.0):
    """Map true colour rows to palette indices (only the allowed ones). dither: Floyd-Steinberg strength 0..1."""
    h, w = len(rows), len(rows[0])
    buf = [[list(p) for p in row] for row in rows]
    out = [[0] * w for _ in range(h)]

    def dist(c, p):
        dr, dg, db = c[0] - p[0], c[1] - p[1], c[2] - p[2]
        rm = (c[0] + p[0]) / 2
        return (2 + rm / 256) * dr * dr + 4 * dg * dg + (2 + (255 - rm) / 256) * db * db
    for y in range(h):
        for x in range(w):
            c = buf[y][x]
            i = min(allowed, key=lambda k: dist(c, palette[k]))
            out[y][x] = i
            if dither:
                err = [(c[k] - palette[i][k]) * dither for k in range(3)]
                for dx, dy, f in ((1, 0, 7 / 16), (-1, 1, 3 / 16), (0, 1, 5 / 16), (1, 1, 1 / 16)):
                    if 0 <= x + dx < w and y + dy < h:
                        n = buf[y + dy][x + dx]
                        for k in range(3):
                            n[k] += err[k] * f
    return out

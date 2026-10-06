"""4-bit packed 3D textures (walls, objects, overlays), palettes and a tiny PNG writer."""
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

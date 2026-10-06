"""Parse and serialize labdata (2Lab_data.amb / 3Lab_data.amb sub-files) losslessly."""
import struct


class Labdata:
    pass


def parse(raw):
    ld = Labdata()
    ld.header = bytearray(raw[:8])
    p = 8
    n = struct.unpack('>H', raw[p:p + 2])[0]
    p += 2
    ld.object_groups = [bytearray(raw[p + i * 66:p + i * 66 + 66]) for i in range(n)]
    p += 66 * n
    n = struct.unpack('>H', raw[p:p + 2])[0]
    p += 2
    ld.objects = [bytearray(raw[p + i * 14:p + i * 14 + 14]) for i in range(n)]
    p += 14 * n
    n = struct.unpack('>H', raw[p:p + 2])[0]
    p += 2
    ld.walls = []
    for _ in range(n):
        header = bytearray(raw[p:p + 8])
        p += 8
        overlays = [bytearray(raw[p + k * 6:p + k * 6 + 6]) for k in range(header[7])]
        p += 6 * header[7]
        ld.walls.append((header, overlays))
    ld.tail = raw[p:]
    return ld


def serialize(ld):
    out = bytearray(ld.header)
    out += struct.pack('>H', len(ld.object_groups))
    for g in ld.object_groups:
        out += g
    out += struct.pack('>H', len(ld.objects))
    for o in ld.objects:
        out += o
    out += struct.pack('>H', len(ld.walls))
    for header, overlays in ld.walls:
        assert header[7] == len(overlays)
        out += header
        for o in overlays:
            out += o
    out += ld.tail
    return bytes(out)

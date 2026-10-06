"""Read-only access to Ambermoon container files (AMPC, AMNP, AMBR, AMNC, JH, LOB).

Writing is done with AmbermoonPack (AmbermoonTools). Unpacking a container
with "AmbermoonPack UNPACK" and packing it again with default options
reproduces the original file byte by byte.
"""
import struct


def lob_decompress(data, size):
    out = bytearray()
    p = 0
    while len(out) < size:
        header = data[p]
        p += 1
        for _ in range(8):
            if header & 0x80 == 0:  # match
                b1, b2 = data[p], data[p + 1]
                p += 2
                length = (b1 & 0x0f) + 3
                offset = ((b1 << 4) & 0xff00) | b2
                start = len(out) - offset
                for k in range(length):
                    out.append(out[start + k])
            else:
                out.append(data[p])
                p += 1
            if len(out) == size:
                break
            header = (header << 1) & 0xff
    return bytes(out)


def jh_crypt(data, key):
    data = bytearray(data)
    d0 = key
    for i in range(0, len(data), 2):
        if i == len(data) - 1:
            value = data[i] << 8
        else:
            value = (data[i] << 8) | data[i + 1]
        value ^= d0
        data[i] = value >> 8
        if i + 1 < len(data):
            data[i + 1] = value & 0xff
        d1 = d0
        d0 = (d0 << 4) & 0xffff
        d0 = (d0 + d1 + 87) & 0xffff
    return bytes(data)


def _decode(f, container_type, number):
    if len(f) >= 4 and f[:2] == b'JH':
        key = struct.unpack('>I', f[:4])[0]
        f = jh_crypt(f[4:], ((key >> 16) ^ (key & 0xffff)) & 0xffff)
    elif container_type == b'AMNC':
        f = jh_crypt(f, number)
    if f[:4] == b'\x01LOB':
        size = struct.unpack('>I', f[4:8])[0] & 0xffffff
        if container_type == b'AMNP':
            rest = jh_crypt(f[8:], number)
            return lob_decompress(rest[4:], size)
        return lob_decompress(f[12:], size)
    if container_type == b'AMNP':
        return jh_crypt(f[4:], number)
    return f


def read_container(path):
    """Returns {1-based file number: decoded bytes}. Empty entries are b''."""
    with open(path, 'rb') as fh:
        d = fh.read()
    ctype = d[:4]
    count = struct.unpack('>H', d[4:6])[0]
    kind = count >> 14
    count &= 0x3ff
    if kind not in (0, 2):
        raise NotImplementedError('Section based containers are not supported')
    entry_size = 4 if kind == 0 else 2
    sizes = struct.unpack('>%d%s' % (count, 'I' if entry_size == 4 else 'H'), d[6:6 + entry_size * count])
    offset = 6 + entry_size * count
    files = {}
    for i, size in enumerate(sizes, 1):
        files[i] = _decode(d[offset:offset + size], ctype, i) if size else b''
        offset += size
    return files

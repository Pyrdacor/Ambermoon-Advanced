"""Transpose a Sonic Arranger song by changing the note transpose of every voice in the overtable.

Works on the export format (Music.amb entries, starts with the song table pointer $28) and on the
editable module format (.sa, "SOARV1.0" with OVTB chunk). Voices can be excluded (e.g. drums).

Usage: python transpose_music.py <in> <out> <semitones> [--skip-voices 3 4]
       python transpose_music.py --amb <Music.amb> <song id> <out> <semitones> [--skip-voices ...]
"""
import argparse
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'ambtools'))


def overtable(d):
    """(offset, number of positions) of the overtable."""
    if d[:8] == b'SOARV1.0':
        p = d.index(b'OVTB')
        n = struct.unpack('>I', d[p + 4:p + 8])[0]
        return p + 8, n
    for base in range(0, len(d) - 0x24, 2):
        if struct.unpack('>I', d[base:base + 4])[0] == 0x28:
            ptrs = struct.unpack('>7I', d[base:base + 28])
            if all(ptrs[k] < ptrs[k + 1] for k in (0, 1, 2)) and ptrs[6] < len(d) - base:
                return base + ptrs[1], (ptrs[2] - ptrs[1]) // 16
    raise ValueError('no Sonic Arranger data found')


def transpose(d, semitones, skip=()):
    d = bytearray(d)
    off, n = overtable(d)
    for pos in range(n):
        for v in range(4):
            if v + 1 in skip:
                continue
            i = off + pos * 16 + v * 4 + 3
            t = struct.unpack('b', d[i:i + 1])[0] + semitones
            if not -128 <= t <= 127:
                raise ValueError(f'transpose out of range at position {pos}, voice {v + 1}')
            d[i] = t & 0xff
    return bytes(d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--amb')
    ap.add_argument('args', nargs='+')
    ap.add_argument('--skip-voices', type=int, nargs='*', default=[])
    a = ap.parse_args()
    if a.amb:
        import ambcontainer as amb
        song, out, semis = int(a.args[0]), a.args[1], int(a.args[2])
        data = amb.read_container(a.amb)[song]
    else:
        src, out, semis = a.args[0], a.args[1], int(a.args[2])
        data = open(src, 'rb').read()
    open(out, 'wb').write(transpose(data, semis, a.skip_voices))
    print('written', out)


if __name__ == '__main__':
    main()

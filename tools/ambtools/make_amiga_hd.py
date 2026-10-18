"""Build an FS-UAE hard drive folder with Ambermoon Advanced for tests on the Amiga.

The drive is made of:
- the boot files (C, Devs, L, S, System) of an existing bootable Ambermoon drive,
- the latest german Advanced release (loader, music, intro, ...),
- the current german Advanced data of this repo (git-tracked files only),
- Save.00 of this repo, also copied to Initial (like make_testdata.py) and to the slots Save.01-10,
- an AM2_CPU of your choice (default: code_changes/AM2_CPU).

Usage: python make_amiga_hd.py <output dir> [--exe <AM2_CPU>] [--extra <file>...] [--boot <drive>] [--release <zip>]

Files given with --extra are copied to Amberfiles too (e.g. AM2_CPU_OLD for a comparison).
"""
import argparse
import os
import shutil
import subprocess
import zipfile

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
FSUAE_DRIVES = os.path.join(os.path.expanduser('~'), 'Documents', 'FS-UAE', 'Hard Drives')
DEFAULT_BOOT = os.path.join(FSUAE_DRIVES, 'AmbermoonDE')
DEFAULT_RELEASE = os.path.join(REPO, 'releases', 'german', 'ambermoon_advanced_german_1.33_extracted.zip')
BOOT_DIRS = ['C', 'Devs', 'L', 'S', 'System']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('output')
    ap.add_argument('--exe', default=os.path.join(REPO, 'code_changes', 'AM2_CPU'))
    ap.add_argument('--extra', nargs='*', default=[])
    ap.add_argument('--boot', default=DEFAULT_BOOT)
    ap.add_argument('--release', default=DEFAULT_RELEASE)
    args = ap.parse_args()

    if os.path.exists(args.output):
        shutil.rmtree(args.output)
    os.makedirs(args.output)

    for name in BOOT_DIRS:
        shutil.copytree(os.path.join(args.boot, name), os.path.join(args.output, name))

    with zipfile.ZipFile(args.release) as z:
        z.extractall(args.output)

    # git-tracked german data only (no unpacked container folders)
    files = subprocess.run(['git', 'ls-files', 'german/Amberfiles'], cwd=REPO, capture_output=True, text=True,
                           check=True).stdout.split('\n')
    target = os.path.join(args.output, 'Amberfiles')
    for rel in files:
        if not rel:
            continue
        sub = rel[len('german/Amberfiles/'):]
        top = sub.split('/')[0]
        if top in ('AllTexts', '.gitignore') or top.endswith('.bat'):
            continue
        dest = os.path.join(target, *sub.split('/'))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(os.path.join(REPO, *rel.split('/')), dest)

    shutil.rmtree(os.path.join(target, 'Initial'), ignore_errors=True)
    shutil.copytree(os.path.join(target, 'Save.00'), os.path.join(target, 'Initial'))
    # The release only has empty placeholder slots (Episode 3 data). Fill them with the current Save.00 so every
    # slot matches the data (e.g. the automap entries of new 3D maps).
    for i in range(1, 11):
        slot = os.path.join(target, 'Save.%02d' % i)
        shutil.rmtree(slot, ignore_errors=True)
        shutil.copytree(os.path.join(target, 'Save.00'), slot)
    shutil.copyfile(args.exe, os.path.join(target, 'AM2_CPU'))
    for extra in args.extra:
        shutil.copyfile(extra, os.path.join(target, os.path.basename(extra)))
    print('Amiga drive written to', args.output)


if __name__ == '__main__':
    main()

"""Build a complete game data folder for testing with the remake.

The Advanced Amberfiles folder lacks files like music, intro and the original
executables. This script extracts an original version (default: german 1.20)
and puts the Advanced files on top. Save.00 is also copied to Initial.

Only german is supported for now (code_changes/AM2_CPU is the german executable).

Usage: python make_testdata.py <output dir> [--base <extracted zip>]

Then start the remake with:
  Ambermoon.net --data <output dir>/Amberfiles --skip-intro --load 0 --cheat 3 "teleport 483 22 9 down" --screenshot 6 --exit-after 8
"""
import argparse
import os
import shutil
import zipfile

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
DEFAULT_BASE = r'C:\Users\Robert\source\repos\Ambermoon\Disks\German\ambermoon_german_1.20_extracted.zip'
LANGUAGE = 'german'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('output')
    ap.add_argument('--base', default=DEFAULT_BASE)
    args = ap.parse_args()

    if os.path.exists(args.output):
        shutil.rmtree(args.output)
    os.makedirs(args.output)
    with zipfile.ZipFile(args.base) as z:
        z.extractall(args.output)

    target = os.path.join(args.output, 'Amberfiles')
    source = os.path.join(REPO, LANGUAGE, 'Amberfiles')
    for name in os.listdir(source):
        path = os.path.join(source, name)
        if name == 'AllTexts' or name.endswith('.bat'):
            continue
        if os.path.isdir(path):
            shutil.rmtree(os.path.join(target, name), ignore_errors=True)
            shutil.copytree(path, os.path.join(target, name))
        else:
            shutil.copyfile(path, os.path.join(target, name))

    shutil.rmtree(os.path.join(target, 'Initial'), ignore_errors=True)
    shutil.copytree(os.path.join(source, 'Save.00'), os.path.join(target, 'Initial'))
    shutil.copyfile(os.path.join(REPO, 'code_changes', 'AM2_CPU'), os.path.join(target, 'AM2_CPU'))
    print('Test data written to', target)


if __name__ == '__main__':
    main()

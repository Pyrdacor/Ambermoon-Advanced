#!/bin/sh
# port onto a fresh copy of the base commit, build, compare
set -e
W="$(cd "$(dirname "$0")/.." && pwd)"
cd "$W"
ADV_REPO="${ADV_REPO:-/c/Users/Robert/source/repos/Ambermoon-Advanced}"
VASM="$ADV_REPO/code_changes/vasmm68k_mot.exe"
rm -rf work && mkdir work && git -C "$ADV_REPO" archive 6c2a4997 code_changes/AmbermoonSource | tar -x -C work --strip-components=2
python -I tools/port.py work/src | tail -2
python -I tools/build.py work/src "$W/work.bin" | tail -1
(cd work/src && "$VASM" -m68030 -Fhunkexe -o "$W/cmp/work.bin" -L "$W/cmp/work.lst" -nosym -kick1hunks -keepempty -no-opt -align AMBERMOON.S > "$W/cmp/work.log" 2>&1)
grep -c "warning 58" cmp/work.log || true
python -I tools/bincmp.py cmp/adv.bin cmp/adv.lst cmp/work.bin cmp/work.lst cmp/advwork | tail -1
python -I tools/review.py | tail -1
python -I tools/relcheck.py | head -1
python -I tools/labelcheck.py

#!/bin/sh
# Builds AM2_CPU_CHEAT (for tests) from the source code in AmbermoonSource/src and writes it to this folder.
# In the map screens, Amiga + key calls the diagnostic functions of DIAGNOST.S:
#   t = jump to map (enter the number), z = toggle super chicken (walk through walls),
#   o = kill all monsters, p = heal the party, a = next travel mode, i = status (map, position),
#   s = select music, d = event tracer, f = minimap, k = examine all monsters, y = repair weight
# To use it, copy it as AM2_CPU to the Amberfiles folder of a test installation.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE/AmbermoonSource/src"
"$HERE/vasmm68k_mot.exe" -m68030 -Fhunkexe -o "$HERE/AM2_CPU_CHEAT" -nosym -kick1hunks -keepempty -no-opt -align -DCheat=1 AMBERMOON.S

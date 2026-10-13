#!/bin/sh
# full pipeline: mapping -> diff -> plan -> classify -> port -> build
set -e
W="$(cd "$(dirname "$0")/.." && pwd)"
cd "$W"
ADV_REPO="${ADV_REPO:-/c/Users/Robert/source/repos/Ambermoon-Advanced}"
python -I tools/labelmap.py base/62823505 adv map_adv_to_62823505.tsv
python -I tools/rename.py adv.lines map_adv_to_62823505.tsv adv_renamed.lines
python -I tools/canon.py adv_renamed.lines adv.canon
git diff --no-index --histogram -U0 base/62823505.canon adv.canon > canon62.diff || true
git diff --no-index --histogram -U0 base/382eaeda.canon adv.canon > canon382.diff || true
python -I tools/plan.py
python -I tools/already.py
python -I tools/classify.py
rm -rf work && mkdir work && git -C "$ADV_REPO" archive 6c2a4997 code_changes/AmbermoonSource | tar -x -C work --strip-components=2
python -I tools/port.py work/src
python -I tools/build.py work/src work.bin || true

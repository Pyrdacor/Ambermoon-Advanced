# ambtools

Small Python helpers (no dependencies, Python 3.8+) to inspect and patch the game data.

| Script | Purpose |
|---|---|
| `validate.py [Amberfiles dir] [map ...]` | Checks all reachable map events for broken references: missing map texts, monster groups, chest data, items, teleport targets, out-of-range event pointers. Run it after every data change. |
| `dumpmap.py <map> [--layout] [--chains 1,2]` | Readable dump of a map: characters, goto points, optional ASCII layout and all event chains (with else branches). |
| `ambcontainer.py` | Read-only container access (LOB, JH, AMPC, AMNP, ...). |
| `mapmodel.py` | Lossless parse/serialize of a single unpacked map file plus event descriptions. |

## Patching map data

The containers are written with `AmbermoonPack` (AmbermoonTools). Unpacking and packing again
with default options gives a byte-identical file, so patches stay minimal:

```
AmbermoonPack UNPACK german/Amberfiles/2Map_data.amb tmp/2map
# patch tmp/2map/484 with mapmodel.parse() / mapmodel.serialize()
AmbermoonPack AMPC tmp/2map german/Amberfiles/2Map_data.amb
python tools/ambtools/validate.py
```

`Monster_groups.amb` works the same way with `AMNP`.

Texts are changed in `AllTexts` and then imported with
`AmbermoonTextManager -i german/Amberfiles german/Amberfiles/AllTexts -f 2Map_texts.amb`.
The release creator imports `AllTexts`, so `AllTexts` must always contain the current texts.

## Testing with the remake

`make_testdata.py <dir>` builds a complete data folder (german 1.20 original + Advanced files,
Save.00 also as Initial). The remake (branch `aa4-fixes` in Ambermoon.net) can then be started
directly into the game, e.g. to look at the ancient city:

```
Ambermoon.net --data <dir>/Amberfiles --skip-intro --load 0 --cheat 3 "teleport 483 22 9 down" --screenshot 6 --exit-after 8
```

Screenshots are written to the `Screenshots` folder next to the executable. `Ambermoon.net --help`
lists all options.

# Test scenarios for the remake

Scenario scripts are run by Ambermoon.net (branch `aa4-fixes`) with `--script`:

```
python tools/ambtools/make_testdata.py <dir>
Ambermoon.net --data <dir>/Amberfiles --skip-intro --load 0 --script tests/scenarios/morag_riddle_1_happy_path.txt
```

`--load 0` starts from the initial savegame without the start event on the first map.
Each check prints `PASS`/`FAIL`, at the end a summary like
`Script finished: 19 of 19 checks passed, 0 failed.` is printed to stdout.

## Commands (one per line, `#` starts a comment)

| Command | Meaning |
|---|---|
| `wait <ms>` | wait |
| `waitidle [timeout ms]` | wait until no window/popup is open |
| `cheat <command>` | cheat console command, e.g. `teleport 484 16 26 left`, `give 551 2` |
| `useitem <item>` | use an item of the active party member like via the inventory (consumption and map events included) |
| `key <key>` | press a key (Ambermoon `Key` name) |
| `click <x> <y> [right]` | click at window pixel coordinates (same as screenshot coordinates) |
| `dismiss` | close an open popup |
| `dismissall [timeout ms] [quiet ms]` | close popups until nothing happened for `quiet` ms (default 1500), fail after `timeout` ms (default 15000) |
| `screenshot <name>` | save `Screenshots/<name>.png` next to the executable |
| `state` | print map, position, window, popup and battle state |
| `var <index> [0\|1]` | print/check a global variable |
| `count <item> [amount]` | print/check the amount of an item in the party |
| `log <text>` | print text |
| `exit` | close the game (add a short `wait` before if a screenshot was taken) |

## MORAG riddle (map 484)

| Script | Case | Result 2026-10-06 |
|---|---|---|
| `morag_riddle_1_happy_path.txt` | M O R A G in the correct storages | 19/19 |
| `morag_riddle_2_wrong_order.txt` | O M R A G, reset and letters back, then solvable again | 25/25 |
| `morag_riddle_3_correct_letter_closed_storage.txt` | correct letter again on its closed storage (1-4) | 20/20 |
| `morag_riddle_3b_correct_letter_closed_storage_5.txt` | same for storage 5 | 7/7 |
| `morag_riddle_4_wrong_letter_closed_storage.txt` | wrong letters on closed storages | 16/16 |

Negative control: scripts 3 and 3b fail with the map data before the fix (`6c355c40^`), the letters are lost.

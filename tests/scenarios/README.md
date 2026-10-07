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
| `waitbattle [timeout ms]` | wait until a battle starts, presses Return on popups meanwhile ("Wollt ihr kämpfen?" → Ja) |
| `yes` | answer a decision popup with yes (Return) |
| `closewindow` | close the current window like the exit button (e.g. battle loot) |
| `battlebg [index]` | print/check the combat background of the active battle |
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

## Combat backgrounds

| Script | Case | Result 2026-10-06 |
|---|---|---|
| `combat_background_ancient_city.txt` | Monster in map 483 uses background 13 (char tile flags), event battle in 484 uses the labdata 44 default (4) | 2/2 |

Background 13 is rendered as the desert graphic (13) only with the remake fix in `CombatBackgrounds.AdvancedReplacements3D` (branch `aa4-fixes`). Before it showed graphic 1.

## Bandit house passage (map 274)

| Script | Case | Result 2026-10-07 |
|---|---|---|
| `bandit_house_passage.txt` | Enter from map 141, pull the lever in the left fireplace, pass the archway (`cheat berserk` removes the bandits), then try all steps around the opened passage | exploration, no checks |

Observed in the remake: after the lever (11,7), (10,6), (11,6) and (12,6) are walkable, (10,7) and (12,7) block.
The lever's tile changes (to 50/52) set the background tile, so the curved wall pieces 666-669 stay
visible and the player stands half behind them on (10,6)/(12,6). Before the lever (10,6)/(12,6) can be
entered from the upper room (which is also reachable from map 276).

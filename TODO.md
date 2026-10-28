# Ambermoon Advanced – Todo

State: 2026-10-14, branch `episode4`.

This file is the only todo list. The *Todo* sheet of `AmbermoonAdvanced.xlsx` and the former `todo.txt` were merged into it.

Sources:
- the sheets *Todo*, *Summary*, *Changelog* and *SavegamePatching* of `AmbermoonAdvanced.xlsx`;
- `todo.txt`;
- the design docs in `docs/AmbermoonAdvanced/4` (mainly `000 Plan Episode 4.md` and `000Reihenfolge.md`);
- the older lists in `docs/AmbermoonAdvanced/2` and `3`;
- the git history since 2026-10-06.

The detailed design of each Episode 4 item is in the docs folder, see the file in brackets. Items marked *(check)* may already be done and must be verified first.

---

## 1. Engine / code (Amiga, `code_changes/AmbermoonSource`)

`AM2_CPU` is now built from source (`code_changes/compile.sh`). `AM2_CPU.s` is gone.

### Port follow-ups
- [ ] **Test the source-built `AM2_CPU` in FS-UAE.** It was never started; only the binary comparisons were done. The remake doesn't run `AM2_CPU`, so it can't test the port.
  - Ready to start (2026-10-13): the configs `AmbermoonADV` (A1200), `AmbermoonADV_Cheat` (A1200, diagnostic keys) and `AmbermoonADV_A500` (68000).
  - The drives were built with `tools/ambtools/make_amiga_hd.py` and contain `AM2_CPU_OLD` for comparisons.
  - Cover at least combat, events, Sage and dialogues, because the port bugs were there.
- [ ] 68000 (A500) support: since the 1.21 base, `AM2_CPU` chooses the blitter renderer on a 68000. The only 68020 instruction in the Advanced code was `tst.l A2`, which is now replaced. Test on the A500 config; the debug build (`compile_debug.sh` in the Ambermoon repo) shows the location of address errors.
- [ ] Test the two fixes from 2026-10-13 in a fight:
  - Foresee Attack now only affects monsters.
  - The aging index is now 0–17 for monsters and 18–23 for party members.
- [ ] Check whether the remake has the same two bugs (Foresee Attack, aging index) or its own logic.
- [x] Moved `FUN_CalculateSpellDamage`, `FUN_GetWorstElementBonus` and `DAT_ElementTable` from `KERNEL/TEXTS.S` to `COMBAT/COMBAT_M.S` and `FUN_DebugPrint` to `KERNEL/START.S` (2026-10-28). Fixed on the way: the table index D4.w had garbage in the upper byte, the worst bonus used a signed compare (150% counted as negative, an immune 0% was ignored as first element), and wind against water was 150% instead of 100% (see ElementalSpells.md and the remake).
- [x] Element table: the game data is right (mental column: spirit 125%, earth/wind/fire/water 75%), ElementalSpells.md updated (2026-10-28).
- [x] Nalven's element table (Object_texts 1/6, German and English) shows the mental column of the game data, and the hint also lists Ghost Inferno and Mystic Decay (both spirit) (2026-10-28).
- [ ] Optional: restore the original source formatting where the port only replaced lines with disassembly style. Examples: `Default_PA`/`Default_MA`, the stack definitions, comments lost on `cmpa.l`.

### Missing Advanced features on the Amiga (remake has them)
- [x] Level > 50 through events, and the max-attribute increases for levels 51–55: done and tested 2026-10-19 with the wise man in S'Angrila (NPC 79). From level 50 on, the level reward goes up to 55; each of the levels 51–55 raises the maximum of a class attribute by 5 (`Level_shard_attributes` in `MAIN.S`, same table as the remake). Also fixed: the level reward used the "all" loop counter as party slot (wrong for the active member), and the level counters are now cleared after the level up. Remake: the level reward from level 50 on now also shows the level-up window like the Amiga (`EventHandling.cs`, Ambermoon.net master, not committed yet).
- [ ] Events 28–32 (show map, toggle switch, dynamic tile change, rectangular exploration, vertical line reveal): **implemented 2026-10-18** (`EVENTS.S`), built, not tested yet. Test in FS-UAE in the ancient city (483) and the ancient building (484): switches (29) with their doors/walls (30), the map tables (28) and the revealed rooms (31). The map table (28) and the revealed areas (31) work (2026-10-18, hide/reveal fixed); switches (29/30) still to be tested. Before, these events were silently skipped on the Amiga.
- [x] Hour movement does not seem to work on the Amiga: **fixed 2026-10-20**, tested 2026-10-21. Loading and the position per time step (step modulo 12) were already right. The cause was the 3D collision check: two path persons on the same square (objects 0/1 at (13,13) and 2/3 at (6,5) in the ancient building 484) blocked each other forever. Path persons in 3D now follow their path without collision checks, like the remake (`NPC_manager_3D` in `PERSONS.S`).
- [ ] New spells:
  - [x] New spell target "enemies in close range" (spell target bits $02, was the unused "row of friends"): hits all enemies on the 8 surrounding tiles, no target selection (only "out of reach" if nobody is there), the targets are determined when the spell is cast. No longer range with a long-range weapon (Amiga and remake, 2026-10-28).
  - [x] Magic sword attack (class 6 spell 26, energy sword item 556), Amiga like the remake: a physical special attack, so parade instead of anti-magic and no failing via "use magic". Damage = attack damage x (APR + 1) / 2 (decided 2026-10-14), plus 0–25% and the spell damage bonus (spirit), heals the caster by 10% of the damage. The item can only be used when equipped (new message 327, German and English). Monsters use it if the mean danger of the party members around them is >= 50. Since 2026-10-28 the target's protection x APR (50–100%) is subtracted, "no damage" if not positive. Like a weapon attack no damage at all if the target has the element of the weapon (energy sword: spirit). Remake: the battle froze because the sword swing used the animation ticks (fixed). Not tested yet (FS-UAE and remake). Note: on the Amiga a parrying monster can also parry it (like weapon attacks), in the remake only party members parry.
  - [ ] Implement the other new spells (bow and staff of bosses 2/3).
  - [ ] Function spells for monsters, spell infos (class 6 is now possible for monsters, only spell 26 has a handler).
  - [x] Monster spell fallback: without a spell for the chosen target monsters now use the row in range, row or all spells (remake: didn't cast; Amiga: cast a stale spell from the list) (2026-10-28).
- [x] Weapon and ammunition elements ([Weapon elements.md], 2026-10-28): element in Misc_1 / SpecialValue (0 none, 1 spirit, 3 undead, 4–7 earth, wind, fire, water), ammunition with an element overrides the weapon. Same element as the target: no damage and no critical hit. Otherwise the factor of the spell element table (after the defense). Monster immunity flags (monster byte $0B, bit 0 = without element, bit n = element n) abort all attacks of the round with "<monster> is immune against an attack with element <x>". Amiga new, remake completed (factor, same element, no crit). Not tested yet. Elements set (2026-10-28): spirit 187, 276, 298, 417, 477, 556, 233, 323; undead 237, 415; water 196, 465; fire 428, 429; wind 473; earth 202. Only monster 98 (Staubteufel) has immunity flags ($39).
  - Note: Weapon elements.md says ghost = 2 and immunity bits 2..7, the code uses spirit = 1 (like the element table) and bit = element index.
  - Remake fixes on the way: the immunity message named the attacker instead of the monster, and item element names were off by one (spirit showed "Mental").
- [x] Minimum level for all equipment (item byte 22 = Misc_2 / TextSubIndex, 0 = none, 2026-10-28): equipping with a lower level shows message 328 "~INVN~ ist nicht erfahren genug, um diesen Gegenstand auszurüsten.". The second item window (identified items) is one row higher for equipment and shows ELEMENT (name incl. "Keins") and MIN-LEVEL ("-" or the number), messages 329/330. Remake tested 2026-10-28, Amiga not tested yet. Energy sword (556) has minimum level 50.
- [ ] Extended languages.
- [x] 3D combat background 13 → graphic 13 (desert, palettes 35/46/47 like the remake, 2026-10-28).
- [x] The APR reward adjusts `APRPerLevel` like the remake (level / (APR − 1), at APR 1 at least level + 1), and a level up never lowers the APR anymore (2026-10-28).
- [x] Reward targets 100+ and 200+ ("all but X") work. Fixed: the pointer was not freed for 100+ / first animal, and death (HP −100%) and revival / kill via conditions used the loop counter as the member number, so they were wrong for the active and random targets. Killing via a condition reward now shows the death instead of setting 1 HP (2026-10-28). Not tested in FS-UAE yet.
- [x] A 100+ / first animal reward target without a matching member stops the event chain like in the remake (Break_event, 2026-10-28). Dead and petrified members are never rewarded (except condition removal) and count as no match, now also in the remake (2026-10-28).
- [ ] Automaps for the new maps.

### Remake (Ambermoon.net, branch `aa4-fixes`)
- [ ] Move `AdvancedMonsterFlags | ItemElements | ExtendedLanguages | LevelShards` into `Features.AmbermoonAdvanced` with version gating. They are currently switched on by a hack in `GameWindow.cs`.
- [ ] Episode 3 changes that are missing in the remake:
  - STA/25 HP on level up, including bonus STA.
  - Bow damage bonus (STR/50 + DEX/25).
  - DEX/50 bonus for other weapons.
- [ ] Bow and staff boss spells, item minimum level (see 2.1).
- [ ] Combat conditions like on the Amiga (2026-10-14):
  - Poison: per round 1 to 5% of max LP. The maximum is limited to 20 for party members and bosses and to 35 for other monsters. The remake uses a fixed 1–5.
  - Hit and parry penalties: drugs −25 (attack only), blind −50, aging −10 per step. The steps rise every round up to 5 and are reset each battle. Blind replaces aging. Bosses get half the penalty.
  - Damage and defense: disease −50% (bosses −25%), aging −10% per step up to −50% (bosses half).
- [ ] Crash when removing many items twice.
- [ ] Casting Self Heal in battle and clicking fast afterwards blocks the player selection (the keyboard still works).
- [ ] Short wrong wall colours after teleporting (Cavetown, Spannenberg goto point), probably time-of-day dependent.
- [ ] 3D movement with WASD is sometimes slow.
- [ ] Lava stream: player drawn above the bottom rocks when moving down (remake bug?).
- [ ] Wise man house: chairs and shelf have a strange z-order with the player. Screenshots exist; compare with the Amiga, maybe change Normal → Background.
- [ ] Laser trap is noticed by Clairvoyance although its condition is not met *(check, maybe fixed)*.
- [ ] Eye cursor near lockpick doors in the Gral temple shows the spinner text.

---

## 2. Episode 4 content (German first)

Order and details: `000 Plan Episode 4.md`, milestones M1–M4.

### 2.1 Ancient city (M1)
- [ ] **Boss 1 (S-1, sword)** in map 484: boss room events (vars 461/464), blue plate drop, energy sword item 556 (test the spell-from-item path).
- [ ] **Boss 2 (B-1, bow):** spell (all enemies, heal 2% MaxHP per target, DEX/20), monster, gfx, ancient bow ([Neue Zauber.md]).
- [ ] **Boss 3 (F-1, staff):** spell (fireball per target, SP refill, INT/20, 5 SP, 50 charges, rechargeable), monster, gfx, ancient staff.
- Decided (2026-10-14) for the ancient weapon spells ([Neue Zauber.md]):
  - Each target is hit once, and the damage is multiplied by 1 + (APR - 1) * 0.5 (1 APR: x1, 3 APR: x2, 5 APR: x3).
  - A normal attack with an ancient weapon is a plain weapon attack. The spell is only cast via "use item".
- [ ] Bosses use the new spells and may need different battle actions (moving closer).
- [ ] Boss rooms 2/3 of map 484 use the placeholder groups 170/171. Only adjust these groups when building the real bosses.
- [ ] Map 484: remaining events, debris for the boss rooms, other robots.
- [ ] Map 483 (surface):
  - Patrols (trap + text + teleport, maybe a new "unavoidable trap" flag).
  - Attribute-gated levers.
  - Morag golems (no gfx yet).
  - Giant lizard at the red entrance.
- [ ] **Central temple, map 485** (empty so far):
  - Four entrances matching the plates.
  - Rotating centre section.
  - Switch chain leading to the central room with 3 teleporters.
  - Consume all key cards when the portals are activated.
- [ ] Giant lizard drops the Kasimir essence. The wise man applies it, and Kasimir becomes level 55 ([Neue Essenz.md]).
- [ ] New monsters: Morag golem, giant lizard and its escort ([Neue Monster.md]).

### 2.2 Portals and Lyramion vault (M2)
- [ ] Two new teleporter stone items in colours that don't exist yet (e.g. violet and white) instead of green/red, so they can't be confused with item 488 (decided 2026-10-14).
- [ ] New 3D map(s) for the vault in the Thuna desert, using a free index 487–512. Never append: the Amiga archive limit is 530 entries.
  - Riddles, lever, rumble.
  - The temple rises on the Lyramion world map.
- [ ] Portal 1: Morag ↔ Lyramion vault.
- [ ] Portal 2: Morag ↔ AA2. On arrival, disable the walking lightning and place the red stone.
- [ ] Portal 3: "coming in Episode 5" text, then the party is teleported back 1 tile.

### 2.3 Morag progression and balancing (M3)
- [ ] **Shard economy:** the budget sheet lists 46 shards obtainable now and about 525 planned; the goal is about 600 without grinding.
  - Drops from council lizards, golems, the giant lizard and the bosses.
  - Temple chests.
  - Random battles on all Morag world maps (513 and 526 have none yet).
  - Hide shards, add them to monsters.
- [ ] **Level-gated equipment 51–55** ([Waffenlevel.md]):
  - Item byte for the minimum level, shown in the item window.
  - Enforce it in the remake and on the Amiga.
  - Ancient weapons need 51/53/55, the Rebellenklinge 52.
- [ ] **Elemental weapons in the data:**
  - Feuerbrand gets the element fire (decided 2026-10-14). Place another weapon in Luminor's tower, so you can't get stuck there.
  - Flamberge, Eisschwert, Waldbogen, Nekromantendolch, Geisterstab.
  - New Sandschwert (earth).
  - Check the undead entry of the element table.
- [ ] Are there element change spell scrolls anywhere?
- [ ] Monster immunity flags in the data (e.g. dust devil: only fire/ghost/ice weapons).
- [ ] Council lizards and machines much stronger ([Ratsechsen.md]): very high MBR, DEF and damage, magic damage reduction. Not winnable without endgame equipment, and long fights even with it.
- [ ] New endgame weapons and armour.
- [ ] Moranians stronger, maybe with stronger escorts (enhanced magic guards).
- [ ] New item gfx for the Morag weapons and armour.
- [ ] New items ([000Reihenfolge.md]).

### 2.4 Quests, temples, polish (M4)
- [ ] S'Ebi texts (only possible after the prison).
- [ ] S'Ebi quest or reward. Rescuing him is optional, so maybe something better than a shard (sabotage idea in [4 Todo.md]).
- [ ] Rebel side quests ([Levelgrenze.md]):
  - Poisoning quest in the tavern.
  - Eavesdropping in the hangar → digging site → chest and fight. Reward: Rebellenklinge or gold.
- [ ] Council temple rework of **all 7 temples** in Episode 4 (decided 2026-10-14), one temple at a time ([Tempelanalyse.md], [Tempel 1 - Labyrinth.md]).
  - Suggested order: S'Riel, S'Orel, S'Arin, S'Endar, S'Trog, S'Kat, S'Lorwin.
  - Song 33 (Psychedelic Dune Groove, temple version, `assets/Temples/music/`) is chosen but **not in `Music.amb` yet**: in the remake `Song` 33 is `Intro` (34 Outro, 35 Menu), so a 33rd entry makes loading the game data fail. First change the remake (e.g. move Intro/Outro/Menu out of the Music.amb range), then append the song. The Amiga code already allows it (`Max_music` = 33). Then decide which temple uses it.
  - Optics: mockups in `assets/Temples/mockups/` (Gala/Sansri textures, one palette per temple).
  - **Prototypes** in `assets/Temples/prototypes/` (labdata 46 = temple base, see `assets/Temples/Labdata 46.md`): S'Riel (map 487, palette 59) and S'Orel (map 488, palette 60, monster group 172). Test on the Amiga with a new game and the cheat map jump. Next: S'Arin.
  - Stronger temple guards (new monsters) are still missing, the prototypes only use the magic guard (monster 42).
  - Savegame patcher: add the automaps 485, 486, 487 and 488 (missing in old saves → fatal error on the Amiga when entering these maps).
  - Remake test works (`make_testdata.py` + teleport cheat), screenshots in `assets/Temples/prototypes/`.
- [x] **Bore the dwarf as a party member** (built 2026-10-14, german data + english AllTexts, see the xlsx):
  - NPC 24 (Gemstone) is level 30. Leaving the forest moon (airship 436, var 320) hides him and shows party member 18 (dwarf warrior level 30) at his place.
  - Party member 18 tells about the forest moon on the first talk (gives the first navstone, var 399), trades amber chunks for navstones and can join.
  - Dor Kiredon (343), chain 20 at (16,21)/(16,23): with Bore in the party, text 21, the remove party member event puts his things into the extended chests 307/308, he is hidden in Gemstone, NPC 80 and the chests appear in the mine (345), var 471.
  - NPC 80 in the mine: first talk gives 5000 EXP (var 472), then he trades navstones.
- [ ] Bore quest follow-ups:
  - Test it on the Amiga (cheat build) and in the remake.
  - Remake: implement the remove party member event, including the extended chest flags (byte 4, bit 0/1).
  - Savegame patcher: add the chests 307/308 (the remove party member event crashes on the Amiga if the chest file is missing), hide party member 18 in Gemstone (char bit 12961) and NPC 80 in the mine (char bit 11009). For saves after the forest moon (var 320) hide NPC 24 (char bit 12960) and show party member 18 instead.
  - English release: party member 18 must be in the english Save.00/Party_char.amb (currently only the german one has the episode 4 party members).
- [ ] Easter eggs ([Eastereggs.md]):
  - S'Ebi at the Fountain of Life → "Horus" → 10 all-heal vials in Burnville.
  - Baron Karsten's diary → reward and teleporters.
- [ ] Prison: furniture in the cells (torture room), more stones at the broken wall (needs gfx).
- [ ] Wise man house: Sage and alchemy scrolls ([Hauptstadt.md]). Map 482 only has the exit event.
- [ ] Can Kasimir (or others) be revived in the mystic boss room? Is a camp possible?
- [ ] Episode 5:
  - Pirate encounters on the sea ([4 Todo.md]) (decided 2026-10-14).
  - Underground town S'Ekur ([4 Ideas.md]).
  - Race byte in items (dwarf weapons for Bore, Moranian/male thief items for S'Ebi).

---

## 3. Savegames, English, release (M6)

- [ ] **Savegame patcher Ep3 → Ep4.** Episode 3 saves don't load with Episode 4 data in the remake.
  - Kasimir (party member 16): event 22 → `0d 00 00 00 00 00 01 34 00 1d 00 17`, append event 29 `11 09 00 00 00 00 00 00 00 00 00 18` (event count 29 → 30), for the dismiss text after the essence.
  - Party member 17 (S'Ebi).
  - Extended chests 286+.
  - Global vars 402+.
  - Map changes 441/454.
  - New automaps, char/event bits.
- [ ] Savegame patcher, older open items:
  - Current damage of left-hand items (e.g. sling daggers).
  - Wrong weights of some party members (Erik > 50 kg with nothing carried); reduce by 225 g per food.
  - Remove all tile change events of Antique Area 3.
  - Aman doesn't spawn if the thief cellar was visited before patching. If event bit 265:4 is inactive and glob var 376 is 0, set character bit 407:4 (show) and 264:3 (hide).
- [ ] English:
  - Proofread the 244 translated Episode 4 texts (`tools/translations/ep4_english.py`).
  - Add translations for later German texts.
  - Copy the German binaries for the release.
- [ ] Run `tools/ambtools/validate.py` and `tools/ambtools/audit.py` after every data change.
- [ ] Full playthrough of Episode 4 on the remake and the Amiga, German and English.
- [ ] `Changes.md`, `NewContent.md`, release creator, version bump.
- [ ] Manual: level shard effects, new spells, more spell details, spoiler section.
- [ ] Release announcements: itch, Patreon, website, GitHub. Mention the savegame patcher and the remake auto patching.

---

## 4. Bugs in data and texts

### Data audit (`tools/ambtools/audit.py`, 2026-10-18) – open questions
Fixed: barrels on the door teleport targets in Ship's End (372), stone block on the arrival tile of the ancient city (483 from 522), stray floor tile in the prison (479).
- [ ] Manyeyes' castle 1 (461): the undead groups 90/91 start inside statues (15,10) and (17,12). Intended (living statues) or move them?
- [ ] Ancient building (484): the dark doors (wall 115, texture 192) at (2,5) and (2,13) are walkable but have no event and lead to the map border. Make them solid or give them a destination?
- [ ] 3D maps with walkable floor at the map edge (no event): 284, 339, 413, 415, 416, 424 (all original, cosmetic).

### English text check (`tools/ambtools/textcheck.py`, 2026-10-18)
Fixed: untranslated text 369/2, 22 texts with missing or extra quotes, typos (also in the Ambermoon repo), stale English texts of maps 335 and 440, monster 111 renamed to ANCIENT WARDEN (16 characters didn't fit), German party text 8/8 quote.
- [x] Grail swamp hint (NPC 47, text 4): GRAL, AT NIGHT and the mountain flank highlighted in English too, like in German.

### Original bugs (also fix in the Ambermoon repo)
- [x] Lava tiles must block walking and the horse (world map). Tileset 1, tiles 235-238 (2026-10-18). Already fixed in the Ambermoon repo.
- [x] Stairs in the Thalion office: original fix taken over, new tileset 4 tiles 0x4a6-0x4a8 in map 257 (2026-10-23).
- [ ] Non-blocking walls: trainer house 268 upper wall fixed in both repos (tileset 4 tiles 0x3b1-0x3b3 use background flags, 2026-10-23). Remaining candidates to check visually: witch house 411 (17,7) ts4 0x324 (BringToFront object on blocking background), armoury 407 (10,10) ts5 0x186; probably intended: 417 (14..18,8), 341 (18,11), 477 (2..3,2).
- [x] Text bug in the thief cellar (bandit house cellar, map 276): the original fix from the Ambermoon repo taken over (2026-10-23).
- [x] Two-hand weapon and shield: the Amiga is correct (drag and drop only). Remake bug in shift-click equipping fixed in `Windowing.cs` (2026-10-23, Ambermoon.net, not committed).
- [x] Monsters can't pass the green slime in the old cave. Labdata 2, objects 15-17 also allow class 1 (2026-10-18, also in the Ambermoon repo, master).
- [x] Map 273 (town house): teleport from map 263 (event 72) now leads to (10,4), both repos (2026-10-23).
- [x] S'Angrila (map 442 text 2) "bin": was already fixed in Advanced, fixed in the Ambermoon repo (2026-10-23).
- [ ] Sleep and fear lead to game over: **fixed 2026-10-23**, not tested. Amiga (both repos): no defeat while members are on the battlefield, the leader is kept if nobody can lead, OK starts the next round. Remake: `RecheckActivePartyMember` starts the next round automatically. Stalemate check after each round (2026-10-27, Amiga in both repos, remake): mad, asleep, panicked, lamed and petrified count as incapable; the battle goes on if a party member is capable, anyone is only panicked or a member is only asleep while a monster is capable, otherwise game over. Ambermoon repo: branch `fix/combat-stalemate` (needs a PR). Test: battle where all members get asleep/panicked/lamed.
- [x] Forest moon navstones: left as is (2026-10-27). Gemstone gives navstones after the return to Lyramion (the first one for free), Morag has some too.
- [x] Text 2 in AA4 ("GEHEMNISVOLL"): already fixed in Advanced, fixed in the Ambermoon repo (2026-10-23).
- [x] Automap shows traps without Mystic Map: the Amiga now also hides trap/trapdoor/spinner icons of walls and objects without the trap function, like the remake and the legend (both repos, 2026-10-23).
- [x] Attack icon after the weapon breaks: the Amiga was correct; the remake now updates the battle buttons after each round (`BattleHandling.cs`, 2026-10-23, not committed).

### Advanced
- [ ] Some world map shadows are broken (sand boat tower etc.).
- [ ] Wrong tiles on the Morag world map (low priority, check visually later). Known so far: 522 tower at (4,2) has a broken shadow (only the bottom row 0x96-0x98 at (5..7,4) plus a rock decal 0x13d-0x140 at (6..7,3..4)); the tower at 522 (6..8,48..50) overwrote overlay 0x1d8 at (7,48) of an original 6x4 structure (0x1c5-0x1db at x 5..10, y 45..48) and should move; towers at 523 (27,19) and 528 (31,6) have no shadow. Robert also suspects errors at the transition on the right edge.
- [x] Moving mushrooms in Dor Grestin: hand/eye condition in front of the text (map 339, 2026-10-23). The original has the same data, but the condition needs the Advanced executable.
- [x] Protection spell: the protection bonus was added when the attacker was a party member, so it protected the monsters instead of the party (original bug, fixed in Advanced and on the Ambermoon branch fix/combat-stalemate, 2026-10-28). The remake was already right.
- [x] Wall storages in map 484 could only be used diagonally because the robot wrecks blocked the front tile: the wreck object (lab 44 object 2) is walkable now (2026-10-27).
- [x] Transfer stone on yourself: the caster can't be selected anymore (Amiga) / the stone is not used up (remake, not committed) (2026-10-23).
- [x] Battery: items added by events go to the active member first (Amiga: the loop advanced the item pointer instead of the party pointer; remake too, not committed). Also fixed the random reward target code (2026-10-23).
- [x] Empowered Kasimir dismiss text: with glob var 308 set he says Party_texts 16/9 ("SO, SO. ERST MACHT IHR AUS MIR DEN MÄCHTIGSTEN KATER…"), Save.00 Party_char 16 event 22 checks the var, new event 29 (2026-10-27). Existing saves need the savegame patcher (see 3.).
- [x] Kasimir TP: Sandra gives +10 parry max instead of +25 TP, and crit max +7 instead of +5 (NPC 5, 2026-10-27). Existing saves are not affected (NPC data).
- [x] "Here is a trap" too often: clairvoyance reports each square only once (it also ran on every idle time step), both repos (2026-10-23).
- [x] Magic while drugged: `Magic_mask` no longer contains drugged (Amiga, 2026-10-23); the remake already allowed it.
- [ ] Unused texts: map 368 text 3 is already used (skeleton hint, chain 15). Map 339 texts 18/19 are the old inn texts (inn moved to map 381, which has no "refreshed" text; could reuse 339/18 there). AA4 text 14 is empty in the original too.
- [ ] Event editor crashes on chains 8 and E in AA4 and chain 26 in map 368 (graph command).
- [x] Mystic tower: doing the 3 map events out of order breaks nothing; the later ones just stay active until the right order (no feedback).
- [ ] Check all automap icons of all events.
- [x] Glob var 193 (Shandra's grave, map 428): chain 8 is not connected, so you have to use the amber again if you close the chest without the key. No soft-lock, left as is (2026-10-27).
- [ ] Episode 3 changelog: the Gnome mine goto points must also be in the English version *(check)*.
- [x] Old Ep3 notes (2026-10-23): crystal shield and "began" no longer found; Kapitän Torle fixed in both repos; turtle/torch music was fixed in be63b8bf, the same music bug fixed in Isdir's cave (377), Milzor (NPC 21) and the original S'Arin palace (446, Ambermoon repo); rune texts in 465/469/470 switch back to the normal font.
- [ ] Black Mountains *(check)*:
  - Test huge lava performance on the Amiga.
  - Players can slip through the double pillars.
- [ ] Swamp dungeon *(check)*: gral mages more distinct, wasp battle colours, larger undead on the map.

---

## 5. Balancing and ideas (from the former `todo.txt` and older lists)

- [ ] **Thief skill rework:**
  - Open Locks is the chance that the lockpick survives.
  - Fewer lockpicks in the game.
  - Locks only open when there is no trap.
  - Maybe more characters get some Open Locks points.
- [ ] SLP: reduced for 72 spells and per-level SLP adjusted on 2026-10-06. Check what is left from `todo.txt`:
  - Hero/Valdyn/Gryban lower SLP, SP and max M-B.
  - Valdyn very low SLP.
  - Raise the SLP of the "cool" spells.
- [ ] Targor replacement equipment: Mystic Set: orb (35 Atk, 15 STA, 3 Crit, 3 M-B-W, Mystic Globe 10 charges, 100 g), robe (17 Def, 10 SPD, 25 M-B, 3 M-B-R, LP stealer 5 charges), hat (Madness 10 charges, 5 Def, 15 INT, 25 R-M, 2 M-B-R), boots (15 SPD, 8 Def, Blink 10 charges) on the forest moon. Leonaria: alchemist staff (LP stealer), hat (SP stealer).
- [ ] Remove scrolls:
  - Blind, Drug, Age, Disease.
  - Single-target heal-ailment spells that have an "all" version.
  - Restore Stamina.
  - Escape (or fix it).
- [ ] Replace the strengthening potions (e.g. Heal I + SP I).
- [ ] Spell effects on monsters: poison damages them, disease and aging weaken them, blind makes them miss.
- [ ] Trap event flag that makes avoiding it via luck harder (0–100).
- [ ] Merchant/library price factor in the place data (for the Morag underground city).
- [ ] Option to leave party members at your house when it is renovated.
- [ ] Hide more stones of knowledge.
- [ ] Remove unused map graphics (tiles, walls, objects, overlays) and adjust the references.
- [ ] Export overviews and stats: chests, monsters, monster groups, party members, NPC items, rewards, potions, spell list.
- [ ] Allow automap types for 3D map events.
- [ ] Wasp nest: glowing pillars could stop when the elevator stops.
- [ ] Improve the old item gfx in the thief quest and the white plants.

---

## 6. Repo housekeeping
- [ ] Remove the `Co-Authored-By: Claude` trailers from the history (commands prepared; needs to be run by Robert or allowed for Claude):
  - Ambermoon: `master`, `release/v1.21`, tags `game-v1.21`/`tools-v1.18`.
  - Ambermoon-Advanced: `episode4`, `main`.
- [ ] The repo lists (`maps.txt`, `new_items.txt`, `global_vars.txt`, …) were not updated for Episode 4. The xlsx is the source of truth; update or delete them.


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
- [ ] Move `FUN_CalculateSpellDamage`, `FUN_GetWorstElementBonus` and `DAT_ElementTable` from `KERNEL/TEXTS.S` (the old patch space) to the combat files. Move `FUN_DebugPrint` to the kernel.
- [ ] Optional: restore the original source formatting where the port only replaced lines with disassembly style. Examples: `Default_PA`/`Default_MA`, the stack definitions, comments lost on `cmpa.l`.

### Missing Advanced features on the Amiga (remake has them)
- [ ] Level > 50 through events, and the max-attribute increases for levels 51–55: **implemented 2026-10-19**, built, not tested yet. From level 50 on, the level reward goes up to 55 (below 50 it still stops at 50). Each of the levels 51–55 raises the maximum of a class attribute by 5 (`Level_shard_attributes` in `MAIN.S`, same table as the remake). Test: the wise man in S'Angrila (NPC 79) with a level-50 character and level fragments (item 545). Also fixed: the level reward used the "all" loop counter as party slot, so for the active member (the wise man) a random slot got the levels.
- [ ] Events 28–32 (show map, toggle switch, dynamic tile change, rectangular exploration, vertical line reveal): **implemented 2026-10-18** (`EVENTS.S`), built, not tested yet. Test in FS-UAE in the ancient city (483) and the ancient building (484): switches (29) with their doors/walls (30), the map tables (28) and the revealed rooms (31). The map table (28) and the revealed areas (31) work (2026-10-18, hide/reveal fixed); switches (29/30) still to be tested. Before, these events were silently skipped on the Amiga.
- [ ] Hour movement does not seem to work on the Amiga.
- [ ] New spells:
  - New spell target "enemy row in range": picking for player and monster, visuals, range checks.
  - Implement the new spells.
  - Function spells for monsters, spell infos.
  - Monster spell fallback: if the average priority is below 50, monsters currently don't cast at all. They should fall back to single-target spells.
- [ ] Item elements, monster immunity flags (AdvancedMonsterFlags), item minimum level ([Weapon elements.md], [Waffenlevel.md]).
- [ ] Extended languages.
- [ ] 3D combat background 13 → graphic 13 (remake done).
- [ ] The APR reward must also adjust `APRPerLevel`.
- [ ] Check reward targets 100+ (and add 200+ = "all but X"). Check killing with HP −100% and reviving with remove condition / HP +100%.
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
- [ ] Stairs in the Thalion office.
- [ ] Non-blocking walls in 3 maps *(check: #123/#146 fixed several walls on 2026-10-06/07)*.
- [ ] Text bug in the thief cellar: early rooms show texts although a later room was already entered (wrong teleport rooms).
- [ ] Two-hand weapon equipped while a shield is equipped and no free slot: the shield stays in its slot (red cross) or seems lost. Check v1.07.
- [x] Monsters can't pass the green slime in the old cave. Labdata 2, objects 15-17 also allow class 1 (2026-10-18, also in the Ambermoon repo, master).
- [ ] Map 273 (town house): move the teleport lower so you don't land in the door.
- [ ] S'Angrila inn NPC: "und ich der letzte meiner Familie" is missing "bin".
- [ ] Sleep and fear lead to game over although you can wake up or flee.
- [ ] Forest moon: don't allow leaving without a yellow or green navstone (you can get stuck on Morag/Lyramion).
- [ ] Text 2 in AA4 ("GEHEMNISVOLL").
- [ ] Automap shows traps without Mystic Map (but not in the legend). Decide, and make the remake match.
- [ ] Remove the sword/attack icon if the weapon breaks.

### Advanced
- [ ] Some world map shadows are broken (sand boat tower etc.).
- [ ] Wrong tiles on the Morag world map.
- [ ] Moving mushrooms in Dor Grestin can't be picked up.
- [ ] The 4th wall storage can be reached diagonally through the wall from the corner (original too?).
- [ ] Transfer stone can be used on yourself (Amiga too?).
- [ ] The battery goes to the first member with space, not to the active one (original behaviour?).
- [ ] Empowered Kasimir still says "I am too weak…" when dismissed.
- [ ] Kasimir gets many TP, but all skills except Crit are already maxed after the transformations.
- [ ] "Here is a trap" message comes too often.
- [ ] Magic should be usable on drugs (the drug penalty now reduces the hit chance), at least in battle.
- [ ] Unused texts: map 339 texts 18/19 (Dor Grestin), map 368 text 3 (reuse as skeleton hint), AA4 text 14 (empty).
- [ ] Event editor crashes on chains 8 and E in AA4 and chain 26 in map 368 (graph command).
- [ ] Mystic tower: check the 3 map events when done in a different order.
- [ ] Check all automap icons of all events.
- [ ] Check glob var 193 (set when looting Shandra's grave, not connected in map 428).
- [ ] Episode 3 changelog: the Gnome mine goto points must also be in the English version *(check)*.
- [ ] Old Ep3 notes *(check)*:
  - Crystal shield is English in the German version.
  - Kapitain → Kapitän, began → begann.
  - Music missing after the turtle and when using a torch in the wine cellar.
  - Reading runes in the wine cellar turns the whole UI into runes.
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


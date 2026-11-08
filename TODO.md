# Ambermoon Advanced – Todo

State: 2026-10-29, branch `episode4`.

This file is the only todo list. The *Todo* sheet of `AmbermoonAdvanced.xlsx` and the former `todo.txt` were merged into it.

Sources:
- the sheets *Todo*, *Summary*, *Changelog* and *SavegamePatching* of `AmbermoonAdvanced.xlsx`;
- `todo.txt`;
- the design docs in `docs/AmbermoonAdvanced/4` (mainly `000 Plan Episode 4.md` and `000Reihenfolge.md`);
- the older lists in `docs/AmbermoonAdvanced/2` and `3`;
- the git history since 2026-10-06.

The detailed design of each Episode 4 item is in the docs folder, see the file in brackets. Items marked *(check)* may already be done and must be verified first.

---

## 0. Still to test (Robert)

Details are in the items further down.

**Amiga (FS-UAE, config `AmbermoonADV_Cheat`):**
- [ ] Source-built `AM2_CPU` in general: combat, events, Sage, dialogues. Also on the A500 config (68000).
- [ ] Extended languages (not committed yet):
  - Morag maps 522 (4,3) and (7,49), 523 (27,20) and 528 (31,7) without the ancient language: the other text must come.
  - Talk to NPC 79 in the wise man house (482): "Alte Sprache" must be in the inventory.
  - The same Morag spots with the language: the chain goes on.
  - Inventory: languages at the bottom, condition icons at the top in the right place.
  - Switch to a member without a common language in a conversation with an NPC which only has an extended language.
- [ ] Battle: Foresee Attack only affects monsters; aging index; poison, hit, parry and damage penalties.
- [ ] Battle stalemate: all members asleep, panicked or lamed (no wrong game over, OK starts the next round).
- [ ] Magic sword attack with the energy sword (556): damage, heal, parade, "no damage" against spirit, must be equipped, minimum level 51.
- [ ] Weapon and ammunition elements: factor, same element no damage and no crit, immune message at the dust devil (98).
- [ ] Minimum level: equipping with a too low level (message 328), second item window with ELEMENT and MIN-LEVEL.
- [ ] Reward targets 100+ and 200+, killing and reviving via condition rewards, no match stops the chain.
- [ ] Events 29/30: switches and doors in the ancient city (483) and the ancient building (484).
- [ ] Bore quest: forest moon (436), Gemstone, Dor Kiredon (343), mine (345) with the chests (14,3)/(15,4), NPC 80 at (13,3) with texture 322.
- [ ] Boss 1 in map 484: teleporter (4,20), statue at (4,17), flee, win, wall (12,21) opens.
- [ ] Boss 2 in map 484: teleporter (3,21), statue at (12,17), flee, win, wall (12,23) opens, energy bow (559) with arrow hail (equipped, party member cast, damage, heal 5%, parade). Amiga: source-built `AM2_CPU` with the extended languages from 161a524a, which did not assemble before.
- [ ] Tower top 405 on the Amiga: lever (10,11) while standing on (10,10). The banish chain starts through a teleport onto the own tile, which works in the remake. If it does not on the Amiga, the player just stays in the room with the wall open. Also the whole flow: wall, Lebab, song 30, world map (38,28), wall closed and lever usable again.
- [ ] Temple prototypes S'Riel (487) and S'Orel (488) with a new game.
- [ ] Huge lava performance in the Black Mountains.

**Remake:**
- [ ] Magic sword attack (not tested in a real fight yet).
- [ ] Sleep and fear stalemate, as above.
- [ ] Self Heal and fast clicking with several party members and the real spell list: does the player selection still hang? Number keys working means `InputEnable` is stuck.
- [ ] Laser traps of map 380 with the new cheat `clairvoyance`: no message when the laser is off (vars 336-341). The cheats `clairvoyance` and `mysticmap` themselves.

**Visual, compare remake and Amiga:**
- [ ] Shelf corner tile 0x1d4 is blocking: wise man house (482) at (6,5), also 442 (20,11) and (20,15), 443 (5,10), 451 (13,11).

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
- [x] Nalven's element table (Object_texts 1/6, German and English) shows the mental column of the game data, and the hint also lists Ghost Inferno and Mystic Decay (both spirit) (2026-10-28). Undead row added, left side is now spell/weapon element, hint: only weapons have the element undead (2026-10-29).
- [ ] Optional: restore the original source formatting where the port only replaced lines with disassembly style. Examples: `Default_PA`/`Default_MA`, the stack definitions, comments lost on `cmpa.l`.

### Missing Advanced features on the Amiga (remake has them)
- [x] Level > 50 through events, and the max-attribute increases for levels 51–55: done and tested 2026-10-19 with the wise man in S'Angrila (NPC 79). From level 50 on, the level reward goes up to 55; each of the levels 51–55 raises the maximum of a class attribute by 5 (`Level_shard_attributes` in `MAIN.S`, same table as the remake). Also fixed: the level reward used the "all" loop counter as party slot (wrong for the active member), and the level counters are now cleared after the level up. Remake: the level reward from level 50 on now also shows the level-up window like the Amiga (`EventHandling.cs`, Ambermoon.net master).
- [ ] Events 28–32 (show map, toggle switch, dynamic tile change, rectangular exploration, vertical line reveal): **implemented 2026-10-18** (`EVENTS.S`), built, not tested yet. Test in FS-UAE in the ancient city (483) and the ancient building (484): switches (29) with their doors/walls (30), the map tables (28) and the revealed rooms (31). The map table (28) and the revealed areas (31) work (2026-10-18, hide/reveal fixed); switches (29/30) still to be tested. Before, these events were silently skipped on the Amiga.
- [x] Hour movement does not seem to work on the Amiga: **fixed 2026-10-20**, tested 2026-10-21. Loading and the position per time step (step modulo 12) were already right. The cause was the 3D collision check: two path persons on the same square (objects 0/1 at (13,13) and 2/3 at (6,5) in the ancient building 484) blocked each other forever. Path persons in 3D now follow their path without collision checks, like the remake (`NPC_manager_3D` in `PERSONS.S`).
- [ ] New spells:
  - [x] New spell target "enemies in close range" (spell target bits $02, was the unused "row of friends"): hits all enemies on the 8 surrounding tiles, no target selection (only "out of reach" if nobody is there), the targets are determined when the spell is cast. No longer range with a long-range weapon (Amiga and remake, 2026-10-28).
  - [x] Magic sword attack (class 6 spell 26, energy sword item 556), Amiga like the remake: a physical special attack, so parade instead of anti-magic and no failing via "use magic". Damage = (attack damage + STR/25 + DEX/50, attribute bonus since 2026-10-31) x (APR + 1) / 2 (decided 2026-10-14), plus 0–25% and the spell damage bonus (spirit), heals the caster by 10% of the damage. The item can only be used when equipped (new message 327, German and English). Monsters use it if the mean danger of the party members around them is >= 50. Since 2026-10-28 the target's protection x APR (50–100%) is subtracted, "no damage" if not positive. Like a weapon attack no damage at all if the target has the element of the weapon (energy sword: spirit). Remake: the battle froze because the sword swing used the animation ticks (fixed). Not tested yet (FS-UAE and remake). Note: on the Amiga a parrying monster can also parry it (like weapon attacks), in the remake only party members parry.
  - [ ] Implement the other new spells (bow and staff of bosses 2/3).
  - [ ] Function spells for monsters, spell infos (class 6 is now possible for monsters, only spell 26 has a handler).
  - [x] Monster spell fallback: without a spell for the chosen target monsters now use the row in range, row or all spells (remake: didn't cast; Amiga: cast a stale spell from the list) (2026-10-28).
- [x] Weapon and ammunition elements ([Weapon elements.md], 2026-10-28): element in Misc_1 / SpecialValue (0 none, 1 spirit, 3 undead, 4–7 earth, wind, fire, water), ammunition with an element overrides the weapon. Same element as the target: no damage and no critical hit. Otherwise the factor of the spell element table (after the defense). Monster immunity flags (monster byte $0B, bit 0 = without element, bit n = element n) abort all attacks of the round with "<monster> is immune against an attack with element <x>". Amiga new, remake completed (factor, same element, no crit). Not tested yet. Elements set (2026-10-28): spirit 187, 276, 298, 417, 477, 556, 233, 323; undead 237, 415; water 196, 465; fire 428, 429; wind 473; earth 202. Only monster 98 (Staubteufel) has immunity flags ($39).
  - Note: Weapon elements.md says ghost = 2 and immunity bits 2..7, the code uses spirit = 1 (like the element table) and bit = element index.
  - Remake fixes on the way: the immunity message named the attacker instead of the monster, and item element names were off by one (spirit showed "Mental").
- [x] Minimum level for all equipment (item byte 22 = Misc_2 / TextSubIndex, 0 = none, 2026-10-28): equipping with a lower level shows message 328 "~INVN~ ist nicht erfahren genug, um diesen Gegenstand auszurüsten.". The second item window (identified items) is one row higher for equipment and shows ELEMENT (name incl. "Keins") and MIN-LEVEL ("-" or the number), messages 329/330. Remake tested 2026-10-28, Amiga not tested yet. Energy sword (556) has minimum level 51.
- [x] Extended languages on the Amiga (2026-10-30, built, not tested in FS-UAE): character byte $0D, conversations and switching the active member compare them too, language reward bits 8-15, party member condition type 4 (language, index 8 = ancient, used in the Morag maps 522, 523, 528; before it was skipped, so the chain went on as if true), inventory shows them with languages and conditions swapped like the remake. NPC 79 gives the ancient language. Test: Morag events without and with the language, NPC 79, inventory.
- [x] 3D combat background 13 → graphic 13 (desert, palettes 35/46/47 like the remake, 2026-10-28).
- [x] The APR reward adjusts `APRPerLevel` like the remake (level / (APR − 1), at APR 1 at least level + 1), and a level up never lowers the APR anymore (2026-10-28).
- [x] Reward targets 100+ and 200+ ("all but X") work. Fixed: the pointer was not freed for 100+ / first animal, and death (HP −100%) and revival / kill via conditions used the loop counter as the member number, so they were wrong for the active and random targets. Killing via a condition reward now shows the death instead of setting 1 HP (2026-10-28). Not tested in FS-UAE yet.
- [x] A 100+ / first animal reward target without a matching member stops the event chain like in the remake (Break_event, 2026-10-28). Dead and petrified members are never rewarded (except condition removal) and count as no match, now also in the remake (2026-10-28).
- [x] Automaps for the new maps: `Save.00/Automap.amb` has an entry for all 3D maps incl. 483-488 (checked 2026-10-30). Entry 483 shrunk to its 191 bytes. It starts fully revealed on purpose: the 3 monitors on the walls (show map event) show the whole map. The icons are a separate item (see 4.).

### Remake (Ambermoon.net, branch `master`)
- [ ] On the Episode 4 release (v1.40, Episode 3 is 1.3x): move `AdvancedMonsterFlags | ItemElements | ExtendedLanguages | LevelShards` into `Features.AmbermoonAdvanced`. Until then they are only switched on for external data in `GameWindow.cs` on purpose (Episode 4 development), the builtin Episode 3 versions must not get them.
- [x] Episode 3 changes (STA/25 HP on level up incl. bonus STA, bow damage bonus STR/50 + DEX/25, DEX/50 for other weapons): already in the remake (`StaminaHPOnLevelUp`, `AdjustedWeaponDamage`, checked 2026-10-29).
- [ ] Bow and staff boss spells (see 2.1).
- [x] Combat conditions like on the Amiga (2026-10-14): already in the remake (`ExtendedCurseEffects`, checked 2026-10-29). Fixed on the way: drugged bosses got no hit penalty at all, now half of it like on the Amiga.
  - Poison: per round 1 to 5% of max LP. The maximum is limited to 20 for party members and bosses and to 35 for other monsters. The remake uses a fixed 1–5.
  - Hit and parry penalties: drugs −25 (attack only), blind −50, aging −10 per step. The steps rise every round up to 5 and are reset each battle. Blind replaces aging. Bosses get half the penalty.
  - Damage and defense: disease −50% (bosses −25%), aging −10% per step up to −50% (bosses half).
- [ ] Crash when removing many items twice.
- [ ] Casting Self Heal in battle and clicking fast afterwards blocks the player selection (the keyboard still works). Not reproduced (2026-10-30, 6 rounds with one party member, spell picked by script, fast clicks on portrait and battlefield, `InputEnable` stayed true). Hint: portrait clicks need `InputEnable`, the number keys don't, so it was probably stuck on false. Needs a repro with several party members and the real spell list.
- [ ] Short wrong wall colours after teleporting (Cavetown, Spannenberg goto point), probably time-of-day dependent.
- [ ] 3D movement with WASD is sometimes slow.
- [ ] Lava stream: player drawn above the bottom rocks when moving down (remake bug?).
- [x] Wise man house (map 482): the player stood half inside the shelf on the corner (6,5). Tileset 7 tile 0x1d4 is blocking now, also in the maps 442, 443 and 451 (2026-10-30). The chair was already fixed.
- [x] Laser trap is noticed by Clairvoyance although its condition is not met: already fixed in the remake (23ee6720, conditions are evaluated before a trap/spinner is reported, e.g. the lasers of map 380 with vars 336-341). Checked 2026-10-29.
- [x] Eye cursor near lockpick doors in the Gral temple shows the spinner text: no bug. In map 475 the corners (25,18), (27,18), (25,20), (27,20) of the door room are spinners; looking at them from next to a door shows text 58 like on the Amiga (own tile first, then the tile in front). Looking at the door opens the door (tested 2026-10-29).

---

## 2. Episode 4 content (German first)

Order and details: `000 Plan Episode 4.md`, milestones M1–M4.

### 2.1 Ancient city (M1)
- [x] **Boss 1 (S-1, sword)** in map 484 (2026-10-30, tested in the remake): statue at (4,17) with its own graphic from the combat frame (texture 411 in 2Object3D, labdata 44 object 10 / group 16, palette 55, source `assets/desert-city/boss_statue`) and its own debris without the sword (texture 412, object 11 / group 17, `boss_statue_debris`), text 33, battle group 166, on flight text 34 and teleport to (7,16), on victory debris, text 35 and wall (12,21) opens, var 464. Immune to wind and spirit (monster 111, advanced flags 0x22). Combat graphic Monster_gfx 31 (also used by the placeholder of boss 3) has 14 frames since 2026-11-05: frames 9-13 = teleport like boss 2 (dissolve with growing blue ring, ring only, empty), monster 111 animation slot 8 (move) = 0, 9-10-11-12-13-12-11-10-9 each twice, 0 (20 frames), the idle animation (slot 1) stays 0-1-0-1-0-1; raw `assets/desert-city/sword_boss`, sheet `sword_boss.png`. Loot: energy sword and 7 ancient fragments. The blue plate is not a drop, it comes from the letter puzzle; the three boss rooms open the way to the red plate at (12,27).
- [ ] **Boss 2 (B-1, bow)** in map 484, placeholders (2026-10-31, monster cast, flight, win and loot tested in the remake): monster 114 "Antiker Schütze", based on monster 111 with the graphics of boss 1 (combat graphic, statue group 16, debris group 17), speed 75, 680 HP, immune to wind and spirit, battle group 170, texts 36 and 37, var 465. Own combat graphic since 2026-11-04 (Monster_gfx 32, 10 frames 128x128 in palette 26 of combat background 4: idle, drawing, drawn, released, hurt, then teleport frames 5-7 = dissolve with growing blue ring (style of the spell block ring, colours 1/24/25), 8 = ring only, 9 = empty; animations: idle 0, move (slot 8) 0, 5-6-7-8-9-8-7-6-5 each twice, 0 (20 frames, teleport instead of walking), attacks/cast 2-2-3-3-3 (idle, drawn, released, without the drawing frame), hurt 4, die 1 (the drawing frame), start 0/2/3/0; battlefield icons 31 and 32 (all three bosses) = bust downscaled from the boss 1 idle frame, `assets/desert-city/boss_icon.png`; sources `assets/desert-city/bow_boss_sources`, sheet `bow_boss.png`, raw `bow_boss`/`bow_boss_icon`; tested in the remake, not yet on the Amiga). Still needs: own statue. The debris stays the one of boss 1 (group 17): the bow is taken as loot and the bosses look the same otherwise. Energy bow = item 559 ("Energiebogen", renamed from "Magischer Bogen" on 2026-11-08; icon 259, damage 49, DEX +10, use magic +10, max LP +25, max SP +25, parry -20, spirit element, M-B-W 10 (2026-11-08), min level 51, adventurer/thief/ranger, 30000 gold, 1 hand, needs arrows for normal attacks but not for arrow hail, no element). The boss has base attack 100 and 100 magic arrows (233): 25 in the left hand and 75 in the inventory (used first). Energy sword (556), energy bow and energy staff: 50 charges, not cloneable (2026-11-08), unlimited recharges at 100 gold per charge. Energy sword since 2026-11-08: damage 55, defense 2, max LP +25, max SP +25, anti-magic +10, use magic +10, attack -10, parry -10, spirit, M-B-W 10, min level 51, 30000 gold. Spell arrow hail = class 6 spell 27 (remake `MagicArrowHail`, Amiga `CMagic_arrow_hail`): all enemies, (damage + DEX/25 + STR/50) x (APR + 3) / 4 plus 0-25%, minus protection x APR, no spell damage bonus, heals 5% of the damage, parade instead of anti-magic. Shown as one volley of arrows, then per target the hit and a green ball to the shooter (Amiga: 1 arrow per target, Max_COMOBs 48).
- [ ] **Boss 3 (F-1, staff)** in map 484, placeholders (2026-10-31, monster cast, win and debris tested in the remake): monster 115 "Antiker Magier", based on monster 114 with the graphics of boss 1, STR 50, INT 115, DEX 85, 510 HP, 6000 SP, lamed so it always casts (2026-11-08; energy absorption costs 80 SP, so 75 casts; it never moves, so the teleport animation is not used), base attack 60, immune to wind and spirit, 50% magic damage reduction, battle group 171, statue at (4,25), debris, texts 38 and 39, flight to (7,26), var 466. Own combat graphic since 2026-11-08: Monster_gfx 33, 9 frames 128x128 in palette 26 with the feet on one baseline: idle, charge (staff raised), aim (staff pointed at the viewer with an energy burst), hurt, then teleport frames 4-6 = dissolve with growing blue ring, 7 = ring only, 8 = empty; monster 115 animations: idle 0, move (slot 8) 0, 4-5-6-7-8-7-6-5-4 each twice, 0 (20 frames, teleport), attacks/cast 1-1-1-1-2-2-2, hurt 3, die 3, start 0/1/2/0; battlefield icon 33 (new in Combat_graphics, copy of the shared boss icon 31/32; the remake crashes without an icon for each combat graphic); sources `assets/desert-city/staff_boss_sources`, sheet `staff_boss.png`, raw `staff_boss`; tested in the remake (battle start), not yet on the Amiga. Guardian orbs (2026-11-08): monster 117 "Wächterkugel" (English "GUARDIAN ORB" in AllTexts; "Energiekugel" is monster 100), 2 of them in group 171 in the front row (columns 2 and 5), the mage moved to the back row (column 3). Passive damage sponges: lamed, no SP and no spells, 350 HP, defense 25, anti-magic 25, damage 0, morale 100, no boss flag (critical hits kill them), no loot, 1500 defeat experience, level 40. Placeholder combat graphic Monster_gfx 34 (64x64, displayed 64x64, palette 26): idle A, idle B, hurt, then dissolve with growing blue ring 3-5, 6 = ring only, 7 = empty; animations: idle 0/1, hurt 2, die 3-7 (bursting), start 7-6-5-4-3-0 each twice (appearing from the ring, starts invisible); battlefield icon 34 in Combat_graphics. The icon only uses the colours 0-23 for the blue ring: the remake draws battlefield icons with the main UI palette, the Amiga with `Tactic_pal`, and both only match in 0-23. Raw `assets/desert-city/energy_orb`, `energy_orb_icon`, sheet `energy_orb.png`. They appear one after the other after the mage (see the appear order entry below). Remake: appear order and passive first round tested; Amiga not tested. To do: real graphics from the image AI (prompt from 2026-11-08), then replace frames 0-2 and redo the dissolve frames. Still needs: own statue. Energy staff = item 560 (own icon 268 since 2026-11-08: golden staff with a bluish crystal, from the reference `assets/magic-staff.png` converted to the UI palette in the style of the originals (no outline, shadow to the lower right in colour 26), `assets/magic_staff.png` and raw `magic_staff`, item flag ExtendedGraphicIndex; tested in the remake inventory; damage 35, INT +10, use magic +10, max LP +25, max SP +50, attack -20, spirit element, M-B-W 10 (2026-11-08), min level 51, mystic/healer/alchemist/mage, 30000 gold, 50 charges, unlimited recharges at 100 gold per charge). Spell energy absorption = class 6 spell 28 (remake `EnergyAbsorption`, Amiga `CEnergy_absorption`): enemy row, 80 SP (free from the item), normal spell (Use Magic, anti-magic), 50-100% of the caster level plus the usual spell damage bonus, caster gains 5% of the damage as LP and SP. Upside down thunderbolt, then a green and a blue beam per target, then the hurt animation. Untested: player with the staff, flight, Amiga.
- Decided (2026-10-14) for the ancient weapon spells ([Neue Zauber.md]):
  - Each target is hit once, and the damage is multiplied by 1 + (APR - 1) * 0.5 (1 APR: x1, 3 APR: x2, 5 APR: x3).
  - A normal attack with an ancient weapon is a plain weapon attack. The spell is only cast via "use item".
- [ ] Bosses use the new spells and may need different battle actions (moving closer).
- [ ] Boss rooms 2/3 of map 484 use the placeholder groups 170/171. Only adjust these groups when building the real bosses.
- [ ] Separate move animation (2026-11-05): monsters use animation slot 8 (unused in the original) for moving if it has frames, otherwise the idle/move animation of slot 1 as before. Remake: `MonsterAnimationType.AdvancedMove`, `Monster.MoveAnimationType`, used in `Battle.cs`; Amiga: `Move_anim` in `GAME_OFF.S`, `Move_anim_type` in `COMBAT.S` (monster move). Tested in the remake, Amiga assembles (2026-11-05) but is not yet tested. In the remake slot 8 uses a fixed frame duration of 1/12 s per field (like the Amiga, one frame per screen update) instead of spreading the animation over 0.5 s per field. The sprite still slides during the move animation.
- [ ] Bosses appear first (2026-11-08): the appear (start) animations play one after the other in battlefield order (row by row, back row first), in the original and in the remake. Now monsters with the boss flag come first, then the others, so summoned monsters appear after the boss (no matter where they stand; group 171 has the boss in the back row anyway). Remake `Battle.cs` orders the start animation queue by the boss flag; Amiga `COMBAT.S` runs the appear loop twice (bosses, then the others). Remake tested with group 171, Amiga assembles but is not tested.
- [ ] Wait cursor during the monster appear (start) animations (2026-11-05): remake `Battle.cs` sets `CursorType.VideoWait` while the start animations run and the sword afterwards; Amiga `COMBAT.S` pushes the Zzz pointer of the delay event (`Default_Mptr+2700`) around each appear animation. Not yet tested (remake builds, Amiga assembles).
- [ ] Lamed monsters always cast if they have spells and enough SP (2026-11-05): remake `Battle.PickMonsterAction` skips the attack options when the monster can neither attack nor move (before it did nothing in 8 of 16 cases, the original Amiga tries the remaining options); Amiga `MONSTER_.S` `Determine_monster_action` never selects the defensive action when the monster can't move (`Move_mask`). Affects the lamed mechanical guardians. Not yet tested (remake builds, Amiga assembles).
- [ ] Map 484: only boss 2 and boss 3 are still open. No other events are planned (2026-11-01).
- [ ] Map 483 (surface):
  - Patrols (trap + text + teleport, maybe a new "unavoidable trap" flag).
  - Attribute-gated levers.
  - Morag golems (no gfx yet).
  - Giant lizard at the red entrance.
- [ ] **Central temple, map 485**. The four stairs of the city centre building (483) lead to the matching temple entrances: north (20,18) <-> (14,3), east (22,20) <-> (25,14), south (20,22) <-> (14,25), west (18,20) <-> (3,14) (2026-11-01). The doors in front of them need the plates. Still open:
  - Four entrances matching the plates.
  - Rotating centre section.
  - Switch chain leading to the central room with 3 teleporters.
  - Consume all key cards when the portals are activated.
- [ ] Giant lizard: monster 116 and battle group 173 exist (2026-11-01, based on the sand lizard, blood red, 1200/1287 HP, 800/891 SP, damage 100, defense 22, attack 90, M-B 95, crit 2, APR 2). City 483 (20,16), behind the red door: text 8, battle with 3 sand lizards until won, on flight text 9. Drops 15 fragments and the lizard essence for Kasimir (item 564 "Echsenessenz", icon 262, source assets/lizard_essence.png). Spells: madness, whirlwind, earthquake, earth spell damage bonus. The wise man (NPC 79) applies the essence if Kasimir has all others (vars 262-267, 477 set by Dorina for the wasp essence): level + 5, damage 10-12, defense 3-5, APR + 1, M-B-W + 1, search + 20, current luck + 15, portrait 109 (dark red with glowing stripes, assets/KasimirLizard.png). Afterwards he gives the important item 565 "Halsband der Wüste" (animals only, min level 55, LP 40, defense 10, damage 10, M-B-W 1, M-B-R 1, attack 10, anti-magic 10, whirlwind with 30 charges, unlimited recharges at 10 gold per charge). Icon 263, source assets/desert_collar.png. Sandra and Dorina only mention the strong aura. Still open: level of the lizard. Savegame patcher: set glob var 477 if Kasimir already has the wasp essence (portrait 108). The wise man applies it, and Kasimir becomes level 55 ([Neue Essenz.md]).
- [ ] New monsters: Morag golem, giant lizard and its escort ([Neue Monster.md]).

### 2.2 Portals and Lyramion vault (M2)
- [x] Two new portal stones (2026-11-01), so they can't be confused with the red, yellow and green ones: blue (item 561, icon 260, tower top chest 309) and grey (item 562, icon 261, sources assets/portal_orb_*.png). The grey one still has to be placed in the Antike Anlage.
- [x] Thuna desert vault replaced (2026-11-01): the temple teleporter (485, (12,14)) leads to the tower top (405, (13,10)). Lever (10,11) opens the wall (9,10). Without the lever bit of map 404 (tower never played) Lebab banishes the party to the world map (38,28), the wall closes and the lever is usable again. Labdata 27: table with stools (group 24), wall 113 with overlay 70. The upper part of the room has a 1-tile corridor (10,7–8) with chest 309 at (10,7) holding the blue portal stone (item 561) and the Portalbuch (item 563, object text 5/5). Opening it sets glob var 475; on a later talk Lebab tells about it once (var 476, NPC 23 text 12) and adds the keywords 175-177 (text 13). Showing or giving him the portal stones or the book also gives text 13, the items stay with the party. The corridor is open to the lower room at (10,9). Savegame patcher: add chest 309. Free map indices stay 489–512, never append: the Amiga archive limit is 530 entries.
- [x] Portal 1: Morag ↔ tower top (405), both directions (2026-11-01). Still always active, no plate or stone condition yet.
- [x] Portal 2 (2026-11-01): temple (16,14) pushes the party back to (15,14) looking east without the blue portal stone, uses up the blue portal stone (561) once, sets glob var 473 and leads to AA2 367 (12,4) looking east, afterwards it works normally. First arrival (chain 24): guard group of the second storage from the left at (14,3), all walking lightnings off. The groups of the other storages still spawn at the teleporter when picking the lock fails. Wall storage (14,2): defective text while var 473 is 0, otherwise it opens chest 216 (0-based) with the grey portal stone (562), text only once (var 474). The teleporter (11,4) leads back to the temple center when var 473 is 1.
- [ ] Portal 3: "coming in Episode 5" text, then the party is teleported back 1 tile.

### 2.3 Morag progression and balancing (M3)
- [ ] **Shard economy:** the budget sheet lists 46 shards obtainable now and about 525 planned; the goal is about 600 without grinding.
  - Drops from council lizards, golems, the giant lizard and the bosses.
  - Temple chests.
  - Random battles on all Morag world maps (513 and 526 have none yet).
  - Hide shards, add them to monsters.
- [ ] **Level-gated equipment 51–55** ([Waffenlevel.md]): the item byte, the item window and the check are done (see 1.). All three boss weapons (energy sword 556, energy bow 559, energy staff 560) have minimum level 51 (2026-11-08). Still to set in the data: the Rebellenklinge 52.
- [ ] **Elemental weapons in the data** (most are set, see the list in 1.):
  - Feuerbrand (276) stays spirit (decided 2026-10-29, with fire it would be useless in Luminor's tower).
  - New Sandschwert (earth). There is no Eisschwert; the Eisstab (465) has water.
  - [x] Flamberge (428, fire), Waldbogen (473, wind), Necromanten Dolch (237, undead), Geisterstab (477, spirit) and the undead row of the element table are done (2026-10-28). Energy bow (559) and energy staff (560) spirit like the energy sword (2026-11-08).
- [ ] Are there element change spell scrolls anywhere?
- [ ] Monster immunity flags in the data: only the dust devil (98, $39) has them so far. Decide which other monsters get some.
- [x] New item icons follow the style of the originals (2026-11-02): no outline, shadow to the lower right in color 26, diagonal corners in color 27. Changed: 211 (also without the red cross), 226, 227, 231, 233, 239, 241-245, 247-255, 257, 264-266.
- [x] Icons (2026-11-02): 239, 240 and 243 edited by hand, 211 is now a green pearl, new icon 267 is an amber pearl for item 446 "Stein der Erkenntnis".
- [x] New icons for Morag equipment (2026-11-02): robe 382 = icon 264, sword 394 = icon 265, dagger 532 = icon 266, sources in assets/morag-equip (*-final.png use the item palette).
- [x] Council lizards on Morag drop ancient fragments (2026-11-01): S'Arin 15, S'Endar 20, S'Trog 25, S'Kat 35, S'Lorwin 50. S'Riel and S'Orel drop none.
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
  - Labdata 14: chest object 54 (block 61) and Bore's graphic from the Gemstone ruins (texture 322, now also in 3Object3D.amb) as object 55 / group 62 for NPC 80. 2Lab_data.amb and 3Lab_data.amb must stay identical (the remake only reads 2Lab_data, the Amiga reads the one of the map disk).
  - NPC 80 in the mine: first talk gives 5000 EXP (var 472), then he trades navstones.
- [ ] Bore quest follow-ups:
  - Test it on the Amiga (cheat build). Remake: remove party member event built and tested (2026-10-29), older savegames get missing party members/chests from the initial savegame.
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
  - Ancient site 2 (367), wall storage (14,2), chest 217 (1-based) now holds the grey portal stone (562), glob vars 473 and 474 are new: hide the guard group of the second storage from the left (character bit 367:2) if it already spawned. Move items, gold and food of the old chest content into a neighbouring open chest of the room (215/217/220, 0-based), otherwise delete them silently, this case is very rare. Reset the chest unlock flag of chest 216 (0-based) to not unlocked for correctness.
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
- [x] Ancient building (484): the dark doors (wall 115, texture 192) at (2,5) and (2,13) are only a design element for the autonomous robots. The player never reaches this area, so they have no events (2026-11-01).
- [ ] 3D maps with walkable floor at the map edge (no event): 284, 339, 413, 415, 416, 424 (all original, cosmetic).

### English text check (`tools/ambtools/textcheck.py`, 2026-10-18)
Fixed: untranslated text 369/2, 22 texts with missing or extra quotes, typos (also in the Ambermoon repo), stale English texts of maps 335 and 440, monster 111 renamed to ANCIENT WARDEN (16 characters didn't fit), German party text 8/8 quote.
- [x] Grail swamp hint (NPC 47, text 4): GRAL, AT NIGHT and the mountain flank highlighted in English too, like in German.

### Original bugs (also fix in the Ambermoon repo)
- [x] Lava tiles must block walking and the horse (world map). Tileset 1, tiles 235-238 (2026-10-18). Already fixed in the Ambermoon repo.
- [x] Stairs in the Thalion office: original fix taken over, new tileset 4 tiles 0x4a6-0x4a8 in map 257 (2026-10-23).
- [ ] Non-blocking walls: trainer house 268 upper wall fixed in both repos (tileset 4 tiles 0x3b1-0x3b3 use background flags, 2026-10-23). Remaining candidates to check visually: witch house 411 (17,7) ts4 0x324 (BringToFront object on blocking background), armoury 407 (10,10) ts5 0x186; probably intended: 417 (14..18,8), 341 (18,11), 477 (2..3,2).
- [x] Text bug in the thief cellar (bandit house cellar, map 276): the original fix from the Ambermoon repo taken over (2026-10-23).
- [x] Two-hand weapon and shield: the Amiga is correct (drag and drop only). Remake bug in shift-click equipping fixed in `Windowing.cs` (2026-10-23).
- [x] Monsters can't pass the green slime in the old cave. Labdata 2, objects 15-17 also allow class 1 (2026-10-18, also in the Ambermoon repo, master).
- [x] Map 273 (town house): teleport from map 263 (event 72) now leads to (10,4), both repos (2026-10-23).
- [x] S'Angrila (map 442 text 2) "bin": was already fixed in Advanced, fixed in the Ambermoon repo (2026-10-23).
- [ ] Sleep and fear lead to game over: **fixed 2026-10-23**, not tested. Amiga (both repos): no defeat while members are on the battlefield, the leader is kept if nobody can lead, OK starts the next round. Remake: `RecheckActivePartyMember` starts the next round automatically. Stalemate check after each round (2026-10-27, Amiga in both repos, remake): mad, asleep, panicked, lamed and petrified count as incapable; the battle goes on if a party member is capable, anyone is only panicked or a member is only asleep while a monster is capable, otherwise game over. Ambermoon repo: branch `fix/combat-stalemate`, merged into master. Test: battle where all members get asleep/panicked/lamed.
- [x] Forest moon navstones: left as is (2026-10-27). Gemstone gives navstones after the return to Lyramion (the first one for free), Morag has some too.
- [x] Text 2 in AA4 ("GEHEMNISVOLL"): already fixed in Advanced, fixed in the Ambermoon repo (2026-10-23).
- [x] Automap shows traps without Mystic Map: the Amiga now also hides trap/trapdoor/spinner icons of walls and objects without the trap function, like the remake and the legend (both repos, 2026-10-23).
- [x] Attack icon after the weapon breaks: the Amiga was correct; the remake now updates the battle buttons after each round (`BattleHandling.cs`, 2026-10-23).

### Advanced
- [ ] Some world map shadows are broken (sand boat tower etc.).
- [ ] Wrong tiles on the Morag world map (low priority, check visually later). Known so far: 522 tower at (4,2) has a broken shadow (only the bottom row 0x96-0x98 at (5..7,4) plus a rock decal 0x13d-0x140 at (6..7,3..4)); the tower at 522 (6..8,48..50) overwrote overlay 0x1d8 at (7,48) of an original 6x4 structure (0x1c5-0x1db at x 5..10, y 45..48) and should move; towers at 523 (27,19) and 528 (31,6) have no shadow. Robert also suspects errors at the transition on the right edge.
- [x] Moving mushrooms in Dor Grestin: hand/eye condition in front of the text (map 339, 2026-10-23). The original has the same data, but the condition needs the Advanced executable.
- [x] Protection spell: the protection bonus was added when the attacker was a party member, so it protected the monsters instead of the party (original bug, fixed in Advanced and on the Ambermoon branch fix/combat-stalemate, 2026-10-28). The remake was already right.
- [x] Wall storages in map 484 could only be used diagonally because the robot wrecks blocked the front tile: the wreck object (lab 44 object 2) is walkable now (2026-10-27).
- [x] Transfer stone on yourself: the caster can't be selected anymore (Amiga) / the stone is not used up (remake) (2026-10-23).
- [x] Battery: items added by events go to the active member first (Amiga: the loop advanced the item pointer instead of the party pointer; remake too). Also fixed the random reward target code (2026-10-23).
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

## Handbook

- [ ] New version of the manual after all 5 episodes are finished (the current one only covers the first episodes). Design sketches are collected in the private repo https://github.com/Pyrdacor/Ambermoon-Advanced-Book.
- [ ] Polished sketches go into the appendix of the manual: `assets/sketches` on master of that repo (2026-11-02, 34 files). 13 are still named Unknown_XX, 7 Ancient-Building-X are not yet matched to the 4 buildings.

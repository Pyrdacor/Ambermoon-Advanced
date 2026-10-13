# Porting the Advanced changes to AmbermoonSource

The Advanced changes were originally made in the disassembly `code_changes/AM2_CPU.s`. That file
is based on the disassembly of the original game `Disks/Bugfixing/Executables/AM2_CPU.s` in the
Ambermoon repository, in the state of commit `62823505`. The disassembly was later replaced there by
the reconstructed source `AmbermoonSource`. It was last available in commit `382eaeda` and deleted in
`4b050b68`.

`code_changes/AmbermoonSource` started as a copy of `AmbermoonSource` from Ambermoon `59352ca2`
(commit `6c2a4997` in this repo). The Advanced changes were then ported onto it, mostly
automatically, with the scripts in `tools/`.

## Method

1. **Normalize** (`norm.py`, `canon.py`): Strip comments from both disassemblies (Advanced and
   original `62823505`), qualify local labels with their global label, and write numbers in decimal
   without branch size suffixes.
2. **Map labels** (`labelmap.py`, `rename.py`): Advanced renamed many disassembly labels. Two kinds
   of label pairs are aligned:
   - pairs of definitions;
   - pairs of references, weighted double.

   The mapping is seeded with the names that `SYMBOLS.txt` knows. It is one-to-one, and suspicious
   pairs are dropped (`validate()`). The Advanced text is then renamed to the original names.
3. **Diff** the canonical texts (`git diff --histogram`) → hunks.
4. **Locate** (`plan.py`, `srcmodel.py`, `lstmap.py`): Find the target of each hunk:
   - base line `62823505`
   - → line `382eaeda` (the last disassembly, byte-identical to `AmbermoonSource` 1.21 = Ambermoon `d7c23c1a`)
   - → section and offset (vasm listing)
   - → `AmbermoonSource` 1.21 file and line (listing)
   - → line in the current `AmbermoonSource` (diff per file).
5. **Classify** (`already.py`, `classify.py`): Sort out hunks that are already contained in 1.21
   (bugfixes that were made in both projects). Decide how every other hunk can be applied:
   replace exactly the source lines of the removed code, insert, or rewrite part of a data or macro
   line (`region.py`).
6. **Apply** (`port.py`): Translate the names of the Advanced text into source names:
   - via `SYMBOLS.txt`, or the source label at the same address;
   - otherwise as `Label+offset`, or by adding the disassembly label to the source.

   Then apply the hunks.

   Advanced's global labels in the middle of an original routine would break the routine's local
   labels (`.x`). `scopes.py` handles this per routine:
   - It makes such an inserted label local if only that routine uses it.
   - Otherwise it makes the crossing local label global (`Routine_Label`).
7. **Build** (`build.py`): Assemble. Short branches that are out of range now are widened
   (`.s` → `.w`).
8. **Verify** (`bincmp.py`, `review.py`, `relcheck.py`), see below.

`run_all.sh` runs steps 1–7, `verify.sh` steps 6–8 on a fresh copy of the base commit. The inputs (`base/*.s` from the Ambermoon history, `adv.s` = old
`code_changes/AM2_CPU.s`, `src121/` = `AmbermoonSource` at Ambermoon `d7c23c1a`, the listings and
`lst.pkl` from `lstmap.py`) were prepared by hand in the working directory (the parent of `tools/`).
The scripts are kept for reference. They are not needed to build the game.

## Decisions taken by hand (`MANUAL` / `EQUIV` in `port.py`)

| Where | Decision |
|-------|----------|
| Monster knowledge (`COMBAT/COMBAT_M.S`) | Advanced plays the animation in a new subroutine. Its moved exit label is not needed (both exits are `rts`). |
| `CShow_monster_LP` | Advanced rewrote the routine. The old routine became the star animation (`FUN_ShowMysticStarsAnimation`). The new routine keeps the source name. |
| Year change (`TIME.S`) | 1.21 already increments `Time_data_year` (= Advanced's `DAT_YearsPassedSince978`). Advanced's own increment was dropped, so the year doesn't count twice. |
| Jump target check (#98) | 1.21 has it as `Check_jump_target` / `Do_condition_events`. Only Advanced's `FUN_ExecuteConditionEventsExcept` (used in `ACTIONS.S`) was added. |
| `MysticBackupData` | New BSS variable at the end of `Longword_BSS`. It is placed with an explicit `SECTION`. |
| `DAT_Random_party_members` | New chip BSS variable at the end of `Chip_BSS2` (`MAP/3D_BLIT.S`). It is placed with an explicit `SECTION`. |
| Item data buffer (`KERNEL/TEXTS.S`) | Size 36000 bytes (600 items). |
| Patch space (`KERNEL/TEXTS.S`) | The new code that Advanced placed in the unused `dcb.b 8322,0` at the end of the Texts code hunk replaces that line. |
| `Combat_data_size` | Defined in the source at the same address, so Advanced's `EQU` is not needed. |
| `FUN_ProcessConversationEvent` | In the base disassembly this was `Dia_action`. Advanced renamed it to `FUN_HandleConversationEventTriggers` and gave the old name to `Handle_DIA_event` (`EQUIV`). |
| `Party_or_monster` | Advanced's label is the same symbol as the source label (`EXTRA_ALIASES`). |
| Datachange random values (`EVENTS.S`) | Advanced and the source both fixed "random value 0…max-1 → 1…max". Only the source fix (`addq.w #1,d2`) is kept, otherwise 1 would be added twice. |
| `Remove_member` (`EVENTS.S`) | Both fixed the item dump loops. The source uses `d1` as loop counter and sets `d1` before saving the chest; Advanced used `d7`. Only the source fix is kept, because Advanced's counter doesn't fit the source loops. |
| `Copy_data` (`KERNEL/TEXTS.S`) | Same `btst` fix in both. The source lines (with their comments) are kept. |
| `Write_file_data` (`KERNEL/FILES.S`) | The source writes in a loop until everything is written (PFS fix). Advanced instead reported a partial write as custom error 501. The source version is kept, so the 501 message mapping in `HULL/CONTROLS.S` is no longer used for writes. |
| `World_data` (`KERNEL/DATA.S`) | The inserted monster tables end on an odd address, so an `even` was added before the label. Before, only the `dc.w` was auto-aligned, not the label. |

## Labels

- New Advanced labels keep their names (`FUN_…`, `DAT_…`, `LAB_…`).
- 88 new labels inside original routines became **local** (`.FUN_EventRewardAttribute`, …).
- 7 local labels of original routines became **global** because Advanced code between them and their
  routine start defines global labels:
  - `Wake_the_dead_Do1`, `Wake_the_dead_Do2`
  - `CMonster_knowledge_Exit2`
  - `Load_subfile_sizes_Skip`, `_Skip2`, `_Skip3`, `_Loop`
- New local labels that clash with a source local label get the suffix `_Adv`, `_Adv3`, ….

## Verification

The old Advanced build (`code_changes/AM2_CPU.s`) was compared with the build of this source.

- **Instruction/data stream** (`bincmp.py`, byte tokens, relocations masked): 46 difference blocks.
  Most of them are the known differences between the original disassembly and `AmbermoonSource`
  1.21 or its later fixes (#69, #73, #74, #134, guru on quit). `review.py` sorts these out. The 17
  remaining blocks are all harmless:
  - The original modules assemble with optimizations (`opt o2+,o4+,o5+,o11+`). The inserted
    Advanced code is optimized as well: `add #1` → `addq`, `move.l #0` → `moveq`, `0(an)` → `(an)`.
    The changed flags (`X`) are not used afterwards.
  - PC-relative displacements in `Decompress_chunk` (#134 fix).
  - The glyph tables are in the `Font_DATA` hunk in `AmbermoonSource`.
  - Alignment bytes.
- **Relocations** (`relcheck.py`): All 16351 relocations of unchanged code were checked. Each must
  point to the same symbol plus offset in both builds. Remaining differences are only names:
  - The same address under another name (`TreeStack_end` = `Window_stack`, `HLC_table` entries,
    `Load_0`, `Cut_A`, …).
  - New Advanced labels that are local now (`FUN_EventRewardAttribute` = `.Attribute`, …).
  - Offsets inside routines that became shorter because of the optimizations above.
  - The #98 decision (`FUN_ExecuteConditionEvents` → `Do_condition_events`).

- **Labels** (`labelcheck.py`): The checks above compare the byte stream and the relocation
  targets, but they can't see a label that sits in front of or behind inserted code. This happened
  where comment lines are between a label and its first instruction. For every label pair, the
  bytes behind the label must be the same in both builds. Only optimized instructions and the
  known name differences remain.
- **Double fixes** (`overlap.py`): Some original bugs were fixed in Advanced and, independently,
  in Ambermoon after `62823505`. The review above treats a difference which equals an original fix
  as known, so it can't see a fix that is applied twice. `overlap.py` therefore lists every applied
  hunk near a line that changed between `62823505` and `382eaeda`, or between 1.21 and the current
  source. Each of these hunks was checked by hand, which found the Datachange, `Remove_member` and
  `Copy_data` cases above.

The ported source has not been tested in the game yet. Test it in the remake and on the Amiga before
it replaces `code_changes/AM2_CPU`.

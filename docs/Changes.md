Note: The changes are only done to the german files. The only exception are the executables which are fixed both.
The english version can then be done by diffs or adding the files.


## Party_char.amb

- Changed max ATT of hero from 80 to 85. Change byte 0x00BF from 0x50 to 0x55.
- Set max for all 3 lock-related skills to 0 for hero. Bytes 0x00DF, 0x00E7 and 0x00EF.
- Set cur/max for lockpicking skill to 0 for Valdyn. Bytes 0x1F5F and 0x1F61.
- Set cur find trap skill to 15 and max to 85 for Valdyn. Change 0x1F4F to 0x0F and 0x1F51 to 0x55.
- Set cur disarm trap skill to 10 and max to 75 for Valdyn. Change 0x1F57 to 0x0A and 0x1F59 to 0x4B.
- Set max find trap and disarm trap skill for Selana to 99. Change 0x15AF to 0x63 and 0x15B7 to 0x63.
- Set cur lockpick skill to 5 and max to 35. Change 0x15BD to 0x05 and 0x15BF to 0x23.
- Set max crit for Selena to 5. Change byte at 0x15A7 to 05.
- Set cur and max search skill for Gryban to 0. Change bytes 0x285F and 0x2861 to 0.
- Set cur and max search skill for Selena to 0. Change bytes 0x15C5 and 0x15C7 to 0.
- Set cur and max search skill for Egil to 0. Change bytes 0x1289 and 0x128B to 0.
- Set max search skill for hero to 50. Change byte 0x00F7 to 0x32.
- Set cur/max search skill for Valdyn to 15/99. Change byte 0x1F67 to 0x0F and byte 0x1F69 to 0x63.
- Set cur/max crit skill for Valdyn to 00/02. Change byte 0x1F47 to 0 and byte 0x1F49 to 0x02.
- Set max read magic skill to 99 for all magic classes. Changes all of the following bytes to 0x63:
    - 0x00FF, 0x02EB, 0x0ABD, 0x0ABF, 0x0D59, 0x0D5B, 0x0FF5, 0x0FF7, 0x18F1, 0x1C15, 0x1F71, 0x22D1, 0x2591 and 0x2869.
- Set max use magic skill to 99 for all magic master classes and 50 otherwise.
    - Set bytes to 0x63: 0x0AC5, 0x0AC7, 0x0D61, 0x0D63, 0x0FFD, 0x0FFF, 0x18F9, 0x1C1D, 0x22D9, 0x2599.
- Change SLPperlvl for hero to 1. Change byte 0x012B to 0x01.
- Change SLPperlvl for Valdyn to 1. Change byte 0x1F9D to 0x01.
- Change SLPperlvl for Gryban to 1. Change byte 0x2895 to 0x01.
- Change SLPperlvl for all other magic chars to 58. Change the following bytes to 0x3A:
    - 0x1023, 0x191D, 0x1C41, 0x22FD, 0x25BD
- Change start SLP of Tar to 85. Change byte 0x0F4F to 0x55.
- Change start SLP of Nelvin to 278. Change byte 0x1848 to 0x01 and byte 0x1849 to 0x16.
- Change start SLP of Sabine to 180. Change byte 0x1B6D to 0xB4.
- Change start SLP of Targor to 455. Change byte 0x2228 to 0x01 and byte 0x2229 to 0xC7.
- Change start SLP of Leonaria to 1310. Change byte 0x24E8 to 0x05 and byte 0x24E9 to 0x1E.
- Change start SLP of hero to 2. Change byte 0x0057 to 0x02.
- Change start SLP of Valdyn to 3. Change byte 0x1EC9 to 0x03.
- Change start SLP of Gryban to 5. Change byte 0x27C1 to 0x05.
- Change hero start INT to 20. Change byte 0x0075 to 0x14.
- Change Valdyn start INT to 24. Change byte 0x1EE7 to 0x18.
- Change Hero APRPerLevel value to 16. This changes end APR to 4. Change byte 0x0125 to 0x10.
- Change Gryban APRPerLevel value to 12. This changes end APR to 5. Change byte 0x288F to 0x0C.
- Change Tar APRPerLevel value to 30. This changes end APR to 2. Change byte 0x101D to 0x1E.
- Change Egil APRPerLevel value to 9. This changes end APR to 6. Change byte 0x12B9 to 0x09.
- Change Selena APRPerLevel value to 17. This changes end APR to 3. Change byte 0x15F5 to 0x11.
- Change Nelvin APRPerLevel value to 40. This changes end APR to 2. Change byte 0x1917 to 0x28.
- Change Sabine APRPerLevel value to 26. This changes end APR to 2. Change byte 0x1C3B to 0x1A.
- Change Valdyn APRPerLevel value to 14. This changes end APR to 4. Change byte 0x1F97 to 0x0E.
- Change Targor APRPerLevel value to 16. This keeps end APR at 4. Change byte 0x22F7 to 0x10.
- Change Leonaria APRPerLevel value to 16. This keeps end APR at 4. Change byte 0x25B7 to 0x10.
- Change Gryban start APR to 3. Change byte 0x27BD to 0x03.
- Change max strength of Selena to 40. Change byte 0x153F to 0x28.
- Change max attack skill of Selena to 80. Change byte 0x158F to 0x50.
- Change current attack skill of Selena to 45. Change byte 0x158D to 0x2D.


## AM2_CPU / AM2_BLIT (german | english)

- Add ATT bonus of 15% to Knife. Change byte 0x4FD84 / 0x52AD4 | 0x4F510 / 0x52260 to 0x0F.
- Add ATT bonus of 15% to Dagger. Change byte 0x4FDC0 / 0x52B10 | 0x4F54C / 0x5229C to 0x0F.
- Add ATT bonus of 10% to Shortsword. Change byte 0x4FDFC / 0x52B4C | 0x4F588 / 0x522D8 to 0x0A.
- Add ATT bonus of 5% to Longsword. Change byte 0x4FE38 / 0x52B88 | 0x4F5C4 / 0x52314 to 0x05.
- Add ATT bonus of 5% to Club. Change byte 0x4FF64 / 0x52CB4 | 0x4F6F0 / 0x52440 to 0x05.
- Reduce break chance of Firebrand down to 0.01%. Change byte 0x513BF / 0x5410F | 0x50B4B / 0x5389B to 0x01.
- Add PAR bonus of 15% to Buckler. Change word 0x4FC93 / 0x529E3 | 0x4F41F / 0x5216F to 0x010F.
- Add PAR bonus of 25% to Round Shield. Change word 0x4FCCF / 0x52A1F | 0x4F45B / 0x521AB to 0x0119.
- Add PAR bonus of 35% to Small Shield. Change word 0x4FD0B / 0x52A5B | 0x4F497 / 0x521E7 to 0x0123.
- Add PAR bonus of 45% to Large Shield. Change word 0x4FD47 / 0x52A97 | 0x4F4D3 / 0x52223 to 0x012D.
- Add PAR bonus of 55% to Morag Shield. Change word 0x52FAB / 0x55CFB | 0x52737 / 0x55487 to 0x0137.
- Reduce weight of sling stones from 200 to 50. Change byte 0x5028B / 0x52FDB | 0x4FA17 / 0x52767 to 0x32.
- Reduce weight of arrows from 150 to 15. Change byte 0x502C7 / 0x53017 | 0x4FA53 / 0x527A3 to 0x0F.
- Reduce weight of bolts from 350 to 100. Change word 0x50302 / 0x53052 | 0x4FA8E / 0x527DE to 0x0064.
- Reduce weight of magic arrows from 125 to 10. Change byte 0x509CF / 0x5371F | 0x5015B / 0x52EAB to 0x0A.
- Added item "TAGEBUCH" / "DIARY" which is a text scroll with item index 403 (0x193) via ItemEditor.
- Changed price for the 3 Lyramion plants (255, 317, 344) to 0 via ItemEditor.


## Chest_data.amb

- Replace Shortsword in Grandpa's cellar with Dagger. Change byte 0x4B27 to 0xB6 (chest index 123).
- Replace Rope in the chest in your own room by the new diary item. Change byte 0x0660 from 0x00 to 0x01 and byte 0x0661 from 0x8A to 0x93.


## Monster_char_data.amb

- Change exp of Pond Lizard from 10 to 15. Change byte 0x21 in sub-file 001 to 0x0F.
- Change exp of Bandit from 45 to 50. Change byte 0x21 in sub-file 009 to 0x32.


## NPC_char.amb

- Added new NPC "Kasimir" (new sub-file 036)


## NPC_texts.amb

- Added new NPC texts for Kasimir (new sub-file 036)


## 2Map_data.amb

- Added new NPC "Kasimir" to map file 273 (Town House) at tile 18, 4.


## Object_texts.amb

- Added new text 004.005 for the diary item.

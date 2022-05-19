# Blazing Mountain

Labdata 36 (new).
Palette 6.

## Walls

Hex ID | Gfx Id | Description
--- | --- | --
65 | 110 | Door
66 | 111 | Wall
67 | 112 | Wall
68 | 113 | Wall with pillar
69 | 114 | Wall with grate
6A | 115 | Wall with face
6B | 121 | Stairs up
6C | 122 | Stairs down
6D | 119 | Spider web
6E | 120 | Destroyed spider web
6F | 116 | Cave wall
70 | 133 | Cave wall with wooden pillar
71 | 116 | Cave wall with rock (overlay 29 with 32x80 in center)
72 | 132 | Cave-in with space


## Object Infos

Hex ID | Gfx Id | Description
--- | --- | --
01  | 30 | Pillar with faces
02  | 16 | Flame
03  | 17 | Torch
04  | 32 | Stones on the floor
05  | 89 | Large lava
06  | 89 | Large lava (smaller version)
07  | 89 | Unused lava
08  | 125 | Fountain
09  | 118 | Cage with skeleton
0A  | 36 | Skeleton
0B  | 82 | Skulls
0C  | 58 | Crystal ball
0D  | 94 | Bat
0E  | 93 | Bat
0F  | 141 | Fire place
10  | 164 | Iron chest
11  | 31 | Teleporter (multiple frames)
12  | 38 | Imp
13  | 51 | Fire dragon
14  | 51 | Huge fire dragon


## Objects

Hex ID | Description
--- | ---
01 | Pillar with faces
02 | Large lava
03 | Large lava with smaller parts at the bottom
04 | Large lava with smaller parts at the bottom and right
05 | Fountain
06 | Cage with skeleton lower left
07 | Cage with skeleton upper right
08 | Skeleton
09 | Skulls
0A | Crystal ball
0B | 3 bats
0C | Fire place
0D | Iron chest
0E | Teleporter
0F | Stones on the floor
10 | Burning torch top wall
11 | Burning torch bottom wall
12 | Large lava with smaller parts at the right
13 | Imp
14 | Fire dragon
15 | Huge fire dragon
16 | 2x pillar left to right (left aligned)
17 | Burning torch left wall
18 | Burning torch right wall
19 | 3x pillar left to right
1A | 2x pillar left to right (right aligned)


## Monsters

ID | Name
--- | ---
65 | Dämonenbrut / Demon Spawn
66 | Lavadrache / Lava Dragon
67 | Pyrdacor (mage version)
!68 | Pyrdacor
!69 | Pyrdacor


## Monster groups

ID | Description
--- | ---
97 | 2x Demon Spawn
98 | 3x Demon Spawn
99 | 1x Lava Dragon
114 | 3x Lava Dragon
115 | 2x Lava Dragon + 2x Demon Spawn
116 | 1x Pyrdacor I + 2x Demon Spawn
!117 | 1x Pyrdacor II + 2x Demon Spawn
!118 | 1x Pyrdacor III + 2x Lava Dragon


## Items

ID | Type | Name | Image | Info
--- | --- | --- | --- | ---
421 | Key | Flame Key / Flammenschlüssel | 145 | Opens a door in the fire dungeon
422 | Key | Fire Key / Feuerschlüssel | 145 | Opens a door in the fire dungeon
423 | Key | Lava Key / Lavaschlüssel | 140 | Opens a door in the fire dungeon
424 | Key | Magma Key / Magmaschlüssel | 140 | Opens a door in the fire dungeon
425 | Magic Item | Ice Crystal / Eiskristall | 16 | Place on altar to cool the vulcano
426 | Magic Item | Fire Crystal / Feuerkristall | 188 (new) | Opens the fire temple
427 | Normal Item | Inactive Crystal / Inaktiver Kristall | 16 | Must be imbued with power to become the fire crystal
428 | 2H close-range weapon | Flamberge | 189 (new) | Strong weapon for warrior
429 | Weapon | Fire staff | 190 (new) | Strong weapon for magician
430 | Magic Item | Dragon Essence / Drachenessenz | 151 | Used to empower Kasimir

### Flamberge

- 2 hands
- 40 LP
- 15 STA
- 30 ATK
- 1 DEF
- 33 DMG
- 25/30 Fire Storm
- M-B-W 4
- Indestructible
- Warrior only
- Male only
- Price 33000
- Weight 5500

### Fire staff

- 2 hands
- 20 LP
- 60 SP
- 20 INT
- 30 U-M
- 1 DEF
- 15 DMG
- 25/30 Fire Pillar
- M-B-W 4
- Indestructible
- Mage only
- Male only
- Price 27500
- Weight 2500

## Todos

- fire staff sprite rework
- test if huge lava messes up Amiga performance
- monsters
- events
- you can slip through the double pillars (either use groups of 3 and 2 pillars alternating or make them bigger or place them to make the slit smaller but then also test on Amiga!)
- Does original show map object colors? Does remake not?


## Spinner events

0e: Spin up, reset right path
0f: Spin right, set right path
10: Spin right, reset right path
11: Spin down, reset right path
12: Spin left, reset right path
13: Spin up, keep right path state
14: Spin right, keep right path state
15: Spin down, keep right path state
16: Spin left, keep right path state
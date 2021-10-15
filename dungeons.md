# Your Cave

Karl the architect creates this cave for you when you pay him 15000 gold.
This is only possible after you visited Dor Kiredon on the forest moon.
The cave is located to the east of your house at the north end of the garden.

The cave has 2 levels. You enter at the top level. There are many holes you
can reach which lead to the lower level. You will need ropes and/or levitation
to proceed. But from every lower room you can access one of two corridors back
to a ladder which leads to the upper level and eventually back to the cave entrance.

The corridor is accessed by moving a wall by pulling a lever. The rooms above the
two ladders also need a lever to connect to the cave entrance room. There are also
some fake walls. You can also use the shovel to dig holes.

At the end you can find a chest. It contains Karl's Ring which grants 25 Swim, 1 Damage,
25 Luck and Magic Defense Level 3.

```
Your Cave - Upper Level
+----------------+
|O   |           |
+--+ | --+----+ ++
|  $ |  O|O      |
| ++-+--++----++ |
| |     $     ++ |
|   | | |! O|    |
|#+-+-+ +---+--+-+
|!|O|O  |O    C|O|
|-+$+---+-++-+-+ |
|         ++ $ # |
|#--+-+-+    |C| |
|  !|O| +-----++#|
+---+ |       |! |
|  L| +-+ +-+ +--+
|!  $ |C   O|   O|
+---+X+-----+----+

O: Hole down
L: Ladder down
!: Lever
$: Moveable wall (removed by lever)
#: Fake wall
C: Chest (1x Rope)
L: Chest (1x Levitation spell, 1 Healing Potion II)
X: Spawn)

Your Cave - Lower Level
+----------------+
|O               |
| +----+-+-+#+-+ |
| |! B |O$o| |!| |
| $    +-+     | |
|$+-+ -+ +--+--+ |
|   |    S O|T # |
|$+$+------+--+--+
| |O O   O # !| O|
|$+--------+--+#-+
| $              |
|$+---+-+---+ |  |
| $  O|!|   | +- | 
| +-+ | | | +#+  |
| |L| +#+ | | | -+
|   |     |O|!| O|
+---+-----+-+-+--+

O: Hole up
L: Ladder up
!: Lever
$: Moveable wall (removed by lever)
#: Fake wall
S: Spider web (needs torch)
T: Chest (3x Torch)
B: Boss room (text event)
o: Ceiling hole is only added by an event
```

Labdata 2
---------
Walls:
- 1: Plain wall
- 2: Wall with rock 1
- 3: Wall with rock 2
- 4: Wall with rock 3
- 5: Wall with rock 4
- 6: Wall with all 4 rocks
- 7: Fake wall (blocks sight)
- 8: Fake wall (does not block sight)
- 9: Spider web (player can pass)
- 10: Broken spider web (player and monsters can pass)
- 11: Spider web (player can not pass)
- 14: Open door
- Rest not relevant
Objects infos:
- 8: Small stone
- 9: Hanging brown stuff (small)
- 10: Hanging brown stuff (large)
- 11: Barrel
- 12: Stone pile
- 13: Lizard
- 14: Spider (small)
- 18: Ceiling stone
- 22: Ladder down
- 23: Hole down
- 24: Ladder up
- 25: Hole up
- 26: Lever (left)
- 27: Lever (right)
- 29: Pile of trash
- 30: Wooden chest
- 31: Bigger rock
- 32: Medium rock
- 33: Spider (large)
- 34: Spider (ceiling)
- 35: Spider (tiny)
- 36: Earth pillar
- We add 37: Bigger hole down
- And 38: Bigger hole up
Objects:
- 9: Stones
- 10: Hanging brown stuff (small)
- 11: Barrel
- 12: Pile of stones
- 13: Lizard
- 14: Spider (small)
- 19: Bats
- 20: Ladder down
- 21: Ladder up
- 22: Lever (left)
- 23: Lever (right)
- 24: Pile of trash
- 25: Wooden chest
- 26: Spider (large)
- 27: Spider (ceiling)
- 28: Spider (tiny)
- 29: Earth pillar
- We add 30: Hole down
- And 31: Hole up

# Hidden Sea Cave

There is a new NPC in the Newlake Inn. He talks about his journey to the big vortex.
He said that he travelled with Captain Torle so we should talk to him.

Torle can be asked about "Big Vortex". He won't be chatty about it when not talked
to the NPC in Newlake before. But then he will talk more about it. He say he can harden
the ship to make a travel near the big vortex possible. He needs some Xenobil planks and
gold. You can then ask the woodkeeper for the Xenobil planks. He will sell it to you for
10000 Gold. You need another 10000 Gold for Torle. After that Torle says that the ship
is now ready.

If you then travel to the vortex by boat, you will be teleported to a near location
randomly. But with a small chance you enter the vortex. If you are teleported there
should be a message like "Almost done it. Let's try again.". When you once entered the
vortex, you will always enter immediately.

(TODO: If you can enter the vortex without boat, e.g. by leaving the eagle, there must
be some global var setting nearby in ocean water to avoid entering the vortex without
boat).

In the cave there is a 2D map with beach and water. You have to swim a lot so having
the skill high is good. It is a 2D swim maze. You eventually reach a beach with some
houses in the upper right area. It has some palisaded like Spannenberg. You may enter
the village. It is a very small 3D map with mostly closed doors. A ghost town. Ship's End.
Most houses are abandoned (text messages at the door). You can only enter one house.
You will only find a diary which hints that some villagers moved to a castle in the
south west of the cave. You also can find a shovel and a ring of Sobek.

At the south of the village you find another passage for swimming. On the way you stumble
onto some undeads, spiders and lizards. You finally reach a castle with some newer houses
around. You can find a raft dealer there. Inside the town there are some buildings:

- Vielauge's Inn (2D)
- Vielauge's Castle (3D)
- Raft dealer (Place)
- Merchant (Place)
- Blacksmith (Place)
- Swim Trainer (Place)

```
Size: 35x20 (with map border)
+------------------------------+
|                              |
| +--------+         +---X---+ |
| |        |         |  Merc | |
| | Castle +---+     |  Blac | |
| |            |     +---X---+ |
| |            X               |
| |            |               |
| |        +---+     +-------+ |
| | +XX+ +-+         |       | |
| +-+  +-+           X  Inn  | |
|                    |       | |
|                    +-------+ |
| +---+      +---+             |
| | S |      | R |    +-+ +-+  |
| +-X-+      +-X-+    +X+ +X+  |
|                              |
+--------XX--------------------+
```

The raft dealer places a raft at the docks outside the town. He also opens a passage in
a wall so you can directly travel upwards to the cave exit to the world map.

The castle is locked first. In the Inn you can learn that the castle once was occupied
by a cruel monster called Vielauge. Nowadays it is a tourist attraction and a minor part
is the head council's office. But since there were no tourists for a long time, it was
closed and only the office remains open. He also reveals that he himself is the council
and gives you his keys to water the plants for him. He wants to drink beer and stay at the
inn. He is scared of some strange noises in his office.

You can enter the office through a side door. At a specific wall a text popup is shown
that there are strange noises and that the wall looks strange. You can touch it and it
just disappears. You then enter the castle. It has only two levels. The upper level is
crushed and in ruins (it looks like the ancient ruins) so you see the sky. There are
many undeads in the castle. And many walls that can be removed by touching them. You
finally reach the upper level. There awaits a strong undead banshee. It drops a powerful
amulet and again a Ring of Sobek.

Someone in the inn also says that there are many treasures buried in the sands of the cave.
You can use the shovel at several places and access chests. Mostly junk or gold but some
rare items as well.

#### Lower Level
<img src="file:///C:/Users/Alpapa/Documents/Projects/Ambermoon-Advanced/Vielauge's Castle Level 0.png"
     alt="Vielauge's Castle Level 0"
     style="image-rendering: pixelated; width:320px" />
	 
#### Upper Level
<img src="file:///C:/Users/Alpapa/Documents/Projects/Ambermoon-Advanced/Vielauge's Castle Level 1.png"
     alt="Vielauge's Castle Level 1"
     style="image-rendering: pixelated; width:320px" />
	 
#### Legend:
- Black: Walls
- Red: Monsters
- Brighter red: Boss
- Yellow: Treasure
- Purple: Fake wall
- Pink: Touch disappear wall
- Azure: Ladder
- Brown: Door
- Light green: Lever
- Dark green: Movable wall

The lever moves the wall away. The end boss has a key to unlock the main castle door. As mentioned the
upper level has a sky and broken walls. The monsters all are groups of undeads. Some of them are marked
as bosses and/or have very high anti-magic so they won't be affected by holy spells. All doors beside the
main entrance and boss door are unlocked so you can just pass it.

The three chests behind the fake walls contain:
- Holy horn
- Much gold
- Horned helmet
- Alcohol
- Healing potions
- Spell potions
- Rations
- Scimitar
- Silver cutlery

The other chest in the lower level contains a cursed dagger and simple clothings.

The chests in the upper level just contain:
- Alcohol
- A little bit gold
- Some healing potions

The chest in the upper level's central room instead contains the key to the boss room.

The end boss drops the unique item set for the adventurer. The equipment is not breakable.
- Adventurer's Sword
  Atk: 15, Def: 0, Hands: 1, Spell: Windhowler (**)
  Str +5, Atk +15, Magic Attack Level max
- Adventurer's Bow
  Atk: 15, Def: 0, Hands: 1, Spell: Magic Projectile (**)
  Str +5, Atk +15, Magic Attack Level max
- Adventurer's Suit
  Atk: 0, Def: 12, Spell: None
  Sta +5, Search +15, Magic Defense Level 3
- Adventurer's Shoes
  Atk: 0, Def: 5, Spell: Haste (25)
  Spd + 5, Swi +99
  
The boss casts Thunderstorm and Whirlwind and attacks with the adventurer's bow and magic arrows.
He has 51 of them and he has 3 attacks per round so he can attack 17 rounds at max. Then he switches
to the sword.

He has the following attributes and battle skills:

- STR: 75
- INT: 80
- DEX: 50
- STA: 80
- LUK: 20
- SPD: 95
- A-M: 65
- CHA: 1

- ATK: 95
- PAR: 40
- CRI: 0
- U-M: 95

His base damage is 50 and his variable damage 35.
His magic attack level is max so you can't avoid the damage.


### NPCs

- Marel: He is an older man who is the council of Vielauge's Town. He gives you his keys and informs
         you about the castle.
- The rest are only text popup NPCs. Some are inside the inn and some move through the town.
- Town folks:
  - A woman tells you about Ship's end and that she was born there. Sometimes she travels to the ghost
   village with a raft. She informs you about the raft dealer in town.
  - A man tells you that he just recently has landed here. His ship got into a big storm and he was
    the only survivor. Who would have known which world lies here below the vortex.
  - An older man tells you a bit about Vielauge and the castle. He remember the lore about the group
    of heros who killed Vielauge. Then they moved here and left the village of Ship's End.
- Inn folks:
  - A mighty elf woman who stranded a couple of years here. She is an elfish princess who should be
    married to some rich man in Newlake but on their honeymoon the ship crushed on a rock near the
	vortex and she came here. She doesn't know what happened to her husband but she isn't sad about it.
  - An old dwarf is there as well. He is very sad as he should be part of the mission to the green
    jewel but Kire needed some materials and on the way his ship sunk and he landed here. He dreams
	of the jewel every day. He not even can see it from here. :(
  - A woman drinks lot of alcohol and is very drunk. She got depressed down here. No new people for
    a long time. No good men.
  - The innkeeper's small daughter is playing in her room. There are not many kids at her age so it
    is really boring for her. Sometimes at night she plays near the castle and last night she heard
	voices from inside. She ran home scared then. And now she prefers to stay inside.

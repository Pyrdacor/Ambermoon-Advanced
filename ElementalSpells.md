# Elements

Every monster and every spell in the game has a specific element. Monsters are immune to spells of their element.

For damage dealing spells there are elemental factors which can increase or decrease the damage of those spells against certain monster elements.

There are 8 elements in total:
- Mental
- Spirit
- Physical
- Undead
- Earth
- Wind
- Fire
- Water

However for damage dealing spells only 5 of those elements are used:
- Spirit
- Earth
- Wind
- Fire
- Water

Note that the spells SP Stealer and LP Stealer are not included here as they are handled differently. Their steal amount is not affected by the elemental factor in any way.

The following table shows the damage in percent. On the left side there are the spell elements and on the top side the monster elements.

Spell \\ Monster | Mental | Spirit | Physical | Undead | Earth | Wind | Fire |Water
--- | --- | --- | --- | --- | --- | --- | --- | ---
Spirit | 100 | 0 | 150 | 150 | 100 | 100 | 100 | 100
Earth | 100 | 100 | 100 | 75 | 0 | 50 | 100 | 150
Wind | 100 | 100 | 100 | 75 | 150 | 0 | 50 | 100
Fire | 100 | 75 | 100 | 125 | 100 | 150 | 0 | 50
Water | 100 | 100 | 100 | 75 | 50 | 100 | 150 | 0

So the 4 base elements (earth, wind, fire and water) build a circle of effects:
- Earth deals 150% damage against water but only 50% against wind
- Wind deals 150% damage against earth but only 50% against fire
- Fire deals 150% damage against wind but only 50% against water
- Water deals 150% damage against fire but only 50% against earth

All of them are a bit weaker against undeads (75% damage) with the exception of fire which deals even more damage to them (125%). But in exchange fire is weaker against spirit monsters (75%).

Spirit spells are strong against physical and undead monsters (150%).


# Elemental Damage Spells

## Spirit Spells

Spell | Class | Description
--- | --- | ---
Ghost Weapon | Alchemist | Shoots out a ghostly fire which deals the same damage as your total attack damage
Magical Projectile | Magician | Deals half your level as damage to a single enemy (when cast by monsters it is the the full level)
Magical Arrows | Magician | Deals half your level as damage to a row of enemies (when cast by monsters it is the the full level)

## Earth Spells

Spell | Class | Description
--- | --- | ---
Mudsling | Magician | Deals 5 to 10 damage to a single enemy
Rockfall | Magician | Deals 15 to 25 damage to a single enemy
Earthslide | Magician | Deals 10 to 22 damage to a row of enemies
Earthquake | Magician | Deals 8 to 20 damage to all enemies

## Wind Spells

Spell | Class | Description
--- | --- | ---
Winddevil | Magician | Deals 20 to 35 damage to a single enemy
Windhowler | Magician | Deals 30 to 50 damage to a single enemy
Thunderbolt | Magician | Deals 25 to 45 damage to a row of enemies
Whirlwind | Magician | Deals 20 to 40 damage to all enemies

## Fire Spells

Spell | Class | Description
--- | --- | ---
Firebeam | Magician | Deals 40 to 60 damage to a single enemy
Fireball | Magician | Deals 70 to 120 damage to a single enemy
Firestorm | Magician | Deals 65 to 110 damage to a row of enemies
Firepillar | Magician | Deals 60 to 100 damage to all enemies

## Water Spells

Spell | Class | Description
--- | --- | ---
Waterfall | Magician | Deals 55 to 75 damage to a single enemy
Iceball | Magician | Deals 150 to 200 damage to a single enemy
Icestorm | Magician | Deals 125 to 175 damage to a row of enemies
Iceshower | Magician | Deals 110 to 170 damage to all enemies
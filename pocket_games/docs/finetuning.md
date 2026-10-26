# Fine-Tuning Guide

This document lists the parameters that control gameplay behavior (speed, gravity, jump strength, timers, spawn rates, difficulty scaling). Values are taken from the source files under `../games`. Change a value in its source file, then play the game to check the effect.

> Status: this is the first version. It covers the games and modules listed below. The remaining games are still to be documented (see the last section).

---

## Core Engine (`../core`)

| Parameter | File | Value | Effect |
| :--- | :--- | :--- | :--- |
| `VIRTUAL_WIDTH` / `VIRTUAL_HEIGHT` | `core/engine.py` | 320 x 240 | Native resolution. All game coordinates are in this space. |
| `gravity` (physics helper) | `core/physics.py` | used per game | Vertical acceleration applied by `apply_gravity`. |

---

## Aether Defender (`games/aether_defender.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Player horizontal speed | 190 px/s (`190 * 0.016` per frame) | Movement speed with left/right keys. |
| Player clamp range | x in [25, 295] | Left and right limits. |
| Starting lives | 3 | Lives before game over. |
| Hit invulnerability | 1.5 s | Time the player is safe after losing a life. |
| Spawn interval | `max(0.35, 0.9 - elapsed * 0.008)` s | Enemies spawn faster over time, down to 0.35 s. |
| Enemy speed | `uniform(70, 105) + min(45, elapsed * 0.8)` px/s | Base fall speed plus a boost that caps at +45 px/s. |
| Score per matching enemy | 40 | Points for catching an enemy of the active color. |
| Color switch particles | 6 particles, speed 60 px/s, life 0.35 s | Visual feedback only. |

Tuning tips: lowering the spawn floor (0.35) makes the late game harder. Raising the speed boost cap (45) changes the late-game pace.

---

## Pixel Platformer (`games/pixel_platformer.py`)

### Physics and Player

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| `gravity` | 950 px/s² | Downward acceleration. Higher values make jumps shorter and falls faster. |
| `jump_speed` | -420 px/s | Initial jump velocity. Jump height is about v²/(2g), roughly 93 px. |
| `move_speed` | 160 px/s | Horizontal walking speed. |
| Stomp bounce | `pvy = -260` px/s | Upward bounce after stomping an enemy. |
| Fireball speed | 320 px/s | Projectile speed of the fire flower. |
| `STAR_DURATION` | 8.0 s | Duration of star invulnerability. |
| `SPAWN_INVULNERABILITY` | 1.5 s | Safe time after a respawn or after the fire flower absorbs a hit. |
| Starting lives | 3 | |
| `PLAYER_W` / `PLAYER_H` | 16 / 20 px | Collision box size. |

### Level Layout

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| `MAX_LEVELS` | 20 | Number of levels. |
| `GROUND_Y` | 205 | Y position of the ground surface. |
| `GOAL_X` | 300 | X position that completes the level. |
| `FIRST_TIER_Y` / `TIER_HEIGHTS` | 150 / (150, 125, 100, 75) | Heights of floating platform tiers. |
| `MAX_RISE` | 70 px | Maximum vertical gap between platform tiers, so each platform stays reachable with a jump. |
| `LEVEL_SEED_BASE` | 7919 | Level `n` uses seed `7919 + n`, so every level is reproducible. |

### Difficulty Scaling per Level

| Element | Formula | Effect |
| :--- | :--- | :--- |
| Pits | `min(3, (level - 1) // 4)` pits, width `min(56, 24 + level * 2)` | More and wider gaps in the ground. |
| Floating platforms | `min(7, 3 + level // 4)` | More platforms at higher levels. |
| Walker enemies | `min(5, 1 + level // 4)`, speed `40 + level * 3` px/s | More and faster patrol enemies. |
| Flyer enemies | from level 6, `min(3, (level - 5) // 5 + 1)`, speed `50 + level * 2.5` px/s | Sine-wave flyers with ±18 px amplitude. |
| Spikes | from level 11, `min(3, (level - 10) // 4 + 1)` | Ground hazards. |
| Power-up order | `life, gun, star, life` (repeating) | Power-up type by level. |

### Power-ups

| Power-up | Effect |
| :--- | :--- |
| Life | +1 life. |
| Gun (fire flower) | Enables shooting with Z. Absorbs one hit. |
| Star | Invulnerability for `STAR_DURATION`. Enemies are destroyed on contact. |

Scoring: stomping or star-killing an enemy gives 100 points. A fireball kill gives 150 points.

---

## Cyber Grid Chomp (`games/cyber_grid_chomp.py`)

### Player

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| `speed` | 80 px/s | Pac-Man movement speed along the lanes. |
| Starting lives | 3 | |
| `SPAWN_INVULNERABILITY` | 2.0 s | Safe time at game start and after a respawn. |
| `pill_duration` | `max(4.0, 7.0 - 0.75 * idx)` s | Overclock duration. It shrinks from 7 s to a floor of 4 s across sectors. |

### Phantoms

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| `PHANTOM_COUNTS` | (3, 3, 4, 4, 5) | Phantoms per sector. |
| `phantom_speed` | `62 + 8 * idx` px/s | Normal chase speed. Rises with each sector. |
| `chase_chance` | `min(1.0, 0.6 + 0.1 * idx)` | Probability that a phantom hunts the player at a junction. The rest move randomly. |
| Flee speed (overclock) | 30 px/s | Phantoms slow down while fleeing during overclock. |
| `PHANTOM_SPAWNS` | (7,1), (1,4), (13,4), (7,5), (11,7) | Tile spawn points. |

### Level Structure

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| `MAX_LEVELS` | 5 | Number of sectors. |
| `LEVEL_SEED_BASE` | 4242 | Sector `n` uses seed `4242 + n`, so the layout and random choices are reproducible. |
| `TILE_SIZE` | 20 px | Grid cell size. |
| `POWER_PILL_TILES` | 4 fixed tiles | Overclock pill positions. |

Balance note: phantom speeds, chase chance, and pill duration are first-pass estimates. They have not been playtested.

---

## Gravity Sling (`games/gravity_sling.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| `MAX_LEVELS` | 3 | Number of levels. |
| `LEVEL_TIME` | 40.0 s | Time limit per level. |
| `SPAWN_POS` | (50, 120) | Probe start position. |
| `LEVEL_SEED_BASE` | 4099 | Level layouts are seeded. |
| `BACKGROUND_SEED` | 2024 | Background stars and nebula are seeded. |
| `EFFECT_SEED` | 77 | Particle and effect randomness is seeded. |
| `PLANET_CONFIGS` | per planet: position, radius, gravity radius, strength | Planet size and pull. Strength values are estimates and have not been playtested. |

Crystal spawns are random but seeded, so each run is identical.

---

## Neon Dash (`games/neon_dash.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| `gravity` | 880 px/s² | Downward acceleration. |
| `jump_speed` | -390 px/s | Jump velocity. |
| `level_duration` | `uniform(30, 40)` s | Length of each level. |

---

## Cyber Flipper (`games/cyber_flipper.py`)

All tuning values for this game live in `data/tuning/cyber_flipper.json`, so physics and tables can be changed without editing code. The `physics` and `playfield` objects hold the constants, `frame_walls` holds the outer rails, and `levels` holds the five tables. A `ring_bumpers` object expands into a circle of bumpers. Each table has its own gravity, wall restitution, bumper ring, wall layout, and optionally raised decks (`ramps`, `upper_walls`, `upper_bumpers`). The ball is on one of two height layers. A `RampZone` moves the ball to the raised layer while its center is inside the zone. Outside all zones the ball is on the low layer. Only the bumpers and walls of the current layer collide. Table order is fixed, and reaching the table score target advances to the next table. Clearing table 5 wins.

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| `BALLS_PER_GAME` | 3 | Balls per table. Balls reset when a table is cleared. |
| `BALL_RADIUS` | 5 px | Ball collision size. |
| `gravity` (per table) | 380 to 520 px/s² | Ball fall speed. Lower values float longer. Table 4 is lowest, table 5 is highest. |
| `wall_restitution` (per table) | 0.55 to 0.65 | Wall bounciness. Lower values make the start calmer. |
| `RampZone` | per table (x, y, w, h, layer) | Zones that switch the ball between the low and high layer. |
| `score_target` (per table) | 1500, 2500, 3500, 4500, 6000 | Table score needed to advance. |
| `FLIPPER_LENGTH` | 48 px | Flipper arm length. |
| `FLIPPER_SPEED` | 18 rad/s | Swing speed from rest to active. |
| `FLIPPER_ACTIVE_ANGLE` / `FLIPPER_REST_ANGLE` | -0.45 / 0.50 rad | Swing limits. |
| `FLIPPER_KICK` | 260 px/s | Extra speed added when a rising flipper hits the ball. |
| Flipper hit restitution | 0.6 | Bounce of the ball off a flipper, before the kick. |
| `SUBSTEPS` | 4 | Physics substeps per frame. Higher values reduce tunnelling. |
| `MAX_BALL_SPEED` | 700 px/s | Speed cap. |
| `MAX_CHARGE` | 30 | Maximum plunger charge. |
| `LAUNCH_BASE_SPEED` / `LAUNCH_SPEED_PER_CHARGE` | 260 px/s / 10 px/s per charge | Launch speed is `260 + charge * 10` px/s. Lower values make the first shot gentler. |
| `BUMPER_RESTITUTION` | 0.9 | Bounce of the ball off a bumper. |
| `BUMPER_BOOST` | ×1.08 per hit | Each bumper hit speeds the ball up slightly. |
| Bumper points | 60 to 800 per hit | Per-table value (see `LEVELS`). Circuit Board uses 60 per bumper, Core Meltdown centre uses 800. |
| Bumper radius | 7 to 16 px | Visual and collision size per bumper. |

Tuning tips: lowering a table's `score_target` shortens the level. Raising `wall_restitution` or the bumper boost makes the ball harder to control. The plunger launch formula sets how far the ball travels up the lane. Raised decks are placed so the ball can reach them with a ramp entry, and they should stay clear of the flippers.

---

## Pixel Drop (`games/pixel_drop.py`)

The fall speed formula from the developer guide is `t_drop = max(0.1, 0.6 - lines_cleared * 0.015)` s. Verify this against the source before relying on it.

---

## Bit Blaster (`games/bit_blaster.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Starting lives | 3 | Lives before game over. |
| `max_levels` | 20 | Number of levels. |
| Paddle width | `max(45, 100 - (level - 1) * 3)` px | Paddle shrinks each level, down to 45 px. |
| Keyboard paddle step | 7 px per frame | Paddle movement speed. |
| Ball start speed | `100 + (level - 1) * 7` px/s | Base ball speed per level. |
| Ball speed modifier | `min(1.6, 1.0 + elapsed_time * 0.004)` | Ball speeds up over time, capped at 1.6x. |
| Block rows | `min(6, 4 + (level - 1) // 5)` | More rows at higher levels. Columns fixed at 7. |
| Block HP | 2 for level 10+ in row 0 on even columns, else 1 | Multi-hit bricks. |
| Score per brick | `25 * level` | Points for destroying a brick. |
| Ball loss | ball top below y = 240 | Costs one life. |

Tuning tips: paddle width and the ball speed ramp together make later levels harder. Adjust the 3 px and 7 px/s steps to change the curve.

---

## Bug Hunter (`games/bug_hunter.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Start time | 30 s | Starting timer. |
| `max_time` | 60 s | Timer cap. |
| Timer drain | `dt * (1.0 + elapsed_time * 0.015)` | Timer runs down faster over time. |
| Spawn interval | starts at 1.0 s, -0.04 s every 6 s, floor 0.25 s | Spawn rate ramps up. |
| Max bugs on screen | `min(18, 8 + score // 100)` | Higher score allows more bugs at once. |
| Bug type weights | standard 40, fast 30, armored 20, glitch 10 | Spawn chance per type. |
| Bug speed | standard 22, fast 52, armored 14, glitch 68 px/s | Speed per axis (`vx` and `vy` each use this value). |
| Armored HP | 2 | Needs two clicks. |
| Points per kill | glitch 75, armored 50, fast 30, standard 20 | Score per type. |
| Time gain per kill | glitch 2.5 s, armored 2.0 s, fast 1.2 s, standard 1.0 s | Timer extension per kill, capped at `max_time`. |
| Glitch direction change | 6% chance per frame, velocity ±20 px/s | Erratic movement. |

Tuning tips: the drain multiplier and spawn floor set the late-game pressure. Time gains decide how forgiving the run is.

---

## Byte Hopper (`games/byte_hopper.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Gravity | 540 px/s² | Downward acceleration. |
| Jump velocity | -310 px/s | Bounce velocity on landing. |
| Horizontal speed | 175 px/s | Left/right movement. |
| Platform width | 58 to 80 px | Random width per platform. |
| Vertical gap | 45 to 58 px | Spacing between platform rows. |
| Motion weights | static 65, horizontal 25, vertical 10 | Platform type chance. |
| Moving platform speed | 4 to 10 rad/s (phase speed) | Oscillation speed. |
| Moving platform range | horizontal 20 to 50 px, vertical 10 to 30 px | Oscillation amplitude. |
| Overlap check | 45 px height band, 15 px horizontal margin | Prevents overlapping moving platforms. |
| Coin chance | 25% per platform | Coin spawn. |
| Crystal chance | 12% of non-coin platforms | Crystal spawn. |
| Coin / crystal points | 50 / 150 | Score per pickup. |
| Camera pull | when the player is less than 100 px below the camera top | Pushes the camera up, adds height score, and spawns new platforms. |
| Game over | player falls more than 250 px below the camera | Ends the run. |

Tuning tips: gravity and jump velocity set the reachable platform gap. Keep the vertical gap below the jump height (about v²/2g, roughly 110 px).

---

## Chrono Shift (`games/chrono_shift.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Starting lives | 3 | |
| Acceleration | `360 + level * 40` per frame (dt 0.016) | Player thrust. |
| Damping | `0.93 - level * 0.01` | Velocity decay per frame. Higher levels slide more. |
| Arena bounds | x in [20, 300], y in [40, 220] | Leaving the bounds costs a life. |
| Respawn invulnerability | 1.5 s | Safe time after losing a life. |
| Spawn protection | 1.0 s | Safe time at game start. |
| Anomaly count | `min(6, level + 2)` | Hazard count per zone. |
| Anomaly speed | per axis `uniform(-45, 45) * (1 + 0.35 * level)` px/s | Hazard speed grows with zone. |
| Trail length | `max(30, 50 - level * 5)` nodes | Shorter trail at higher zones. |
| Trail self-collision | after the first 8 trail nodes | Crossing your own trail costs a life. |
| Fragments per zone | 4 | Zone advance after 4 pickups (zones 1 to 3). |
| Fragment points | `50 + level * 25` | Score per pickup. |

Tuning tips: the damping and acceleration pair defines how slippery the controls feel. Trail length controls how much room the player has to move.

---

## Circuit Breaker (`games/circuit_breaker.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Grid width | `min(7, 5 + level // 5)` | Columns per level. |
| Grid height | `min(5, 4 + level // 15)` | Rows per level. |
| Number of states | `min(5, 3 + level // 10)` | Chip states to cycle through. |
| Start timer | 18 s | Timer cap is also 18 s. |
| Timer drain | `dt * (1.0 + (level - 1) * 0.12)` | Drain grows with level. |
| Bonus time | `max(3.0, 6.0 - level * 0.4)` s | Added after each solved circuit, capped at 18 s. |
| Level up | every 3 solved circuits | Advances `level`. |
| Solve points | `250 + level * 50` | Score per solved circuit. |

Tuning tips: the timer drain and bonus time define the pressure. The number of states controls how many clicks a chip needs.

---

## Crypto Decrypt (`games/crypto_decrypt.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| `code_length` | 4 | Digits in the secret code. |
| `max_attempts` | 8 | Guesses before the code is revealed. |
| Input lockout | 3.0 s at the start of each round | Blocks submitting guesses only. Digit editing still works. |
| Solve score | `max(100, int(10000 / time_spent)) + attempts_left * 200` | Faster solves and remaining attempts score more. `time_spent` is at least 0.1 s. |

Tuning tips: `max_attempts` and the lockout set the difficulty. The solve formula rewards speed and remaining attempts.

---

## Cyber Snake (`games/cyber_snake.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Grid cell size | 10 px | Each tile is 10 px. |
| Board size | 32 columns x 24 rows | Playfield. Rows 0 to 2 are the HUD. |
| Start move interval | 0.11 s | Time between snake moves. |
| Speed-up per food | -0.002 s, floor 0.05 s | Snake accelerates each time it eats. |
| Food points | 15 | Score per food. |

Tuning tips: the per-food speed-up and the floor define the late-game speed. The floor of 0.05 s is the maximum speed.

---

## Glitch Runner (`games/glitch_runner.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Grid width | `min(8, 5 + level)` | Columns per sector. |
| Grid height | `min(7, 5 + level // 2)` | Rows per sector. |
| Time limit | `max(10, 18 - level * 2)` s (15 s in the constructor before the first setup) | Time per sector. |
| Initial glitches | `level + 2` | Glitched tiles at sector start. |
| Max glitched tiles | `level + 3` | When a new system glitch exceeds this count, one arbitrary existing glitch is removed. |
| System glitch interval | `max(1.5, 4.0 - level * 0.8)` s | How often a new glitch appears. |
| Sector clear score | `150 * level + int(time_remaining * 10)` | Points for reaching the exit. |
| Sector advance | after 3 exits, up to level 3 | Level progression. |

Tuning tips: the glitch interval and tile cap together set how much room the player has to route.

---

## Kernel Panic (`games/kernel_panic.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Spawn interval | `max(0.4, 1.1 - (score / 350) * 0.20)` s | Leaks spawn faster as score rises. |
| Base fall speed | uniform 70 to 90 px/s | Random speed per leak. |
| Speed multiplier | `1.2 + score / 600` | Leaks fall faster as score rises. |
| Fatal chance | 15% when score > 250 | Spawn chance for fatal errors. |
| Fatal clicks | 2 | Clicks needed to destroy a fatal error. |
| Click reward | 25 (normal), 40 (fatal) | Score per destroyed leak. |
| RAM relief | -6 per normal, -10 per fatal kill | Memory freed on kill. |
| Escape penalty | +12 RAM (normal), +18 RAM (fatal) | Memory added when a leak escapes the bottom. |
| Game over | RAM at 100% | Ends the run. |

Tuning tips: the spawn and speed formulas are driven by score, so score tuning changes difficulty directly.

---

## Matrix Invaders (`games/matrix_invaders.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Player HP | 5 (max 5) | Hits before game over. |
| Player speed | 220 px/s | Ship movement. |
| Player bullet speed | 420 px/s | Shot speed. |
| Weapon levels | 1 to 4 | 1 shot, 2 shots, 3 shots, then beam plus side shots. |
| Shield duration | 8 s | Shield pickup lasts 8 s. It is consumed by the first enemy hit. |
| Formation columns | `min(7, 4 + wave // 3)` | Invaders per row. |
| Formation rows | `min(4, 2 + wave // 3)` | Number of rows. |
| Formation speed | `20 + wave * 2` px/s | Horizontal march speed. |
| Enemy HP | `base + wave // 4`, max 4 | Base HP: cyber lord 3, elite 2, tank 2, others 1. |
| Enemy fire cooldown | uniform 1.8 to 4.5 s, minus `min(1.2, wave * 0.1)` | Shot frequency. |
| Enemy bullet speed | `130 + wave * 10` px/s | Shot speed. |
| Kamikaze dive | from wave 8, chance `0.001 * wave` per invader per frame, speed 140 px/s | Divers fall straight at the player. |
| Bunkers | from wave 2, 3 HP each | Cover against enemy fire. |
| Drop chance | 35% per kill | Chance that a weapon, shield or life pickup drops. |
| Life drop limit | once per wave | A life pickup can drop only once per wave. |
| Invader points | cyber lord 100, elite 60, tank 40, others 25 | Score per kill. |
| Wave clear score | `400 * wave` | Bonus for clearing a wave. |
| Rest between waves | 2 s | Pause before the next wave. |

Note: the code comment near the life pickup says "max 3", but `max_player_hp` is 5. Check which value you want.

---

## Orbital Defense (`games/orbital_defense.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Reactor HP | 3 (max 5) | Core health. |
| Level | `1 + score // 250` | Derived from score. |
| Rotation speed | `5.0 + (level - 1) * 0.8` deg per frame | Shield turn speed. |
| Spawn interval | `max(0.3, 1.6 - time * 0.018 - level * 0.08)` s | Meteor rate. |
| Smart meteor chance | `0.15 * level` (level 2+) | Meteors that home in on the core. |
| Heavy meteor chance | 20% (level 2+), damage 2 | Larger meteors that deal double damage. |
| Meteor speed | uniform 65 to 85, plus `level * 5` px/s | Fall speed. |
| Goodie spawn | every 12 s, speed 50 px/s | Heals one HP. |
| Shield orbit radius | 42 px | Distance of the shield from the core. |
| Shield size | `max(5, 9 - (level - 1) * 1.5)` px | Shields shrink per level. |
| Reactor radius | `12 + (level - 1) * 3` px | Core grows per level. |
| Dual shield | from level 3 | Second shield opposite the first. |
| Points | heavy 40, smart 30, normal 20, goodie 50 | Score per event. |

Tuning tips: shield size and rotation speed decide how hard it is to block. The spawn interval controls the meteor pressure over time.

---

## Pulse Racer (`games/pulse_racer.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Starting lives | 3 | |
| Base speed | `180 + elapsed_time * 3.0` px/s | Road speed grows over time. |
| Respawn acceleration | `base * dt * 1.5` | Car speeds back up after a crash. |
| Distance score | 1 point per px | Score from distance driven. |
| Lane centers | 100, 160, 220 px | Three lanes. |
| Player steer clamp | x in [85, 235] | Steering limits. |
| Steer speed | 190 px/s | Lateral movement. |
| Pylon spawn | every 3 s | Divider obstacles. |
| Roadside drain spawn | every 2.4 s | Paired drains at the edges. |
| Traffic spawn interval | `max(0.45, 2.2 - elapsed_time * 0.03)` s | Traffic density grows over time. |
| Cruiser net offset | 70 px/s slower than base | Slow traffic. |
| Blocker net offset | 10 px/s slower | Slightly slower. |
| Speedy net offset | 25 px/s slower | Medium traffic. |
| Oncoming speed | `110 + elapsed_time * 2.0` px/s | Head-on traffic. |
| Blink warning | 1.0 s | Time before an AI lane change. |
| Lane change speed | 130 px/s | Sideways movement of traffic. |
| Crash clear zone | ±70 px | Traffic near the player is removed on respawn. |

Tuning tips: the net offsets and spawn interval set the traffic difficulty. The blink time sets how readable AI moves are.

---

## Quantum Maze (`games/quantum_maze.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Starting grid | 5 x 5 | Maze size. |
| Grid growth | +1 column and row every 2nd level, max 10 | Larger mazes at higher levels. |
| Level up | every 10 core shards | Advances `level`. |
| Item weights | core 40, fragment 25, timed 20, trap 15 | Spawn chance per item. |
| Timed shard lifetime | 10 s | Shard disappears after 10 s. |
| Player speed | 95 px/s | Movement speed. |
| Points | core 100, fragment 50, timed 200, trap -50 | Score per item. |
| Items on the board | 5 | Active item count. |

Tuning tips: the timed shard lifetime and grid growth set the difficulty. Trap points can make scores go negative.

---

## Retro Pong 2077 (`games/retro_pong.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Start ball velocity | (95, 65) px/s | Initial ball speed. |
| Speed-up interval | every 10 paddle hits | Ball speed increases in steps. |
| Speed-up factor | ×1.15 on both axes | Multiplier applied at each interval. |
| Paddle keyboard speed | 4.5 px per frame | Paddle movement. |
| Paddle clamp | y in [40, 210] | Paddle limits. |
| Hit points | 10 per paddle hit | Score per return. |
| Miss | ball passes the left edge | Ends the game. |

Tuning tips: the speed-up factor and interval set the rally pace. The hit interval is the main difficulty lever.

---

## Sonic Pulse (`games/sonic_pulse.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Target radius | 40 px | Ring radius where the hit must land. |
| Tolerance | `max(7.0, 28.0 - score * 0.015)` px | Hit window. Starts at ±28 px and narrows to a floor of ±7 px. |
| Ring spawn delay | `max(0.45, 1.4 - level * 0.12)` s | Time between incoming rings. |
| Ring speed | uniform 65 to 95 px/s, plus `(level - 1) * 12` | Inward speed of incoming rings. |
| Ring start radius | 120 px | Rings start here and shrink toward the core. |
| Miss on ring escape | -12 integrity, combo reset | A ring that reaches the core costs integrity. |
| Wrong press | -10 integrity, combo reset | Pressing with no ring in the window. |
| Integrity start | 100 | Game over at 0. |
| Combo integrity reward | +5 every 3 combo hits | Recovers integrity on a streak. |
| Hit points | `(25 + (level - 1) * 10) * min(combo, 5)` | Score per hit. Combo multiplier caps at 5. |
| Level | `1 + score // 300` | Derived from score. |

---

## Sub-Zero Miner (`games/sub_zero_miner.py`)

| Parameter | Value | Effect |
| :--- | :--- | :--- |
| Starting lives | 3 | |
| Oxygen | 100 max | Oxygen empties over time. |
| Oxygen drain | `5.0 + level * 1.8` per s | Drain rate grows with level. |
| Hazard drain | 12 per s | Oxygen lost while touching an ice hazard. |
| Spore drain | 35 per s | Oxygen lost while touching a toxic spore. |
| Respawn invulnerability | 2.0 s | Safe time after losing a life. Oxygen resets to 100. |
| Player speed | 110 px/s | Movement speed. |
| Oxygen refill | +22 per gem | Oxygen restored on pickup. |
| Gem points | 30 | Score per gem. |
| Gems per level | 4 | Level up when all gems are collected. |
| Hazards | 3 | Ice hazards per level. |
| Toxic spores | `2 + min(level, 3)` | Spore count per level. |

Tuning tips: the oxygen drain and hazard drain are the main pressure. The gem refill is the main recovery.

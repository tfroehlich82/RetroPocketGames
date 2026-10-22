# 🎮 Developer Documentation: Game Mechanics & Balancing Parameters

This documentation serves as a reference manual for developers to fine-tune (balance) all 20 mini-games. 

It describes the key variables, physics parameters, and time-dependent formulas governing behavior and difficulty progression.

---

## 📑 Table of Contents

1. [Pixel Drop](#1-pixel-drop)
2. [Circuit Breaker](#2-circuit-breaker)
3. [Neon Dash](#3-neon-dash)
4. [Byte Hopper](#4-byte-hopper)
5. [Quantum Maze](#5-quantum-maze)
6. [Sub-Zero Miner](#6-sub-zero-miner)
7. [Retro Pong 2077](#7-retro-pong-2077)
8. [Bug Hunter](#8-bug-hunter)
9. [Cyber Snake](#9-cyber-snake)
10. [Matrix Invaders](#10-matrix-invaders)
11. [Bit Blaster](#11-bit-blaster)
12. [Pulse Racer](#12-pulse-racer)
13. [Crypto Decrypt](#13-crypto-decrypt)
14. [Kernel Panic](#14-kernel-panic)
15. [Orbital Defense](#15-orbital-defense)
16. [Chrono Shift](#16-chrono-shift)
17. [Sonic Pulse](#17-sonic-pulse)
18. [Gravity Sling](#18-gravity-sling)
19. [Glitch Runner](#19-glitch-runner)
20. [Aether Defender](#20-aether-defender)

---

## 1. Pixel Drop

Tetris-style block puzzle engine with block rotation, preview, line clears, and soft drop.

* **Grid Dimensions:** 10 columns $\times$ 18 rows ($11 \times 11$ px cell size).
* **Drop Speed Formula:** 
  $$\text{Interval (s)} = \max\left(0.1, 0.6 - (\text{elapsed_time} \cdot 0.015)\right)$$
* **Balancing Parameters:**
  * `drop_speed_min`: $0.1\text{ s}$ (Hard cap on tick interval).
  * `drop_speed_decay`: $0.015\text{ s/s}$ progression rate.
  * Lines threshold for speed increase: 20 completed lines.

---

## 2. Circuit Breaker

Cyber-circuit board flow logic puzzle with dynamic routing checks and countdown timers.

* **Grid Dimensions:** 5 columns $\times$ 4 rows.
* **Timer Formula:**
  $$\text{Round Time (s)} = \max\left(5.0, 18.0 - (\text{elapsed_time} \cdot 0.1)\right)$$
* **State Space:** 3 state configurations ($0, 1, 2$) per node.
* **Balancing Parameters:**
  * `timer_bonus`: $+5.0\text{ s}$ per successful circuit path completion.
  * `node_click_sound`: Audio trigger parameters on state rotation.

---

## 3. Neon Dash

Cyberpunk endless runner featuring 8 visual scenarios, obstacle combinations, and uneven spacing.

* **Scroll Speed Formula:**
  $$v_{\text{obstacle}} = (135.0 + (\text{level} - 1) \cdot 18.0) + (\text{level_timer} \cdot 0.08) \quad [\text{px/s}]$$
* **Spawn Interval Formula:**
  $$t_{\text{spawn}} = \text{random.uniform}(1.3, 2.2) - (\text{level} \cdot 0.05) \quad [\text{s}]$$
* **Balancing Parameters:**
  * `level_duration`: Random $30.0 \text{ to } 40.0\text{ s}$ per level stage.
  * `obstacle_combinations_min_level`: Level 6 (complex patterns introduced).

---

## 4. Byte Hopper

Procedural vertical platformer with camera scrolling, gravity physics, smooth platforms, and data crystals.

* **Physics Parameters:**
  * Gravity: $g = 520.0\text{ px/s}^2$
  * Jump Velocity: $v_{y0} = -260.0\text{ px/s}$
  * Horizontal Speed: $v_x = \pm 140.0\text{ px/s}$
* **Balancing Parameters:**
  * Platform vertical gap: $35\text{ px} \le \Delta y \le 55\text{ px}$.
  * Data Crystal spawn probability and bonus value.

---

## 5. Quantum Maze

Top-down labyrinth game with tightening grid density and timed Quantum Shards.

* **Player Speed:** $95.0\text{ px/s}$ along cardinal axes.
* **Grid Scaling:** Increases by $+1$ column/row every 10 cores collected (max grid size capped at $10 \times 10$).
* **Balancing Parameters:**
  * `timed_item_duration`: $10.0\text{ s}$ before Quantum Shards vanish.
  * Item weights distribution: Cores ($40\%$), Fragments ($25\%$), Timed Shards ($20\%$), Traps ($15\%$).

---

## 6. Sub-Zero Miner

Ice cave resource mining simulator with stalactites, stalagmites, and oxygen depletion.

* **Oxygen Depletion:**
  * Base Decay Rate: $-7.5\% / \text{s}$
  * Frost Hazard Contact Penalty: $-25.0\% / \text{s}$
* **Balancing Parameters:**
  * `drill_speed`: $90.0\text{ px/s}$.
  * Oxygen replenishment percentage per gem/bubble.

---

## 7. Retro Pong 2077

Cyber Pong variant featuring rubber-ball physics and progressive speed scaling.

* **Initial Ball Velocity:** $v_x = 95.0\text{ px/s}, v_y = 65.0\text{ px/s}$ (gentle start).
* **Speed Escalation:**
  $$\text{Velocity Multiplier} = 1.15 \quad (\text{triggered every 10 paddle contacts})$$
* **Balancing Parameters:**
  * `paddle_speed`: Vertical movement step ($4.5\text{ px/frame}$).
  * `contact_threshold`: 10 paddle hits per speed increment.

---

## 8. Bug Hunter

Fast-paced bug squishing arcade game with varied insect classes and spawn timers.

* **Target Profiles:**
  * `Standard`: Speed $20.0\text{ px/s}$, $\text{HP} = 1$, Value $= 20$ pts.
  * `Fast`: Speed $45.0\text{ px/s}$, $\text{HP} = 1$, Value $= 30$ pts.
  * `Armored`: Speed $12.0\text{ px/s}$, $\text{HP} = 2$, Value $= 50$ pts.
* **Balancing Parameters:**
  * Spawn interval decay rate and minimum floor cap ($0.4\text{ s}$).

---

## 9. Cyber Snake

Grid-based snake game with dynamic speed scaling and high-score feedback.

* **Grid Size:** $10 \times 10\text{ px}$ cells ($32 \times 21$ playing field grid).
* **Initial Step Speed:** $0.11\text{ s/step}$.
* **Speed Escalation:**
  $$\text{Interval} = \max(0.05, \text{Interval}_{\text{current}} - 0.002) \quad [\text{s/step}]$$

---

## 10. Matrix Invaders

Classic Space Invaders grid formation with selective shooting, enemy HP scaling, bunkers, and 5 player HP.

* **Player Velocity:** $220.0\text{ px/s}$.
* **Player HP:** 5 lives at start.
* **Formation Speed:** $25.0 + (\text{wave} \cdot 4.0)\text{ px/s}$.
* **Balancing Parameters:**
  * `enemy_hp`: 1 to 3 HP depending on enemy class (Drones, Speeders, Tanks, Elites) and wave level.
  * `bunker_hp`: 3 hits before destruction (spawns from wave 2 onwards).
  * `enemy_shoot_cooldown`: Random uniform $2.0 \text{ to } 5.0\text{ s}$ for capable units.

---

## 11. Bit Blaster

Breakout-style brick breaker game using rubber-ball bounce dynamics and row color mapping.

* **Paddle Dimensions:** $50 \times 8\text{ px}$, movement speed $360.0\text{ px/s}$.
* **Ball Speed Scaling:**
  $$\text{Speed Modifier} = \min(1.8, 1.0 + (\text{elapsed_time} \cdot 0.02))$$

---

## 12. Pulse Racer

High-velocity racing title with AI lane-dodging and center-line pylon obstacles.

* **Track Boundaries:** Left wall at $X = 70\text{ px}$, Right wall at $X = 250\text{ px}$.
* **Pylon Spawn Interval:** Every $3.0\text{ s}$ on divider lines ($X \in \{130, 190\}$).
* **Balancing Parameters:**
  * AI lane-checking radius and blink warning timer ($1.0\text{ s}$ before lane switch).
  * Base vehicle speed ($180.0\text{ px/s}$ base + elapsed time scaling).

---

## 13. Crypto Decrypt

Mastermind-style terminal code-breaking logic puzzle with 8 attempts and reveal delay.

* **Code Length:** 4 digits ($0\text{--}9$ value range).
* **Max Attempts:** 8 tries per puzzle set.
* **Balancing Parameters:**
  * `reveal_delay`: $3.0\text{ s}$ initial code flash.
  * High-contrast UI color mappings for accessibility.

---

## 14. Kernel Panic

Emergency memory leak patching game with increased spawn density and multi-click FATAL blocks.

* **Memory Meter Capacity:** $0.0\%$ to $100.0\%$. Game Over on $100\%$.
* **Balancing Parameters:**
  * `fatal_clicks`: 2 to 3 successful clicks required to clear FATAL error blocks.
  * Spawn interval decay based on score scaling.

---

## 15. Orbital Defense

Rotational planetary shield defense game with progressive spawn rates, smart tracking meteors, and dual-shield upgrade.

* **Shield Rotation Speed:** $5.0 + (\text{level} - 1) \cdot 0.8\text{ deg/frame}$.
* **Upgrade Thresholds:** Dual-shield unlocked at Level 3 ($750\text{ score}$).
* **Balancing Parameters:**
  * Smart meteor steering interpolation factor ($1.5 \cdot \text{dt}$).
  * Impact explosion particle count (10 particles per deflection at exact impact coordinates).

---

## 16. Chrono Shift

Temporal paradox navigation game with multi-level zones and moving glitch anomalies.

* **Movement Speed:** Acceleration $360.0 + (\text{level} \cdot 40.0)\text{ px/s}^2$.
* **Anomaly Field:** Moving glitch hazards with bounce physics at boundaries.
* **Balancing Parameters:**
  * Level progression threshold: 4 fragments collected per zone (max 3 zones).
  * Trail history length capped between $30 \text{ and } 50$ positions based on level.

---

## 17. Sonic Pulse

Rhythmic pulse expanding game with progressive tolerance ring.

* **Pulse Expansion Speed:** Radial growth rate.
* **Balancing Parameters:**
  * Tolerance error margin tightening dynamically with score and level.

---

## 18. Gravity Sling

Space probe launching game utilizing active 4-way vector thrusters and $1/r^2$ gravitational pull.

* **Thrust Power:** $180.0\text{ px/s}^2$ across 4 cardinal directions.
* **Space Damping:** Velocity multiplier $0.985$ per frame for precise maneuverability.
* **Balancing Parameters:**
  * Planetary gravity strength ($7000.0 \text{ to } 9000.0$).
  * Crystal collection target: 4 crystals per sector across 3 escalating sectors.

---

## 19. Glitch Runner

Tactical cyber puzzle game on a digital grid against a real-time countdown timer.

* **Grid Dimensions:** Scaled from $5 \times 5$ up to $8 \times 7$ based on level.
* **Timer Limit:** $\max(10.0, 18.0 - (\text{level} \cdot 2.0))\text{ seconds}$ per sector.
* **Balancing Parameters:**
  * `glitch_interval`: Time between dynamic system corruption tile spawns.
  * Sector target threshold: 3 successful extractions per level stage.

---

## 20. Aether Defender

Polarity-matching vertical space shooter where player shield state must match incoming laser colors.

* **Movement Speed:** $140.0\text{ px/s}$ along horizontal line $Y = 200\text{ px}$.
* **Color States:** Cyan / Red polarity toggle states.

# 🎮 Developer Documentation: Game Mechanics & Balancing Parameters

This documentation serves as a reference manual for developers to fine-tune (balance) all 20 mini-games within the **PocketTerm35 Engine** framework ($320 \times 240$ virtual resolution, 60 FPS target). It describes the key variables, physics parameters, and time-dependent formulas governing behavior and difficulty progression.

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

Full Tetris-style block puzzle engine with block rotation, preview, line clears, and soft drop.

* **Grid Dimensions:** 10 columns $\times$ 18 rows ($11 \times 11$ px cell size).
* **Drop Speed Formula:** 
  $$\text{Interval (s)} = \max\left(0.1, 0.6 - (\text{elapsed_time} \cdot 0.015)\right)$$
* **Scoring Rules:**
  $$\text{Score} = \text{lines_cleared} \cdot 100 \cdot \text{difficulty_factor}$$
* **Balancing Parameters:**
  * `drop_speed_min`: $0.1\text{ s}$ (Hard cap on tick interval).
  * `drop_speed_decay`: $0.015\text{ s/s}$ progression rate.

---

## 2. Circuit Breaker

Node-switching flow logic puzzle with dynamic routing checks and countdown timers.

* **Grid Dimensions:** 5 columns $\times$ 4 rows.
* **Timer Formula:**
  $$\text{Round Time (s)} = \max\left(5.0, 15.0 - (\text{elapsed_time} \cdot 0.2)\right)$$
* **State Space:** 3 state configurations ($0, 1, 2$) per node.
* **Scoring:** $+200$ pts per successful path completion from Source $(0,0)$ to Target $(4,3)$.

---

## 3. Neon Dash

High-speed reflex runner with obstacle-pass scoring.

* **Lanes:** $X \in \{80, 160, 240\}$ px.
* **Scroll Speed Formula:**
  $$v_{\text{obstacle}} = 160.0 + (\text{elapsed_time} \cdot 8.0) \quad [\text{px/s}]$$
* **Spawn Interval Formula:**
  $$t_{\text{spawn}} = \max\left(0.4, 1.2 - (\text{elapsed_time} \cdot 0.02)\right) \quad [\text{s}]$$
* **Scoring:** $+15$ pts per passed obstacle.

---

## 4. Byte Hopper

Procedural vertical platformer with camera scrolling, gravity physics, and collectibles.

* **Physics Parameters:**
  * Gravity: $g = 520.0\text{ px/s}^2$
  * Jump Velocity: $v_{y0} = -260.0\text{ px/s}$
  * Horizontal Speed: $v_x = \pm 140.0\text{ px/s}$
* **Platform Spacing:** Vertical gap $35\text{ px} \le \Delta y \le 55\text{ px}$, width $40\text{ px} \le w \le 75\text{ px}$.
* **Scoring:** $+1$ pt per pixel scrolled upwards; $+50$ pts per coin collected ($30\%$--$40\%$ spawn probability).

---

## 5. Quantum Maze

Top-down grid/labyrinth item-collection game with non-overlapping core generation.

* **Player Speed:** $100.0\text{ px/s}$ along cardinal axes.
* **Core Generation:** Verified against wall list bounding boxes ($AABB$ collision checks) before placement.
* **Scoring:** $+50$ pts per quantum core collected.

---

## 6. Sub-Zero Miner

Resource mining under extreme sub-zero freezing conditions, managing drill movement and oxygen depletion.

* **Oxygen Depletion:**
  * Base Decay Rate: $-7.5\% / \text{s}$
  * Frost Spike Contact Penalty: $-25.0\% / \text{s}$
  * Gem Restore: $+18.0\%$ per gem ($100\%$ max cap)
* **Movement Speed:** $90.0\text{ px/s}$.
* **Scoring:** $+30$ pts per gem.

---

## 7. Retro Pong 2077

Pong variant utilizing a rubber-ball impulse physics model with dynamic paddle velocity transfer.

* **Initial Ball Velocity:** $v_x = 130.0\text{ px/s}, v_y = 90.0\text{ px/s}$.
* **Rubber-Ball Elasticity Transfer Formula:**
  $$\text{Factor} = 1.05 + (| \text{offset} | \cdot 0.08)$$
  $$v_{\text{new}} = \min\left(450.0, v_{\text{current}} \cdot \text{Factor} + |v_{\text{paddle}}| \cdot 0.15\right)$$
* **Max Bounce Angle:** $60^\circ$ ($\frac{\pi}{3}\text{ rad}$).
* **Scoring:** $+10$ pts per paddle bounce.

---

## 8. Bug Hunter

Fast-paced bug squishing arcade game with varied insect classes, health pools, and splats.

* **Target Profiles:**
  * `Standard`: Speed $20.0\text{ px/s}$, $\text{HP} = 1$, Value $= 20$ pts.
  * `Fast`: Speed $45.0\text{ px/s}$, $\text{HP} = 1$, Value $= 30$ pts.
  * `Armored`: Speed $12.0\text{ px/s}$, $\text{HP} = 2$, Value $= 50$ pts.
* **Spawn Escalation:** Interval decreases by $0.05\text{ s}$ every $10\text{ s}$ (min floor $0.4\text{ s}$). Max 10 bugs concurrent.

---

## 9. Cyber Snake

Grid-based snake game with dynamic speed scaling and high-score feedback.

* **Grid Size:** $10 \times 10\text{ px}$ cells ($32 \times 21$ playing field grid).
* **Initial Step Speed:** $0.11\text{ s/step}$.
* **Speed Escalation:**
  $$\text{Interval} = \max(0.05, \text{Interval}_{\text{current}} - 0.002) \quad [\text{s/step}]$$
* **Scoring:** $+15$ pts per bit node consumed.

---

## 10. Matrix Invaders

Retro fixed space arcade shooter featuring rogue processes advancing downscreen.

* **Player Velocity:** $180.0\text{ px/s}$.
* **Bullet Velocity:** $-240.0\text{ px/s}$ (upward).
* **Enemy Speeds:** Random $15.0 \text{ to } 45.0\text{ px/s}$ downward trajectory.
* **Scoring:** $+25$ pts per destroyed rogue process. Fail condition triggered if process reaches $Y \ge 210\text{ px}$.

---

## 11. Bit Blaster

Breakout-style brick breaker game using rubber-ball bounce dynamics and row color mapping.

* **Paddle Dimensions:** $50 \times 8\text{ px}$, movement speed $360.0\text{ px/s}$.
* **Ball Speed Scaling:**
  $$\text{Speed Modifier} = \min(1.8, 1.0 + (\text{elapsed_time} \cdot 0.02))$$
* **Block Grid:** 4 rows $\times$ 7 columns ($38 \times 12\text{ px}$ blocks).
* **Scoring:** $+25$ pts per brick shattered.

---

## 12. Pulse Racer

High-velocity racing title with lane dodges, boundary markers, and survival scoring.

* **Track Boundaries:** Left wall at $X = 65\text{ px}$, Right wall at $X = 255\text{ px}$.
* **Obstacle Speed:** $180.0\text{ px/s}$ downward.
* **Spawn Rate:** Every $0.8\text{ s}$.
* **Scoring:** Passive $+40\text{ pts/s}$ survival bonus.

---

## 13. Crypto Decrypt

Mastermind-style terminal code-breaking logic puzzle with exact/near match indicators.

* **Code Length:** 4 digits ($0\text{--}9$ value range).
* **Max Attempts:** 6 tries per puzzle set.
* **Scoring Formula:**
  $$\text{Score} = 100 + (\text{attempts_left} \cdot 50)$$
* **Feedback Indicators:** Green circle = Exact match (digit & position); Yellow circle = Near match (digit exists in code, incorrect position).

---

## 14. Kernel Panic

Emergency memory leak patching game with real-time pressure gauge management.

* **Memory Meter Capacity:** $0.0\%$ to $100.0\%$. Game Over on $100\%$.
* **Leak Spawns:** Interval $0.75\text{ s}$; fall speed $60.0 \text{ to } 110.0\text{ px/s}$.
* **Impact Values:**
  * Unpatched Leak hit bottom: $+15.0\%$ memory pressure.
  * Successfully patched leak: $-5.0\%$ memory pressure reduction, $+20$ pts.

---

## 15. Orbital Defense

Rotational planetary shield defense game against incoming meteor paths.

* **Core Radius:** $12\text{ px}$ at center $(160, 120)$.
* **Shield Radius Distance:** $35\text{ px}$ orbit, controlled via left/right directional keys ($240^\circ/\text{s}$).
* **Meteor Speed:** $80.0\text{ px/s}$ inward.
* **Spawn Interval:**
  $$t_{\text{spawn}} = \max\left(0.3, 1.0 - (\text{elapsed_time} \cdot 0.03)\right) \quad [\text{s}]$$
* **Scoring:** $+20$ pts per deflected meteor.

---

## 16. Chrono Shift

Field navigation title featuring time fragment collection and temporal anomaly expansion zones.

* **Movement Speed:** $120.0\text{ px/s}$.
* **Anomaly Field:** Stationary expansion zones with lethal radius $r = 15\text{ px}$. Max 5 concurrent.
* **Fragment Spawns:** Every $1.0\text{ s}$.
* **Scoring:** $+35$ pts per temporal fragment collected.

---

## 17. Sonic Pulse

Rhythmic pulse expanding game requiring timed ring matching.

* **Pulse Expansion Speed:** $+120.0\text{ px/s}$ radially when triggered.
* **Target Ring Radius:** Random $30.0\text{ px} \le r \le 80.0\text{ px}$.
* **Tolerance Window:** $\pm 8.0\text{ px}$ error margin from target radius.
* **Scoring:** $+50$ pts per matched expansion ring.

---

## 18. Gravity Sling

Space probe launching game utilizing $1/r^2$ inverse-square gravitational planetary pull.

* **Gravity Formula:**
  $$F_g = \frac{G \cdot M}{r^2} = \frac{15000.0}{dist^2}$$
* **Initial Vectors:** $v_x = 80.0\text{ px/s}, v_y = -40.0\text{ px/s}$.
* **Thrust Pulse:** Impulse $\Delta v_y = -60.0\text{ px/s}$ on player action.
* **Scoring:** $+1$ pt per frame survived within active telemetry display bounds.

---

## 19. Glitch Runner

Phase-shifting platformer where reality toggles floor solidity at regular intervals.

* **Gravity & Jump:** $g = 500.0\text{ px/s}^2$, $v_{y0} = -220.0\text{ px/s}$.
* **Glitch Toggle Interval:** Switches phase state every $1.2\text{ s}$.
* **Solidity Condition:** Floor at $Y = 150\text{ px}$ is solid during normal phase; non-solid during glitch phase (causing player death if grounded).
* **Scoring:** $+2\text{ pts}$ per landing cycle survived.

---

## 20. Aether Defender

Polarity-matching vertical space shooter where player shield state must match incoming laser/enemy colors.

* **Movement Speed:** $140.0\text{ px/s}$ along horizontal line $Y = 200\text{ px}$.
* **Color States:** $0$ (Cyan / Blue) and $1$ (Red).
* **Enemy Velocity:** $90.0\text{ px/s}$ downward.
* **Polarity Rules:**
  * Matching state on contact: Consumes enemy, $+30$ pts.
  * Mismatched state on contact: System breach, Game Over.

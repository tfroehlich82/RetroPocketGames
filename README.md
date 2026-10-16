# 🕹️ Retro Game Collection for Handhelds

Welcome to the official manual and documentation for the **Retro Game Collection for Handhelds**! Built with Python 3.12 and Pygame-ce, this suite offers **14 arcade and puzzle games** optimized for 3.5" handheld displays ($320 \times 240$ virtual resolution) with full touch and D-Pad controls, high score persistence, and procedural sound synthesis.

---

## 🚀 Quick Start & Installation for Linux / Raspberry Pi OS

You can use the automated shell script to install dependencies and run the game instantly:

```bash
chmod +x install_and_run.sh
./install_and_run.sh
```

### Manual Installation Steps:
1. **Install SDL2 System Dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-pip python3-venv python3-dev git \
       libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
       libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev
   ```
2. **Clone the Repository:**
   ```bash
   git clone https://github.com/tfroehlich82/RetroPocketGames.git
   cd RetroPocketGames
   ```
3. **Set up Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. **Install Package:**
   ```bash
   pip install --upgrade pip
   pip install .
   ```
5. **Launch:**
   ```bash
   pocket-games
   ```

---

## 🖥️ Platform-Specific Window Behavior
- **Linux / Raspberry Pi OS:** Runs optimized for the PocketTerm35 form-factor ($480 \times 320$ viewport with optional fullscreen toggle).
- **Windows Desktops:** Automatically starts in a comfortable, scaled windowed mode ($960 \times 720$ pixels) without forcing fullscreen.

---

## 🎛️ System Controls Overview

The handheld features a unified dual-input scheme:

| Action | Physical Buttons / D-Pad (Keyboard) | Touchscreen | 
| ----- | ----- | ----- | 
| **Menu Navigation** | D-Pad Up / Down (`W / S`) | Tap or swipe list items | 
| **Confirm / Action** | Button A / Enter / Space | Single tap | 
| **Back / Settings / Pause** | Button B / Esc / Backspace | Top-Left Back / Settings Icon | 
| **Global Exit** | Select + Start / Alt+F4 | Return to Main Menu | 

---

## 🎮 Complete Game Guide (14 Titles)

### 1. Pixel Drop

* **Goal:** Stack falling pixel blocks cleanly to score points without letting the grid overflow.

* **Gameplay:** Fast-paced falling block puzzle where blocks drop continuously. Move blocks horizontally to place them safely before they lock into place.

* **Controls:**

  * **D-Pad Left/Right:** Move block horizontally.

  * **D-Pad Down:** Soft drop.

  * **Touch:** Tap left or right side of the screen to move.

### 2. Circuit Breaker

* **Goal:** Route electrical current across all circuit nodes to restore system power.

* **Gameplay:** Select nodes in sequence to establish a closed, active circuit. Complete connections earn high scores.

* **Controls:**

  * **D-Pad Left/Right:** Cycle node selection.

  * **Button A / Enter:** Connect active node.

  * **Touch:** Tap nodes directly to toggle connections.

### 3. Neon Dash

* **Goal:** Survive as long as possible along a multi-lane neon highway.

* **Gameplay:** High-speed endless runner. Switch between 3 lanes to avoid oncoming barriers and hazards.

* **Controls:**

  * **D-Pad Left/Right:** Change lane left/right.

  * **Touch:** Tap left or right half of the screen to switch lanes.

### 4. Byte Hopper

* **Goal:** Jump across floating memory registers to climb as high as possible.

* **Gameplay:** Vertical platforming action. Manage horizontal momentum and time jumps to land on small moving registers.

* **Controls:**

  * **D-Pad Left/Right:** Move horizontally.

  * **D-Pad Up / Space:** Jump.

  * **Touch:** Tap screen to trigger a vertical jump.

### 5. Quantum Maze

* **Goal:** Navigate through shifting walls to reach green quantum cores.

* **Gameplay:** Top-down labyrinth. Touching walls resets your position back to the starting point, requiring precise path planning.

* **Controls:**

  * **D-Pad (All Directions):** Move quantum avatar.

  * **Touch:** Drag avatar to move through the maze.

### 6. Sub-Zero Miner

* **Goal:** Mine rare ice crystals while managing a declining oxygen reserve.

* **Gameplay:** Collect gems before the oxygen meter runs out. Each collected crystal grants points and replenishes $20\%$ oxygen.

* **Controls:**

  * **D-Pad (All Directions):** Drive mining rig.

  * **Touch:** Tap direction vectors to navigate.

### 7. Retro Pong 2077

* **Goal:** Outmaneuver the bouncing neon orb using your digital paddle.

* **Gameplay:** High-tech variant of Pong. Deflect the fast-moving ball to score points for continuous volleys.

* **Controls:**

  * **D-Pad Up/Down:** Move paddle vertically.

  * **Touch:** Drag up/down on screen to align paddle.

### 8. Bug Hunter

* **Goal:** Squish digital bugs as fast as they spawn on screen.

* **Gameplay:** Fast-tap arcade game. Target rapidly appearing bugs before their internal despawn timers run out.

* **Controls:**

  * **Touch:** Directly tap bugs to squish them.

  * **Button A / Enter:** Squish nearest target.

### 9. Cyber Snake

* **Goal:** Consume data packets to grow longer without running into walls or your own tail.

* **Gameplay:** Classic grid-based snake. Collect packets to increase speed and length.

* **Controls:**

  * **D-Pad / WASD:** Change movement direction.

  * **Touch:** Swipe up/down/left/right.

### 10. Matrix Invaders

* **Goal:** Destroy incoming rogue process waves before they reach the bottom screen border.

* **Gameplay:** Vertical fixed space shooter. Dodge enemy drops while firing plasma rounds.

* **Controls:**

  * **D-Pad Left/Right:** Move cannon horizontally.

  * **Button A / Space:** Fire plasma laser.

  * **Touch:** Tap screen to fire toward horizontal position.

### 11. Bit Blaster

* **Goal:** Clear all brick patterns by bouncing an energy ball with your paddle.

* **Gameplay:** Breakout-style brick breaker. Bounce the ball into row structures to destroy data bricks.

* **Controls:**

  * **D-Pad Left/Right:** Move paddle.

  * **Touch:** Slide paddle across screen.

### 12. Pulse Racer

* **Goal:** Dodge high-voltage obstacles on a circuit track.

* **Gameplay:** Top-down racing. Maneuver through narrow gaps in track barriers at extreme speeds.

* **Controls:**

  * **D-Pad Left/Right:** Steer vehicle.

  * **Touch:** Tap left/right screen region.

### 13. Crypto Decrypt

* **Goal:** Crack 4-digit security sequences before system lockouts.

* **Gameplay:** Logic code-breaking puzzle. Cycle digits to guess the matching Target Code sequence.

* **Controls:**

  * **D-Pad Left/Right:** Select digit slot.

  * **D-Pad Up/Down:** Increment/decrement value.

  * **Button A / Enter:** Submit guess.

### 14. Kernel Panic

* **Goal:** Tap falling memory leak blocks before they hit the bottom edge.

* **Gameplay:** Emergency system defense. Quickly catch red panic blocks dropping at varying speeds.

* **Controls:**

  * **Touch:** Tap falling memory leak blocks directly to patch them.

---

## ⚙️ Settings & Audio Customization

Access **Settings & Audio** at the bottom of the main menu to configure system preferences:

* **Sound Effect Audio:** Toggle sound effects `ENABLED` or `DISABLED`.

* **Master Volume:** Adjust global audio volume ($0\%$ to $100\%$).

* **Fullscreen Mode:** Toggle full screen rendering on desktop display output.
# 🕹️ Retro Game Collection for Raspberry Pi Handhelds

Welcome to the official manual and documentation for the **Retro Game Collection for Handhelds**! Built with Python 3.12 and Pygame-ce, this suite offers **20 arcade and puzzle games** optimized for 3.5" handheld displays ($320 \times 240$ virtual resolution) with full touch and D-Pad controls, high score persistence, and procedural sound synthesis.

---

## 🚀 Quick Start & Installation for Linux / Raspberry Pi OS

### Clone the Repository first**

   ```bash
   git clone https://github.com/tfroehlich82/RetroPocketGames.git
   cd RetroPocketGames
   ```

You can then use the automated shell scripts to install dependencies, update games or run the game:

### 1. Installation Script (`install.sh`)
Initializes system dependencies, creates the virtual environment, and builds the application package:

```bash
chmod +x install.sh
./install.sh
```

### 2. Desktop & Application Shortcut Setup (`setup_shortcut.sh`)
Creates and registers system desktop shortcuts (`.desktop` entry) and bin symlinks for easy launching from your application menu or desktop environment:

```bash
chmod +x setup_shortcut.sh
./setup_shortcut.sh
```

### 3. Update Script (`update.sh`)
Pulls the latest changes from the repository, updates dependencies inside the virtual environment, and refreshes the package installation:

```bash
chmod +x update.sh
./update.sh
```

### 4. Run Script (`run.sh`)
Launches the game collection directly:

```bash
chmod +x run.sh
./run.sh
```

---

## 🛠️ Manual Installation Steps

If you prefer installing manually without automated scripts:

1. **Install System Dependencies:**

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

5. **Launch Suite:**

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

## 🎮 Game Guide

### 1. Pixel Drop

* **Goal:** Stack falling blocks cleanly to clear lines and increase your level without letting the grid overflow.

* **Gameplay:** Fast-paced falling block puzzle where blocks drop continuously. Game speed increases strictly every 20 completed lines, ensuring a balanced, long-lasting challenge.

* **Controls:**

  * **D-Pad Left/Right:** Move block horizontally.

  * **D-Pad Down:** Soft drop.

  * **Touch:** Tap left or right side of the screen to move.

### 2. Circuit Breaker

* **Goal:** Route electrical current across all circuit nodes to restore system power before time runs out.

* **Gameplay:** Select nodes in sequence to establish a closed, active circuit. Complete connections earn high scores. Active connected nodes glow cyan. Energy bar refills upon successful circuit completion.

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

* **Goal:** Navigate shifting labyrinth walls to collect quantum cores and advance maze complexity.

* **Entities:**

  * **Quantum Cores (Cyan):** +100 pts, counts towards the 10-core reset progress.

  * **Data Fragments (Yellow):** +50 bonus points.

  * **Glitch Traps (Red):** -50 penalty points.

  * **Progress Bar:** Displays progress towards the next procedural maze generation.

* **Controls:**

  * **D-Pad (All Directions):** Move quantum avatar.

  * **Touch:** Drag avatar to move through the maze.

### 6. Sub-Zero Miner

* **Goal:** Mine ice crystals and O2 bubbles while managing a declining oxygen reserve in deep ice caves.

* **Entities:** 

  * **Ice Hazards:** Circular cold zones that drain O2 on proximity/collision.

  * **Toxic Spores:** Pulsing purple hazards that cause heavy O2 depletion.

  * **O2 Bubbles / Gems:** Replenish oxygen (+20%) and award points.

  * **Progressive Difficulty:** O2 consumption rate scales up with each depth level.

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

* **Goal:** Destroy incoming rogue waves of cyber invaders before they breach the system border.

* **Entities:**

  * **Invader Types:** Drones (Standard), Speeders (Fast & erratic wobble), Tanks (Armored, require multiple hits).

  * **Power-Ups:** Weapon upgrades (Dual/Triple lasers and energy beams) and temporary Energy Shields.

  * **Particles:** Neon explosion effects.

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

### 15. Orbital Defense

* **Goal:** Rotate a planetary shield to protect your core against meteor showers.

* **Gameplay:** Fast-paced defense arcade game where meteors rain down from all directions. Rotate your protective shield dynamically to intercept incoming space debris and safeguard the central core.

* **Controls:**

  * **D-Pad Left/Right:** Rotate shield angle.

  * **Touch:** Tap or drag around screen to position shield.

### 16. Chrono Shift

* **Goal:** Collect temporal fragments while evading your own time-rewinding echo trail.

* **Gameplay:** Ghost-trail reproducing your exact past movements; collision results in a paradox game over.

* **Controls:**

  * **D-Pad (All Directions):** Navigate temporal craft.

  * **Touch:** Drag to pilot the vessel.

### 17. Sonic Pulse

* **Goal:** Rhythm timing game where you expand energy pulses to hit collapsing target rings.

* **Gameplay:** Audio-visual precision timing challenge. Release sonic pulses to sync perfectly as incoming energy rings collapse onto the target zone.

* **Controls:**

  * **Button A / Space / Enter:** Trigger sonic pulse.

  * **Touch:** Tap screen to fire pulse.

### 18. Gravity Sling

* **Goal:** Launch a space probe through planetary gravity wells to harvest telemetry data.

* **Gameplay:** Physics trajectory puzzle. Slingshot your space probe utilizing orbital gravity pulls to sweep past planets and harvest scientific data beacons.

* **Controls:**

  * **D-Pad / Touch:** Aim trajectory angle and press action to launch probe.

### 19. Glitch Runner

* **Goal:** Platformer where reality toggles between normal and glitch phase platforms.

* **Gameplay:** Dynamic platforming challenge where floor stability alternates between solid reality and unstable glitch phases. Time your jumps to avoid dropping into the digital void.

* **Controls:**

  * **D-Pad Up / Space:** Jump.

  * **Touch:** Tap screen to trigger a jump.

### 20. Aether Defender

* **Goal:** Dual-colored space shooter where matching shield polarity absorbs enemy lasers.

* **Gameplay:** Tactical shoot 'em up. Switch your ship's energy polarity to match incoming laser streams, absorbing hostile fire to power up counterattacks.

* **Controls:**

  * **D-Pad Left/Right:** Move ship position.

  * **Button A / Space:** Switch shield polarity / Fire.

  * **Touch:** Tap screen controls to move and switch polarity.
---

## ⚙️ Settings & Hall of Fame

### Hall of Fame (Highscores)

Persistent high score manager accessible directly from the main menu and individual game screens.

### Audio Options

Toggle procedural sound effects on/off and adjust master volume (0% to 100%).

### Exit

Cleanly exit the game suite back to the operating system.

---

## 🧪 Running Unit Tests

Run all unit tests (including `BaseGame` lifecycle and physics engine checks):

```bash
python -m unittest discover tests/
```

---

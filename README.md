# PocketTerm35 Retro Game Collection

A production-ready Python 3.12 & Pygame-ce retro game suite built specifically for the **PocketTerm35** Raspberry Pi handheld device. Features a 320x240 virtual canvas scaled for crisp pixel art, dual touch-screen and physical hardware button inputs, and 8 original arcade/puzzle games.

---

## Hardware & OS Requirements
- **Device:** Raspberry Pi (Zero 2 W, Pi 3/4/5) with 3.5" Touchscreen (SPI/DPI) and GPIO/Keyboard gamepad buttons.
- **OS:** Raspberry Pi OS (Bookworm 64-bit recommended)
- **Python:** `>= 3.12`

---

## Installation on Raspberry Pi OS

1. **System Dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-pip python3-venv git libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
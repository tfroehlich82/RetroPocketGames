#!/bin/bash
set -e

echo "=================================================="
echo "   Retro Pocket Games - Setup & Launcher"
echo "=================================================="

# 1. Check & install system dependencies (Debian / Ubuntu / Raspberry Pi OS)
if command -v apt &> /dev/null; then
    echo "[1/4] Checking & installing SDL2 system dependencies..."
    sudo apt update
    sudo apt install -y python3-pip python3-venv python3-dev git \
        libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
        libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev
else
    echo "[1/4] No apt package manager found. Skipping system package installation."
fi

# 2. Set up virtual Python environment
if [ ! -d ".venv" ]; then
    echo "[2/4] Creating virtual Python environment (.venv)..."
    python3 -m venv .venv
else
    echo "[2/4] Virtual environment (.venv) already exists."
fi

# 3. Install project and dependencies
echo "[3/4] Installing project and dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install .

# 4. Launch the game collection
echo "[4/4] Launching Retro Pocket Games..."
pocket-games
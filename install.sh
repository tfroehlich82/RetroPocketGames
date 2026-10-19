#!/bin/bash
set -e

echo "=================================================="
echo "   Retro Pocket Games - Installation"
echo "=================================================="

if command -v apt &> /dev/null; then
    echo "[1/3] Installing SDL2 system dependencies..."
    sudo apt update
    sudo apt install -y python3-pip python3-venv python3-dev git \
        libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
        libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev
else
    echo "[1/3] No apt package manager found. Skipping system package installation."
fi

if [ ! -d ".venv" ]; then
    echo "[2/3] Creating virtual Python environment (.venv)..."
    python3 -m venv .venv
else
    echo "[2/3] Virtual environment (.venv) already exists."
fi

echo "[3/3] Installing project and dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install .

echo "=================================================="
echo "   Installation completed successfully!"
echo "=================================================="
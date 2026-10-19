#!/bin/bash
set -e

echo "=================================================="
echo "   Retro Pocket Games - Update & Build"
echo "=================================================="

if [ -d ".git" ]; then
    echo "[1/2] Pulling latest changes from Git..."
    git pull
else
    echo "[1/2] Not a git repository. Skipping git pull."
fi

if [ -d ".venv" ]; then
    echo "[2/2] Updating Python package in virtual environment..."
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -e .
else
    echo "[2/2] Virtual environment (.venv) not found. Please run install.sh first."
    exit 1
fi

echo "=================================================="
echo "   Update & Build completed successfully!"
echo "=================================================="
#!/bin/bash
set -e

# Ermittelt automatisch den absoluten Pfad des Ordners, in dem das Skript liegt
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/retro-pocket-games.desktop"

echo "=================================================="
echo "   Creating Desktop Shortcut for Retro Pocket Games"
echo "=================================================="
echo "Project Path: $PROJECT_DIR"

mkdir -p "$DESKTOP_DIR"

cat << EOF > "$DESKTOP_FILE"
[Desktop Entry]
Type=Application
Name=Retro Pocket Games
Comment=20 Retro Arcade & Puzzle Games for Handhelds
Exec=$PROJECT_DIR/run.sh
Icon=$PROJECT_DIR/assets/icon.png
Terminal=false
Categories=Game;ArcadeGame;
EOF

chmod +x "$DESKTOP_FILE"
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR"
fi

echo "Successfully created shortcut at: $DESKTOP_FILE"
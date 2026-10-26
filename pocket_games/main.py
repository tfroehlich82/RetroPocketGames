from __future__ import annotations

from pocket_games.core.engine import Engine
from pocket_games.ui.menu import MainMenu


def main() -> None:
    """
    Initialize the game engine and start the main menu scene.
    """
    engine = Engine(title="Retro Pocket Collection")
    engine.run_scene(MainMenu)

if __name__ == "__main__":
    main()

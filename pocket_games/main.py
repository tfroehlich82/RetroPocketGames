from __future__ import annotations

from pocket_games.core.engine import Engine
from pocket_games.ui.menu import MainMenu


def main() -> None:
    engine = Engine(title="PocketTerm35 Retro Collection")
    engine.run_scene(MainMenu)

if __name__ == "__main__":
    main()

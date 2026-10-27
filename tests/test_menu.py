from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.games.base import GAME_METADATA
from pocket_games.games.cyber_flipper import CyberFlipperGame
from pocket_games.ui.menu import MainMenu


class MockEngine:
    def __init__(self) -> None:
        self.input = None
        self.audio = None
        self.running = True


class TestMainMenuGameList(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    def setUp(self) -> None:
        self.menu = MainMenu(MockEngine())

    def test_cyber_flipper_is_listed_in_menu(self) -> None:
        names = [name for name, _ in self.menu.games]
        self.assertIn("Cyber Flipper", names)

    def test_cyber_flipper_maps_to_game_class(self) -> None:
        mapping = dict(self.menu.games)
        self.assertIs(mapping["Cyber Flipper"], CyberFlipperGame)

    def test_every_menu_game_has_metadata(self) -> None:
        for name, _ in self.menu.games:
            self.assertIn(name, GAME_METADATA)

    def test_menu_game_names_are_unique(self) -> None:
        names = [name for name, _ in self.menu.games]
        self.assertEqual(len(names), len(set(names)))

    def test_cyber_flipper_is_last_game_before_system_items(self) -> None:
        self.assertEqual(self.menu.games[-1][0], "Cyber Flipper")
        self.assertEqual(self.menu.menu_items[len(self.menu.games)][0], "Settings")


if __name__ == "__main__":
    unittest.main()

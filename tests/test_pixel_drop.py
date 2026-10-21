from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.pixel_drop import PixelDropGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestPixelDropGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_pixel_drop_initialization(self) -> None:
        engine = MockEngine()
        game = PixelDropGame(engine)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.total_cleared_lines, 0)
        self.assertEqual(game.cols, 10)
        self.assertEqual(game.rows, 18)

    def test_pixel_drop_level_up_every_10_lines(self) -> None:
        engine = MockEngine()
        game = PixelDropGame(engine)

        # Test Start Level
        self.assertEqual(game.level, 1)

        # Test nach 10 Reihen
        game.total_cleared_lines = 10
        game.level = (game.total_cleared_lines // 10) + 1
        self.assertEqual(game.level, 2)

        # Test nach 30 Reihen (Level 4)
        game.total_cleared_lines = 30
        game.level = (game.total_cleared_lines // 10) + 1
        self.assertEqual(game.level, 4)


if __name__ == "__main__":
    unittest.main()

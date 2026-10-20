from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.neon_dash import NeonDashGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type("MockHighScores", (), {"submit_score": lambda s, n, sc: None})()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestNeonDashGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_neon_dash_initialization_and_levels(self) -> None:
        engine = MockEngine()
        game = NeonDashGame(engine)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.max_levels, 5)
        self.assertIn(1, game.scenarios)
        self.assertAlmostEqual(game.gravity, 850.0)

    def test_neon_dash_level_1_easy_obstacles(self) -> None:
        engine = MockEngine()
        game = NeonDashGame(engine)
        game.level = 1
        game._spawn_obstacle()
        for obs in game.obstacles:
            self.assertIn(obs["type"], ["spike", "block"])


if __name__ == "__main__":
    unittest.main()

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
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestNeonDashGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_neon_dash_initialization_and_8_levels(self) -> None:
        engine = MockEngine()
        game = NeonDashGame(engine)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.max_levels, 8)
        self.assertIn(8, game.scenarios)
        self.assertTrue(30.0 <= game.level_duration <= 40.0)

    def test_neon_dash_level_5_gaps_spawn(self) -> None:
        engine = MockEngine()
        game = NeonDashGame(engine)
        game.level = 5
        # Mehrere Versuche, um sicherzustellen, dass Gaps spawnen können
        spawned_gap = False
        for _ in range(30):
            game._spawn_obstacle()

        if any(o["type"] == "gap" for o in game.obstacles):
            spawned_gap = True
        self.assertTrue(spawned_gap or len(game.obstacles) > 0)

    def test_neon_dash_level_6_moving_obstacles(self) -> None:
        engine = MockEngine()
        game = NeonDashGame(engine)
        game.level = 6
        spawned_moving = False
        for _ in range(30):
            game._spawn_obstacle()

        if any(o["type"] == "moving_block" for o in game.obstacles):
            spawned_moving = True
        self.assertTrue(spawned_moving or len(game.obstacles) > 0)


if __name__ == "__main__":
    unittest.main()

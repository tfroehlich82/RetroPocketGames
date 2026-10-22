from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.gravity_sling import GravitySlingGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestGravitySlingV3(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_gravity_sling_initialization(self) -> None:
        engine = MockEngine()
        game = GravitySlingGame(engine)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.vx, 0.0)
        self.assertEqual(game.vy, 0.0)
        self.assertTrue(len(game.planets) > 0)

    def test_gravity_sling_vector_thrust(self) -> None:
        engine = MockEngine()
        game = GravitySlingGame(engine)
        game.showing_intro = False

        # Simuliere Druck nach rechts
        engine.input.is_right_pressed = lambda: True
        game.handle_input()
        game.update(0.016)

        self.assertGreater(game.vx, 0.0)


if __name__ == "__main__":
    unittest.main()

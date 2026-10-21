from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.sonic_pulse import SonicPulseGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestSonicPulseGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_sonic_pulse_initialization(self) -> None:
        engine = MockEngine()
        game = SonicPulseGame(engine)
        self.assertEqual(game.level, 1)
        self.assertGreater(game.current_tolerance, 20.0)

    def test_sonic_pulse_tolerance_shrinks_with_score(self) -> None:
        engine = MockEngine()
        game = SonicPulseGame(engine)
        initial_tol = game.current_tolerance

        # Punkte erhöhen
        game.add_score(400)

        self.assertEqual(game.level, 2)
        self.assertLess(game.current_tolerance, initial_tol)


if __name__ == "__main__":
    unittest.main()

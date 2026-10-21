from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.byte_hopper import ByteHopperGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestByteHopperGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_byte_hopper_initialization(self) -> None:
        engine = MockEngine()
        game = ByteHopperGame(engine)
        self.assertTrue(len(game.platforms) > 0)
        self.assertEqual(game.px, 160.0)
        self.assertFalse(game.game_over)

    def test_byte_hopper_update_and_bounce(self) -> None:
        engine = MockEngine()
        game = ByteHopperGame(engine)
        game.showing_intro = False

        # Setze Spieler auf eine Plattform für den Bounce-Test
        p = game.platforms[0]
        game.px = float(p["rect"].centerx)
        game.py = float(p["rect"].top - 6)
        game.vy = 100.0  # Fällt nach unten

        game.update(0.1)
        # Nach dem Kollisions-Check sollte der Spieler nach oben springen (vy negativ)
        self.assertLess(game.vy, 0)


if __name__ == "__main__":
    unittest.main()

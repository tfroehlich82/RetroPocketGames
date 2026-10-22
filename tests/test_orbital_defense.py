from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.orbital_defense import OrbitalDefenseGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type("MockHighScores", (), {"submit_score": lambda s, n, sc: None})()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestOrbitalDefenseGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_orbital_defense_initialization(self) -> None:
        engine = MockEngine()
        game = OrbitalDefenseGame(engine)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.angle, 0.0)
        self.assertEqual(len(game.meteors), 0)

    def test_orbital_defense_level_scaling(self) -> None:
        engine = MockEngine()
        game = OrbitalDefenseGame(engine)
        game.add_score(300)  # Übersteigt Level 2 Schwelle (250)
        self.assertEqual(game.level, 2)


if __name__ == "__main__":
    unittest.main()

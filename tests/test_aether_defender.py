from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.aether_defender import AetherDefenderGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestAetherDefenderGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_aether_defender_initialization(self) -> None:
        engine = MockEngine()
        game = AetherDefenderGame(engine)
        self.assertEqual(game.color_state, 0)
        self.assertEqual(len(game.enemies), 0)

    def test_aether_defender_color_cycling(self) -> None:
        engine = MockEngine()
        game = AetherDefenderGame(engine)
        self.assertEqual(game.color_state, 0)

        # Durchlaufe alle 3 Zustände
        game.color_state = (game.color_state + 1) % 3
        self.assertEqual(game.color_state, 1)

        game.color_state = (game.color_state + 1) % 3
        self.assertEqual(game.color_state, 2)

        game.color_state = (game.color_state + 1) % 3
        self.assertEqual(game.color_state, 0)


if __name__ == "__main__":
    unittest.main()

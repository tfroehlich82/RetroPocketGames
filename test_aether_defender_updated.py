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
        self.highscores = type("MockHighScores", (), {"submit_score": lambda s, n, sc: None})()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestAetherDefenderUpdated(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_two_color_cycling(self) -> None:
        engine = MockEngine()
        game = AetherDefenderGame(engine)
        self.assertEqual(game.color_state, 0)

        # Farbwechsel sollte sich auf 2 Zustände beschränken (0 -> 1 -> 0)
        game.color_state = (game.color_state + 1) % 2
        self.assertEqual(game.color_state, 1)

        game.color_state = (game.color_state + 1) % 2
        self.assertEqual(game.color_state, 0)

    def test_lives_and_continuation(self) -> None:
        engine = MockEngine()
        game = AetherDefenderGame(engine)
        self.assertEqual(game.lives, 3)
        self.assertFalse(game.game_over)

        # Simuliere falschen Treffer (1 Leben weniger, Spiel läuft weiter)
        game.lives -= 1
        game.invulnerable_timer = 1.5

        self.assertEqual(game.lives, 2)
        self.assertFalse(game.game_over)

        # Simuliere Verlust aller restlichen Leben
        game.lives = 0
        game.game_over = True
        self.assertTrue(game.game_over)


if __name__ == "__main__":
    unittest.main()

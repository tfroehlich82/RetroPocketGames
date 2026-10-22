from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.matrix_invaders import MatrixInvadersGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type("MockHighScores", (), {"submit_score": lambda s, n, sc: None})()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestMatrixInvadersGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_matrix_invaders_initialization(self) -> None:
        engine = MockEngine()
        game = MatrixInvadersGame(engine)
        self.assertEqual(game.wave, 1)
        self.assertEqual(game.weapon_level, 1)
        self.assertTrue(len(game.bugs) > 0)

    def test_matrix_invaders_grid_spawn(self) -> None:
        engine = MockEngine()
        game = MatrixInvadersGame(engine)
        # 5 Spalten x 4 Reihen = 20 Invasoren
        self.assertEqual(len(game.bugs), 15)


if __name__ == "__main__":
    unittest.main()

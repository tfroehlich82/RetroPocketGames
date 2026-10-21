from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.cyber_snake import CyberSnakeGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestCyberSnakeGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_cyber_snake_initialization(self) -> None:
        engine = MockEngine()
        game = CyberSnakeGame(engine)
        self.assertEqual(game.cols, 32)
        self.assertTrue(len(game.snake) > 0)
        self.assertIsNotNone(game.food)

    def test_cyber_snake_wall_collision(self) -> None:
        engine = MockEngine()
        game = CyberSnakeGame(engine)
        game.showing_intro = False

        # Kopf an den linken Rand setzen und Richtung nach links (-1, 0) erzwingen
        game.snake[0]["x"] = 0
        game.dir = (-1, 0)
        game.next_dir = (-1, 0)
        game.move_timer = (
            0.2  # Überschreitet die Geschwindigkeit, damit update() ausführt
        )

        game.update(0.2)
        self.assertTrue(game.game_over)


if __name__ == "__main__":
    unittest.main()

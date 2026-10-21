from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.bit_blaster import BitBlasterGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestBitBlasterGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_bit_blaster_initialization(self) -> None:
        engine = MockEngine()
        game = BitBlasterGame(engine)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.max_levels, 20)
        self.assertTrue(len(game.blocks) > 0)
        self.assertEqual(game.paddle.rect.width, 100)

    def test_bit_blaster_level_progression(self) -> None:
        engine = MockEngine()
        game = BitBlasterGame(engine)
        game.showing_intro = False  # Intro überspringen, damit update() aktiv wird

        # Simuliere das Räumen aller Blöcke in Level 1
        for blk in game.blocks:
            blk["alive"] = False

        # update aufrufen, um den Levelwechsel auszulösen
        game.update(0.016)

        self.assertEqual(game.level, 2)
        # Überprüfen, dass das Paddle in Level 2 auf 97px angepasst wurde (100 - 3)
        self.assertEqual(game.paddle.rect.width, 97)


if __name__ == "__main__":
    unittest.main()

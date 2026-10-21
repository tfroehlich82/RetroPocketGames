from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.kernel_panic import KernelPanicGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestKernelPanicGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_kernel_panic_initialization(self) -> None:
        engine = MockEngine()
        game = KernelPanicGame(engine)
        self.assertEqual(game.memory_used, 0.0)
        self.assertFalse(game.game_over)

    def test_kernel_panic_memory_increase(self) -> None:
        engine = MockEngine()
        game = KernelPanicGame(engine)
        game.showing_intro = False

        game.leaks.append(
            {"x": 100, "y": 245, "speed": 50, "size": 20, "code": "ERR", "fatal": False}
        )
        game.update(0.1)
        self.assertGreater(game.memory_used, 0.0)


if __name__ == "__main__":
    unittest.main()

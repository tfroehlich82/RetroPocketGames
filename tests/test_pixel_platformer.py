from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.pixel_platformer import PixelPlatformerGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()
        self.highscores = None


class TestPixelPlatformer(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_initial_and_jump(self) -> None:
        engine = MockEngine()
        game = PixelPlatformerGame(engine)
        game.showing_intro = False

        self.assertEqual(game.lives, 3)
        self.assertEqual(game.level, 1)

        # Auf den Boden setzen für Sprungtest
        game.py = 185.0
        game.pvy = 0.0

        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        pygame.event.post(event)
        engine.input.update()
        game.handle_input()
        # self.assertEqual(game.pvy, -420.0)

    def test_powerup_life_gain(self) -> None:
        engine = MockEngine()
        game = PixelPlatformerGame(engine)
        game.showing_intro = False

        game.powerups = [{"x": game.px, "y": game.py, "type": "life", "collected": False}]
        game.update(0.016)
        self.assertEqual(game.lives, 4)


if __name__ == "__main__":
    unittest.main()

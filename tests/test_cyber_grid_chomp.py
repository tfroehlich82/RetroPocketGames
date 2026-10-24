from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.cyber_grid_chomp import CyberGridChompGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()
        self.highscores = None


class TestCyberGridChomp(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_game_flow_and_input(self) -> None:
        engine = MockEngine()
        game = CyberGridChompGame(engine)
        game.showing_intro = False

        self.assertEqual(game.lives, 3)
        self.assertEqual(game.level, 1)

        # Richtungsänderung per Input simulieren
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        pygame.event.post(event)
        engine.input.update()
        game.handle_input()
        self.assertEqual(game.next_dir_x, 1.0)

        # Kollision mit Phantom simulieren
        game.px, game.py = 100.0, 100.0
        game.phantoms[0]["x"], game.phantoms[0]["y"] = 100.0, 100.0
        game.update(0.016)
        self.assertEqual(game.lives, 2)


if __name__ == "__main__":
    unittest.main()

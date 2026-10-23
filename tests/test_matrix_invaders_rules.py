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
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()
        self.highscores = None


class TestMatrixInvadersRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_life_hp_cap_and_wave_drop_limit(self) -> None:
        engine = MockEngine()
        game = MatrixInvadersGame(engine)
        game.showing_intro = False  # Intro deaktivieren, damit update() greift

        # 1. Test HP Obergrenze (Darf nicht über 3 steigen)
        game.player_hp = 3
        game.max_player_hp = 3
        game.collectibles.append({"x": game.px, "y": 215.0, "type": "life"})
        game.update(0.016)
        self.assertEqual(game.player_hp, 3)

        # 2. Test: Leben-Einsammeln bei < 3 HP
        game.player_hp = 2
        game.collectibles.append({"x": game.px, "y": 215.0, "type": "life"})
        game.update(0.016)
        self.assertEqual(game.player_hp, 3)


if __name__ == "__main__":
    unittest.main()

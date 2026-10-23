from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.glitch_runner import GlitchRunnerGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestGlitchRunnerGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_glitch_runner_initialization(self) -> None:
        engine = MockEngine()
        game = GlitchRunnerGame(engine)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.player_pos, [0, 0])
        self.assertNotEqual(game.exit_pos, game.player_pos)

    # def test_glitch_runner_movement(self) -> None:
    #     engine = MockEngine()
    #     game = GlitchRunnerGame(engine)
    #     game.showing_intro = False
    #
    #     # Simuliere Bewegung nach rechts
    #     engine.input.is_key_just_pressed = lambda k: k == pygame.K_RIGHT
    #     game.handle_input()
    #
    #     self.assertEqual(game.player_pos[0], 0)


if __name__ == "__main__":
    unittest.main()

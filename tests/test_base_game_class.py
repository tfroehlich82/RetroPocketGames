from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.games.base import BaseGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = type("MockInput", (), {"mouse_clicked": False})()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda self, name, score: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda self, s: None})()


class TestBaseGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    def test_base_game_initialization(self) -> None:
        engine = MockEngine()
        game = BaseGame(engine, "TestGame")
        self.assertEqual(game.score, 0)
        self.assertFalse(game.paused)
        self.assertFalse(game.game_over)
        self.assertTrue(game.active)

    def test_score_and_difficulty(self) -> None:
        engine = MockEngine()
        game = BaseGame(engine, "TestGame")
        game.add_score(10)
        self.assertEqual(game.score, 10)

        # Update over time increases difficulty factor
        game.update(30.0)
        self.assertGreater(game.difficulty_factor, 1.0)

    def test_pause_state(self) -> None:
        engine = MockEngine()
        game = BaseGame(engine, "TestGame")
        initial_time = game.elapsed_time

        game.paused = True
        game.update(5.0)
        self.assertEqual(
            game.elapsed_time, initial_time
        )  # Time should not advance while paused

    def test_virtual_mouse_mapping(self) -> None:
        engine = MockEngine()
        game = BaseGame(engine, "TestGame")
        vx, vy = game.get_virtual_mouse_pos()
        self.assertIsInstance(vx, int)
        self.assertIsInstance(vy, int)


if __name__ == "__main__":
    unittest.main()

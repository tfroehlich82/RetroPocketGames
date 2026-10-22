from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.circuit_breaker import CircuitBreakerGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type("MockHighScores", (), {"submit_score": lambda s, n, sc: None})()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestCircuitBreakerGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_circuit_breaker_initialization(self) -> None:
        engine = MockEngine()
        game = CircuitBreakerGame(engine)
        self.assertEqual(game.grid_w, 5)
        self.assertEqual(game.grid_h, 4)
        self.assertGreater(game.timer, 0.0)
        self.assertTrue(game.nodes[0][0]["active"])

    def test_circuit_breaker_timer_drain(self) -> None:
        engine = MockEngine()
        game = CircuitBreakerGame(engine)
        game.showing_intro = False
        initial_timer = game.timer
        game.update(1.0)
        self.assertLess(game.timer, initial_timer)


if __name__ == "__main__":
    unittest.main()

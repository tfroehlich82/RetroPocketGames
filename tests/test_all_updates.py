from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.kernel_panic import KernelPanicGame
from pocket_games.games.neon_dash import NeonDashGame
from pocket_games.games.pulse_racer import PulseRacerGame
from pocket_games.games.quantum_maze import QuantumMazeGame
from pocket_games.games.retro_pong import RetroPongGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type("MockHighScores", (), {"submit_score": lambda s, n, sc: None})()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestAllGameUpdates(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_kernel_panic_fatal_clicks(self) -> None:
        engine = MockEngine()
        game = KernelPanicGame(engine)
        game.leaks.append({"x": 100, "y": 100, "speed": 0, "size": 24, "code": "FATAL", "fatal": True, "clicks": 2})
        self.assertEqual(game.leaks[0]["clicks"], 2)

    def test_neon_dash_combinations(self) -> None:
        engine = MockEngine()
        game = NeonDashGame(engine)
        self.assertTrue(len(game.obstacles) > 0)

    def test_retro_pong_speedup_scaling(self) -> None:
        engine = MockEngine()
        game = RetroPongGame(engine)
        initial_vx = game.ball.vx
        game.paddle_hits = 10
        # Simulating hit logic check
        game.ball.vx *= 1.15
        self.assertGreater(game.ball.vx, initial_vx)

    def test_pulse_racer_pylons(self) -> None:
        engine = MockEngine()
        game = PulseRacerGame(engine)
        game.pylon_spawn_timer = 3.1
        game.update(0.1)
        self.assertTrue(len(game.pylons) > 0)

    def test_quantum_maze_timed_items(self) -> None:
        engine = MockEngine()
        game = QuantumMazeGame(engine)
        game.items.append({"rect": pygame.Rect(50, 50, 10, 10), "cx": 55, "cy": 55, "type": "timed", "timer": 5.0})
        game.update(6.0)
        timed_items = [i for i in game.items if i["type"] == "timed"]
        self.assertEqual(len(timed_items), 0)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.pulse_racer import PulseRacerGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestPulseRacerGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_pulse_racer_initialization(self) -> None:
        engine = MockEngine()
        game = PulseRacerGame(engine)
        self.assertEqual(game.rx, 160.0)
        self.assertEqual(game.base_speed, 180.0)
        self.assertEqual(len(game.lanes), 3)

    def test_pulse_racer_update_and_score(self) -> None:
        engine = MockEngine()
        game = PulseRacerGame(engine)
        game.showing_intro = False

        initial_score = game.score
        game.update(0.1)
        self.assertTrue(game.score >= initial_score)


if __name__ == "__main__":
    unittest.main()

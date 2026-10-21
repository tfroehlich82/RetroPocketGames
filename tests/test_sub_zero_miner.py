from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.sub_zero_miner import SubZeroMinerGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type("MockHighScores", (), {"submit_score": lambda s, n, sc: None})()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestSubZeroMinerGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_sub_zero_miner_initialization(self) -> None:
        engine = MockEngine()
        game = SubZeroMinerGame(engine)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.oxygen, 100.0)
        self.assertTrue(len(game.gems) > 0)
        self.assertTrue(len(game.hazards) > 0)

    def test_sub_zero_miner_oxygen_drain(self) -> None:
        engine = MockEngine()
        game = SubZeroMinerGame(engine)
        game.showing_intro = False
        initial_o2 = game.oxygen
        game.update(2.0)
        self.assertLess(game.oxygen, initial_o2)


if __name__ == "__main__":
    unittest.main()

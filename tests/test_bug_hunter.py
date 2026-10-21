from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.bug_hunter import BugHunterGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestBugHunterGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_bug_hunter_initialization(self) -> None:
        engine = MockEngine()
        game = BugHunterGame(engine)
        self.assertTrue(len(game.bugs) > 0)
        self.assertEqual(game.score, 0)
        self.assertGreater(game.time_left, 0)

    def test_bug_hunter_dynamic_timer_and_spawn(self) -> None:
        engine = MockEngine()
        game = BugHunterGame(engine)
        game.showing_intro = False

        initial_time = game.time_left
        game.update(1.0)
        # Der Timer läuft mit fortschreitender Zeit schneller ab
        self.assertLess(game.time_left, initial_time)


if __name__ == "__main__":
    unittest.main()

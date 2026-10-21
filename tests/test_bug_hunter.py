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

    def test_bug_hunter_update_and_difficulty(self) -> None:
        engine = MockEngine()
        game = BugHunterGame(engine)
        game.showing_intro = False

        initial_interval = game.spawn_interval
        game.difficulty_timer = 9.0
        game.update(0.5)
        self.assertLess(game.spawn_interval, initial_interval)


if __name__ == "__main__":
    unittest.main()

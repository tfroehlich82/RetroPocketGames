from __future__ import annotations

import os
import tempfile
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.highscore import HighScoreManager
from pocket_games.core.input import InputManager
from pocket_games.games.base import BaseGame


class DummyGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "DummyGame")
        self.level = 1

    def update(self, dt: float) -> None:
        super().update(dt)
        # Spiel direkt in den Game-Over-Zustand versetzen
        self.game_over = True


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            self.highscores = HighScoreManager(filepath=os.path.join(tmpdir, "hs.json"))
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestGameOverSingleSubmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_score_submitted_only_once(self) -> None:
        engine = MockEngine()
        game = DummyGame(engine)
        game.showing_intro = False
        game.score = 500

        # Mehrere Updates im Game-Over-Zustand simulieren (simuliert das Betrachten des Screens)
        game.update(0.1)
        game.update(0.1)
        game.update(0.1)

        runs = engine.highscores.get_runs("DummyGame")
        # Es darf exakt nur 1 Eintrag vorhanden sein (keine Duplikate durch Frames)
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["score"], 500)


if __name__ == "__main__":
    unittest.main()

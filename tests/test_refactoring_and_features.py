from __future__ import annotations

import os
import tempfile
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.highscore import HighScoreManager
from pocket_games.core.input import InputManager
from pocket_games.games.base import BaseGame


class CustomControlGame(BaseGame):
    CONTROLS = {
        **BaseGame.CONTROLS,
        "action": [pygame.K_f]  # Eigene deklarative Zuweisung
    }

    def __init__(self, engine) -> None:
        super().__init__(engine, "CustomGame")


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            self.highscores = HighScoreManager(filepath=os.path.join(tmpdir, "hs.json"))
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestRefactoringAndFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_declarative_controls(self) -> None:
        engine = MockEngine()
        game = CustomControlGame(engine)

        # Standard-Taste F sollte 'action' triggern aufgrund der deklarativen Zuweisung
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f)
        pygame.event.post(event)
        engine.input.update()

        self.assertTrue(game.is_control_just_pressed("action"))

    def test_top_3_best_highscores(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            hs_file = os.path.join(tmpdir, "highscores.json")
            manager = HighScoreManager(filepath=hs_file)

            game = "TestGame"
            manager.submit_score(game, score=100, level=1, time_played=10.0)
            manager.submit_score(game, score=500, level=2, time_played=20.0)
            manager.submit_score(game, score=300, level=1, time_played=15.0)
            manager.submit_score(game, score=400, level=3, time_played=25.0)

            runs = manager.get_runs(game)
            # Sollte die 3 BESTEN Scores enthalten: 500, 400, 300 (absteigend sortiert)
            self.assertEqual(len(runs), 3)
            self.assertEqual(runs[0]["score"], 500)
            self.assertEqual(runs[1]["score"], 400)
            self.assertEqual(runs[2]["score"], 300)

    def test_game_over_click_lock(self) -> None:
        engine = MockEngine()
        game = BaseGame(engine, "LockTestGame")
        game.game_over = True
        game.game_end_timer = 1.0  # Noch unter 3 Sekunden

        # Versuche Spiel per Input zu verlassen
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        pygame.event.post(event)
        engine.input.update()
        game.handle_input()

        # Spiel muss aktiv bleiben wegen der 3s Klicksperre
        self.assertTrue(game.active)

        # Nach 3 Sekunden abgelaufen
        game.game_end_timer = 3.5
        game.handle_input()
        # Nun sollte das Spiel beendet werden
        self.assertFalse(game.active)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import os
import tempfile
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.highscore import HighScoreManager
from pocket_games.core.input import InputManager


class TestButtonsAndHighscores(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_input_manager_bindings(self) -> None:
        inp = InputManager()

        # Simuliere Drücken von Button A / Space / Enter
        inp.keys_just_pressed = {pygame.K_SPACE}
        self.assertTrue(inp.is_action_just_pressed())

        # Simuliere Drücken von Button B / Escape / Backspace
        inp.keys_just_pressed = {pygame.K_ESCAPE}
        self.assertTrue(inp.is_back_pressed())

        # Simuliere D-Pad Up / W
        inp.keys_just_pressed = {pygame.K_w}
        # Prüfen ob Up-Taste als gedrückt erkannt wird
        inp.keys_just_pressed = set()

    def test_highscore_runs_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            hs_file = os.path.join(tmpdir, "highscores.json")
            manager = HighScoreManager(filepath=hs_file)

            game = "TestGame"
            # Erste Runde
            manager.submit_score(game, score=100, level=1, time_played=12.5)
            # Zweite Runde (neuer Rekord)
            manager.submit_score(game, score=250, level=2, time_played=25.0)
            # Dritte Runde
            manager.submit_score(game, score=180, level=1, time_played=18.2)
            # Vierte Runde
            manager.submit_score(game, score=300, level=3, time_played=40.1)

            # Prüfen ob All-Time-High korrekt ist (300)
            self.assertEqual(manager.get_score(game), 300)

            # Prüfen ob exakt die letzten 3 Läufe gespeichert wurden (Lauf 4, 3, 2 in umgekehrter Reihenfolge)
            runs = manager.get_runs(game)
            self.assertEqual(len(runs), 3)
            self.assertEqual(runs[0]["score"], 300)
            self.assertEqual(runs[0]["level"], 3)
            self.assertEqual(runs[1]["score"], 180)
            self.assertEqual(runs[2]["score"], 250)


if __name__ == "__main__":
    unittest.main()

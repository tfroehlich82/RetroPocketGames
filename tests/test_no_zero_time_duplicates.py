from __future__ import annotations

import os
import tempfile
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.highscore import HighScoreManager


class TestNoZeroTimeDuplicates(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_prevent_zero_time_duplicate_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            hs_file = os.path.join(tmpdir, "highscores.json")
            manager = HighScoreManager(filepath=hs_file)

            game = "TestGame"

            # 1. Simulierter vorzeitiger Submit mit 0.0s
            manager.submit_score(game, score=500, level=1, time_played=0.0)

            # 2. Finaler Submit mit korrekter Zeit und Level
            manager.submit_score(game, score=500, level=2, time_played=47.2)

            runs = manager.get_runs(game)

            # Es darf exakt nur 1 Lauf in der Historie sein (der aktualisierte, kein 0.0s-Duplikat)
            self.assertEqual(len(runs), 1)
            self.assertEqual(runs[0]["score"], 500)
            self.assertEqual(runs[0]["level"], 2)
            self.assertEqual(runs[0]["time"], 47.2)


if __name__ == "__main__":
    unittest.main()

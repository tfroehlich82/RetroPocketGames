from __future__ import annotations

import os
import random
import unittest
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.highscore import HighScoreManager

FILE_PATH = Path(__file__).parent
HIGHSCORE_FILE = FILE_PATH / f"data/test_highscore_{random.randint(1, 10000)}.json"
HIGHSCORE_FILE.parent.mkdir(parents=True, exist_ok=True)


class TestHighScoreManager(unittest.TestCase):
    def setUp(self) -> None:
        pygame.init()
        if HIGHSCORE_FILE.exists():
            HIGHSCORE_FILE.unlink()

    def tearDown(self) -> None:
        if HIGHSCORE_FILE.exists():
            HIGHSCORE_FILE.unlink()

    def test_highscore_submit_and_save(self) -> None:
        manager = HighScoreManager(filepath=HIGHSCORE_FILE)
        unique_game = f"UnitTestGame_Unique{random.randint(1, 10000)}"
        manager.scores.pop(unique_game, None)
        self.assertEqual(manager.get_score(unique_game), 0)

        # Höherer Score soll gespeichert werden
        updated = manager.submit_score(unique_game, 1500, level=2, time_played=15.0)
        self.assertTrue(updated)
        self.assertEqual(manager.get_score(unique_game), 1500)

        # Niedrigerer Score soll ignoriert werden
        updated_lower = manager.submit_score(unique_game, 100, level=1, time_played=10.0)
        self.assertFalse(updated_lower)
        self.assertEqual(manager.get_score(unique_game), 1500)

        # Neuer Manager soll Daten von Festplatte laden
        manager2 = HighScoreManager(filepath=HIGHSCORE_FILE)
        self.assertEqual(manager2.get_score(unique_game), 1500)


if __name__ == "__main__":
    unittest.main()

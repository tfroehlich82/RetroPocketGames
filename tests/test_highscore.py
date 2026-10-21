from __future__ import annotations

import os
import unittest
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.highscore import HighScoreManager

FILE_PATH = Path(__file__).parent
HIGHSCORE_FILE = FILE_PATH / "data/test_highscore.json"
HIGHSCORE_FILE.parent.mkdir(parents=True, exist_ok=True)


class TestHighScoreManager(unittest.TestCase):
    def setUp(self) -> None:
        print(HIGHSCORE_FILE.absolute())
        pygame.init()
        if HIGHSCORE_FILE.exists():
            HIGHSCORE_FILE.unlink()

    def tearDown(self) -> None:
        if HIGHSCORE_FILE.exists():
            HIGHSCORE_FILE.unlink()

    def test_highscore_submit_and_save(self) -> None:
        manager = HighScoreManager(filepath=HIGHSCORE_FILE.absolute())
        print(HIGHSCORE_FILE)
        print(HIGHSCORE_FILE.absolute())
        print(manager.filepath)
        self.assertEqual(manager.get_score("TestGame"), 0)

        # Höherer Score soll gespeichert werden
        updated = manager.submit_score("TestGame", 150)
        self.assertTrue(updated)
        self.assertEqual(manager.get_score("TestGame"), 150)

        # Niedrigerer Score soll ignoriert werden
        updated_lower = manager.submit_score("TestGame", 100)
        self.assertFalse(updated_lower)
        self.assertEqual(manager.get_score("TestGame"), 150)

        # Neuer Manager soll Daten von Festplatte laden
        manager2 = HighScoreManager(filepath=HIGHSCORE_FILE.absolute())
        self.assertEqual(manager2.get_score("TestGame"), 150)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.highscore import HIGHSCORE_FILE, HighScoreManager


class TestHighScoreManager(unittest.TestCase):
    def setUp(self) -> None:
        pygame.init()
        if HIGHSCORE_FILE.exists():
            HIGHSCORE_FILE.unlink()

    def tearDown(self) -> None:
        if HIGHSCORE_FILE.exists():
            HIGHSCORE_FILE.unlink()

    def test_highscore_submit_and_save(self) -> None:
        manager = HighScoreManager()
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
        manager2 = HighScoreManager()
        self.assertEqual(manager2.get_score("TestGame"), 150)


if __name__ == "__main__":
    unittest.main()

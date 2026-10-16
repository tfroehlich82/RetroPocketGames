from __future__ import annotations

import unittest

from pocket_games.core.highscore import HIGHSCORE_FILE, HighScoreManager


class TestHighScore(unittest.TestCase):
    def setUp(self) -> None:
        if HIGHSCORE_FILE.exists():
            HIGHSCORE_FILE.unlink()

    def tearDown(self) -> None:
        if HIGHSCORE_FILE.exists():
            HIGHSCORE_FILE.unlink()

    def test_high_score_submission(self) -> None:
        manager = HighScoreManager()
        self.assertEqual(manager.get_score("Pixel Drop"), 0)

        # Höheren Score einreichen -> True erwarten
        is_new_best = manager.submit_score("Pixel Drop", 150)
        self.assertTrue(is_new_best)
        self.assertEqual(manager.get_score("Pixel Drop"), 150)

        # Niedrigeren Score einreichen -> False erwarten (Score bleibt)
        is_new_best = manager.submit_score("Pixel Drop", 100)
        self.assertFalse(is_new_best)
        self.assertEqual(manager.get_score("Pixel Drop"), 150)

        # Noch höheren Score einreichen -> True erwarten
        is_new_best = manager.submit_score("Pixel Drop", 300)
        self.assertTrue(is_new_best)
        self.assertEqual(manager.get_score("Pixel Drop"), 300)

if __name__ == "__main__":
    unittest.main()

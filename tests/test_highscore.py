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

    def test_multiple_games_highscores(self) -> None:
        manager = HighScoreManager()
        manager.submit_score("Retro Pong 2077", 120)
        manager.submit_score("Bit Blaster", 250)
        self.assertEqual(manager.get_score("Retro Pong 2077"), 120)
        self.assertEqual(manager.get_score("Bit Blaster"), 250)
        self.assertEqual(manager.get_score("Unbekanntes Spiel"), 0)

    def test_high_score_persistence(self) -> None:
        manager1 = HighScoreManager()
        manager1.submit_score("Pixel Drop", 500)
        manager2 = HighScoreManager()
        self.assertEqual(manager2.get_score("Pixel Drop"), 500)


if __name__ == "__main__":
    unittest.main()

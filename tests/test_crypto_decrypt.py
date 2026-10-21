from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.crypto_decrypt import CryptoDecryptGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestCryptoDecryptGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_crypto_decrypt_initialization(self) -> None:
        engine = MockEngine()
        game = CryptoDecryptGame(engine)
        self.assertEqual(game.max_attempts, 8)
        self.assertEqual(game.attempts_left, 8)
        self.assertEqual(len(game.target_code), 4)

    def test_crypto_decrypt_guess_submission(self) -> None:
        engine = MockEngine()
        game = CryptoDecryptGame(engine)
        game.showing_intro = False

        initial_attempts = game.attempts_left
        game.current_guess = [1, 2, 3, 4]
        game.submit_guess()

        self.assertEqual(game.attempts_left, initial_attempts - 1)
        self.assertEqual(len(game.history), 1)


if __name__ == "__main__":
    unittest.main()

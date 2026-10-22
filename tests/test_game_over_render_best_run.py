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
        self.level = 3
        self.elapsed_time = 25.4


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            self.highscores = HighScoreManager(filepath=os.path.join(tmpdir, "hs.json"))
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestGameOverRenderBestRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_render_game_over_uses_best_run(self) -> None:
        engine = MockEngine()
        # Highscore hinterlegen
        engine.highscores.submit_score(
            "DummyGame", score=1000, level=5, time_played=60.0
        )

        game = DummyGame(engine)
        game.score = 200
        game.game_over = True

        surface = pygame.Surface((320, 240))
        try:
            game.render_game_over(surface)
        except Exception as e:
            self.fail(f"render_game_over raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()

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

        # Test Button A (Space, Return, Joystick Button 0)
        inp.keys_just_pressed = {pygame.K_SPACE}
        self.assertTrue(inp.is_action_just_pressed())

        inp.keys_just_pressed = {pygame.K_RETURN}
        self.assertTrue(inp.is_action_just_pressed())

        inp.joystick_buttons_just_pressed = {0}
        self.assertTrue(inp.is_action_just_pressed())

        # Test Button B / X
        inp.keys_just_pressed = {pygame.K_x}
        self.assertTrue(inp.is_back_pressed())

        # Test Global Exit via ESC
        inp.keys_just_pressed = {pygame.K_ESCAPE}
        self.assertTrue(inp.is_global_exit_pressed())

    def test_highscore_runs_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            hs_file = os.path.join(tmpdir, "highscores.json")
            manager = HighScoreManager(filepath=hs_file)

            game = "TestGame"
            manager.submit_score(game, score=100, level=1, time_played=12.5)
            manager.submit_score(game, score=300, level=3, time_played=40.1)

            self.assertEqual(manager.get_score(game), 300)
            runs = manager.get_runs(game)
            self.assertEqual(len(runs), 2)
            self.assertEqual(runs[0]["score"], 300)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.base import BaseGame
from pocket_games.ui.highscore_screen import HighScoreScreen


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type("MockHighScores", (), {"scores": {"Neon Dash": 500}})()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class DummyGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Dummy Game")


class TestUIScreens(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_highscore_screen_scroll_step(self) -> None:
        engine = MockEngine()
        screen = HighScoreScreen(engine)
        self.assertEqual(screen.scroll_offset, 0)

        # Simuliere einen Tastendruck nach unten (K_DOWN)
        engine.input.keys_just_pressed.add(pygame.K_DOWN)
        screen.handle_input()

        # Durch einen einzelnen Tastendruck soll offset exakt um 1 steigen
        self.assertEqual(screen.scroll_offset, 1)

    def test_game_finished_state(self) -> None:
        engine = MockEngine()
        game = DummyGame(engine)
        game.showing_intro = False

        # Setze Spiel auf gewonnen ("Game Finished")
        game.game_won = True
        surface = pygame.Surface((320, 240))

        # Prüfen, ob render_game_finished fehlerfrei durchläuft
        try:
            game.render(surface)
        except Exception as e:  # noqa: BLE001
            self.fail(f"render_game_finished raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()

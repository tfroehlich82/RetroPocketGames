from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.settings import SETTINGS_FILE, Settings
from pocket_games.games.base import GAME_METADATA
from pocket_games.ui.highscore_screen import HighScoreScreen


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = type("MockInput", (), {
            "mouse_clicked": False,
            "is_back_pressed": False,
            "is_key_just_pressed": lambda self, key: False,
            "is_key_down": lambda self, key: False,
        })()
        self.settings = Settings()

        class MockHighScores:
            def __init__(self):
                self.scores = {"Pixel Drop": 1250, "Neon Dash": 850, "Byte Hopper": 420}

        self.highscores = MockHighScores()

        class MockAudio:
            def play(self, s):
                pass

            def set_volume(self, v):
                pass

        self.audio = MockAudio()


class TestSettingsAndHighScores(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    def setUp(self) -> None:
        # Vor jedem Test temporäre Einstellungsdatei bereinigen
        if SETTINGS_FILE.exists():
            SETTINGS_FILE.unlink()

    def tearDown(self) -> None:
        # Nach Test aufräumen
        if SETTINGS_FILE.exists():
            SETTINGS_FILE.unlink()

    def test_settings_defaults(self) -> None:
        settings = Settings()
        self.assertTrue(settings.sound_enabled)
        self.assertEqual(settings.master_volume, 0.6)
        self.assertTrue(settings.fullscreen)
        self.assertEqual(settings.language, "English")

    def test_settings_save_and_load(self) -> None:
        settings = Settings()
        settings.sound_enabled = False
        settings.master_volume = 0.3
        settings.fullscreen = False
        settings.language = "Deutsch"
        settings.save()

        # Neue Instanz laden und Werte prüfen
        loaded_settings = Settings()
        self.assertFalse(loaded_settings.sound_enabled)
        self.assertEqual(loaded_settings.master_volume, 0.3)
        self.assertFalse(loaded_settings.fullscreen)
        self.assertEqual(loaded_settings.language, "Deutsch")

    def test_highscore_screen_game_order(self) -> None:
        engine = MockEngine()
        screen = HighScoreScreen(engine)

        self.assertTrue(screen.active)
        self.assertEqual(screen.scroll_offset, 0)

        # Überprüfen, ob exakt alle 20 Spiele in derselben Reihenfolge wie im Menü vorhanden sind
        game_keys = list(GAME_METADATA.keys())
        self.assertEqual(len(game_keys), 22)
        self.assertEqual(game_keys[0], "Pixel Drop")
        self.assertEqual(game_keys[1], "Circuit Breaker")
        self.assertEqual(game_keys[-1], "Pixel Platformer")

    def test_highscore_screen_rendering(self) -> None:
        engine = MockEngine()
        screen = HighScoreScreen(engine)

        # Testen, ob das Rendern ohne Exceptions durchläuft (inklusive Scrolling und Highscores)
        surface = pygame.Surface((320, 240))
        try:
            screen.render(surface)
        except Exception as e:  # noqa: BLE001
            self.fail(f"HighScoreScreen.render raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()

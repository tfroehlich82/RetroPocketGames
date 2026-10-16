from __future__ import annotations

import unittest

from pocket_games.core.settings import SETTINGS_FILE, Settings


class TestSettings(unittest.TestCase):
    def setUp(self) -> None:
        # Vor jedem Test eventuelle alte Test-Dateien löschen
        if SETTINGS_FILE.exists():
            SETTINGS_FILE.unlink()

    def tearDown(self) -> None:
        # Nach dem Test aufräumen
        if SETTINGS_FILE.exists():
            SETTINGS_FILE.unlink()

    def test_default_settings(self) -> None:
        settings = Settings()
        self.assertTrue(settings.sound_enabled)
        self.assertEqual(settings.master_volume, 0.8)
        self.assertTrue(settings.fullscreen)

    def test_save_and_load(self) -> None:
        settings = Settings()
        settings.sound_enabled = False
        settings.master_volume = 0.5
        settings.fullscreen = False
        settings.save()

        # Instanz neu laden, um Persistenz zu prüfen
        new_settings = Settings()
        self.assertFalse(new_settings.sound_enabled)
        self.assertEqual(new_settings.master_volume, 0.5)
        self.assertFalse(new_settings.fullscreen)

if __name__ == "__main__":
    unittest.main()

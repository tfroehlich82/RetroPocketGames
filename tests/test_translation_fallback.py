from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from pocket_games.games import base


class TestTranslationFallback(unittest.TestCase):
    def setUp(self) -> None:
        self.translations = {
            "English": {"only_english": "English text", "both": "English both"},
            "German": {"both": "Deutsch beides"},
        }

    def _engine(self, language: str) -> SimpleNamespace:
        return SimpleNamespace(settings=SimpleNamespace(language=language))

    def test_returns_selected_language_when_key_exists(self) -> None:
        with patch.object(base, "TRANSLATIONS", self.translations):
            self.assertEqual(base.t(self._engine("German"), "both"), "Deutsch beides")

    def test_falls_back_to_english_when_key_missing_in_language(self) -> None:
        with patch.object(base, "TRANSLATIONS", self.translations):
            self.assertEqual(base.t(self._engine("German"), "only_english"), "English text")

    def test_returns_key_when_missing_in_all_languages(self) -> None:
        with patch.object(base, "TRANSLATIONS", self.translations):
            self.assertEqual(base.t(self._engine("German"), "unknown_key"), "unknown_key")

    def test_unknown_language_uses_english(self) -> None:
        with patch.object(base, "TRANSLATIONS", self.translations):
            self.assertEqual(base.t(self._engine("Klingon"), "both"), "English both")

    def test_engine_without_settings_uses_english(self) -> None:
        with patch.object(base, "TRANSLATIONS", self.translations):
            self.assertEqual(base.t(SimpleNamespace(), "both"), "English both")


if __name__ == "__main__":
    unittest.main()

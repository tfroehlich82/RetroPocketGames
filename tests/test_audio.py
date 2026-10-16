from __future__ import annotations

import os
import unittest

# Dummy-Treiber für Headless-Testumgebungen setzen
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

from pocket_games.core.audio import AudioManager


class TestAudio(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    def test_audio_manager_init(self) -> None:
        audio = AudioManager(enabled=True, volume=0.6)
        self.assertTrue(audio.enabled)
        self.assertEqual(audio.volume, 0.6)

    def test_tone_generation(self) -> None:
        audio = AudioManager(enabled=True)
        sound = audio._create_tone(440, 0.05, "square")
        self.assertIsNotNone(sound)

        sine_sound = audio._create_tone(880, 0.05, "sine")
        self.assertIsNotNone(sine_sound)

if __name__ == "__main__":
    unittest.main()

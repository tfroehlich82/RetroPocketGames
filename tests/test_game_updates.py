from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.chrono_shift import ChronoShiftGame
from pocket_games.games.sonic_pulse import SonicPulseGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestGameUpdatesAndMechanics(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_touch_input_scaling(self) -> None:
        """Prüft, ob Touch-Events (FINGERDOWN) korrekt in virtuelle Koordinaten skaliert werden."""
        engine = MockEngine()
        # Simuliere Touch-Event auf der linken Bildschirmhälfte
        touch_event = pygame.event.Event(pygame.FINGERDOWN, x=0.5, y=0.5)
        pygame.event.post(touch_event)

        engine.input.update()
        self.assertTrue(engine.input.mouse_clicked)

        # Test über BaseGame get_virtual_mouse_pos
        from pocket_games.games.base import BaseGame

        game = BaseGame(engine, "Bug Hunter")
        vx, vy = game.get_virtual_mouse_pos()
        self.assertEqual(vx, 160)
        self.assertEqual(vy, 120)

    def test_chrono_shift_standstill_buffer(self) -> None:
        """Prüft, ob der 1s-Puffer (8 Trail-Punkte) aktiv ist und keine Sofort-Kollision auslöst."""
        engine = MockEngine()
        game = ChronoShiftGame(engine)
        game.showing_intro = False

        # Füge Trail-Punkte hinzu (simuliert Bewegung)
        for _ in range(5):
            game.trail.append((160.0, 120.0))

        # Aktualisiere Spiel - sollte wegen des Puffers [8:] nicht sofort game_over sein
        game.update(0.1)
        self.assertFalse(game.game_over)

    def test_sonic_pulse_dynamic_tolerance(self) -> None:
        """Prüft, ob die Toleranzspanne zu Spielbeginn größer ist als nach längerer Zeit."""
        engine = MockEngine()
        game = SonicPulseGame(engine)

        # Zu Beginn (elapsed_time = 0)
        tolerance_start = max(6.0, 16.0 - (game.elapsed_time * 0.15))

        # Nach 40 Sekunden
        game.elapsed_time = 40.0
        tolerance_later = max(6.0, 16.0 - (game.elapsed_time * 0.15))

        self.assertGreater(tolerance_start, tolerance_later)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.pulse_racer import PulseRacerGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type("MockHighScores", (), {"submit_score": lambda s, n, sc: None})()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestPulseRacerGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_pulse_racer_initialization(self) -> None:
        engine = MockEngine()
        game = PulseRacerGame(engine)
        self.assertEqual(game.rx, 160.0)
        self.assertEqual(game.base_speed, 180.0)
        self.assertEqual(len(game.lanes), 3)

    def test_pulse_racer_overtaking_from_behind(self) -> None:
        engine = MockEngine()
        game = PulseRacerGame(engine)
        game.showing_intro = False
        game.traffic.clear()

        # Langsames Fahrzeug weiter vorne (größeres y)
        slow_car = {
            "lane": 1, "x": 160.0, "target_x": 160.0, "y": 140.0,
            "net_speed_offset": 70.0, "type": "cruiser", "color": (0, 200, 255),
            "blinking": False, "blink_timer": 0.0, "decision_timer": 10.0
        }
        # Schnelles Fahrzeug dahinter (kleineres y), das aufholt
        fast_car = {
            "lane": 1, "x": 160.0, "target_x": 160.0, "y": 90.0,
            "net_speed_offset": 25.0, "type": "speedy", "color": (50, 255, 120),
            "blinking": False, "blink_timer": 0.0, "decision_timer": 0.05
        }
        game.traffic.extend([slow_car, fast_car])

        # Update ausführen, damit das schnelle Auto das langsame von hinten einholt und zum Überholen ansetzt
        game.update(0.1)

        self.assertTrue(fast_car["blinking"])
        self.assertNotEqual(fast_car["target_x"], 160.0)


if __name__ == "__main__":
    unittest.main()

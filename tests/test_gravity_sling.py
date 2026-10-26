from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.gravity_sling import GravitySlingGame


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = type(
            "MockHighScores", (), {"submit_score": lambda s, n, sc: None}
        )()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestGravitySling(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_gravity_sling_initialization(self) -> None:
        engine = MockEngine()
        game = GravitySlingGame(engine)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.vx, 0.0)
        self.assertEqual(game.vy, 0.0)
        self.assertTrue(len(game.planets) > 0)

    def test_gravity_sling_vector_thrust(self) -> None:
        engine = MockEngine()
        game = GravitySlingGame(engine)
        game.showing_intro = False

        # Simuliere Druck nach rechts
        engine.input.is_right_pressed = lambda: True
        game.handle_input()
        game.update(0.016)

        self.assertGreater(game.vx, 0.0)

    def test_levels_are_reproducible(self) -> None:
        first = GravitySlingGame(MockEngine())
        second = GravitySlingGame(MockEngine())
        for level in (1, 2, 3):
            first.level = second.level = level
            first._setup_level()
            second._setup_level()
            self.assertEqual(first.planets, second.planets)
            self.assertEqual(first.crystals, second.crystals)

    def test_crystals_respawn_at_seeded_positions(self) -> None:
        game = GravitySlingGame(MockEngine())
        game.crystals_collected = 1
        game._spawn_crystal()
        first = list(game.crystals)
        game._spawn_crystal()
        self.assertEqual(first, game.crystals)

    def test_planets_vary_in_size_and_gravity(self) -> None:
        game = GravitySlingGame(MockEngine())
        game.level = 3
        game._setup_level()
        radii = {p["r"] for p in game.planets}
        strengths = {p["strength"] for p in game.planets}
        self.assertGreater(len(radii), 1)
        self.assertGreater(len(strengths), 1)

    def test_render_all_levels_without_error(self) -> None:
        game = GravitySlingGame(MockEngine())
        game.showing_intro = False
        surface = pygame.Surface((320, 240))
        for level in (1, 2, 3):
            game.level = level
            game._setup_level()
            game.thrust_x, game.thrust_y = 1.0, 0.0
            game.particles = []
            game._burst(100.0, 100.0, (255, 0, 0), 5)
            game.render(surface)

    def test_crystal_pickup_advances_level(self) -> None:
        game = GravitySlingGame(MockEngine())
        game.showing_intro = False
        game.crystals_collected = 3
        c = game.crystals[0]
        game.px, game.py = float(c["x"]), float(c["y"])
        game.planets = []
        game.update(0.016)
        self.assertEqual(game.level, 2)
        self.assertEqual(game.crystals_collected, 0)


if __name__ == "__main__":
    unittest.main()

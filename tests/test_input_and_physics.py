from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.core.physics import (
    apply_gravity,
    calculate_orbital_pull,
    check_circle_collision,
    clamp,
    handle_paddle_collision,
    update_velocity_damping,
)


class MockPaddle:
    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.rect = pygame.Rect(x, y, w, h)


class MockBall:
    def __init__(self, x: float, y: float, radius: int, vx: float, vy: float) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = vx
        self.vy = vy
        self.rect = pygame.Rect(int(x - radius), int(y - radius), radius * 2, radius * 2)

    def update_rect(self) -> None:
        self.rect.center = (int(self.x), int(self.y))


class TestInputAndPhysics(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_centralized_input_helpers(self) -> None:
        """Prüft die zentralisierten Input-Methoden des InputManagers."""
        inp = InputManager()
        # Simuliere Klick / Taste
        inp.keys_just_pressed.add(pygame.K_SPACE)
        self.assertTrue(inp.is_action_just_pressed())

    def test_physics_clamp_and_gravity(self) -> None:
        self.assertEqual(clamp(15.0, 0.0, 10.0), 10.0)
        self.assertAlmostEqual(apply_gravity(100.0, 500.0, 0.016), 108.0)

    def test_physics_circle_collision(self) -> None:
        self.assertTrue(check_circle_collision(0.0, 0.0, 10.0, 12.0, 0.0, 5.0))
        self.assertFalse(check_circle_collision(0.0, 0.0, 5.0, 30.0, 0.0, 5.0))

    def test_physics_velocity_damping(self) -> None:
        vx, vy = update_velocity_damping(100.0, -200.0, 0.9)
        self.assertAlmostEqual(vx, 90.0)
        self.assertAlmostEqual(vy, -180.0)

    def test_physics_orbital_pull(self) -> None:
        fx, fy = calculate_orbital_pull(0.0, 0.0, 50.0, 0.0, 10000.0)
        self.assertGreater(fx, 0.0)
        self.assertAlmostEqual(fy, 0.0)

    def test_physics_paddle_collision(self) -> None:
        paddle = MockPaddle(100, 200, 50, 10)
        ball = MockBall(125.0, 201.0, 5, 0.0, 100.0)
        handle_paddle_collision(ball, paddle)
        self.assertLess(ball.vy, 0.0)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

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
        self.rect = pygame.Rect(
            int(x - radius), int(y - radius), radius * 2, radius * 2
        )

    def update_rect(self) -> None:
        self.rect.center = (int(self.x), int(self.y))


class TestPhysicsEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    def test_clamp(self) -> None:
        self.assertEqual(clamp(5.0, 0.0, 10.0), 5.0)
        self.assertEqual(clamp(-5.0, 0.0, 10.0), 0.0)
        self.assertEqual(clamp(15.0, 0.0, 10.0), 10.0)

    def test_check_circle_collision(self) -> None:
        self.assertTrue(check_circle_collision(0.0, 0.0, 10.0, 15.0, 0.0, 10.0))
        self.assertTrue(check_circle_collision(0.0, 0.0, 10.0, 20.0, 0.0, 10.0))
        self.assertFalse(check_circle_collision(0.0, 0.0, 10.0, 25.0, 0.0, 10.0))

    def test_apply_gravity(self) -> None:
        vy = 100.0
        gravity = 500.0
        dt = 0.016
        new_vy = apply_gravity(vy, gravity, dt)
        self.assertAlmostEqual(new_vy, 108.0)

    def test_update_velocity_damping(self) -> None:
        vx, vy = 100.0, -200.0
        damping = 0.94
        nvx, nvy = update_velocity_damping(vx, vy, damping)
        self.assertAlmostEqual(nvx, 94.0)
        self.assertAlmostEqual(nvy, -188.0)

    def test_calculate_orbital_pull(self) -> None:
        fx, fy = calculate_orbital_pull(0.0, 0.0, 100.0, 0.0, 10000.0)
        self.assertGreater(fx, 0.0)
        self.assertAlmostEqual(fy, 0.0)

    def test_handle_paddle_collision_horizontal(self) -> None:
        paddle = MockPaddle(100, 200, 60, 10)
        ball = MockBall(130.0, 201.0, 5, 50.0, 120.0)

        handle_paddle_collision(ball, paddle, paddle_vy=0.0)
        self.assertLess(ball.vy, 0.0)

    def test_handle_paddle_collision_vertical(self) -> None:
        paddle = MockPaddle(50, 100, 10, 60)
        ball = MockBall(51.0, 130.0, 5, -100.0, 20.0)

        handle_paddle_collision(ball, paddle, paddle_vy=0.0)
        self.assertGreater(ball.vx, 0.0)


if __name__ == "__main__":
    unittest.main()

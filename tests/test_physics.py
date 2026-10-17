from __future__ import annotations

import unittest

import pygame

from pocket_games.core.physics import handle_paddle_collision


class MockPaddle:
    def __init__(self, y: int, height: int) -> None:
        self.rect = pygame.Rect(15, y - height // 2, 8, height)


class MockBall:
    def __init__(
        self, x: float, y: float, vx: float, vy: float, radius: int = 5
    ) -> None:
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


class TestPhysics(unittest.TestCase):
    def test_paddle_collision_physics(self) -> None:
        # Paddle von Y: 80 bis 120 (Zentrum bei 100, Höhe 40)
        paddle = MockPaddle(100, 40)
        # Ball trifft genau das Zentrum des Paddles (Offset = 0.0)
        ball = MockBall(19.0, 100.0, -100.0, 0.0)

        initial_speed = (ball.vx**2 + ball.vy**2) ** 0.5

        handle_paddle_collision(ball, paddle)

        # Die Richtung auf der X-Achse muss umgekehrt worden sein
        self.assertGreater(ball.vx, 0)

        new_speed = (ball.vx**2 + ball.vy**2) ** 0.5
        # Erwartet: 5% Grund-Beschleunigung bei Offset 0 (Faktor 1.05 gemäß Gummiball-Physik)
        self.assertAlmostEqual(new_speed, initial_speed * 1.05, places=2)


if __name__ == "__main__":
    unittest.main()

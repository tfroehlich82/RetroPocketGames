from __future__ import annotations

import pygame

from pocket_games.core.physics import handle_paddle_collision


class Paddle:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.rect = pygame.Rect(x, y, width, height)


class Ball:
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


class BitBlasterGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.px = 160.0

        self.paddle = Paddle(int(self.px) - 25, 215, 50, 8)
        self.ball = Ball(160.0, 120.0, 5, 100.0, -100.0)

        self.blocks = [
            {"x": c * 38 + 15, "y": r * 15 + 25, "alive": True}
            for r in range(3)
            for c in range(7)
        ]

    def handle_input(self) -> None:
        inp = self.engine.input
        if (
            inp.is_key_pressed(pygame.K_ESCAPE)
            or inp.is_key_pressed(pygame.K_BACKSPACE)
            or self.engine.input.is_back_pressed()
        ):
            self.active = False
        if inp.is_key_down(pygame.K_LEFT):
            self.px = max(25, self.px - 5)
        if inp.is_key_down(pygame.K_RIGHT):
            self.px = min(295, self.px + 5)
        if inp.mouse_clicked:
            self.px = max(25, min(295, inp.mouse_pos[0]))

        self.paddle.rect.x = int(self.px) - 25

    def update(self, dt: float) -> None:
        self.ball.x += self.ball.vx * dt
        self.ball.y += self.ball.vy * dt
        self.ball.update_rect()

        if self.ball.rect.left <= 10:
            self.ball.rect.left = 10
            self.ball.x = self.ball.rect.centerx
            self.ball.vx *= -1
        elif self.ball.rect.right >= 310:
            self.ball.rect.right = 310
            self.ball.x = self.ball.rect.centerx
            self.ball.vx *= -1

        if self.ball.rect.top <= 10:
            self.ball.rect.top = 10
            self.ball.y = self.ball.rect.centery
            self.ball.vy *= -1

        # Paddle-Kollision mit Gummiball-Physik
        if self.ball.rect.colliderect(self.paddle.rect):
            handle_paddle_collision(self.ball, self.paddle)
            self.ball.x, self.ball.y = self.ball.rect.center

        # Block-Kollision
        for blk in self.blocks:
            if blk["alive"]:
                blk_rect = pygame.Rect(blk["x"], blk["y"], 34, 12)
                if self.ball.rect.colliderect(blk_rect):
                    blk["alive"] = False
                    self.ball.vy *= -1
                    self.score += 15
                    self.engine.highscores.submit_score("Bit Blaster", self.score)

        if self.ball.rect.top > 240:
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 10, 25))
        pygame.draw.rect(surface, (0, 200, 255), self.paddle.rect, border_radius=3)
        pygame.draw.circle(surface, (255, 255, 0), self.ball.rect.center, 5)
        for blk in self.blocks:
            if blk["alive"]:
                pygame.draw.rect(
                    surface,
                    (255, 100, 200),
                    (blk["x"], blk["y"], 34, 12),
                    border_radius=2,
                )
        sc = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))

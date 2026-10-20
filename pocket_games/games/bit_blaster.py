# ==========================================
# BIT BLASTER (Enhanced Brick Breaker)
# ==========================================
from __future__ import annotations

import pygame

from pocket_games.core.physics import clamp, handle_paddle_collision
from pocket_games.games.base import BaseGame


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
        self.rect = pygame.Rect(int(x - radius), int(y - radius), radius * 2, radius * 2)

    def update_rect(self) -> None:
        self.rect.center = (int(self.x), int(self.y))


class BitBlasterGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Bit Blaster")
        self.px = 160.0
        self.paddle = Paddle(int(self.px) - 25, 215, 50, 8)
        self.ball = Ball(160.0, 120.0, 5, 120.0, -120.0)
        self.blocks = []
        self._init_blocks()

    def _init_blocks(self) -> None:
        colors = [(255, 80, 80), (255, 180, 0), (0, 220, 255), (180, 100, 255)]
        for r in range(4):
            for c in range(7):
                self.blocks.append({
                    "rect": pygame.Rect(c * 42 + 13, r * 16 + 30, 38, 12),
                    "color": colors[r],
                    "alive": True
                })

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.is_left_pressed():
            self.px = max(28, self.px - 6)
        if inp.is_right_pressed():
            self.px = min(292, self.px + 6)
        if inp.mouse_clicked:
            vx, _vy = self.get_virtual_mouse_pos()
            self.px = clamp(vx, 28.0, 292.0)

        self.paddle.rect.x = int(self.px) - 25

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        speed_mod = min(1.5, 1.0 + (self.elapsed_time * 0.005))
        self.ball.x += self.ball.vx * dt * speed_mod
        self.ball.y += self.ball.vy * dt * speed_mod
        self.ball.update_rect()

        if self.ball.rect.left <= 5:
            self.ball.rect.left = 5
            self.ball.vx = abs(self.ball.vx)
            self.play_sound("bounce")
        elif self.ball.rect.right >= 315:
            self.ball.rect.right = 315
            self.ball.vx = -abs(self.ball.vx)
            self.play_sound("bounce")

        if self.ball.rect.top <= 5:
            self.ball.rect.top = 5
            self.ball.vy = abs(self.ball.vy)
            self.play_sound("bounce")

        if self.ball.rect.colliderect(self.paddle.rect):
            handle_paddle_collision(self.ball, self.paddle)
            self.ball.x, self.ball.y = float(self.ball.rect.centerx), float(self.ball.rect.centery)
            self.play_sound("hit")

        all_cleared = True
        for blk in self.blocks:
            if blk["alive"]:
                all_cleared = False
                if self.ball.rect.colliderect(blk["rect"]):
                    blk["alive"] = False
                    self.ball.vy *= -1
                    self.add_score(25)
                    self.play_sound("score")
                    break

        if all_cleared:
            self._init_blocks()

        if self.ball.rect.top > 240:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 10, 25))
        pygame.draw.rect(surface, (0, 200, 255), self.paddle.rect, border_radius=3)
        pygame.draw.circle(surface, (255, 255, 0), self.ball.rect.center, 5)
        for blk in self.blocks:
            if blk["alive"]:
                pygame.draw.rect(surface, blk["color"], blk["rect"], border_radius=2)
        self.render_ui(surface)

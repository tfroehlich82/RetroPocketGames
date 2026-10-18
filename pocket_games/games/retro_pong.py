# ==========================================
# RETRO PONG
# ==========================================
from __future__ import annotations

import pygame

from pocket_games.core.physics import handle_paddle_collision
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
        self.rect = pygame.Rect(
            int(x - radius), int(y - radius), radius * 2, radius * 2
        )

    def update_rect(self) -> None:
        self.rect.center = (int(self.x), int(self.y))


class RetroPongGame(BaseGame):
    """Refactored Retro Pong 2077 using BaseGame architecture."""

    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Retro Pong 2077")
        self.paddle_y = 120.0
        self.paddle_prev_y = 120.0
        self.paddle = Paddle(15, int(self.paddle_y) - 20, 8, 40)
        self.ball = Ball(160.0, 120.0, 6, 130.0, 90.0)

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active:
            return

        inp = self.engine.input
        self.paddle_prev_y = self.paddle_y

        if inp.is_key_down(pygame.K_UP) or inp.is_key_down(pygame.K_w):
            self.paddle_y = max(40.0, self.paddle_y - 4.5)
        if inp.is_key_down(pygame.K_DOWN) or inp.is_key_down(pygame.K_s):
            self.paddle_y = min(210.0, self.paddle_y + 4.5)

        if inp.mouse_clicked:
            _vx, vy = self.get_virtual_mouse_pos()
            self.paddle_y = max(40.0, min(210.0, float(vy)))

        self.paddle.rect.y = int(self.paddle_y) - 20

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        paddle_vy = (self.paddle_y - self.paddle_prev_y) / max(0.001, dt)

        self.ball.x += self.ball.vx * dt
        self.ball.y += self.ball.vy * dt
        self.ball.update_rect()

        # Wall Bounces
        if self.ball.rect.top <= 25:
            self.ball.rect.top = 25
            self.ball.y = self.ball.rect.centery
            self.ball.vy *= -1
            self.engine.audio.play("select")
        elif self.ball.rect.bottom >= 235:
            self.ball.rect.bottom = 235
            self.ball.y = self.ball.rect.centery
            self.ball.vy *= -1
            self.engine.audio.play("select")

        if self.ball.rect.right >= 315:
            self.ball.rect.right = 315
            self.ball.x = self.ball.rect.centerx
            self.ball.vx *= -1
            self.engine.audio.play("select")

        # Paddle Collision with Gummiball Impulse Transfer
        if self.ball.rect.colliderect(self.paddle.rect):
            handle_paddle_collision(self.ball, self.paddle, paddle_vy=paddle_vy)
            self.ball.x, self.ball.y = self.ball.rect.center
            self.add_score(10)
            self.engine.audio.play("confirm")

        if self.ball.rect.left < 0:
            self.game_over = True
            self.engine.audio.play("hit")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 10, 18))

        # Center Line
        pygame.draw.line(surface, (30, 30, 50), (160, 20), (160, 240), 2)

        # Paddle & Ball
        pygame.draw.rect(surface, (0, 255, 200), self.paddle.rect, border_radius=3)
        pygame.draw.circle(surface, (255, 200, 0), self.ball.rect.center, 6)

        if self.game_over:
            go = self.title_font.render("SYSTEM OUT", True, (255, 50, 50))
            surface.blit(go, (160 - go.get_width() // 2, 110))

        self.render_ui(surface)

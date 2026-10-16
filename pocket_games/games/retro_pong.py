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


class RetroPongGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)

        self.paddle_y = 100.0
        self.paddle = Paddle(15, int(self.paddle_y) - 20, 8, 40)
        self.ball = Ball(160.0, 120.0, 6, 120.0, 90.0)

    def handle_input(self) -> None:
        inp = self.engine.input
        if (
            inp.is_key_pressed(pygame.K_ESCAPE)
            or inp.is_key_pressed(pygame.K_BACKSPACE)
            or self.engine.input.is_back_pressed()
        ):
            self.active = False
        if inp.is_key_down(pygame.K_UP):
            self.paddle_y = max(20, self.paddle_y - 5)
        if inp.is_key_down(pygame.K_DOWN):
            self.paddle_y = min(220, self.paddle_y + 5)
        if inp.mouse_clicked:
            self.paddle_y = max(20, min(220, inp.mouse_pos[1]))

        self.paddle.rect.y = int(self.paddle_y) - 20

    def update(self, dt: float) -> None:
        self.ball.x += self.ball.vx * dt
        self.ball.y += self.ball.vy * dt
        self.ball.update_rect()

        if self.ball.rect.top <= 10:
            self.ball.rect.top = 10
            self.ball.y = self.ball.rect.centery
            self.ball.vy *= -1
        elif self.ball.rect.bottom >= 230:
            self.ball.rect.bottom = 230
            self.ball.y = self.ball.rect.centery
            self.ball.vy *= -1

        if self.ball.rect.right >= 310:
            self.ball.rect.right = 310
            self.ball.x = self.ball.rect.centerx
            self.ball.vx *= -1

        # Paddle-Kollision mit Gummiball-Physik
        if self.ball.rect.colliderect(self.paddle.rect):
            handle_paddle_collision(self.ball, self.paddle)
            self.ball.x, self.ball.y = self.ball.rect.center
            self.score += 10
            self.engine.highscores.submit_score("Retro Pong 2077", self.score)

        if self.ball.rect.left < 0:
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 10, 15))
        pygame.draw.rect(surface, (255, 255, 255), self.paddle.rect)
        pygame.draw.circle(surface, (0, 255, 200), self.ball.rect.center, 6)
        sc = self.font.render(f"Pong Score: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))

from __future__ import annotations
import pygame

class RetroPongGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.paddle_y = 100.0
        self.ball_x, self.ball_y = 160.0, 120.0
        self.ball_vx, self.ball_vy = 120.0, 90.0

    def handle_input(self) -> None:
        inp = self.engine.input
        if inp.is_key_pressed(pygame.K_ESCAPE):
            self.active = False
        if inp.is_key_down(pygame.K_UP): self.paddle_y = max(15, self.paddle_y - 5)
        if inp.is_key_down(pygame.K_DOWN): self.paddle_y = min(225, self.paddle_y + 5)
        if inp.mouse_clicked:
            self.paddle_y = inp.mouse_pos[1]

    def update(self, dt: float) -> None:
        self.ball_x += self.ball_vx * dt
        self.ball_y += self.ball_vy * dt

        if self.ball_y <= 10 or self.ball_y >= 230:
            self.ball_vy *= -1
        if self.ball_x >= 310:
            self.ball_vx *= -1

        # Paddle collision
        if self.ball_x <= 25 and abs(self.ball_y - self.paddle_y) < 20:
            self.ball_vx *= -1
            self.score += 10
            self.engine.highscores.submit_score("Retro Pong 2077", self.score)

        if self.ball_x < 0:
            self.active = False  # Game over

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 10, 15))
        pygame.draw.rect(surface, (255, 255, 255), (15, int(self.paddle_y) - 20, 8, 40))
        pygame.draw.circle(surface, (0, 255, 200), (int(self.ball_x), int(self.ball_y)), 6)
        sc = self.font.render(f"Pong Score: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))

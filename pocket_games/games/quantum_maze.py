from __future__ import annotations

import pygame


class QuantumMazeGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.x, self.y = 30.0, 30.0
        self.target = {"x": 280, "y": 200}
        self.walls = [
            pygame.Rect(80, 0, 15, 180),
            pygame.Rect(160, 60, 15, 180),
            pygame.Rect(230, 0, 15, 150),
        ]

    def handle_input(self) -> None:
        inp = self.engine.input
        if (
            inp.is_key_pressed(pygame.K_ESCAPE)
            or inp.is_key_pressed(pygame.K_BACKSPACE)
            or self.engine.input.is_back_pressed()
        ):
            self.active = False
        dx, dy = 0, 0
        speed = 80
        dt = 0.02
        if inp.is_key_down(pygame.K_LEFT): dx -= speed * dt
        if inp.is_key_down(pygame.K_RIGHT): dx += speed * dt
        if inp.is_key_down(pygame.K_UP): dy -= speed * dt
        if inp.is_key_down(pygame.K_DOWN): dy += speed * dt

        self.x += dx
        self.y += dy

    def update(self, dt: float) -> None:
        player_rect = pygame.Rect(self.x - 5, self.y - 5, 10, 10)
        for w in self.walls:
            if player_rect.colliderect(w):
                self.x, self.y = 30.0, 30.0  # Reset on wall hit

        target_rect = pygame.Rect(self.target["x"] - 8, self.target["y"] - 8, 16, 16)
        if player_rect.colliderect(target_rect):
            self.score += 100
            self.engine.highscores.submit_score("Quantum Maze", self.score)
            self.target["x"] = 50 + (self.score * 30) % 220
            self.target["y"] = 50 + (self.score * 50) % 140

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((20, 10, 20))
        for w in self.walls:
            pygame.draw.rect(surface, (100, 50, 150), w)

        pygame.draw.rect(surface, (0, 255, 100), (self.target["x"] - 8, self.target["y"] - 8, 16, 16))
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x), int(self.y)), 6)
        sc = self.font.render(f"Maze Score: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))

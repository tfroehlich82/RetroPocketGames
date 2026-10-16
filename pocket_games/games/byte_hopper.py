from __future__ import annotations
import pygame

class ByteHopperGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.px, self.py = 160.0, 180.0
        self.vx, self.vy = 0.0, 0.0
        self.platforms = [{"x": 100, "y": 200}, {"x": 40, "y": 140}, {"x": 200, "y": 90}, {"x": 120, "y": 40}]

    def handle_input(self) -> None:
        inp = self.engine.input
        if inp.is_key_pressed(pygame.K_ESCAPE):
            self.active = False
        self.vx = 0
        if inp.is_key_down(pygame.K_LEFT):
            self.vx = -120
        if inp.is_key_down(pygame.K_RIGHT):
            self.vx = 120
        if (inp.is_key_pressed(pygame.K_SPACE) or inp.is_key_pressed(pygame.K_UP) or inp.mouse_clicked) and abs(self.vy) < 1.0:
            self.vy = -220

    def update(self, dt: float) -> None:
        self.py += self.vy * dt
        self.px += self.vx * dt
        self.vy += 500 * dt  # Gravity

        # Floor collision
        if self.py > 200:
            self.py = 200
            self.vy = 0

        # Platform collision
        for p in self.platforms:
            p_rect = pygame.Rect(p["x"], p["y"], 60, 8)
            player_rect = pygame.Rect(self.px - 6, self.py - 12, 12, 12)
            if player_rect.colliderect(p_rect) and self.vy > 0:
                self.vy = -250
                self.score += 20
                self.engine.highscores.submit_score("Byte Hopper", self.score)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 20, 35))
        for p in self.platforms:
            pygame.draw.rect(surface, (0, 180, 255), (p["x"], p["y"], 60, 8), border_radius=2)

        pygame.draw.rect(surface, (255, 200, 0), (int(self.px) - 6, int(self.py) - 12, 12, 12), border_radius=2)
        sc = self.font.render(f"Bytes: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))

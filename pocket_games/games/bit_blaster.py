from __future__ import annotations
import pygame

class BitBlasterGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.px = 160.0
        self.bx, self.by = 160.0, 120.0
        self.bvx, self.bvy = 100.0, -100.0
        self.blocks = [{"x": c * 38 + 15, "y": r * 15 + 25, "alive": True} for r in range(3) for c in range(7)]

    def handle_input(self) -> None:
        inp = self.engine.input
        if inp.is_key_pressed(pygame.K_ESCAPE):
            self.active = False
        if inp.is_key_down(pygame.K_LEFT): self.px = max(25, self.px - 5)
        if inp.is_key_down(pygame.K_RIGHT): self.px = min(295, self.px + 5)
        if inp.mouse_clicked:
            self.px = inp.mouse_pos[0]

    def update(self, dt: float) -> None:
        self.bx += self.bvx * dt
        self.by += self.bvy * dt

        if self.bx <= 10 or self.bx >= 310: self.bvx *= -1
        if self.by <= 10: self.bvy *= -1

        # Paddle collision
        if abs(self.bx - self.px) < 25 and abs(self.by - 215) < 8:
            self.bvy *= -1

        # Block collision
        for blk in self.blocks:
            if blk["alive"]:
                if abs(self.bx - (blk["x"] + 18)) < 20 and abs(self.by - (blk["y"] + 6)) < 10:
                    blk["alive"] = False
                    self.bvy *= -1
                    self.score += 15
                    self.engine.highscores.submit_score("Bit Blaster", self.score)

        if self.by > 240:
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 10, 25))
        pygame.draw.rect(surface, (0, 200, 255), (int(self.px) - 25, 215, 50, 8), border_radius=3)
        pygame.draw.circle(surface, (255, 255, 0), (int(self.bx), int(self.by)), 5)
        for blk in self.blocks:
            if blk["alive"]:
                pygame.draw.rect(surface, (255, 100, 200), (blk["x"], blk["y"], 34, 12), border_radius=2)
        sc = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))

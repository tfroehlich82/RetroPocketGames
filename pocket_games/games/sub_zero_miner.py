from __future__ import annotations

import random

import pygame


class SubZeroMinerGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.oxygen = 100.0
        self.font = pygame.font.SysFont(None, 18)
        self.rx, self.ry = 160, 120
        self.gem = {"x": random.randint(30, 290), "y": random.randint(30, 210)}

    def handle_input(self) -> None:
        inp = self.engine.input
        if (
            inp.is_key_pressed(pygame.K_ESCAPE)
            or inp.is_key_pressed(pygame.K_BACKSPACE)
            or self.engine.input.is_back_pressed()
        ):
            self.active = False
        speed = 3
        if inp.is_key_down(pygame.K_LEFT): self.rx = max(10, self.rx - speed)
        if inp.is_key_down(pygame.K_RIGHT): self.rx = min(310, self.rx + speed)
        if inp.is_key_down(pygame.K_UP): self.ry = max(10, self.ry - speed)
        if inp.is_key_down(pygame.K_DOWN): self.ry = min(230, self.ry + speed)

    def update(self, dt: float) -> None:
        self.oxygen -= dt * 8
        if self.oxygen <= 0:
            self.active = False

        if abs(self.rx - self.gem["x"]) < 15 and abs(self.ry - self.gem["y"]) < 15:
            self.score += 50
            self.oxygen = min(100.0, self.oxygen + 20.0)
            self.engine.highscores.submit_score("Sub-Zero Miner", self.score)
            self.gem = {"x": random.randint(30, 290), "y": random.randint(30, 210)}

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 25, 35))
        pygame.draw.circle(surface, (0, 255, 255), (self.gem["x"], self.gem["y"]), 8)
        pygame.draw.rect(surface, (255, 100, 0), (self.rx - 8, self.ry - 8, 16, 16), border_radius=3)

        sc = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        ox_surf = self.font.render(f"O2: {int(self.oxygen)}%", True, (0, 255, 0) if self.oxygen > 30 else (255, 0, 0))
        surface.blit(sc, (10, 10))
        surface.blit(ox_surf, (10, 30))

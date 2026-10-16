from __future5__ import annotations
import random
import pygame

class PulseRacerGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.rx = 160
        self.obstacles = [{"x": random.randint(80, 240), "y": -30}]
        self.timer = 0.0

    def handle_input(self) -> None:
        inp = self.engine.input
        if inp.is_key_pressed(pygame.K_ESCAPE):
            self.active = False
        if inp.is_key_down(pygame.K_LEFT): self.rx = max(70, self.rx - 4)
        if inp.is_key_down(pygame.K_RIGHT): self.rx = min(250, self.rx + 4)

    def update(self, dt: float) -> None:
        self.score += int(dt * 30)
        self.engine.highscores.submit_score("Pulse Racer", self.score)
        self.timer += dt
        if self.timer > 1.0:
            self.timer = 0.0
            self.obstacles.append({"x": random.randint(80, 240), "y": -30})

        for obs in self.obstacles:
            obs["y"] += 160 * dt
            if abs(obs["x"] - self.rx) < 15 and abs(obs["y"] - 190) < 15:
                self.active = False
        self.obstacles = [o for o in self.obstacles if o["y"] < 250]

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((20, 10, 30))
        pygame.draw.line(surface, (100, 50, 150), (60, 0), (60, 240), 2)
        pygame.draw.line(surface, (100, 50, 150), (260, 0), (260, 240), 2)

        pygame.draw.rect(surface, (0, 255, 200), (self.rx - 10, 180, 20, 25), border_radius=4)
        for obs in self.obstacles:
            pygame.draw.rect(surface, (255, 0, 100), (obs["x"] - 12, int(obs["y"]), 24, 12), border_radius=2)

        sc = self.font.render(f"Distance: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))

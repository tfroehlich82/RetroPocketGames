from __future__ import annotations
import random
import pygame

class KernelPanicGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.leaks = [{"x": random.randint(30, 290), "y": -20, "speed": random.randint(40, 80)}]
        self.spawn_timer = 0.0

    def handle_input(self) -> None:
        inp = self.engine.input
        if inp.is_key_pressed(pygame.K_ESCAPE):
            self.active = False
        if inp.mouse_clicked:
            mw, mh = self.engine.screen.get_size()
            vx = int(inp.mouse_pos[0] * (320 / mw))
            vy = int(inp.mouse_pos[1] * (240 / mh))
            for l in self.leaks[:]:
                if abs(l["x"] - vx) < 16 and abs(l["y"] - vy) < 16:
                    self.leaks.remove(l)
                    self.score += 10
                    self.engine.highscores.submit_score("Kernel Panic", self.score)

    def update(self, dt: float) -> None:
        self.spawn_timer += dt
        if self.spawn_timer > 0.8:
            self.spawn_timer = 0.0
            self.leaks.append({"x": random.randint(30, 290), "y": -20, "speed": random.randint(50, 90)})

        for l in self.leaks[:]:
            l["y"] += l["speed"] * dt
            if l["y"] > 240:
                self.active = False

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((30, 10, 10))
        for l in self.leaks:
            pygame.draw.rect(surface, (255, 50, 50), (l["x"] - 10, int(l["y"]) - 10, 20, 20), border_radius=3)
        sc = self.font.render(f"Patched Leaks: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))

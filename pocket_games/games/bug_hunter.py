from __future__ import annotations
import random
import pygame

class BugHunterGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.bugs = [{"x": random.randint(30, 290), "y": random.randint(30, 210), "timer": 2.0}]
        self.spawn_timer = 0.0

    def handle_input(self) -> None:
        inp = self.engine.input
        if inp.is_key_pressed(pygame.K_ESCAPE):
            self.active = False
        if inp.mouse_clicked:
            mw, mh = self.engine.screen.get_size()
            vx = int(inp.mouse_pos[0] * (320 / mw))
            vy = int(inp.mouse_pos[1] * (240 / mh))
            for b in self.bugs[:]:
                if abs(b["x"] - vx) < 15 and abs(b["y"] - vy) < 15:
                    self.bugs.remove(b)
                    self.score += 25
                    self.engine.highscores.submit_score("Bug Hunter", self.score)

    def update(self, dt: float) -> None:
        self.spawn_timer += dt
        if self.spawn_timer > 1.0:
            self.spawn_timer = 0.0
            if len(self.bugs) < 6:
                self.bugs.append({"x": random.randint(30, 290), "y": random.randint(30, 210), "timer": 3.0})

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((25, 20, 15))
        for b in self.bugs:
            pygame.draw.circle(surface, (255, 50, 50), (b["x"], b["y"]), 8)
            pygame.draw.line(surface, (255, 255, 255), (b["x"] - 10, b["y"] - 10), (b["x"] + 10, b["y"] + 10), 1)

        sc = self.font.render(f"Bugs Squashed: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))

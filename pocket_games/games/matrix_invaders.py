from __future__ import annotations

import random

import pygame


class MatrixInvadersGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.px = 160
        self.bullets: list[dict[str, int]] = []
        self.bugs = [{"x": random.randint(20, 300), "y": random.randint(20, 80)} for _ in range(5)]

    def handle_input(self) -> None:
        inp = self.engine.input
        if (
            inp.is_key_pressed(pygame.K_ESCAPE)
            or inp.is_key_pressed(pygame.K_BACKSPACE)
            or self.engine.input.is_back_pressed()
        ):
            self.active = False
        if inp.is_key_down(pygame.K_LEFT): self.px = max(15, self.px - 4)
        if inp.is_key_down(pygame.K_RIGHT): self.px = min(305, self.px + 4)
        if inp.is_key_pressed(pygame.K_SPACE) or inp.mouse_clicked:
            self.bullets.append({"x": self.px, "y": 200})

    def update(self, dt: float) -> None:
        for b in self.bullets[:]:
            b["y"] -= 200 * dt
            if b["y"] < 0:
                self.bullets.remove(b)

        for bug in self.bugs[:]:
            bug["y"] += 25 * dt
            for b in self.bullets[:]:
                if abs(b["x"] - bug["x"]) < 12 and abs(b["y"] - bug["y"]) < 12:
                    self.bullets.remove(b)
                    self.bugs.remove(bug)
                    self.score += 20
                    self.engine.highscores.submit_score("Matrix Invaders", self.score)
                    self.bugs.append({"x": random.randint(20, 300), "y": random.randint(10, 50)})
                    break

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((5, 10, 15))
        pygame.draw.rect(surface, (0, 255, 150), (self.px - 10, 215, 20, 10), border_radius=2)
        for b in self.bullets:
            pygame.draw.rect(surface, (255, 255, 0), (b["x"] - 2, b["y"], 4, 8))
        for bug in self.bugs:
            pygame.draw.rect(surface, (255, 50, 100), (bug["x"] - 8, bug["y"] - 8, 16, 16), border_radius=3)
        sc = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))

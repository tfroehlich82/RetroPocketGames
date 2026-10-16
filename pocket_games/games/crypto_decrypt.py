from __future__ import annotations

import random

import pygame


class CryptoDecryptGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.target_code = [random.randint(0, 9) for _ in range(4)]
        self.user_code = [0, 0, 0, 0]
        self.cursor = 0

    def handle_input(self) -> None:
        inp = self.engine.input
        if inp.is_key_pressed(pygame.K_ESCAPE):
            self.active = False
        if inp.is_key_pressed(pygame.K_LEFT): self.cursor = (self.cursor - 1) % 4
        if inp.is_key_pressed(pygame.K_RIGHT): self.cursor = (self.cursor + 1) % 4
        if inp.is_key_pressed(pygame.K_UP): self.user_code[self.cursor] = (self.user_code[self.cursor] + 1) % 10
        if inp.is_key_pressed(pygame.K_DOWN): self.user_code[self.cursor] = (self.user_code[self.cursor] - 1) % 10
        if inp.is_key_pressed(pygame.K_RETURN) or inp.is_key_pressed(pygame.K_SPACE):  # noqa: SIM102
            if self.user_code == self.target_code:
                self.score += 100
                self.engine.highscores.submit_score("Crypto Decrypt", self.score)
                self.target_code = [random.randint(0, 9) for _ in range(4)]

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 25, 20))
        t_surf = self.font.render(f"Target: {' '.join(map(str, self.target_code))}", True, (0, 255, 100))
        surface.blit(t_surf, (80, 60))

        code_str = " ".join([f"[{v}]" if i == self.cursor else f" {v} " for i, v in enumerate(self.user_code)])
        c_surf = self.font.render(code_str, True, (255, 255, 0))
        surface.blit(c_surf, (95, 110))

        sc = self.font.render(f"Solved: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))

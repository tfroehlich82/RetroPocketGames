# ==========================================
# QUANTUM MAZE (Wall Collision Validated Spawns)
# ==========================================
import random

import pygame

from pocket_games.games.base import BaseGame


class QuantumMazeGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Quantum Maze")
        self.px, self.py = 20, 20
        self.cores = []
        self.walls = [
            pygame.Rect(60, 0, 15, 160),
            pygame.Rect(140, 80, 15, 160),
            pygame.Rect(220, 0, 15, 160),
        ]
        self._spawn_core()

    def _spawn_core(self) -> None:
        while True:
            candidate = pygame.Rect(random.randint(20, 290), random.randint(20, 210), 12, 12)
            if not any(candidate.colliderect(w) for w in self.walls):
                self.cores.append(candidate)
                break

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        dx, dy = 0, 0
        speed = 100
        if inp.is_key_down(pygame.K_LEFT):
            dx -= speed
        if inp.is_key_down(pygame.K_RIGHT):
            dx += speed
        if inp.is_key_down(pygame.K_UP):
            dy -= speed
        if inp.is_key_down(pygame.K_DOWN):
            dy += speed

        # Move with Wall Collision Check
        dt = 0.016
        next_rect = pygame.Rect(int(self.px + dx * dt), int(self.py + dy * dt), 12, 12)
        if not any(next_rect.colliderect(w) for w in self.walls):
            self.px += dx * dt
            self.py += dy * dt

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        player_rect = pygame.Rect(int(self.px), int(self.py), 12, 12)
        for core in self.cores[:]:
            if player_rect.colliderect(core):
                self.cores.remove(core)
                self.add_score(50)
                self.play_sound("score")
                self._spawn_core()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 15, 25))
        for w in self.walls:
            pygame.draw.rect(surface, (80, 80, 120), w, border_radius=2)
        for c in self.cores:
            pygame.draw.ellipse(surface, (0, 255, 200), c)

        pygame.draw.rect(surface, (255, 200, 0), (int(self.px), int(self.py), 12, 12), border_radius=2)
        self.render_ui(surface)

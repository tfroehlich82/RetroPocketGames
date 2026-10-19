# ==========================================
# CHRONO SHIFT (Temporal Echo Paradox)
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.games.base import BaseGame


class ChronoShiftGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Chrono Shift")
        self.px, self.py = 160.0, 120.0
        self.vx, self.vy = 0.0, 0.0
        self.fragments: list[dict] = []
        self.trail: list[tuple[float, float]] = []
        self.trail_timer = 0.0
        self._spawn_fragment()

    def _spawn_fragment(self) -> None:
        self.fragments = [{
            "x": float(random.randint(40, 280)),
            "y": float(random.randint(50, 200)),
            "r": 8
        }]

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        accel = 220.0
        dt = 0.016

        dx, dy = 0.0, 0.0
        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            dx -= accel * dt
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            dx += accel * dt
        if inp.is_key_down(pygame.K_UP) or inp.is_key_down(pygame.K_w):
            dy -= accel * dt
        if inp.is_key_down(pygame.K_DOWN) or inp.is_key_down(pygame.K_s):
            dy += accel * dt

        self.vx = self.vx * 0.92 + dx
        self.vy = self.vy * 0.92 + dy

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over or self.paused:
            return

        self.px += self.vx * dt
        self.py += self.vy * dt

        if self.px < 20 or self.px > 300 or self.py < 40 or self.py > 220:
            self.game_over = True
            self.play_sound("gameover")
            return

        self.trail_timer += dt
        if self.trail_timer > 0.15:
            self.trail_timer = 0.0
            self.trail.insert(0, (self.px, self.py))
            if len(self.trail) > 35:
                self.trail.pop()

        for i, pos in enumerate(self.trail[5:]):
            if math.hypot(self.px - pos[0], self.py - pos[1]) < 8:
                self.game_over = True
                self.play_sound("gameover")
                return

        for f in self.fragments[:]:
            if math.hypot(self.px - f["x"], self.py - f["y"]) < f["r"] + 6:
                self.fragments.remove(f)
                self.add_score(50)
                self.play_sound("score")
                self._spawn_fragment()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((18, 10, 28))

        for x in range(0, 320, 32):
            pygame.draw.line(surface, (28, 16, 45), (x, 0), (x, 240), 1)
        for y in range(0, 240, 32):
            pygame.draw.line(surface, (28, 16, 45), (0, y), (320, y), 1)

        for i, pos in enumerate(self.trail):
            alpha_radius = max(2, 6 - int(i / 6))
            pygame.draw.circle(surface, (140, 60, 220), (int(pos[0]), int(pos[1])), alpha_radius)

        for f in self.fragments:
            pygame.draw.circle(surface, (255, 215, 0), (int(f["x"]), int(f["y"])), f["r"])
            pygame.draw.circle(surface, (255, 255, 255), (int(f["x"]), int(f["y"])), 3)

        px, py = int(self.px), int(self.py)
        pygame.draw.circle(surface, (0, 255, 180), (px, py), 9)
        pygame.draw.circle(surface, (255, 255, 255), (px, py), 4)

        self.render_ui(surface)

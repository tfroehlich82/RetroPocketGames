# ==========================================
# CHRONO SHIFT (High-Speed Temporal Paradox)
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.core.physics import (
    check_circle_collision,
    update_velocity_damping,
)
from pocket_games.games.base import BaseGame


class ChronoShiftGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Chrono Shift")
        self.px, self.py = 160.0, 120.0
        self.vx, self.vy = 0.0, 0.0
        self.fragments: list[dict] = []
        self.trail: list[tuple[float, float]] = []
        self.trail_timer = 0.0
        self.spawn_protection = 1.0
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
        accel = 340.0
        dt = 0.016

        dx, dy = 0.0, 0.0
        if inp.is_left_pressed():
            dx -= accel * dt
        if inp.is_right_pressed():
            dx += accel * dt
        if inp.is_up_pressed():
            dy -= accel * dt
        if inp.is_down_pressed():
            dy += accel * dt

        self.vx, self.vy = update_velocity_damping(self.vx + dx, self.vy + dy, 0.94)

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over or self.paused:
            return

        if self.spawn_protection > 0:
            self.spawn_protection -= dt

        self.px += self.vx * dt
        self.py += self.vy * dt

        if self.px < 20 or self.px > 300 or self.py < 40 or self.py > 220:
            self.game_over = True
            self.play_sound("gameover")
            return

        self.trail_timer += dt
        if self.trail_timer > 0.12:
            self.trail_timer = 0.0
            self.trail.insert(0, (self.px, self.py))
            if len(self.trail) > 42:
                self.trail.pop()

        if self.spawn_protection <= 0:
            for pos in self.trail[8:]:
                if check_circle_collision(self.px, self.py, 4.0, pos[0], pos[1], 5.0):
                    self.game_over = True
                    self.play_sound("gameover")
                    return

        for f in self.fragments[:]:
            if check_circle_collision(self.px, self.py, 6.0, f["x"], f["y"], float(f["r"])):
                self.fragments.remove(f)
                self.add_score(60)
                self.play_sound("score")
                self._spawn_fragment()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 8, 25))

        for x in range(0, 320, 24):
            pygame.draw.line(surface, (25, 12, 40), (x, 0), (x, 240), 1)
        for y in range(0, 240, 24):
            pygame.draw.line(surface, (25, 12, 40), (0, y), (320, y), 1)

        for i, pos in enumerate(self.trail):
            alpha_radius = max(2, 7 - int(i / 6))
            pygame.draw.circle(surface, (180, 50, 240), (int(pos[0]), int(pos[1])), alpha_radius)

        for f in self.fragments:
            pygame.draw.circle(surface, (255, 215, 0), (int(f["x"]), int(f["y"])), f["r"])
            pygame.draw.circle(surface, (255, 255, 255), (int(f["x"]), int(f["y"])), 3)

        px, py = int(self.px), int(self.py)
        pygame.draw.circle(surface, (0, 255, 220), (px, py), 10)
        pygame.draw.circle(surface, (255, 255, 255), (px, py), 4)

        self.render_ui(surface)

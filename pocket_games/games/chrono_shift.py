# ==========================================
# CHRONO SHIFT v1.0
# A fast-paced temporal continuum action game.
# Navigate your energy sphere through distinct temporal zones,
# collect glowing fragments, and avoid colliding with your
# own time trail or moving glitch anomalies.
# Multiple challenging levels and escalating speeds deliver pure arcade thrills.
# ==========================================
from __future__ import annotations

import math
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
        self.level = 1
        self.score_in_level = 0
        self.fragments: list[dict] = []
        self.anomalies: list[dict] = []
        self.trail: list[tuple[float, float]] = []
        self.trail_timer = 0.0
        self.spawn_protection = 1.0
        self._reset_level_objects()

    def _spawn_fragment(self) -> None:
        self.fragments = [
            {
                "x": float(random.randint(50, 270)),
                "y": float(random.randint(50, 190)),
                "r": 9,
                "pulse": 0.0,
            }
        ]

    def _reset_level_objects(self) -> None:
        self._spawn_fragment()
        self.anomalies = []
        anomaly_count = min(5, self.level + 1)
        for _ in range(anomaly_count):
            self.anomalies.append(
                {
                    "x": float(random.randint(40, 280)),
                    "y": float(random.randint(50, 190)),
                    "vx": random.uniform(-40.0, 40.0) * (1 + 0.3 * self.level),
                    "vy": random.uniform(-40.0, 40.0) * (1 + 0.3 * self.level),
                    "r": 10,
                }
            )

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        accel = 360.0 + (self.level * 40.0)
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

        damping = 0.93 - (self.level * 0.01)
        self.vx, self.vy = update_velocity_damping(self.vx + dx, self.vy + dy, damping)

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
        if self.trail_timer > 0.1:
            self.trail_timer = 0.0
            self.trail.insert(0, (self.px, self.py))
            max_trail = max(30, 50 - (self.level * 5))
            if len(self.trail) > max_trail:
                self.trail.pop()

        if self.spawn_protection <= 0:
            for pos in self.trail[8:]:
                if check_circle_collision(self.px, self.py, 4.0, pos[0], pos[1], 5.0):
                    self.game_over = True
                    self.play_sound("gameover")
                    return

        for an in self.anomalies:
            an["x"] += an["vx"] * dt
            an["y"] += an["vy"] * dt
            if an["x"] < 30 or an["x"] > 290:
                an["vx"] *= -1
            if an["y"] < 50 or an["y"] > 210:
                an["vy"] *= -1

            if check_circle_collision(
                self.px, self.py, 6.0, an["x"], an["y"], float(an["r"])
            ):
                self.game_over = True
                self.play_sound("gameover")
                return

        for f in self.fragments[:]:
            f["pulse"] += dt * 6
            if check_circle_collision(
                self.px, self.py, 7.0, f["x"], f["y"], float(f["r"])
            ):
                self.fragments.remove(f)
                self.add_score(50 + self.level * 25)
                self.score_in_level += 1
                self.play_sound("score")

                if self.score_in_level >= 4 and self.level < 3:
                    self.level += 1
                    self.score_in_level = 0
                    self.play_sound("confirm")
                    self._reset_level_objects()
                else:
                    self._spawn_fragment()

    def render(self, surface: pygame.Surface) -> None:
        bg_colors = {1: (15, 8, 25), 2: (25, 8, 15), 3: (10, 20, 30)}
        surface.fill(bg_colors.get(self.level, (15, 8, 25)))

        for x in range(0, 320, 24):
            pygame.draw.line(surface, (30, 15, 50), (x, 0), (x, 240), 1)
        for y in range(0, 240, 24):
            pygame.draw.line(surface, (30, 15, 50), (0, y), (320, y), 1)

        for i, pos in enumerate(self.trail):
            alpha_radius = max(2, 7 - int(i / 5))
            trail_col = (
                (180, 50, 240)
                if self.level == 1
                else ((255, 100, 50) if self.level == 2 else (0, 200, 255))
            )
            pygame.draw.circle(
                surface, trail_col, (int(pos[0]), int(pos[1])), alpha_radius
            )

        for an in self.anomalies:
            ax, ay, ar = int(an["x"]), int(an["y"]), int(an["r"])
            pygame.draw.circle(surface, (255, 40, 80), (ax, ay), ar)
            pygame.draw.circle(surface, (255, 255, 255), (ax, ay), ar - 4, 1)

        for f in self.fragments:
            fx, fy = int(f["x"]), int(f["y"])
            pulse_r = int(f["r"] + math.sin(f["pulse"]) * 2)
            pygame.draw.circle(surface, (0, 255, 200), (fx, fy), pulse_r)
            pygame.draw.circle(surface, (255, 255, 255), (fx, fy), 3)

        px, py = int(self.px), int(self.py)
        pygame.draw.circle(surface, (255, 215, 0), (px, py), 10)
        pygame.draw.circle(surface, (255, 255, 255), (px, py), 4)

        lvl_txt = self.font.render(f"TEMPORAL ZONE {self.level}", True, (200, 220, 255))
        surface.blit(lvl_txt, (160 - lvl_txt.get_width() // 2, 10))

        self.render_ui(surface)

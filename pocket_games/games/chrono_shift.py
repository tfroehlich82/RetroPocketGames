# ==========================================
# CHRONO SHIFT v1.2
# A fast-paced temporal continuum action game.
# Featuring dynamic quantum backgrounds, energy storms,
# and an escalating 3-zone time-warp progression.
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
        self.lives = 3
        self.level = 1
        self.score_in_level = 0
        self.fragments: list[dict] = []
        self.anomalies: list[dict] = []
        self.trail: list[tuple[float, float]] = []
        self.trail_timer = 0.0
        self.spawn_protection = 1.0
        self.invulnerable_timer = 0.0

        # Korrigierte List Comprehension für die Quanten-Partikel
        self.quantum_particles = [
            {
                "x": random.randint(0, 320),
                "y": random.randint(0, 240),
                "speed": random.uniform(20.0, 50.0),
                "size": random.randint(1, 3),
            }
            for _ in range(35)
        ]
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
        anomaly_count = min(6, self.level + 2)
        for _ in range(anomaly_count):
            self.anomalies.append(
                {
                    "x": float(random.randint(40, 280)),
                    "y": float(random.randint(50, 190)),
                    "vx": random.uniform(-45.0, 45.0) * (1 + 0.35 * self.level),
                    "vy": random.uniform(-45.0, 45.0) * (1 + 0.35 * self.level),
                    "r": 11,
                }
            )

    def handle_damage(self) -> None:
        if self.invulnerable_timer > 0.0 or self.spawn_protection > 0.0:
            return
        self.lives -= 1
        self.play_sound("hit")
        if self.lives <= 0:
            self.game_over = True
            self.play_sound("gameover")
        else:
            self.px, self.py = 160.0, 120.0
            self.vx, self.vy = 0.0, 0.0
            self.invulnerable_timer = 1.5
            self.trail.clear()

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

        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        for qp in self.quantum_particles:
            qp["y"] += qp["speed"] * dt
            if qp["y"] > 240:
                qp["y"] = 0
                qp["x"] = random.randint(0, 320)

        self.px += self.vx * dt
        self.py += self.vy * dt

        if (
            self.px < 20 or self.px > 300 or self.py < 40 or self.py > 220
        ) and self.invulnerable_timer <= 0.0:
            self.handle_damage()
            return

        self.trail_timer += dt
        if self.trail_timer > 0.1:
            self.trail_timer = 0.0
            if (
                not self.trail
                or math.hypot(self.px - self.trail[0][0], self.py - self.trail[0][1])
                > 4.0
            ):
                self.trail.insert(0, (self.px, self.py))
                max_trail = max(30, 50 - (self.level * 5))
                if len(self.trail) > max_trail:
                    self.trail.pop()

        if self.spawn_protection <= 0 and self.invulnerable_timer <= 0.0:
            for pos in self.trail[8:]:
                if check_circle_collision(self.px, self.py, 4.0, pos[0], pos[1], 5.0):
                    self.handle_damage()
                    return

        for an in self.anomalies:
            an["x"] += an["vx"] * dt
            an["y"] += an["vy"] * dt
            if an["x"] < 30 or an["x"] > 290:
                an["vx"] *= -1
            if an["y"] < 50 or an["y"] > 210:
                an["vy"] *= -1

            if self.invulnerable_timer <= 0.0 and check_circle_collision(
                self.px, self.py, 6.0, an["x"], an["y"], float(an["r"])
            ):
                self.handle_damage()
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
        scene_backgrounds = {
            1: (8, 14, 32),
            2: (26, 10, 32),
            3: (35, 8, 12),
        }
        grid_colors = {
            1: (20, 35, 70),
            2: (50, 20, 60),
            3: (70, 18, 22),
        }
        particle_colors = {
            1: (0, 220, 255),
            2: (255, 100, 220),
            3: (255, 150, 50),
        }

        surface.fill(scene_backgrounds.get(self.level, (8, 14, 32)))
        g_col = grid_colors.get(self.level, (20, 35, 70))
        p_col = particle_colors.get(self.level, (0, 220, 255))

        for x in range(0, 320, 24):
            pygame.draw.line(surface, g_col, (x, 0), (x, 240), 1)
        for y in range(0, 240, 24):
            pygame.draw.line(surface, g_col, (0, y), (320, y), 1)

        for qp in self.quantum_particles:
            surface.set_at((int(qp["x"]), int(qp["y"])), p_col)

        for i, pos in enumerate(self.trail):
            alpha_radius = max(2, 7 - int(i / 5))
            trail_col = (
                (0, 255, 200)
                if self.level == 1
                else ((255, 0, 180) if self.level == 2 else (255, 215, 0))
            )
            pygame.draw.circle(
                surface, trail_col, (int(pos[0]), int(pos[1])), alpha_radius
            )

        for an in self.anomalies:
            ax, ay, ar = int(an["x"]), int(an["y"]), int(an["r"])
            pygame.draw.circle(surface, (10, 10, 15), (ax, ay), ar)
            pygame.draw.circle(surface, (255, 50, 100), (ax, ay), ar, 2)
            pygame.draw.circle(surface, (255, 255, 255), (ax, ay), 3)

        for f in self.fragments:
            fx, fy = int(f["x"]), int(f["y"])
            pulse_r = int(f["r"] + math.sin(f["pulse"]) * 2)
            pygame.draw.circle(surface, (50, 255, 150), (fx, fy), pulse_r)
            pygame.draw.circle(surface, (255, 255, 255), (fx, fy), 3)

        if self.invulnerable_timer <= 0 or int(pygame.time.get_ticks() / 100) % 2 == 0:
            px, py = int(self.px), int(self.py)
            pygame.draw.circle(surface, (0, 180, 255), (px, py), 12, 1)
            pygame.draw.circle(surface, (0, 240, 255), (px, py), 9)
            pygame.draw.circle(surface, (255, 255, 255), (px, py), 4)

        pygame.draw.rect(
            surface, (10, 12, 22, 220), (10, 215, 300, 20), border_radius=4
        )

        zone_names = {1: "QUANTUM GRID", 2: "TACHYON STORM", 3: "EVENT HORIZON"}
        info_txt = self.font.render(
            f"ZONE {self.level}: {zone_names.get(self.level, '')}  |  LIVES: {self.lives}",
            True,
            (200, 220, 255),
        )
        surface.blit(info_txt, (160 - info_txt.get_width() // 2, 218))

        self.render_ui(surface)

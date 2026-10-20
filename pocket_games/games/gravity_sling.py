# ==========================================
# GRAVITY SLING (Stellar Navigation Edition)
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.core.physics import calculate_orbital_pull, check_circle_collision
from pocket_games.games.base import BaseGame


class GravitySlingGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Gravity Sling")
        self.px, self.py = 50.0, 120.0
        self.vx, self.vy = 70.0, -35.0
        self.planets = [
            {"x": 160, "y": 120, "r": 22, "color": (80, 140, 255)},
            {"x": 80, "y": 60, "r": 16, "color": (255, 120, 80)},
            {"x": 240, "y": 180, "r": 18, "color": (160, 80, 255)},
        ]
        self.crystals = []
        self._spawn_crystal()

    def _spawn_crystal(self) -> None:
        while True:
            cx = random.randint(30, 290)
            cy = random.randint(40, 200)
            valid = True
            for p in self.planets:
                if check_circle_collision(cx, cy, 0.0, float(p["x"]), float(p["y"]), float(p["r"] + 20)):
                    valid = False
                    break
            if valid:
                self.crystals.append({"x": cx, "y": cy})
                break

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.is_action_just_pressed():
            mag = math.hypot(self.vx, self.vy)
            if mag > 0:
                self.vx += (self.vx / mag) * 55.0
                self.vy += (self.vy / mag) * 55.0
            else:
                self.vy -= 55.0
            self.play_sound("bounce")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        for p in self.planets:
            # Physik: Orbital pull via physics.py
            if check_circle_collision(self.px, self.py, 5.0, float(p["x"]), float(p["y"]), float(p["r"])):
                self.game_over = True
                self.play_sound("gameover")
                return

            fx, fy = calculate_orbital_pull(self.px, self.py, float(p["x"]), float(p["y"]), strength=20000.0)
            self.vx += fx * dt
            self.vy += fy * dt

        self.px += self.vx * dt
        self.py += self.vy * dt

        for c in self.crystals[:]:
            if check_circle_collision(self.px, self.py, 5.0, float(c["x"]), float(c["y"]), 6.0):
                self.crystals.remove(c)
                self.add_score(50)
                self.play_sound("score")
                self._spawn_crystal()

        if self.px < 10 or self.px > 310 or self.py < 30 or self.py > 230:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((5, 8, 18))
        for p in self.planets:
            pygame.draw.circle(surface, p["color"], (p["x"], p["y"]), p["r"])
        for c in self.crystals:
            pygame.draw.circle(surface, (0, 255, 200), (int(c["x"]), int(c["y"])), 6)
        pygame.draw.circle(surface, (255, 215, 0), (int(self.px), int(self.py)), 5)
        self.render_ui(surface)

# ==========================================
# ORBITAL DEFENSE (Reactor Core Edition)
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.core.physics import check_circle_collision
from pocket_games.games.base import BaseGame


class OrbitalDefenseGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Orbital Defense")
        self.angle = 0.0
        self.meteors = []
        self.particles = []
        self.spawn_timer = 0.0
        self.time_counter = 0.0

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.is_left_pressed():
            self.angle -= 5.0
        if inp.is_right_pressed():
            self.angle += 5.0

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.time_counter += dt
        self.spawn_timer += dt

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        if self.spawn_timer > max(0.25, 0.9 - self.elapsed_time * 0.02):
            self.spawn_timer = 0.0
            a = random.uniform(0, math.pi * 2)
            self.meteors.append({
                "x": 160 + math.cos(a) * 190,
                "y": 120 + math.sin(a) * 190,
                "angle": a,
                "size": random.randint(6, 10),
                "rot": random.uniform(1, 3)
            })

        shield_rad = math.radians(self.angle)
        sx, sy = 160 + math.cos(shield_rad) * 42, 120 + math.sin(shield_rad) * 42

        for m in self.meteors[:]:
            m["x"] -= math.cos(m["angle"]) * 95 * dt
            m["y"] -= math.sin(m["angle"]) * 95 * dt

            if check_circle_collision(m["x"], m["y"], float(m["size"]), sx, sy, 9.0):
                self.meteors.remove(m)
                self.add_score(25)
                self.play_sound("bounce")
                for _ in range(10):
                    ang = random.uniform(0, math.pi * 2)
                    spd = random.uniform(40, 120)
                    self.particles.append({
                        "x": sx, "y": sy,
                        "vx": math.cos(ang) * spd, "vy": math.sin(ang) * spd,
                        "life": 0.3, "color": (255, 220, 50)
                    })

            elif check_circle_collision(m["x"], m["y"], float(m["size"]), 160.0, 120.0, 14.0):
                self.game_over = True
                self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 12, 22))

        for i in range(20):
            x = (i * 37) % 320
            y = (i * 53) % 240
            surface.set_at((x, y), (70, 90, 130))

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        pulse = (math.sin(self.time_counter * 6) + 1) * 0.5
        core_rad = int(12 + pulse * 4)
        pygame.draw.circle(surface, (0, 120, 255), (160, 120), core_rad + 6, 2)
        pygame.draw.circle(surface, (0, 220, 255), (160, 120), core_rad)
        pygame.draw.circle(surface, (255, 255, 255), (160, 120), 5)

        pygame.draw.circle(surface, (30, 60, 100), (160, 120), 42, 1)

        shield_rad = math.radians(self.angle)
        sx, sy = 160 + math.cos(shield_rad) * 42, 120 + math.sin(shield_rad) * 42
        pygame.draw.circle(surface, (255, 215, 0), (int(sx), int(sy)), 9)
        pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), 4)

        for m in self.meteors:
            mx, my = int(m["x"]), int(m["y"])
            pygame.draw.circle(surface, (180, 50, 40), (mx, my), m["size"])
            pygame.draw.circle(surface, (255, 120, 0), (mx, my), m["size"] - 3)

        self.render_ui(surface)

# ==========================================
# GRAVITY SLING v1.2
# Actively pilot your space probe through gravity-dense star systems.
# Utilize full 4-way vector thrusters for precision control while
# leveraging planetary gravitational pull to perform slingshot maneuvers.
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.core.physics import calculate_orbital_pull, check_circle_collision
from pocket_games.games.base import BaseGame


class GravitySlingGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Gravity Sling")
        self.px, self.py = 50.0, 120.0
        self.vx, self.vy = 0.0, 0.0
        self.lives = 3
        self.level = 1
        self.crystals_collected = 0
        self.rest_timer = 0.0
        self.invulnerable_timer = 0.0
        self.time_left = 40.0
        self.planets: list[dict] = []
        self.crystals: list[dict] = []
        self.particles: list[dict] = []
        self._setup_level()

    def _setup_level(self) -> None:
        self.planets = []
        self.time_left = 40.0
        planet_configs = [
            [
                {
                    "x": 160,
                    "y": 120,
                    "r": 18,
                    "gravity_r": 70,
                    "color": (80, 140, 255),
                    "strength": 8500.0,
                }
            ],
            [
                {
                    "x": 110,
                    "y": 90,
                    "r": 15,
                    "gravity_r": 55,
                    "color": (80, 140, 255),
                    "strength": 7000.0,
                },
                {
                    "x": 210,
                    "y": 150,
                    "r": 18,
                    "gravity_r": 75,
                    "color": (255, 100, 70),
                    "strength": 11000.0,
                },
            ],
            [
                {
                    "x": 90,
                    "y": 80,
                    "r": 14,
                    "gravity_r": 50,
                    "color": (80, 140, 255),
                    "strength": 7500.0,
                },
                {
                    "x": 230,
                    "y": 90,
                    "r": 16,
                    "gravity_r": 60,
                    "color": (255, 120, 80),
                    "strength": 9500.0,
                },
                {
                    "x": 160,
                    "y": 170,
                    "r": 18,
                    "gravity_r": 80,
                    "color": (180, 80, 255),
                    "strength": 13000.0,
                },
            ],
        ]
        cfg_idx = min(self.level - 1, len(planet_configs) - 1)
        self.planets = planet_configs[cfg_idx]
        self._spawn_crystal()

    def _spawn_crystal(self) -> None:
        self.crystals = []
        while True:
            cx = random.randint(40, 280)
            cy = random.randint(50, 190)
            valid = True
            for p in self.planets:
                if check_circle_collision(
                    cx, cy, 0.0, float(p["x"]), float(p["y"]), float(p["r"] + 25)
                ):
                    valid = False
                    break
            if valid:
                self.crystals.append({"x": cx, "y": cy})
                break

    def handle_damage(self) -> None:
        if self.invulnerable_timer > 0.0:
            return
        self.lives -= 1
        self.play_sound("hit")
        if self.lives <= 0:
            self.game_over = True
            self.play_sound("gameover")
        else:
            self.px, self.py = 50.0, 120.0
            self.vx, self.vy = 0.0, 0.0
            self.invulnerable_timer = 1.5

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over or self.rest_timer > 0:
            return

        inp = self.engine.input
        thrust = 190.0
        dt = 0.016

        pushed = False
        if inp.is_left_pressed():
            self.vx -= thrust * dt
            pushed = True
        if inp.is_right_pressed():
            self.vx += thrust * dt
            pushed = True
        if inp.is_up_pressed():
            self.vy -= thrust * dt
            pushed = True
        if inp.is_down_pressed():
            self.vy += thrust * dt
            pushed = True

        if pushed and random.random() < 0.4:
            self.particles.append(
                {
                    "x": self.px,
                    "y": self.py,
                    "vx": -self.vx * 0.3 + random.uniform(-10, 10),
                    "vy": -self.vy * 0.3 + random.uniform(-10, 10),
                    "life": 0.2,
                    "color": (255, 200, 50),
                }
            )

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        if self.rest_timer > 0:
            self.rest_timer -= dt
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self.handle_damage()
            self.time_left = 40.0
            return

        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer -= dt

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        for p in self.planets:
            if self.invulnerable_timer <= 0.0 and check_circle_collision(
                self.px, self.py, 3.0, float(p["x"]), float(p["y"]), float(p["r"] - 2)
            ):
                self.handle_damage()
                return

            fx, fy = calculate_orbital_pull(
                self.px, self.py, float(p["x"]), float(p["y"]), strength=p["strength"]
            )
            self.vx += fx * dt
            self.vy += fy * dt

        self.vx *= 0.985
        self.vy *= 0.985

        self.px += self.vx * dt
        self.py += self.vy * dt

        for c in self.crystals[:]:
            if check_circle_collision(
                self.px, self.py, 6.0, float(c["x"]), float(c["y"]), 10.0
            ):
                self.crystals.remove(c)
                self.add_score(50 * self.level)
                self.crystals_collected += 1
                self.play_sound("score")

                if self.crystals_collected >= 4 and self.level < 3:
                    self.level += 1
                    self.crystals_collected = 0
                    self.rest_timer = 2.0
                    self.play_sound("confirm")
                    self.px, self.py = 50.0, 120.0
                    self.vx, self.vy = 0.0, 0.0
                    self._setup_level()
                else:
                    self._spawn_crystal()

        if (
            self.px < 5 or self.px > 315 or self.py < 25 or self.py > 235
        ) and self.invulnerable_timer <= 0.0:
            self.handle_damage()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((5, 8, 18))

        for i in range(15):
            surface.set_at(((i * 31) % 320, (i * 47) % 240), (60, 80, 120))

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        for p in self.planets:
            # Gravity field radius with a transparency effect, i.e. a fine ring
            pygame.draw.circle(
                surface, (p["color"][0]//3, p["color"][1]//3, p["color"][2]//3), (p["x"], p["y"]), p["gravity_r"], 1
            )
            # Planet base and layers (improved look)
            pygame.draw.circle(surface, (15, 25, 45), (p["x"], p["y"]), p["r"] + 2)
            pygame.draw.circle(surface, p["color"], (p["x"], p["y"]), p["r"])
            # Surface details / craters / shadow
            pygame.draw.circle(
                surface, (255, 255, 255), (p["x"] - 3, p["y"] - 3), max(2, p["r"] // 3), 1
            )
            pygame.draw.arc(
                surface, (10, 15, 30),
                pygame.Rect(p["x"] - p["r"], p["y"] - p["r"], p["r"] * 2, p["r"] * 2),
                0, 3.14, 2
            )

        for c in self.crystals:
            pygame.draw.circle(surface, (0, 255, 200), (int(c["x"]), int(c["y"])), 6)
            pygame.draw.circle(surface, (255, 255, 255), (int(c["x"]), int(c["y"])), 2)

        if self.invulnerable_timer <= 0 or int(pygame.time.get_ticks() / 100) % 2 == 0:
            px, py = int(self.px), int(self.py)
            pygame.draw.circle(surface, (255, 215, 0), (px, py), 6)
            pygame.draw.circle(surface, (255, 255, 255), (px, py), 2)

        # Info bar at the bottom
        pygame.draw.rect(
            surface, (10, 12, 22, 220), (10, 215, 300, 20), border_radius=4
        )

        info_txt = self.font.render(
            f"L: {self.lives} | SEC: {self.level} | GEMS: {self.crystals_collected}/4 | TIME: {max(0, int(self.time_left))}s",
            True,
            (0, 255, 200),
        )
        surface.blit(info_txt, (160 - info_txt.get_width() // 2, 218))

        if self.rest_timer > 0:
            rest_txt = self.title_font.render(
                f"ENTERING SECTOR {self.level}...", True, (255, 215, 0)
            )
            surface.blit(rest_txt, (160 - rest_txt.get_width() // 2, 110))

        self.render_ui(surface)

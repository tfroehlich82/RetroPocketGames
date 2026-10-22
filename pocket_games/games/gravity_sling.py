# ==========================================
# GRAVITY SLING v1.0
# Actively pilot your space probe through gravity-dense star systems.
# Utilize full 4-way vector thrusters for precision control while
# leveraging planetary gravitational pull to perform slingshot maneuvers.
# Collect crystals, avoid planetary crashes, and navigate through
# multiple escalating sectors with tactical rest breaks.
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
        self.level = 1
        self.crystals_collected = 0
        self.rest_timer = 0.0
        self.planets: list[dict] = []
        self.crystals: list[dict] = []
        self.particles: list[dict] = []
        self._setup_level()

    def _setup_level(self) -> None:
        self.planets = []
        # Ausgewogene Planeten-Konfigurationen mit sichtbarem Gravitationsradius
        planet_configs = [
            [{"x": 160, "y": 120, "r": 18, "gravity_r": 65, "color": (80, 140, 255), "strength": 7500.0}],
            [{"x": 110, "y": 90, "r": 16, "gravity_r": 55, "color": (80, 140, 255), "strength": 8000.0},
             {"x": 210, "y": 150, "r": 16, "gravity_r": 55, "color": (255, 120, 80), "strength": 8000.0}],
            [{"x": 90, "y": 80, "r": 15, "gravity_r": 50, "color": (80, 140, 255), "strength": 8500.0},
             {"x": 230, "y": 90, "r": 15, "gravity_r": 50, "color": (255, 120, 80), "strength": 8500.0},
             {"x": 160, "y": 170, "r": 16, "gravity_r": 55, "color": (160, 80, 255), "strength": 9000.0}]
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
                if check_circle_collision(cx, cy, 0.0, float(p["x"]), float(p["y"]), float(p["r"] + 25)):
                    valid = False
                    break
            if valid:
                self.crystals.append({"x": cx, "y": cy})
                break

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over or self.rest_timer > 0:
            return

        inp = self.engine.input
        thrust = 180.0
        dt = 0.016

        # Aktive 4-Richtungen Steuerungsdüsen
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

        # Triebwerks-Partikel erzeugen bei Schub
        if pushed and random.random() < 0.4:
            self.particles.append({
                "x": self.px, "y": self.py,
                "vx": -self.vx * 0.3 + random.uniform(-10, 10),
                "vy": -self.vy * 0.3 + random.uniform(-10, 10),
                "life": 0.2, "color": (255, 200, 50)
            })

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        if self.rest_timer > 0:
            self.rest_timer -= dt
            return

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        # Orbital-Physik & Kollisionsprüfung
        for p in self.planets:
            # Aufprall auf Planetenoberfläche
            if check_circle_collision(self.px, self.py, 3.0, float(p["x"]), float(p["y"]), float(p["r"] - 2)):
                self.game_over = True
                self.play_sound("gameover")
                return

            # Gravitationsanziehung
            fx, fy = calculate_orbital_pull(self.px, self.py, float(p["x"]), float(p["y"]), strength=p["strength"])
            self.vx += fx * dt
            self.vy += fy * dt

        # Sanfter Weltraum-Widerstand (Dämpfung für präzise Manövrierbarkeit)
        self.vx *= 0.985
        self.vy *= 0.985

        self.px += self.vx * dt
        self.py += self.vy * dt

        # Kristall einsammeln
        for c in self.crystals[:]:
            if check_circle_collision(self.px, self.py, 6.0, float(c["x"]), float(c["y"]), 10.0):
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

        # Spielfeldbegrenzung
        if self.px < 5 or self.px > 315 or self.py < 25 or self.py > 235:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((5, 8, 18))

        # Sternenhintergrund
        for i in range(15):
            surface.set_at(((i * 31) % 320, (i * 47) % 240), (60, 80, 120))

        # Partikel
        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        # Planeten & Gravitationsringe
        for p in self.planets:
            # Gravitationsfeld
            pygame.draw.circle(surface, (20, 40, 70), (p["x"], p["y"]), p["gravity_r"], 1)
            # Planet
            pygame.draw.circle(surface, p["color"], (p["x"], p["y"]), p["r"])
            pygame.draw.circle(surface, (255, 255, 255), (p["x"], p["y"]), p["r"] - 3, 1)

        # Kristalle
        for c in self.crystals:
            pygame.draw.circle(surface, (0, 255, 200), (int(c["x"]), int(c["y"])), 6)
            pygame.draw.circle(surface, (255, 255, 255), (int(c["x"]), int(c["y"])), 2)

        # Raumsonde (Player)
        px, py = int(self.px), int(self.py)
        pygame.draw.circle(surface, (255, 215, 0), (px, py), 6)
        pygame.draw.circle(surface, (255, 255, 255), (px, py), 2)

        lvl_txt = self.font.render(f"SECTOR {self.level} | CRYSTALS: {self.crystals_collected}/4", True, (0, 255, 200))
        surface.blit(lvl_txt, (160 - lvl_txt.get_width() // 2, 10))

        if self.rest_timer > 0:
            rest_txt = self.title_font.render(f"ENTERING SECTOR {self.level}...", True, (255, 215, 0))
            surface.blit(rest_txt, (160 - rest_txt.get_width() // 2, 110))

        self.render_ui(surface)

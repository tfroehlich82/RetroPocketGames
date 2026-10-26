# ==========================================
# ORBITAL DEFENSE v1.2
# Protect the central reactor core from incoming meteors,
# collect goodies, and survive advanced hazards.
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
        self.reactor_hp = 3
        self.max_reactor_hp = 5
        self.meteors = []
        self.goodies = []
        self.particles = []
        self.spawn_timer = 0.0
        self.goodie_spawn_timer = 0.0
        self.time_counter = 0.0

    @property
    def level(self) -> int:
        return 1 + (self.score // 250)

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        rot_speed = 5.0 + (self.level - 1) * 0.8
        if inp.is_left_pressed():
            self.angle -= rot_speed
        if inp.is_right_pressed():
            self.angle += rot_speed

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.time_counter += dt
        self.spawn_timer += dt
        self.goodie_spawn_timer += dt

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        # Spawn interval for meteors / hazards
        spawn_interval = max(
            0.3, 1.6 - (self.time_counter * 0.018) - (self.level * 0.08)
        )

        if self.spawn_timer > spawn_interval:
            self.spawn_timer = 0.0
            a = random.uniform(0, math.pi * 2)

            is_smart = self.level >= 2 and random.random() < (0.15 * self.level)
            is_heavy = self.level >= 2 and random.random() < 0.2  # Meteor +2 danger

            self.meteors.append(
                {
                    "x": 160 + math.cos(a) * 190,
                    "y": 120 + math.sin(a) * 190,
                    "angle": a,
                    "size": random.randint(10, 14) if is_heavy else random.randint(6, 9),
                    "rot": random.uniform(1, 3),
                    "smart": is_smart,
                    "heavy": is_heavy,
                    "damage": 2 if is_heavy else 1,
                    "speed": random.uniform(65.0, 85.0) + (self.level * 5.0),
                }
            )

        # Goodies (e.g. +1 life / HP) spawn
        if self.goodie_spawn_timer > 12.0:
            self.goodie_spawn_timer = 0.0
            a = random.uniform(0, math.pi * 2)
            self.goodies.append(
                {
                    "x": 160 + math.cos(a) * 170,
                    "y": 120 + math.sin(a) * 170,
                    "angle": a,
                    "speed": 50.0,
                }
            )

        # Reactor and shield size calculation (reactor grows with each level, shields shrink)
        reactor_radius = int(12 + (self.level - 1) * 3)
        shield_radius = max(5.0, 9.0 - (self.level - 1) * 1.5)

        shield_rad = math.radians(self.angle)
        sx, sy = 160 + math.cos(shield_rad) * 42, 120 + math.sin(shield_rad) * 42

        has_dual_shield = self.level >= 3
        sx2, sy2 = 0.0, 0.0
        if has_dual_shield:
            shield_rad2 = math.radians(self.angle + 180.0)
            sx2, sy2 = (
                160 + math.cos(shield_rad2) * 42,
                120 + math.sin(shield_rad2) * 42,
            )

        # Goodies verarbeiten
        for g in self.goodies[:]:
            dx = 160.0 - g["x"]
            dy = 120.0 - g["y"]
            dist = math.hypot(dx, dy)
            g["x"] += (dx / dist) * g["speed"] * dt if dist > 0 else 0
            g["y"] += (dy / dist) * g["speed"] * dt if dist > 0 else 0

            if check_circle_collision(g["x"], g["y"], 6.0, sx, sy, shield_radius) or \
               (has_dual_shield and check_circle_collision(g["x"], g["y"], 6.0, sx2, sy2, shield_radius)):
                self.goodies.remove(g)
                self.reactor_hp = min(self.max_reactor_hp, self.reactor_hp + 1)
                self.play_sound("confirm")
                self.add_score(50)
            elif check_circle_collision(g["x"], g["y"], 6.0, 160.0, 120.0, float(reactor_radius)):
                self.goodies.remove(g)
                self.reactor_hp = min(self.max_reactor_hp, self.reactor_hp + 1)
                self.play_sound("score")

        for m in self.meteors[:]:
            if m.get("smart"):
                dx = 160.0 - m["x"]
                dy = 120.0 - m["y"]
                target_angle = math.atan2(dy, dx)
                m["angle"] += (target_angle - m["angle"]) * dt * 1.5

            m["x"] -= math.cos(m["angle"]) * m["speed"] * dt
            m["y"] -= math.sin(m["angle"]) * m["speed"] * dt

            hit_shield1 = check_circle_collision(
                m["x"], m["y"], float(m["size"]), sx, sy, shield_radius
            )
            hit_shield2 = has_dual_shield and check_circle_collision(
                m["x"], m["y"], float(m["size"]), sx2, sy2, shield_radius
            )

            if hit_shield1 or hit_shield2:
                impact_x, impact_y = m["x"], m["y"]
                self.meteors.remove(m)
                pts = 40 if m.get("heavy") else (30 if m.get("smart") else 20)
                self.add_score(pts)
                self.play_sound("bounce")

                for _ in range(10):
                    ang = random.uniform(0, math.pi * 2)
                    spd = random.uniform(40, 120)
                    self.particles.append(
                        {
                            "x": impact_x,
                            "y": impact_y,
                            "vx": math.cos(ang) * spd,
                            "vy": math.sin(ang) * spd,
                            "life": 0.3,
                            "color": (255, 220, 50) if hit_shield1 else (0, 255, 200),
                        }
                    )

            elif check_circle_collision(
                m["x"], m["y"], float(m["size"]), 160.0, 120.0, float(reactor_radius)
            ):
                # Meteor trifft den Reaktor direkt (Heavy Meteor zieht 2 HP ab)
                self.meteors.remove(m)
                damage = m.get("damage", 1)
                self.reactor_hp -= damage
                self.play_sound("hit")

                for _ in range(15):
                    ang = random.uniform(0, math.pi * 2)
                    spd = random.uniform(30, 90)
                    self.particles.append(
                        {
                            "x": 160.0,
                            "y": 120.0,
                            "vx": math.cos(ang) * spd,
                            "vy": math.sin(ang) * spd,
                            "life": 0.4,
                            "color": (255, 50, 50),
                        }
                    )

                if self.reactor_hp <= 0:
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

        reactor_radius = int(12 + (self.level - 1) * 3)
        shield_radius = int(max(5, 9 - (self.level - 1) * 1.5))

        pulse = (math.sin(self.time_counter * 6) + 1) * 0.5
        core_rad = int(reactor_radius + pulse * 2)

        core_col = (0, 220, 255) if self.reactor_hp > 1 else (255, 80, 80)
        pygame.draw.circle(
            surface,
            (0, 120, 255) if self.reactor_hp > 1 else (180, 30, 30),
            (160, 120),
            core_rad + 6,
            2,
        )
        pygame.draw.circle(surface, core_col, (160, 120), core_rad)
        pygame.draw.circle(surface, (255, 255, 255), (160, 120), 4)

        pygame.draw.circle(surface, (30, 60, 100), (160, 120), 42, 1)

        shield_rad_angle = math.radians(self.angle)
        sx, sy = 160 + math.cos(shield_rad_angle) * 42, 120 + math.sin(shield_rad_angle) * 42
        pygame.draw.circle(surface, (255, 215, 0), (int(sx), int(sy)), shield_radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), max(2, shield_radius - 4))

        if self.level >= 3:
            shield_rad2 = math.radians(self.angle + 180.0)
            sx2, sy2 = (
                160 + math.cos(shield_rad2) * 42,
                120 + math.sin(shield_rad2) * 42,
            )
            pygame.draw.circle(surface, (0, 255, 200), (int(sx2), int(sy2)), shield_radius)
            pygame.draw.circle(surface, (255, 255, 255), (int(sx2), int(sy2)), max(2, shield_radius - 4))

        for g in self.goodies:
            gx, gy = int(g["x"]), int(g["y"])
            pygame.draw.circle(surface, (50, 255, 50), (gx, gy), 7)
            pygame.draw.circle(surface, (255, 255, 255), (gx, gy), 3)

        for m in self.meteors:
            mx, my = int(m["x"]), int(m["y"])
            col = (255, 50, 150) if m.get("heavy") else ((255, 80, 40) if m.get("smart") else (180, 50, 40))
            pygame.draw.circle(surface, col, (mx, my), m["size"])
            pygame.draw.circle(surface, (255, 120, 0), (mx, my), max(2, m["size"] - 3))

        lvl_txt = self.font.render(
            f"LVL {self.level} | CORE HP: {self.reactor_hp}/{self.max_reactor_hp}", True, (200, 220, 255)
        )
        surface.blit(lvl_txt, (160 - lvl_txt.get_width() // 2, 10))

        self.render_ui(surface)

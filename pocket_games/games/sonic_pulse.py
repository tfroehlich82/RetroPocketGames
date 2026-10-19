# ==========================================
# SONIC PULSE (Quantum Rhythm Core)
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.games.base import BaseGame


class SonicPulseGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Sonic Pulse")
        self.rings: list[dict] = []
        self.particles: list[dict] = []
        self.spawn_timer = 0.0
        self.integrity = 100.0
        self.combo = 0

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.is_key_just_pressed(pygame.K_SPACE) or inp.mouse_clicked or inp.is_key_just_pressed(pygame.K_UP):
            hit_success = False
            tolerance = max(6.0, 16.0 - (self.elapsed_time * 0.15))
            target_r = 40.0
            for r in self.rings[:]:
                if abs(r["radius"] - target_r) <= tolerance:
                    self.rings.remove(r)
                    self.combo += 1
                    self.add_score(25 * min(self.combo, 5))
                    self.play_sound("score")
                    hit_success = True
                    for _ in range(10):
                        ang = random.uniform(0, math.pi * 2)
                        spd = random.uniform(40, 100)
                        self.particles.append({
                            "x": 160, "y": 120,
                            "vx": math.cos(ang) * spd, "vy": math.sin(ang) * spd,
                            "life": 0.3, "color": (0, 255, 200)
                        })
                    break

            if not hit_success:
                self.combo = 0
                self.integrity = max(0.0, self.integrity - 10.0)
                self.play_sound("hit")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over or self.paused:
            return

        self.spawn_timer += dt
        if self.spawn_timer > max(0.6, 1.3 - self.elapsed_time * 0.02):
            self.spawn_timer = 0.0
            self.rings.append({"radius": 120.0, "speed": random.uniform(70.0, 110.0)})

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        for r in self.rings[:]:
            r["radius"] -= r["speed"] * dt
            if r["radius"] <= 15.0:
                self.rings.remove(r)
                self.integrity -= 15.0
                self.combo = 0
                self.play_sound("hit")

        if self.integrity <= 0.0:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 12, 22))

        for i in range(4):
            pygame.draw.circle(surface, (15, 25, 40), (160, 120), 30 + i * 30, 1)

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        pygame.draw.circle(surface, (255, 100, 200), (160, 120), 40, 2)
        pygame.draw.circle(surface, (255, 100, 200), (160, 120), 35, 1)

        for r in self.rings:
            pygame.draw.circle(surface, (0, 240, 255), (160, 120), int(r["radius"]), 2)

        pygame.draw.circle(surface, (0, 200, 255), (160, 120), 16)
        pygame.draw.circle(surface, (255, 255, 255), (160, 120), 6)

        pygame.draw.rect(surface, (40, 20, 20), (20, 225, 280, 8), border_radius=3)
        bar_w = int(280 * (max(0.0, self.integrity) / 100.0))
        if bar_w > 0:
            pygame.draw.rect(surface, (0, 255, 150) if self.integrity > 30 else (255, 50, 50), (20, 225, bar_w, 8), border_radius=3)

        combo_txt = self.font.render(f"COMBO: x{self.combo}", True, (255, 220, 0))
        surface.blit(combo_txt, (20, 15))

        tolerance = max(6.0, 16.0 - (self.elapsed_time * 0.15))
        tol_txt = self.font.render(f"TOL: ±{tolerance:.1f}", True, (150, 150, 200))
        surface.blit(tol_txt, (220, 15))

        self.render_ui(surface)

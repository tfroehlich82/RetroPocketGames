# ==========================================
# SONIC PULSE v1.0
# An engaging cyber-style rhythm game. Target incoming sound waves
# and hit the core ring at the exact moment. The tolerance window
# starts generously and gradually tightens as your score and level increase.
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

    @property
    def level(self) -> int:
        return 1 + (self.score // 300)

    @property
    def current_tolerance(self) -> float:
        # Starts very generous (28.0) and narrows smoothly with higher score and level
        score_factor = self.score * 0.015
        return max(7.0, 28.0 - score_factor)

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.is_key_just_pressed(pygame.K_SPACE) or inp.mouse_clicked or inp.is_key_just_pressed(pygame.K_UP):
            hit_success = False
            tolerance = self.current_tolerance
            target_r = 40.0

            for r in self.rings[:]:
                if abs(r["radius"] - target_r) <= tolerance:
                    self.rings.remove(r)
                    self.combo += 1
                    base_pts = 25 + (self.level - 1) * 10
                    self.add_score(base_pts * min(self.combo, 5))
                    self.play_sound("score")
                    hit_success = True

                    # O2 / integrity reward for a combo chain
                    if self.combo % 3 == 0:
                        self.integrity = min(100.0, self.integrity + 5.0)

                    for _ in range(12):
                        ang = random.uniform(0, math.pi * 2)
                        spd = random.uniform(40, 110)
                        self.particles.append({
                            "x": 160, "y": 120,
                            "vx": math.cos(ang) * spd, "vy": math.sin(ang) * spd,
                            "life": 0.35, "color": (0, 255, 200) if self.combo > 3 else (0, 220, 255)
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
        spawn_delay = max(0.45, 1.4 - (self.level * 0.12))
        if self.spawn_timer > spawn_delay:
            self.spawn_timer = 0.0
            spd_boost = (self.level - 1) * 12.0
            self.rings.append({"radius": 120.0, "speed": random.uniform(65.0, 95.0) + spd_boost})

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
                self.integrity -= 12.0
                self.combo = 0
                self.play_sound("hit")

        if self.integrity <= 0.0:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 12, 22))

        # Background grid rings
        for i in range(4):
            pygame.draw.circle(surface, (15, 25, 40), (160, 120), 30 + i * 30, 1)

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        # Visualize the current tolerance window
        tol = self.current_tolerance
        target_r = 40.0
        pygame.draw.circle(surface, (40, 20, 50), (160, 120), int(target_r + tol), 1)
        pygame.draw.circle(surface, (40, 20, 50), (160, 120), max(1, int(target_r - tol)), 1)

        # Main target ring
        pygame.draw.circle(surface, (255, 100, 200), (160, 120), int(target_r), 2)
        pygame.draw.circle(surface, (255, 100, 200), (160, 120), 35, 1)

        # Incoming sound rings
        for r in self.rings:
            pygame.draw.circle(surface, (0, 240, 255), (160, 120), int(r["radius"]), 2)

        pygame.draw.circle(surface, (0, 200, 255), (160, 120), 16)
        pygame.draw.circle(surface, (255, 255, 255), (160, 120), 6)

        # Integrity bar
        pygame.draw.rect(surface, (40, 20, 20), (20, 225, 280, 8), border_radius=3)
        bar_w = int(280 * (max(0.0, self.integrity) / 100.0))
        if bar_w > 0:
            pygame.draw.rect(surface, (0, 255, 150) if self.integrity > 30 else (255, 50, 50), (20, 225, bar_w, 8), border_radius=3)

        combo_txt = self.font.render(f"COMBO: x{self.combo}", True, (255, 220, 0))
        surface.blit(combo_txt, (15, 12))

        lvl_txt = self.font.render(f"LEVEL {self.level}", True, (0, 255, 200))
        surface.blit(lvl_txt, (160 - lvl_txt.get_width() // 2, 12))

        tol_txt = self.font.render(f"TOL: ±{tol:.1f}", True, (150, 150, 200))
        surface.blit(tol_txt, (305 - tol_txt.get_width(), 12))

        self.render_ui(surface)

# ==========================================
# ORBITAL DEFENSE (Rotating Shield)
# ==========================================
import math
import random

import pygame

from pocket_games.games.base import BaseGame


class OrbitalDefenseGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Orbital Defense")
        self.angle = 0.0
        self.meteors = []
        self.spawn_timer = 0.0

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.is_key_down(pygame.K_LEFT):
            self.angle -= 4.0
        if inp.is_key_down(pygame.K_RIGHT):
            self.angle += 4.0

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.spawn_timer += dt
        if self.spawn_timer > max(0.3, 1.0 - self.elapsed_time * 0.03):
            self.spawn_timer = 0.0
            a = random.uniform(0, math.pi * 2)
            self.meteors.append({"x": 160 + math.cos(a) * 180, "y": 120 + math.sin(a) * 180, "angle": a})

        shield_rad = math.radians(self.angle)
        sx, sy = 160 + math.cos(shield_rad) * 35, 120 + math.sin(shield_rad) * 35

        for m in self.meteors[:]:
            m["x"] -= math.cos(m["angle"]) * 80 * dt
            m["y"] -= math.sin(m["angle"]) * 80 * dt

            # Shield deflection
            if math.hypot(m["x"] - sx, m["y"] - sy) < 15:
                self.meteors.remove(m)
                self.add_score(20)
                self.play_sound("bounce")

            # Core Hit
            elif math.hypot(m["x"] - 160, m["y"] - 120) < 12:
                self.game_over = True
                self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 10, 20))
        pygame.draw.circle(surface, (0, 200, 255), (160, 120), 12)  # Core

        # Shield
        shield_rad = math.radians(self.angle)
        sx, sy = 160 + math.cos(shield_rad) * 35, 120 + math.sin(shield_rad) * 35
        pygame.draw.circle(surface, (255, 215, 0), (int(sx), int(sy)), 8)

        for m in self.meteors:
            pygame.draw.circle(surface, (255, 60, 60), (int(m["x"]), int(m["y"])), 5)

        self.render_ui(surface)

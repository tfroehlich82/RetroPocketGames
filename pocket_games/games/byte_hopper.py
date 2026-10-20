# ==========================================
# BYTE HOPPER (Dynamic Moving Platforms)
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.core.physics import apply_gravity, clamp
from pocket_games.games.base import BaseGame


class ByteHopperGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Byte Hopper")
        self.px, self.py = 160.0, 180.0
        self.vx, self.vy = 0.0, 0.0
        self.camera_y = 0.0
        self.platforms = []
        self._generate_initial_platforms()

    def _generate_initial_platforms(self) -> None:
        self.platforms = [{"rect": pygame.Rect(100, 200, 100, 8), "has_coin": False, "motion": "static", "base_x": 100.0, "base_y": 200.0, "offset": 0.0, "speed": 0.0, "range": 0.0}]
        y = 150
        while y > -1000:
            w = random.randint(55, 75)
            x = random.randint(30, 290 - w)
            self.platforms.append({"rect": pygame.Rect(x, y, w, 8), "has_coin": random.random() < 0.3, "motion": "static", "base_x": float(x), "base_y": float(y), "offset": 0.0, "speed": 0.0, "range": 0.0})
            y -= random.randint(42, 56)

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        self.vx = 0
        if inp.is_left_pressed():
            self.vx = -160
        if inp.is_right_pressed():
            self.vx = 160

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        # Physik: Gravitation via physics.py
        self.vy = apply_gravity(self.vy, 520.0, dt)
        self.px += self.vx * dt
        self.py += self.vy * dt

        # Screen Wrap mit clamp
        self.px = clamp(self.px, 0.0, 320.0)

        player_rect = pygame.Rect(int(self.px) - 6, int(self.py) - 12, 12, 12)
        if self.vy > 0:
            for p in self.platforms:
                if player_rect.colliderect(p["rect"]) and abs(player_rect.bottom - p["rect"].top) < 10:
                    self.vy = -290
                    self.play_sound("bounce")

                if p["has_coin"] and player_rect.colliderect(p["rect"]):
                    p["has_coin"] = False
                    self.add_score(50)
                    self.play_sound("score")

        if self.py - self.camera_y < 100:
            diff = 100 - (self.py - self.camera_y)
            self.camera_y -= diff
            self.add_score(int(diff))

        if self.py - self.camera_y > 250:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 12, 22))
        for p in self.platforms:
            ry = p["rect"].y - int(self.camera_y)
            if -20 < ry < 260:
                pygame.draw.rect(surface, (0, 200, 255), (p["rect"].x, ry, p["rect"].w, p["rect"].h), border_radius=3)
                if p["has_coin"]:
                    pygame.draw.circle(surface, (255, 215, 0), (p["rect"].centerx, ry - 6), 5)
        py_screen = int(self.py - self.camera_y)
        pygame.draw.rect(surface, (255, 180, 0), (int(self.px) - 6, py_screen - 12, 12, 12), border_radius=3)
        self.render_ui(surface)

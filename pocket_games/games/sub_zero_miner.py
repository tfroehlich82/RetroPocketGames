# ==========================================
# SUB ZERO MINER
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class SubZeroMinerGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Sub-Zero Miner")
        self.rx, self.ry = 160.0, 120.0
        self.oxygen = 100.0
        self.gems: list[dict] = []
        self.hazards: list[dict] = []
        self.reset_level()

    def reset_level(self) -> None:
        self.gems = [
            {"x": random.randint(40, 280), "y": random.randint(40, 200), "val": 30}
            for _ in range(4)
        ]
        self.hazards = [
            {"x": random.randint(50, 270), "y": random.randint(50, 190), "r": 16}
            for _ in range(3)
        ]

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active or self.game_over:
            return

        inp = self.engine.input
        speed = 100.0
        dt = 0.016

        dx, dy = 0.0, 0.0
        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            dx -= speed * dt
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            dx += speed * dt
        if inp.is_key_down(pygame.K_UP) or inp.is_key_down(pygame.K_w):
            dy -= speed * dt
        if inp.is_key_down(pygame.K_DOWN) or inp.is_key_down(pygame.K_s):
            dy += speed * dt

        new_x = max(20.0, min(300.0, self.rx + dx))
        new_y = max(35.0, min(220.0, self.ry + dy))

        collides = False
        for h in self.hazards:
            if abs(new_x - h["x"]) < h["r"] + 8 and abs(new_y - h["y"]) < h["r"] + 8:
                collides = True
                self.oxygen -= dt * 15.0
                break

        if not collides:
            self.rx, self.ry = new_x, new_y

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        self.oxygen -= dt * 6.0
        if self.oxygen <= 0:
            self.game_over = True
            self.play_sound("gameover")
            return

        for g in self.gems[:]:
            if abs(self.rx - g["x"]) < 14 and abs(self.ry - g["y"]) < 14:
                self.gems.remove(g)
                self.add_score(g["val"])
                self.oxygen = min(100.0, self.oxygen + 20.0)
                self.play_sound("score")

        if not self.gems:
            self.reset_level()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 20, 32))

        # Ice Hazards
        for h in self.hazards:
            pygame.draw.circle(surface, (120, 200, 255), (int(h["x"]), int(h["y"])), h["r"])
            pygame.draw.circle(surface, (200, 240, 255), (int(h["x"]), int(h["y"])), h["r"] - 4, 1)

        # Gems
        for g in self.gems:
            pygame.draw.circle(surface, (0, 255, 255), (int(g["x"]), int(g["y"])), 6)

        # Miner Rig
        mx, my = int(self.rx), int(self.ry)
        pygame.draw.rect(surface, (255, 120, 0), (mx - 8, my - 8, 16, 16), border_radius=3)
        pygame.draw.rect(surface, (255, 255, 255), (mx - 3, my - 3, 6, 6))

        # O2 Bar
        pygame.draw.rect(surface, (30, 40, 50), (10, 225, 100, 8), border_radius=2)
        o2_w = int(100 * (min(100.0, max(0.0, self.oxygen)) / 100.0))
        o2_col = (0, 220, 255) if self.oxygen > 30 else (255, 50, 50)
        if o2_w > 0:
            pygame.draw.rect(surface, o2_col, (10, 225, o2_w, 8), border_radius=2)

        self.render_ui(surface)

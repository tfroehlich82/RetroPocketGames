from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class SubZeroMinerGame(BaseGame):
    """Refactored Sub-Zero Miner featuring hazards, dynamic drills, and O2 management."""

    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Sub-Zero Miner")
        self.rx, self.ry = 160.0, 120.0
        self.oxygen = 100.0
        self.gems: list[dict] = []
        self.hazards: list[dict] = []
        self.reset_level()

    def reset_level(self) -> None:
        self.gems = [
            {"x": random.randint(30, 290), "y": random.randint(40, 210), "val": 30}
            for _ in range(4)
        ]
        self.hazards = [
            {"x": random.randint(30, 290), "y": random.randint(40, 210), "r": random.randint(12, 18)}
            for _ in range(3)
        ]

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active:
            return

        inp = self.engine.input
        speed = 90.0
        dt = 0.016

        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            self.rx = max(15.0, self.rx - speed * dt)
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            self.rx = min(305.0, self.rx + speed * dt)
        if inp.is_key_down(pygame.K_UP) or inp.is_key_down(pygame.K_w):
            self.ry = max(30.0, self.ry - speed * dt)
        if inp.is_key_down(pygame.K_DOWN) or inp.is_key_down(pygame.K_s):
            self.ry = min(225.0, self.ry + speed * dt)

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        self.oxygen -= dt * 7.5
        if self.oxygen <= 0:
            self.game_over = True
            self.engine.audio.play("hit")
            return

        # Gem Collection
        for g in self.gems[:]:
            if abs(self.rx - g["x"]) < 14 and abs(self.ry - g["y"]) < 14:
                self.gems.remove(g)
                self.add_score(g["val"])
                self.oxygen = min(100.0, self.oxygen + 18.0)
                self.engine.audio.play("confirm")

        if not self.gems:
            self.reset_level()

        # Hazard Collisions (Sub-Zero Ice Spikes)
        for h in self.hazards:
            if abs(self.rx - h["x"]) < h["r"] and abs(self.ry - h["y"]) < h["r"]:
                self.oxygen -= dt * 25.0  # Rapid frost freeze

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 20, 32))

        # Ice Hazards
        for h in self.hazards:
            pygame.draw.circle(surface, (100, 180, 255), (int(h["x"]), int(h["y"])), h["r"], 2)

        # Gems
        for g in self.gems:
            pygame.draw.circle(surface, (0, 255, 255), (int(g["x"]), int(g["y"])), 6)

        # Miner Ship
        mx, my = int(self.rx), int(self.ry)
        pygame.draw.rect(surface, (255, 120, 0), (mx - 8, my - 8, 16, 16), border_radius=3)

        # O2 Bar Indicator
        pygame.draw.rect(surface, (30, 40, 50), (10, 225, 100, 8), border_radius=2)
        o2_w = int(100 * (min(100.0, max(0.0, self.oxygen)) / 100.0))
        o2_col = (0, 220, 255) if self.oxygen > 30 else (255, 50, 50)
        if o2_w > 0:
            pygame.draw.rect(surface, o2_col, (10, 225, o2_w, 8), border_radius=2)

        if self.game_over:
            go = self.title_font.render("FROZEN IN DEEP ICE", True, (255, 50, 50))
            surface.blit(go, (160 - go.get_width() // 2, 110))

        self.render_ui(surface)

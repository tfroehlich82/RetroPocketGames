# ==========================================
# AETHER DEFENDER (Cyber-Core Edition)
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.games.base import BaseGame


class AetherDefenderGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Aether Defender")
        self.px, self.py = 160.0, 200.0
        self.speed = 150.0

        self.bullets: list[dict] = []
        self.enemies: list[dict] = []

        self.shoot_timer = 0.0
        self.spawn_timer = 0.0

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        dt = 0.016

        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            self.px = max(15.0, self.px - self.speed * dt)
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            self.px = min(305.0, self.px + self.speed * dt)

        if (inp.is_key_down(pygame.K_SPACE) or inp.mouse_clicked or inp.is_key_down(
                pygame.K_UP)) and self.shoot_timer <= 0:
            self.bullets.append({"x": self.px, "y": self.py - 8.0})
            self.shoot_timer = 0.18
            self.play_sound("laser")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over or self.paused:
            return

        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        self.spawn_timer += dt
        spawn_threshold = max(0.25, 0.95 - (self.elapsed_time * 0.018))
        if self.spawn_timer >= spawn_threshold:
            self.spawn_timer = 0.0
            enemy_speed = random.uniform(45.0, 75.0) + (self.elapsed_time * 1.2)
            self.enemies.append({
                "x": float(random.randint(20, 300)),
                "y": -15.0,
                "speed": enemy_speed,
                "r": 9.0
            })

        for b in self.bullets[:]:
            b["y"] -= 260.0 * dt
            if b["y"] < -10:
                self.bullets.remove(b)

        player_rect = pygame.Rect(int(self.px - 10), int(self.py - 8), 20, 16)

        for e in self.enemies[:]:
            e["y"] += e["speed"] * dt
            e_rect = pygame.Rect(int(e["x"] - e["r"]), int(e["y"] - e["r"]), int(e["r"] * 2), int(e["r"] * 2))

            if player_rect.colliderect(e_rect):
                self.game_over = True
                self.play_sound("crash")
                return

            for b in self.bullets[:]:
                if math.hypot(b["x"] - e["x"], b["y"] - e["y"]) < e["r"] + 3.0:
                    if b in self.bullets:
                        self.bullets.remove(b)
                    if e in self.enemies:
                        self.enemies.remove(e)
                    self.add_score(20)
                    self.play_sound("hit")
                    break

            if e["y"] > 250 and e in self.enemies:
                self.enemies.remove(e)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 5, 18))

        for i in range(15):
            sx = (i * 23 + int(self.elapsed_time * 10)) % 320
            sy = (i * 37 + int(self.elapsed_time * 40)) % 240
            surface.set_at((sx, sy), (100, 120, 160))

        for b in self.bullets:
            pygame.draw.line(surface, (0, 255, 200), (int(b["x"]), int(b["y"])), (int(b["x"]), int(b["y"] + 6)), 2)

        for e in self.enemies:
            ex, ey, er = int(e["x"]), int(e["y"]), int(e["r"])
            pygame.draw.circle(surface, (255, 60, 80), (ex, ey), er)
            pygame.draw.circle(surface, (255, 200, 0), (ex, ey), max(1, er - 4))

        px, py = int(self.px), int(self.py)
        pygame.draw.polygon(surface, (0, 220, 255), [(px, py - 10), (px - 10, py + 8), (px + 10, py + 8)])
        pygame.draw.polygon(surface, (255, 255, 255), [(px, py - 6), (px - 4, py + 4), (px + 4, py + 4)])

        self.render_ui(surface)

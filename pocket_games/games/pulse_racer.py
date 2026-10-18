# ==========================================
# PULSE RACER
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class PulseRacerGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Pulse Racer")
        self.rx = 160.0
        self.obstacles: list[dict] = []
        self.spawn_timer = 0.0
        self.speed = 190.0
        self.distance_float = 0.0
        self.last_dist = 0
        self.road_scroll = 0.0

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active or self.game_over:
            return

        inp = self.engine.input
        dt = 0.016
        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            self.rx = max(75.0, self.rx - 160.0 * dt)
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            self.rx = min(245.0, self.rx + 160.0 * dt)

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        self.distance_float += self.speed * dt
        current_dist = int(self.distance_float)
        if current_dist > self.last_dist:
            diff = current_dist - self.last_dist
            self.last_dist = current_dist
            self.add_score(diff)

        self.road_scroll = (self.road_scroll + self.speed * dt) % 40

        self.spawn_timer += dt
        if self.spawn_timer > 0.85:
            self.spawn_timer = 0.0
            self.obstacles.append({"x": float(random.randint(85, 235)), "y": -30.0})

        for obs in self.obstacles[:]:
            obs["y"] += self.speed * dt
            if abs(obs["x"] - self.rx) < 14 and abs(obs["y"] - 180.0) < 18:
                self.game_over = True
                self.play_sound("gameover")

            if obs["y"] > 250:
                self.obstacles.remove(obs)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((20, 20, 25))
        road_rect = pygame.Rect(60, 0, 200, 240)
        pygame.draw.rect(surface, (40, 40, 50), road_rect)
        pygame.draw.line(surface, (255, 255, 0), (62, 0), (62, 240), 3)
        pygame.draw.line(surface, (255, 255, 0), (258, 0), (258, 240), 3)
        for y_pos in range(int(-40 + self.road_scroll), 240, 40):
            pygame.draw.line(surface, (200, 200, 200), (160, y_pos), (160, y_pos + 20), 2)
        px, py = int(self.rx), 180
        pygame.draw.rect(surface, (10, 10, 10), (px - 11, py - 8, 4, 8))
        pygame.draw.rect(surface, (10, 10, 10), (px + 7, py - 8, 4, 8))
        pygame.draw.rect(surface, (10, 10, 10), (px - 11, py + 8, 4, 8))
        pygame.draw.rect(surface, (10, 10, 10), (px + 7, py + 8, 4, 8))
        pygame.draw.rect(surface, (0, 220, 255), (px - 8, py - 12, 16, 24), border_radius=4)
        pygame.draw.rect(surface, (150, 240, 255), (px - 6, py - 6, 12, 8), border_radius=2)
        pygame.draw.circle(surface, (255, 255, 255), (px - 6, py - 12), 2)
        pygame.draw.circle(surface, (255, 255, 255), (px + 6, py - 12), 2)

        for obs in self.obstacles:
            ox, oy = int(obs["x"]), int(obs["y"])
            pygame.draw.rect(surface, (255, 40, 80), (ox - 10, oy - 10, 20, 20), border_radius=3)
            pygame.draw.rect(surface, (255, 255, 0), (ox - 7, oy - 2, 14, 4))

        self.render_ui(surface)

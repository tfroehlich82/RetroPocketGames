# ==========================================
# NEON DASH (Upgraded Graphics & Road)
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class NeonDashGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Neon Dash")
        self.lanes = [110, 160, 210]
        self.player_lane = 1
        self.obstacles = []
        self.spawn_timer = 0.0
        self.road_scroll = 0.0

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if (
            inp.is_key_just_pressed(pygame.K_LEFT)
            or inp.is_key_just_pressed(pygame.K_a)
        ) and self.player_lane > 0:
            self.player_lane -= 1
            self.play_sound("bounce")
        elif (
            inp.is_key_just_pressed(pygame.K_RIGHT)
            or inp.is_key_just_pressed(pygame.K_d)
        ) and self.player_lane < 2:
            self.player_lane += 1
            self.play_sound("bounce")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        speed = 170.0 + self.elapsed_time * 6.0
        self.road_scroll = (self.road_scroll + speed * dt) % 40

        self.spawn_timer += dt
        if self.spawn_timer > max(0.5, 1.3 - self.elapsed_time * 0.015):
            self.spawn_timer = 0.0
            self.obstacles.append(
                {"lane": random.randint(0, 2), "y": -40, "passed": False}
            )

        for obs in self.obstacles[:]:
            obs["y"] += speed * dt

            if obs["lane"] == self.player_lane and abs(obs["y"] - 175) < 18:
                self.game_over = True
                self.play_sound("gameover")

            if not obs["passed"] and obs["y"] > 200:
                obs["passed"] = True
                self.add_score(15)
                self.play_sound("score")

            if obs["y"] > 260:
                self.obstacles.remove(obs)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 10, 25))

        road_rect = pygame.Rect(70, 0, 180, 240)
        pygame.draw.rect(surface, (25, 20, 35), road_rect)

        pygame.draw.line(surface, (0, 255, 200), (70, 0), (70, 240), 3)
        pygame.draw.line(surface, (0, 255, 200), (250, 0), (250, 240), 3)

        for lx in [135, 185]:
            for y_pos in range(int(-40 + self.road_scroll), 240, 40):
                pygame.draw.line(surface, (80, 50, 120), (lx, y_pos), (lx, y_pos + 20), 2)

        px = self.lanes[self.player_lane]
        py = 175
        pygame.draw.rect(surface, (10, 10, 10), (px - 10, py - 10, 4, 8))
        pygame.draw.rect(surface, (10, 10, 10), (px + 6, py - 10, 4, 8))
        pygame.draw.rect(surface, (10, 10, 10), (px - 10, py + 6, 4, 8))
        pygame.draw.rect(surface, (10, 10, 10), (px + 6, py + 6, 4, 8))
        pygame.draw.rect(
            surface, (0, 255, 200), (px - 8, py - 14, 16, 28), border_radius=4
        )
        pygame.draw.rect(
            surface, (200, 255, 255), (px - 5, py - 6, 10, 10), border_radius=2
        )
        pygame.draw.circle(surface, (255, 255, 255), (px - 5, py - 14), 2)
        pygame.draw.circle(surface, (255, 255, 255), (px + 5, py - 14), 2)

        for obs in self.obstacles:
            ox = self.lanes[obs["lane"]]
            oy = int(obs["y"])
            pygame.draw.rect(
                surface,
                (255, 0, 100),
                (ox - 12, oy - 10, 24, 20),
                border_radius=3,
            )
            pygame.draw.rect(surface, (255, 255, 0), (ox - 8, oy - 2, 16, 4))

        self.render_ui(surface)
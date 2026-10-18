# ==========================================
# NEON DASH (Per-Obstacle Score & Dynamic Speed)
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class NeonDashGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Neon Dash")
        self.lanes = [80, 160, 240]
        self.player_lane = 1
        self.obstacles = []
        self.spawn_timer = 0.0

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input

        # Verwende is_key_just_pressed, damit ein Tastendruck exakt einen Spurwechsel auslöst
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

        speed = 160.0 + self.elapsed_time * 8.0
        self.spawn_timer += dt
        if self.spawn_timer > max(0.4, 1.2 - self.elapsed_time * 0.02):
            self.spawn_timer = 0.0
            self.obstacles.append(
                {"lane": random.randint(0, 2), "y": -30, "passed": False}
            )

        for obs in self.obstacles[:]:
            obs["y"] += speed * dt

            # Collision Check
            if obs["lane"] == self.player_lane and abs(obs["y"] - 180) < 18:
                self.game_over = True
                self.play_sound("gameover")

            # Score per passed obstacle
            if not obs["passed"] and obs["y"] > 200:
                obs["passed"] = True
                self.add_score(15)
                self.play_sound("score")

            if obs["y"] > 250:
                self.obstacles.remove(obs)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((20, 10, 30))
        for l in self.lanes:
            pygame.draw.line(surface, (60, 30, 80), (l, 0), (l, 240), 2)

        px = self.lanes[self.player_lane]
        pygame.draw.rect(
            surface, (0, 255, 200), (px - 10, 170, 20, 25), border_radius=4
        )

        for obs in self.obstacles:
            ox = self.lanes[obs["lane"]]
            pygame.draw.rect(
                surface,
                (255, 0, 100),
                (ox - 12, int(obs["y"]), 24, 15),
                border_radius=3,
            )

        self.render_ui(surface)

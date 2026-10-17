from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class PulseRacerGame(BaseGame):
    """Refactored Pulse Racer using BaseGame frame structure."""

    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Pulse Racer")
        self.rx = 160.0
        self.obstacles: list[dict] = []
        self.spawn_timer = 0.0
        self.speed = 180.0

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active:
            return

        inp = self.engine.input
        dt = 0.016
        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            self.rx = max(75.0, self.rx - 150.0 * dt)
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            self.rx = min(245.0, self.rx + 150.0 * dt)

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        self.add_score(int(dt * 40))
        self.spawn_timer += dt

        if self.spawn_timer > 0.8:
            self.spawn_timer = 0.0
            self.obstacles.append({"x": float(random.randint(80, 240)), "y": -20.0})

        for obs in self.obstacles[:]:
            obs["y"] += self.speed * dt
            if abs(obs["x"] - self.rx) < 16 and abs(obs["y"] - 190.0) < 18:
                self.game_over = True
                self.engine.audio.play("hit")

            if obs["y"] > 250:
                self.obstacles.remove(obs)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 10, 25))

        # Track Boundaries
        pygame.draw.line(surface, (120, 50, 180), (65, 0), (65, 240), 3)
        pygame.draw.line(surface, (120, 50, 180), (255, 0), (255, 240), 3)

        # Player Car
        px = int(self.rx)
        pygame.draw.rect(surface, (0, 255, 200), (px - 8, 180, 16, 24), border_radius=3)

        # Obstacles
        for obs in self.obstacles:
            ox, oy = int(obs["x"]), int(obs["y"])
            pygame.draw.rect(surface, (255, 40, 80), (ox - 10, oy, 20, 12), border_radius=2)

        if self.game_over:
            go = self.title_font.render("CRASHED!", True, (255, 50, 50))
            surface.blit(go, (160 - go.get_width() // 2, 110))

        self.render_ui(surface)

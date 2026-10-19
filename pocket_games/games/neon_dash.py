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
        self.player_y = 180.0
        self.player_vy = 0.0
        self.is_grounded = True
        self.gravity = 980.0
        self.jump_speed = -360.0

        # Dynamics
        self.base_speed = 140.0
        self.obstacles: list[dict] = []
        self.spawn_timer = 0.0

        self._spawn_obstacle()

    def _spawn_obstacle(self) -> None:
        obs_type = random.choice(["spike", "block", "tall_block"])
        if obs_type == "spike":
            w, h = 18, 22
        elif obs_type == "block":
            w, h = 22, 22
        else:  # tall_block
            w, h = 20, 38

        self.obstacles.append({
            "x": 330.0,
            "y": 200.0 - h,
            "w": w,
            "h": h,
            "type": obs_type
        })

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if (inp.is_key_just_pressed(pygame.K_SPACE) or inp.is_key_just_pressed(
                pygame.K_UP) or inp.mouse_clicked) and self.is_grounded:
            self.player_vy = self.jump_speed
            self.is_grounded = False
            self.play_sound("jump")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over or self.paused:
            return

        current_speed = self.base_speed + (self.elapsed_time * 8.5)

        self.player_vy += self.gravity * dt
        self.player_y += self.player_vy * dt

        if self.player_y >= 180.0:
            self.player_y = 180.0
            self.player_vy = 0.0
            self.is_grounded = True

        self.spawn_timer += dt
        spawn_delay = max(0.85, 2.0 - (self.elapsed_time * 0.02) + random.uniform(-0.2, 0.3))
        if self.spawn_timer >= spawn_delay:
            self.spawn_timer = 0.0
            self._spawn_obstacle()

        player_rect = pygame.Rect(40, int(self.player_y), 20, 20)

        for obs in self.obstacles[:]:
            obs["x"] -= current_speed * dt

            obs_rect = pygame.Rect(int(obs["x"]), int(obs["y"]), obs["w"], obs["h"])
            if obs_rect.right < 0:
                self.obstacles.remove(obs)
                self.add_score(15)
                self.play_sound("score")

            if player_rect.colliderect(obs_rect):
                self.game_over = True
                self.play_sound("crash")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 10, 20))

        pygame.draw.line(surface, (0, 255, 200), (0, 200), (320, 200), 2)
        for i in range(0, 320, 30):
            offset = int((self.elapsed_time * (self.base_speed + self.elapsed_time * 8.5)) % 30)
            x_pos = i - offset
            if x_pos >= 0:
                pygame.draw.line(surface, (20, 40, 60), (x_pos, 200), (x_pos, 240), 1)

        pygame.draw.rect(surface, (255, 0, 128), (40, int(self.player_y), 20, 20), border_radius=3)
        pygame.draw.rect(surface, (255, 255, 255), (42, int(self.player_y) + 2, 16, 16), 1, border_radius=2)

        for obs in self.obstacles:
            ox, oy, ow, oh = int(obs["x"]), int(obs["y"]), obs["w"], obs["h"]
            if obs["type"] == "spike":
                pygame.draw.polygon(surface, (255, 50, 50), [(ox, oy + oh), (ox + ow // 2, oy), (ox + ow, oy + oh)])
            else:
                pygame.draw.rect(surface, (255, 200, 0), (ox, oy, ow, oh), border_radius=2)

        self.render_ui(surface)

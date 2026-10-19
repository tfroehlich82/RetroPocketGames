# ==========================================
# NEON DASH (Cyberpunk Enhanced Edition)
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
        self.base_speed = 150.0
        self.obstacles: list[dict] = []
        self.spawn_timer = 0.0
        self.stars = [{"x": random.randint(0, 320), "y": random.randint(0, 160), "speed": random.randint(10, 30)} for _ in range(20)]

        self._spawn_obstacle()

    def _spawn_obstacle(self) -> None:
        if self.elapsed_time > 15.0 and random.random() < 0.35:
            group_x = 330.0
            for i in range(3):
                self.obstacles.append({
                    "x": group_x + (i * 24),
                    "y": 178,
                    "w": 20,
                    "h": 22,
                    "type": "block"
                })
        else:
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

        current_speed = self.base_speed + (self.elapsed_time * 9.0)

        for star in self.stars:
            star["x"] -= star["speed"] * dt
            if star["x"] < 0:
                star["x"] = 320
                star["y"] = random.randint(0, 160)

        self.player_vy += self.gravity * dt
        self.player_y += self.player_vy * dt

        if self.player_y >= 180.0:
            self.player_y = 180.0
            self.player_vy = 0.0
            self.is_grounded = True

        self.spawn_timer += dt
        spawn_delay = max(0.75, 1.8 - (self.elapsed_time * 0.02) + random.uniform(-0.15, 0.25))
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
        surface.fill((8, 5, 18))

        for star in self.stars:
            surface.set_at((int(star["x"]), int(star["y"])), (150, 200, 255))

        pygame.draw.line(surface, (0, 240, 255), (0, 200), (320, 200), 2)
        pygame.draw.line(surface, (100, 50, 200), (0, 201), (320, 201), 1)

        current_speed = self.base_speed + (self.elapsed_time * 9.0)
        for i in range(0, 320, 35):
            offset = int((self.elapsed_time * current_speed) % 35)
            x_pos = i - offset
            if x_pos >= 0:
                pygame.draw.line(surface, (40, 20, 70), (x_pos, 200), (x_pos, 240), 1)

        px, py = 40, int(self.player_y)
        pygame.draw.rect(surface, (255, 0, 150), (px - 2, py - 2, 24, 24), border_radius=4)
        pygame.draw.rect(surface, (0, 255, 255), (px, py, 20, 20), border_radius=3)
        pygame.draw.rect(surface, (255, 255, 255), (px + 4, py + 4, 12, 12), border_radius=2)

        for obs in self.obstacles:
            ox, oy, ow, oh = int(obs["x"]), int(obs["y"]), obs["w"], obs["h"]
            if obs["type"] == "spike":
                pygame.draw.polygon(surface, (255, 40, 80), [(ox, oy + oh), (ox + ow // 2, oy), (ox + ow, oy + oh)])
                pygame.draw.polygon(surface, (255, 255, 255), [(ox + 4, oy + oh), (ox + ow // 2, oy + 4), (ox + ow - 4, oy + oh)], 1)
            else:
                pygame.draw.rect(surface, (255, 180, 0), (ox, oy, ow, oh), border_radius=3)
                pygame.draw.rect(surface, (255, 255, 255), (ox + 2, oy + 2, ow - 4, oh - 4), 1, border_radius=2)

        self.render_ui(surface)

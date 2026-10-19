# ==========================================
# BYTE HOPPER (Dynamic Moving Platforms)
# ==========================================
from __future__ import annotations

import math
import random

import pygame

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
        self.platforms = [
            {
                "rect": pygame.Rect(100, 200, 100, 8),
                "has_coin": False,
                "motion": "static",
                "base_x": 100.0,
                "base_y": 200.0,
                "offset": 0.0,
                "speed": 0.0,
                "range": 0.0,
            }
        ]
        y = 150
        while y > -1000:
            w = random.randint(55, 75)
            x = random.randint(30, 290 - w)

            r = random.random()
            if r < 0.5:
                motion = "static"
                speed = 0.0
                rng = 0.0
            elif r < 0.75:
                motion = "horizontal"
                speed = random.uniform(2.5, 4.5)
                rng = random.randint(35, 65)
            else:
                motion = "vertical"
                speed = random.uniform(2.0, 4.0)
                rng = random.randint(18, 35)

            self.platforms.append(
                {
                    "rect": pygame.Rect(x, y, w, 8),
                    "has_coin": random.random() < 0.3,
                    "motion": motion,
                    "base_x": float(x),
                    "base_y": float(y),
                    "offset": random.uniform(0, math.pi * 2),
                    "speed": speed,
                    "range": float(rng),
                }
            )
            y -= random.randint(42, 56)

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        self.vx = 0
        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            self.vx = -160
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            self.vx = 160

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.vy += 520 * dt
        self.px += self.vx * dt
        self.py += self.vy * dt

        if self.px < 0:
            self.px = 320
        elif self.px > 320:
            self.px = 0

        for p in self.platforms:
            if p["motion"] != "static":
                p["offset"] += p["speed"] * dt
                oscillation = math.sin(p["offset"]) * p["range"]
                if p["motion"] == "horizontal":
                    new_x = p["base_x"] + oscillation
                    p["rect"].x = int(max(10, min(320 - p["rect"].w, new_x)))
                elif p["motion"] == "vertical":
                    new_y = p["base_y"] + oscillation
                    p["rect"].y = int(new_y)

        player_rect = pygame.Rect(int(self.px) - 6, int(self.py) - 12, 12, 12)
        if self.vy > 0:
            for p in self.platforms:
                if (
                    player_rect.colliderect(p["rect"])
                    and abs(player_rect.bottom - p["rect"].top) < 10
                ):
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

        highest_p = min(p["rect"].y for p in self.platforms)
        if highest_p - self.camera_y > -100:
            w = random.randint(55, 75)
            x = random.randint(30, 290 - w)
            gen_y = highest_p - random.randint(42, 56)

            r = random.random()
            if r < 0.5:
                motion = "static"
                speed = 0.0
                rng = 0.0
            elif r < 0.75:
                motion = "horizontal"
                speed = random.uniform(2.5, 4.5)
                rng = random.randint(35, 65)
            else:
                motion = "vertical"
                speed = random.uniform(2.0, 4.0)
                rng = random.randint(18, 35)

            self.platforms.append(
                {
                    "rect": pygame.Rect(x, gen_y, w, 8),
                    "has_coin": random.random() < 0.35,
                    "motion": motion,
                    "base_x": float(x),
                    "base_y": float(gen_y),
                    "offset": random.uniform(0, math.pi * 2),
                    "speed": speed,
                    "range": float(rng),
                }
            )

        if self.py - self.camera_y > 250:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 12, 22))

        for x in range(0, 320, 40):
            pygame.draw.line(surface, (14, 20, 35), (x, 0), (x, 240), 1)

        for p in self.platforms:
            ry = p["rect"].y - int(self.camera_y)
            if -20 < ry < 260:
                if p["motion"] == "horizontal":
                    col = (255, 100, 200)
                elif p["motion"] == "vertical":
                    col = (50, 255, 150)
                else:
                    col = (0, 200, 255)

                pygame.draw.rect(
                    surface,
                    col,
                    (p["rect"].x, ry, p["rect"].w, p["rect"].h),
                    border_radius=3,
                )
                pygame.draw.rect(
                    surface,
                    (255, 255, 255),
                    (p["rect"].x + 2, ry + 1, p["rect"].w - 4, 2),
                )
                if p["has_coin"]:
                    pygame.draw.circle(
                        surface, (255, 215, 0), (p["rect"].centerx, ry - 6), 5
                    )
                    pygame.draw.circle(
                        surface, (255, 255, 255), (p["rect"].centerx, ry - 6), 2
                    )

        py_screen = int(self.py - self.camera_y)
        pygame.draw.rect(
            surface,
            (255, 180, 0),
            (int(self.px) - 6, py_screen - 12, 12, 12),
            border_radius=3,
        )
        self.render_ui(surface)

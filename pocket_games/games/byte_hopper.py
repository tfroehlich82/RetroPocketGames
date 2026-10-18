# ==========================================
# BYTE HOPPER (Vertical Endlessly Generated Platforms)
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class ByteHopperGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Byte Hopper")
        self.px, self.py = 160.0, 180.0
        self.vx, self.vy = 0.0, 0.0
        self.camera_y = 0.0
        self.platforms = [{"rect": pygame.Rect(100, 200, 120, 8), "has_coin": False}]
        self._generate_initial_platforms()

    def _generate_initial_platforms(self) -> None:
        y = 160
        while y > -1000:
            w = random.randint(55, 80)
            x = random.randint(20, 300 - w)
            self.platforms.append(
                {"rect": pygame.Rect(x, y, w, 8), "has_coin": random.random() < 0.3}
            )
            # Garantierter maximaler Sprungabstand (max 42 Pixel vertikal, damit immer erreichbar)
            y -= random.randint(25, 42)

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        self.vx = 0
        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            self.vx = -150
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            self.vx = 150

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.vy += 500 * dt  # Gravity
        self.px += self.vx * dt
        self.py += self.vy * dt

        # Screen Wrap
        if self.px < 0:
            self.px = 320
        elif self.px > 320:
            self.px = 0

        # Jump on Platform
        player_rect = pygame.Rect(int(self.px) - 6, int(self.py) - 12, 12, 12)
        if self.vy > 0:
            for p in self.platforms:
                if (
                    player_rect.colliderect(p["rect"])
                    and abs(player_rect.bottom - p["rect"].top) < 10
                ):
                    self.vy = -270
                    self.play_sound("bounce")

                if p["has_coin"] and player_rect.colliderect(p["rect"]):
                    p["has_coin"] = False
                    self.add_score(50)
                    self.play_sound("score")

        # Scroll Camera
        if self.py - self.camera_y < 100:
            diff = 100 - (self.py - self.camera_y)
            self.camera_y -= diff
            self.add_score(int(diff))

        # Generate new platforms mit strenger vertikaler Begrenzung
        highest_p = min(p["rect"].y for p in self.platforms)
        if highest_p - self.camera_y > -100:
            w = random.randint(55, 80)
            x = random.randint(20, 300 - w)
            self.platforms.append(
                {
                    "rect": pygame.Rect(
                        x, highest_p - random.randint(25, 42), w, 8
                    ),
                    "has_coin": random.random() < 0.4,
                }
            )

        # Game Over condition
        if self.py - self.camera_y > 250:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 20, 35))

        for p in self.platforms:
            ry = p["rect"].y - int(self.camera_y)
            if -20 < ry < 260:
                pygame.draw.rect(
                    surface,
                    (0, 180, 255),
                    (p["rect"].x, ry, p["rect"].w, p["rect"].h),
                    border_radius=3,
                )
                if p["has_coin"]:
                    pygame.draw.circle(
                        surface, (255, 215, 0), (p["rect"].centerx, ry - 6), 4
                    )

        py_screen = int(self.py - self.camera_y)
        pygame.draw.rect(
            surface,
            (255, 200, 0),
            (int(self.px) - 6, py_screen - 12, 12, 12),
            border_radius=2,
        )
        self.render_ui(surface)

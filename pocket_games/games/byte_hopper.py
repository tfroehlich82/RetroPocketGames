# ==========================================
# BYTE HOPPER v1.0
# A fast-paced vertical jumping game in a cyber neon design.
# Hop from platform to platform, navigate moving platforms,
# and collect valuable coins as well as rare Data Crystals.
# Infinite level generation and engaging platform mechanics
# deliver endless arcade fun.
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.core.physics import apply_gravity, clamp
from pocket_games.games.base import BaseGame


class ByteHopperGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Byte Hopper")
        self.px, self.py = 160.0, 180.0
        self.vx, self.vy = 0.0, 0.0
        self.camera_y = 0.0
        self.platforms = []
        self.particles = []
        self._generate_initial_platforms()

    def _generate_initial_platforms(self) -> None:
        self.platforms = [
            {
                "rect": pygame.Rect(100, 200, 100, 8),
                "has_coin": False,
                "has_crystal": False,
                "motion": "static",
                "base_x": 100.0,
                "base_y": 200.0,
                "offset": 0.0,
                "speed": 0.0,
                "range": 0.0,
            }
        ]
        y = 140
        while y > -2000:
            self._spawn_platform(y)
            y -= random.randint(45, 58)

    def _spawn_platform(self, y: int) -> None:
        max_attempts = 10
        for _ in range(max_attempts):
            w = random.randint(58, 80)
            x = random.randint(25, 295 - w)

            motion_type = random.choices(
                ["static", "horizontal", "vertical"], weights=[65, 25, 10]
            )[0]
            speed = random.uniform(4.0, 10.0) if motion_type != "static" else 0.0
            rng = (
                random.uniform(20.0, 50.0)
                if motion_type == "horizontal"
                else (random.uniform(10.0, 30.0) if motion_type == "vertical" else 0.0)
            )

            # Calculate the effective movement range (bounding box) of the new platform
            eff_min_x = x - rng if motion_type == "horizontal" else x
            eff_max_x = x + w + rng if motion_type == "horizontal" else x + w

            # Check for overlaps with already existing nearby platforms
            overlapping = False
            for p in self.platforms:
                # Only check platforms in the same height range
                if abs(p["base_y"] - y) < 45:
                    p_motion = p["motion"]
                    p_w = p["rect"].w
                    p_rng = p["range"]
                    p_min_x = p["base_x"] - p_rng if p_motion == "horizontal" else p["base_x"]
                    p_max_x = p["base_x"] + p_w + p_rng if p_motion == "horizontal" else p["base_x"] + p_w

                    # If the movement ranges overlap too much horizontally
                    if not (eff_max_x < p_min_x - 15 or eff_min_x > p_max_x + 15):
                        overlapping = True
                        break

            if not overlapping or _ == max_attempts - 1:
                has_coin = random.random() < 0.25
                has_crystal = not has_coin and (random.random() < 0.12)

                self.platforms.append(
                    {
                        "rect": pygame.Rect(x, y, w, 8),
                        "has_coin": has_coin,
                        "has_crystal": has_crystal,
                        "motion": motion_type,
                        "base_x": float(x),
                        "base_y": float(y),
                        "offset": random.uniform(0, 6.28),
                        "speed": speed,
                        "range": rng,
                    }
                )
                break

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        self.vx = 0
        if inp.is_left_pressed():
            self.vx = -175
        if inp.is_right_pressed():
            self.vx = 175

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        # Physics
        self.vy = apply_gravity(self.vy, 540.0, dt)
        self.px += self.vx * dt
        self.py += self.vy * dt

        # Screen clamp (no wrap)
        self.px = clamp(self.px, 0.0, 320.0)

        # Update particles
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        # Smoothly update moving platforms
        for p in self.platforms:
            p["offset"] += p["speed"] * dt
            if p["motion"] == "horizontal":
                p["rect"].x = int(p["base_x"] + math.sin(p["offset"]) * p["range"])
            elif p["motion"] == "vertical":
                p["rect"].y = int(p["base_y"] + math.sin(p["offset"]) * p["range"])

        # Player collision with platforms
        player_rect = pygame.Rect(int(self.px) - 6, int(self.py) - 12, 12, 12)
        if self.vy > 0:
            for p in self.platforms:
                if (
                    player_rect.colliderect(p["rect"])
                    and abs(player_rect.bottom - p["rect"].top) < 12
                ):
                    self.vy = -310
                    self.play_sound("bounce")
                    for _ in range(5):
                        self.particles.append(
                            {
                                "x": self.px,
                                "y": self.py + 6,
                                "vx": random.uniform(-30, 30),
                                "vy": random.uniform(-15, 0),
                                "life": 0.2,
                                "color": (0, 240, 255),
                            }
                        )

                if p["has_coin"] and player_rect.colliderect(p["rect"]):
                    p["has_coin"] = False
                    self.add_score(50)
                    self.play_sound("score")

                if p["has_crystal"] and player_rect.colliderect(p["rect"]):
                    p["has_crystal"] = False
                    self.add_score(150)
                    self.play_sound("score")
                    for _ in range(8):
                        self.particles.append(
                            {
                                "x": p["rect"].centerx,
                                "y": p["rect"].y,
                                "vx": random.uniform(-40, 40),
                                "vy": random.uniform(-40, -10),
                                "life": 0.3,
                                "color": (255, 0, 255),
                            }
                        )

        # Pull the camera upward & generate new platforms
        if self.py - self.camera_y < 100:
            diff = 100 - (self.py - self.camera_y)
            self.camera_y -= diff
            self.add_score(int(diff))

            highest_platform_y = min(p["rect"].y for p in self.platforms)
            if highest_platform_y > self.camera_y - 150:
                self._spawn_platform(highest_platform_y - random.randint(45, 58))

        if self.py - self.camera_y > 250:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 10, 20))
        for x in range(0, 320, 40):
            pygame.draw.line(surface, (14, 20, 35), (x, 0), (x, 240), 1)

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        for p in self.platforms:
            ry = p["rect"].y - int(self.camera_y)
            if -30 < ry < 270:
                col = (
                    (0, 220, 255)
                    if p["motion"] == "static"
                    else (
                        (50, 255, 150) if p["motion"] == "horizontal" else (255, 180, 0)
                    )
                )
                pygame.draw.rect(
                    surface,
                    col,
                    (p["rect"].x, ry, p["rect"].w, p["rect"].h),
                    border_radius=3,
                )
                pygame.draw.rect(
                    surface,
                    (255, 255, 255),
                    (p["rect"].x, ry, p["rect"].w, 2),
                    border_radius=1,
                )

                if p["has_coin"]:
                    pygame.draw.circle(
                        surface, (255, 215, 0), (p["rect"].centerx, ry - 6), 5
                    )
                    pygame.draw.circle(
                        surface, (255, 255, 255), (p["rect"].centerx - 1, ry - 7), 2
                    )
                elif p["has_crystal"]:
                    cx, cy = p["rect"].centerx, ry - 8
                    pygame.draw.polygon(
                        surface,
                        (255, 0, 255),
                        [(cx, cy - 6), (cx + 5, cy), (cx, cy + 6), (cx - 6, cy)],
                    )
                    pygame.draw.polygon(
                        surface,
                        (255, 255, 255),
                        [(cx, cy - 3), (cx + 2, cy), (cx, cy + 3), (cx - 2, cy)],
                        1,
                    )

        py_screen = int(self.py - self.camera_y)
        pygame.draw.rect(
            surface,
            (255, 130, 0),
            (int(self.px) - 6, py_screen - 12, 12, 12),
            border_radius=3,
        )
        pygame.draw.rect(
            surface, (255, 255, 255), (int(self.px) - 3, py_screen - 9, 6, 4)
        )

        self.render_ui(surface)

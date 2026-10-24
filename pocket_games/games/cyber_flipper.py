# ==========================================
# CYBER FLIPPER v1.0
# An advanced, polished cyberpunk arcade pinball game.
# Featuring dynamic flipper physics, glowing neon bumpers,
# particle effects, launcher spring, and 3 balls.
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.games.base import BaseGame


class CyberFlipperGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Cyber Flipper")
        self.balls_left = 3
        self.bx, self.by = 290.0, 180.0
        self.bvx, self.bvy = 0.0, 0.0
        self.gravity = 450.0
        self.ball_radius = 5
        self.flipper_left_active = False
        self.flipper_right_active = False
        self.launcher_pulled = 0.0
        self.particles: list[dict] = []

        # Stylische Neon-Bumper
        self.bumpers = [
            {
                "x": 110,
                "y": 70,
                "r": 16,
                "pts": 150,
                "color": (0, 255, 200),
                "flash": 0.0,
            },
            {
                "x": 190,
                "y": 70,
                "r": 16,
                "pts": 150,
                "color": (255, 0, 120),
                "flash": 0.0,
            },
            {
                "x": 150,
                "y": 115,
                "r": 12,
                "pts": 300,
                "color": (255, 215, 0),
                "flash": 0.0,
            },
        ]
        self.reset_ball()

    def reset_ball(self) -> None:
        self.bx = 292.0
        self.by = 190.0
        self.bvx = 0.0
        self.bvy = 0.0
        self.launcher_pulled = 0.0

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        self.flipper_left_active = inp.is_left_pressed() or inp.is_key_down(pygame.K_z)
        self.flipper_right_active = inp.is_right_pressed() or inp.is_key_down(
            pygame.K_x
        )

        # Launcher-Mechanik im rechten Schusskanal (x > 280)
        if self.bx > 280 and self.by > 150:
            if inp.is_down_pressed() or inp.is_action_pressed():
                self.launcher_pulled = min(30.0, self.launcher_pulled + 40.0 * 0.016)
            elif (
                inp.is_action_just_pressed() or inp.is_up_pressed()
            ) and self.launcher_pulled > 0:
                self.bvy = -350.0 - (self.launcher_pulled * 15.0)
                self.launcher_pulled = 0.0
                self.play_sound("confirm")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over or self.paused:
            return

        # Partikel aktualisieren
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        for b in self.bumpers:
            if b["flash"] > 0:
                b["flash"] -= dt

        if not (self.bx > 280 and self.by > 170 and self.bvy == 0):
            self.bvy += self.gravity * dt
            self.bx += self.bvx * dt
            self.by += self.bvy * dt

        # Spielfeld-Wände
        if self.bx - self.ball_radius < 25:
            self.bx = 25 + self.ball_radius
            self.bvx = -self.bvx * 0.8
            self.play_sound("hit")
        elif self.bx + self.ball_radius > 275 and not (self.by > 150):
            self.bx = 275 - self.ball_radius
            self.bvx = -self.bvx * 0.8
            self.play_sound("hit")
        elif self.bx + self.ball_radius > 310:
            self.bx = 310 - self.ball_radius
            self.bvx = -self.bvx * 0.8

        if self.by - self.ball_radius < 20:
            self.by = 20 + self.ball_radius
            self.bvy = -self.bvy * 0.8
            self.play_sound("hit")

        # Flipper-Kollisionen unten (Links: 65-135, Rechts: 165-235)
        if 190 <= self.by <= 210:
            if self.flipper_left_active and 65 <= self.bx <= 135:
                self.bvy = -400.0
                self.bvx += 150.0
                self.play_sound("select")
                for _ in range(5):
                    self.particles.append(
                        {
                            "x": self.bx,
                            "y": self.by,
                            "vx": random.uniform(-50, 50),
                            "vy": random.uniform(-80, -20),
                            "life": 0.3,
                            "color": (0, 255, 200),
                        }
                    )
            elif self.flipper_right_active and 165 <= self.bx <= 235:
                self.bvy = -400.0
                self.bvx -= 150.0
                self.play_sound("select")
                for _ in range(5):
                    self.particles.append(
                        {
                            "x": self.bx,
                            "y": self.by,
                            "vx": random.uniform(-50, 50),
                            "vy": random.uniform(-80, -20),
                            "life": 0.3,
                            "color": (255, 0, 120),
                        }
                    )

        # Bumper Kollisionen
        for b in self.bumpers:
            dist = math.hypot(self.bx - b["x"], self.by - b["y"])
            if dist < self.ball_radius + b["r"]:
                nx = (self.bx - b["x"]) / dist
                ny = (self.by - b["y"]) / dist
                self.bx = b["x"] + nx * (self.ball_radius + b["r"])
                self.by = b["y"] + ny * (self.ball_radius + b["r"])
                dot = self.bvx * nx + self.bvy * ny
                self.bvx = (self.bvx - 2 * dot * nx) * 1.25
                self.bvy = (self.bvy - 2 * dot * ny) * 1.25
                self.add_score(b["pts"])
                b["flash"] = 0.2
                self.play_sound("score")
                for _ in range(8):
                    ang = random.uniform(0, math.pi * 2)
                    spd = random.uniform(50, 120)
                    self.particles.append(
                        {
                            "x": b["x"],
                            "y": b["y"],
                            "vx": math.cos(ang) * spd,
                            "vy": math.sin(ang) * spd,
                            "life": 0.4,
                            "color": b["color"],
                        }
                    )

        # Ball verloren (Drain in der Mitte unten)
        if self.by > 235:
            if 115 <= self.bx <= 185:
                self.balls_left -= 1
                self.play_sound("gameover")
                if self.balls_left <= 0:
                    self.game_over = True
                else:
                    self.reset_ball()
            else:
                self.bvy = -200.0
                self.bvx *= -0.7

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 10, 20))

        pygame.draw.line(surface, (0, 200, 255), (25, 20), (25, 215), 3)
        pygame.draw.line(surface, (0, 200, 255), (275, 20), (275, 150), 3)
        pygame.draw.line(surface, (0, 200, 255), (25, 20), (150, 5), 3)
        pygame.draw.line(surface, (0, 200, 255), (275, 20), (150, 5), 3)
        pygame.draw.line(surface, (100, 100, 150), (280, 40), (280, 220), 2)

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        for b in self.bumpers:
            col = (255, 255, 255) if b["flash"] > 0 else b["color"]
            pygame.draw.circle(surface, col, (b["x"], b["y"]), b["r"])
            pygame.draw.circle(surface, (30, 30, 50), (b["x"], b["y"]), b["r"] - 5)

        l_col = (0, 255, 255) if self.flipper_left_active else (80, 130, 160)
        r_col = (255, 0, 150) if self.flipper_right_active else (160, 80, 130)
        l_tip_y = 180 if self.flipper_left_active else 205
        r_tip_y = 180 if self.flipper_right_active else 205

        pygame.draw.line(surface, l_col, (65, 205), (125, l_tip_y), 6)
        pygame.draw.line(surface, r_col, (175, 205), (235, r_tip_y), 6)

        pygame.draw.circle(
            surface, (255, 255, 255), (int(self.bx), int(self.by)), self.ball_radius
        )
        pygame.draw.circle(
            surface, (0, 220, 255), (int(self.bx) - 1, int(self.by) - 1), 2
        )

        # Unten Info-Leiste
        pygame.draw.rect(surface, (15, 20, 35), (10, 218, 300, 18), border_radius=4)
        hud = self.font.render(
            f"BALLS: {self.balls_left}  |  CYBER PINBALL", True, (0, 255, 200)
        )
        surface.blit(hud, (160 - hud.get_width() // 2, 220))

        self.render_ui(surface)

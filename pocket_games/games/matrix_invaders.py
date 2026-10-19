# ==========================================
# MATRIX INVADERS (Cyberpunk Edition)
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.games.base import BaseGame


class MatrixInvadersGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Matrix Invaders")
        self.px = 160.0
        self.bullets: list[dict] = []
        self.bugs: list[dict] = []
        self.particles: list[dict] = []
        self.matrix_chars = [
            {"x": random.randint(10, 310), "y": random.randint(0, 240), "speed": random.randint(40, 90)}
            for _ in range(15)
        ]
        self.spawn_bugs()

    def spawn_bugs(self) -> None:
        for _ in range(7):
            self.bugs.append(
                {
                    "x": float(random.randint(30, 290)),
                    "y": float(random.randint(20, 70)),
                    "speed": float(random.randint(20, 40)),
                    "wobble": random.uniform(0, math.pi * 2),
                }
            )

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active or self.game_over:
            return

        inp = self.engine.input
        speed = 200.0
        dt = 0.016

        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            self.px = max(20.0, self.px - speed * dt)
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            self.px = min(300.0, self.px + speed * dt)

        if inp.is_key_just_pressed(pygame.K_SPACE) or inp.is_key_just_pressed(pygame.K_RETURN) or inp.mouse_clicked:
            self.bullets.append({"x": self.px - 6, "y": 205.0})
            self.bullets.append({"x": self.px + 6, "y": 205.0})
            self.engine.audio.play("select")

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        # Matrix background rain
        for c in self.matrix_chars:
            c["y"] += c["speed"] * dt
            if c["y"] > 240:
                c["y"] = -10
                c["x"] = random.randint(10, 310)

        # Particles
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        # Move bullets
        for b in self.bullets[:]:
            b["y"] -= 320.0 * dt
            if b["y"] < 10:
                self.bullets.remove(b)

        # Move bugs & handle collisions
        for bug in self.bugs[:]:
            bug["wobble"] += dt * 4
            bug["y"] += bug["speed"] * dt
            bug["x"] += math.sin(bug["wobble"]) * 30.0 * dt

            if bug["y"] >= 210:
                self.game_over = True
                self.engine.audio.play("hit")
                return

            for b in self.bullets[:]:
                if abs(b["x"] - bug["x"]) < 12 and abs(b["y"] - bug["y"]) < 12:
                    if b in self.bullets:
                        self.bullets.remove(b)
                    self.bugs.remove(bug)
                    self.add_score(30)
                    self.engine.audio.play("confirm")

                    # Spawn explosion particles (Klammerfehler behoben)
                    for _ in range(8):
                        angle = random.uniform(0, math.pi * 2)
                        spd = random.uniform(30, 90)
                        self.particles.append({
                            "x": bug["x"], "y": bug["y"],
                            "vx": math.cos(angle) * spd, "vy": math.sin(angle) * spd,
                            "life": 0.4, "color": (0, 255, 180)
                        })

                    self.bugs.append(
                        {
                            "x": float(random.randint(30, 290)),
                            "y": float(random.randint(20, 50)),
                            "speed": float(random.randint(25, 55)),
                            "wobble": random.uniform(0, math.pi * 2),
                        }
                    )
                    break

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((3, 8, 12))

        # Matrix rain effect
        for c in self.matrix_chars:
            char_surf = self.font.render("01"[int(c["y"]) % 2], True, (0, 60, 40))
            surface.blit(char_surf, (c["x"], c["y"]))

        # Particles
        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        # Player Ship
        px, py = int(self.px), 215
        pygame.draw.polygon(surface, (0, 255, 200), [(px, py - 12), (px - 10, py + 8), (px + 10, py + 8)])
        pygame.draw.rect(surface, (255, 100, 200), (px - 4, py + 2, 8, 8))
        # Engine glow
        pygame.draw.circle(surface, (0, 200, 255), (px, py + 10), random.randint(2, 4))

        # Dual Lasers
        for b in self.bullets:
            pygame.draw.rect(surface, (0, 255, 255), (int(b["x"]) - 1, int(b["y"]), 3, 10), border_radius=1)

        # Bugs (Cyber Drones)
        for bug in self.bugs:
            bx, by = int(bug["x"]), int(bug["y"])
            pygame.draw.circle(surface, (255, 20, 100), (bx, by), 10)
            pygame.draw.circle(surface, (255, 255, 255), (bx, by), 4)
            # Legs / Wings
            pygame.draw.line(surface, (255, 100, 150), (bx - 12, by - 6), (bx + 12, by + 6), 2)
            pygame.draw.line(surface, (255, 100, 150), (bx - 12, by + 6), (bx + 12, by - 6), 2)

        if self.game_over:
            go = self.title_font.render("SYSTEM BREACH", True, (255, 50, 80))
            surface.blit(go, (160 - go.get_width() // 2, 100))

        self.render_ui(surface)

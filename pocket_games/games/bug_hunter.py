# ==========================================
# BUG HUNTER v1.0
# An action-packed bug-hunting game set in a cyber circuit environment.
# Hunt and click various digital bugs (Standard, Fast, Armored, and Glitch) before they escape.
# As your score increases, difficulty ramps up through faster spawn intervals
# and unpredictable new bug types.
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.games.base import BaseGame


class BugHunterGame(BaseGame):
    """Refactored Bug Hunter using BaseGame and enhanced visual effects."""

    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Bug Hunter")
        self.bugs: list[dict] = []
        self.splats: list[dict] = []
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0
        self.difficulty_timer = 0.0
        self.spawn_bug()

    def spawn_bug(self) -> None:
        # Neuer Bug-Typ "glitch" für erhöhte Schwierigkeit hinzugefügt
        bug_type = random.choices(
            ["standard", "fast", "armored", "glitch"], weights=[40, 30, 20, 10]
        )[0]
        speed = 22.0
        hp = 1
        color = (0, 255, 120)

        if bug_type == "fast":
            speed = 50.0
            color = (255, 200, 0)
        elif bug_type == "armored":
            speed = 14.0
            hp = 2
            color = (200, 50, 255)
        elif bug_type == "glitch":
            speed = 65.0
            hp = 1
            color = (0, 240, 255)

        self.bugs.append(
            {
                "x": float(random.randint(40, 280)),
                "y": float(random.randint(40, 200)),
                "vx": float(random.choice([-1, 1]) * speed),
                "vy": float(random.choice([-1, 1]) * speed),
                "radius": 11 if bug_type == "armored" else 9,
                "type": bug_type,
                "hp": hp,
                "max_hp": hp,
                "color": color,
                "anim_phase": random.uniform(0, 6.28),
            }
        )

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active:
            return

        inp = self.engine.input
        if inp.mouse_clicked:
            vx, vy = self.get_virtual_mouse_pos()
            hit_any = False
            for b in self.bugs[:]:
                dist = math.hypot(b["x"] - vx, b["y"] - vy)
                if dist <= b["radius"] + 6:
                    b["hp"] -= 1
                    hit_any = True
                    if b["hp"] <= 0:
                        self.bugs.remove(b)
                        points = (
                            75
                            if b["type"] == "glitch"
                            else (
                                50
                                if b["type"] == "armored"
                                else (30 if b["type"] == "fast" else 20)
                            )
                        )
                        self.add_score(points)
                        self.splats.append(
                            {
                                "x": b["x"],
                                "y": b["y"],
                                "color": b["color"],
                                "timer": 2.5,
                                "radius": 12,
                            }
                        )
                        self.engine.audio.play("hit")
                    else:
                        self.engine.audio.play("select")
                    break

            if not hit_any:
                self.splats.append(
                    {
                        "x": vx,
                        "y": vy,
                        "color": (120, 120, 120),
                        "timer": 0.3,
                        "radius": 5,
                    }
                )

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        self.spawn_timer += dt
        self.difficulty_timer += dt

        # Ansteigende Schwierigkeit: Kürzeres Spawn-Intervall über Zeit
        if self.difficulty_timer > 8.0 and self.spawn_interval > 0.3:
            self.spawn_interval -= 0.04
            self.difficulty_timer = 0.0

        max_bugs = min(15, 8 + int(self.score / 150))
        if self.spawn_timer >= self.spawn_interval and len(self.bugs) < max_bugs:
            self.spawn_timer = 0.0
            self.spawn_bug()

        for b in self.bugs:
            b["x"] += b["vx"] * dt
            b["y"] += b["vy"] * dt
            b["anim_phase"] += dt * 10.0

            # Glitch-Bugs ändern unvorhersehbar ihren Kurs
            if b["type"] == "glitch" and random.random() < 0.05:
                b["vx"] += random.uniform(-15, 15)
                b["vy"] += random.uniform(-15, 15)

            if b["x"] <= 20 or b["x"] >= 300:
                b["vx"] *= -1
                b["x"] = max(20.0, min(300.0, b["x"]))
            if b["y"] <= 30 or b["y"] >= 220:
                b["vy"] *= -1
                b["y"] = max(30.0, min(220.0, b["y"]))

        for s in self.splats[:]:
            s["timer"] -= dt
            if s["timer"] <= 0:
                self.splats.remove(s)

    def render(self, surface: pygame.Surface) -> None:
        # Cyber-Leiterbahn-Hintergrund
        surface.fill((14, 18, 16))
        for x in range(0, 320, 40):
            pygame.draw.line(surface, (22, 30, 24), (x, 25), (x, 240), 1)
        for y in range(25, 240, 40):
            pygame.draw.line(surface, (22, 30, 24), (0, y), (320, y), 1)

        # Splats mit Alpha-Glow
        for s in self.splats:
            alpha = max(0, min(255, int((s["timer"] / 2.5) * 255)))
            splat_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(
                splat_surf, (*s["color"][:3], alpha), (15, 15), s["radius"]
            )
            surface.blit(splat_surf, (int(s["x"]) - 15, int(s["y"]) - 15))

        # Verbesserte Bug-Grafik mit Schatten und Animation
        for b in self.bugs:
            bx, by = int(b["x"]), int(b["y"])
            leg_offset = int(math.sin(b["anim_phase"]) * 3.5)

            pygame.draw.circle(surface, (10, 15, 12), (bx, by), b["radius"] + 2)
            pygame.draw.line(
                surface,
                (120, 180, 140),
                (bx - 14, by - 6 + leg_offset),
                (bx + 14, by + 6 - leg_offset),
                2,
            )
            pygame.draw.line(
                surface,
                (120, 180, 140),
                (bx - 14, by + 6 - leg_offset),
                (bx + 14, by - 6 + leg_offset),
                2,
            )

            pygame.draw.circle(surface, b["color"], (bx, by), b["radius"])
            pygame.draw.circle(surface, (255, 255, 255), (bx - 3, by - 3), 3)

            if b["max_hp"] > 1 and b["hp"] < b["max_hp"]:
                pygame.draw.rect(surface, (255, 0, 0), (bx - 10, by - 16, 20, 3))
                pygame.draw.rect(
                    surface,
                    (0, 255, 0),
                    (bx - 10, by - 16, int(20 * (b["hp"] / b["max_hp"])), 3),
                )

        self.render_ui(surface)

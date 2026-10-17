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
        bug_type = random.choice(["standard", "fast", "armored"])
        speed = 20.0
        hp = 1
        color = (0, 255, 120)

        if bug_type == "fast":
            speed = 45.0
            color = (255, 200, 0)
        elif bug_type == "armored":
            speed = 12.0
            hp = 2
            color = (200, 50, 255)

        self.bugs.append(
            {
                "x": float(random.randint(40, 280)),
                "y": float(random.randint(40, 200)),
                "vx": float(random.choice([-1, 1]) * speed),
                "vy": float(random.choice([-1, 1]) * speed),
                "radius": 10,
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
                        points = 50 if b["type"] == "armored" else (30 if b["type"] == "fast" else 20)
                        self.add_score(points)
                        self.splats.append({"x": b["x"], "y": b["y"], "color": b["color"], "timer": 2.0})
                        self.engine.audio.play("hit")
                    else:
                        self.engine.audio.play("select")
                    break

            if not hit_any:
                self.splats.append({"x": vx, "y": vy, "color": (100, 100, 100), "timer": 0.3})

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        self.spawn_timer += dt
        self.difficulty_timer += dt

        if self.difficulty_timer > 10.0 and self.spawn_interval > 0.4:
            self.spawn_interval -= 0.05
            self.difficulty_timer = 0.0

        if self.spawn_timer >= self.spawn_interval and len(self.bugs) < 10:
            self.spawn_timer = 0.0
            self.spawn_bug()

        for b in self.bugs:
            b["x"] += b["vx"] * dt
            b["y"] += b["vy"] * dt
            b["anim_phase"] += dt * 8.0

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
        surface.fill((20, 22, 18))

        # Splats
        for s in self.splats:
            alpha = max(0, min(255, int((s["timer"] / 2.0) * 255)))
            splat_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(splat_surf, (*s["color"][:3], alpha), (10, 10), 8)
            surface.blit(splat_surf, (int(s["x"]) - 10, int(s["y"]) - 10))

        # Bugs
        for b in self.bugs:
            bx, by = int(b["x"]), int(b["y"])
            # Legs pulse
            leg_offset = int(math.sin(b["anim_phase"]) * 3)
            pygame.draw.line(surface, (150, 150, 150), (bx - 12, by - 6 + leg_offset), (bx + 12, by + 6 - leg_offset), 2)
            pygame.draw.line(surface, (150, 150, 150), (bx - 12, by + 6 - leg_offset), (bx + 12, by - 6 + leg_offset), 2)

            pygame.draw.circle(surface, b["color"], (bx, by), b["radius"])
            pygame.draw.circle(surface, (255, 255, 255), (bx - 3, by - 3), 3)

            if b["max_hp"] > 1 and b["hp"] < b["max_hp"]:
                pygame.draw.rect(surface, (255, 0, 0), (bx - 10, by - 14, 20, 3))
                pygame.draw.rect(surface, (0, 255, 0), (bx - 10, by - 14, int(20 * (b["hp"] / b["max_hp"])), 3))

        self.render_ui(surface)

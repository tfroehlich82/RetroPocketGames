# ==========================================
# MATRIX INVADERS (Advanced Cyber Wars)
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.games.base import BaseGame


class MatrixInvadersGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Matrix Invaders")
        self.px = 160.0
        self.bullets: list[dict] = []
        self.bugs: list[dict] = []
        self.particles: list[dict] = []
        self.collectibles: list[dict] = []
        self.weapon_level = 1
        self.shield_timer = 0.0
        self.spawn_timer = 0.0
        self.matrix_chars = [
            {
                "x": random.randint(10, 310),
                "y": random.randint(0, 240),
                "speed": random.randint(50, 100),
            }
            for _ in range(18)
        ]
        self._spawn_initial_bugs()

    def _spawn_initial_bugs(self) -> None:
        for _ in range(4):
            self._add_bug()

    def _add_bug(self) -> None:
        b_type = random.choices(["drone", "speeder", "tank"], weights=[65, 25, 10])[0]
        hp = 2 if b_type == "tank" else 1
        speed = float(random.randint(25, 45)) if b_type == "speeder" else float(random.randint(12, 25))
        self.bugs.append({
            "x": float(random.randint(30, 290)),
            "y": float(random.randint(10, 40)),
            "speed": speed,
            "type": b_type,
            "hp": hp,
            "max_hp": hp,
            "wobble": random.uniform(0, math.pi * 2),
        })

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active or self.game_over:
            return

        inp = self.engine.input
        speed = 220.0
        dt = 0.016

        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            self.px = max(20.0, self.px - speed * dt)
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            self.px = min(300.0, self.px + speed * dt)

        if (
            inp.is_key_just_pressed(pygame.K_SPACE)
            or inp.is_key_just_pressed(pygame.K_RETURN)
            or inp.mouse_clicked
        ):
            if self.weapon_level == 1:
                self.bullets.append({"x": self.px - 6, "y": 205.0, "vx": 0.0})
                self.bullets.append({"x": self.px + 6, "y": 205.0, "vx": 0.0})
            elif self.weapon_level == 2:
                self.bullets.append({"x": self.px - 8, "y": 205.0, "vx": 0.0})
                self.bullets.append({"x": self.px, "y": 205.0, "vx": 0.0})
                self.bullets.append({"x": self.px + 8, "y": 205.0, "vx": 0.0})
            else:
                self.bullets.append({"x": self.px, "y": 205.0, "vx": 0.0, "beam": True})
            self.engine.audio.play("select")

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        if self.shield_timer > 0:
            self.shield_timer -= dt

        self.spawn_timer += dt
        max_bugs = min(12, 4 + int(self.elapsed_time / 15.0))
        spawn_interval = max(1.2, 3.0 - (self.elapsed_time * 0.03))
        if self.spawn_timer >= spawn_interval and len(self.bugs) < max_bugs:
            self.spawn_timer = 0.0
            self._add_bug()

        for c in self.matrix_chars:
            c["y"] += c["speed"] * dt
            if c["y"] > 240:
                c["y"] = -10
                c["x"] = random.randint(10, 310)

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        for b in self.bullets[:]:
            b["y"] -= 360.0 * dt
            if b["y"] < 10:
                self.bullets.remove(b)

        for col in self.collectibles[:]:
            col["y"] += 70.0 * dt
            if abs(self.px - col["x"]) < 16 and abs(215.0 - col["y"]) < 16:
                if col["type"] == "weapon":
                    self.weapon_level = min(3, self.weapon_level + 1)
                    self.add_score(100)
                elif col["type"] == "shield":
                    self.shield_timer = 8.0
                    self.add_score(150)
                self.collectibles.remove(col)
                self.engine.audio.play("confirm")
            elif col["y"] > 240:
                self.collectibles.remove(col)

        for bug in self.bugs[:]:
            bug["wobble"] += dt * 5
            bug["y"] += bug["speed"] * dt
            if bug["type"] == "speeder":
                bug["x"] += math.sin(bug["wobble"]) * 35.0 * dt
            else:
                bug["x"] += math.cos(bug["wobble"]) * 15.0 * dt

            if bug["y"] >= 210:
                if self.shield_timer > 0:
                    self.shield_timer = 0.0
                    self.bugs.remove(bug)
                else:
                    self.game_over = True
                    self.engine.audio.play("hit")
                    return

            for b in self.bullets[:]:
                hit_box = 14 if not b.get("beam") else 20
                if (
                    abs(b["x"] - bug["x"]) < hit_box
                    and abs(b["y"] - bug["y"]) < hit_box
                ):
                    if not b.get("beam") and b in self.bullets:
                        self.bullets.remove(b)

                    bug["hp"] -= 1
                    if bug["hp"] <= 0:
                        self.bugs.remove(bug)
                        self.add_score(40 if bug["type"] == "tank" else 25)
                        self.engine.audio.play("confirm")

                        if random.random() < 0.25:
                            ptype = random.choice(["weapon", "shield"])
                            self.collectibles.append(
                                {"x": bug["x"], "y": bug["y"], "type": ptype}
                            )

                        for _ in range(8):
                            angle = random.uniform(0, math.pi * 2)
                            spd = random.uniform(40, 100)
                            self.particles.append(
                                {
                                    "x": bug["x"],
                                    "y": bug["y"],
                                    "vx": math.cos(angle) * spd,
                                    "vy": math.sin(angle) * spd,
                                    "life": 0.4,
                                    "color": (0, 255, 180)
                                    if bug["type"] != "tank"
                                    else (255, 100, 255),
                                }
                            )
                    break

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((4, 10, 16))

        for c in self.matrix_chars:
            char_surf = self.font.render("01"[int(c["y"]) % 2], True, (0, 80, 50))
            surface.blit(char_surf, (c["x"], c["y"]))

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        for col in self.collectibles:
            cx, cy = int(col["x"]), int(col["y"])
            col_color = (0, 255, 255) if col["type"] == "weapon" else (50, 255, 100)
            pygame.draw.circle(surface, col_color, (cx, cy), 9)
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 4)

        px, py = int(self.px), 215
        pygame.draw.polygon(
            surface,
            (0, 255, 220),
            [(px, py - 14), (px - 11, py + 10), (px + 11, py + 10)],
        )
        pygame.draw.rect(surface, (255, 100, 220), (px - 4, py + 2, 8, 8))
        if self.shield_timer > 0:
            pygame.draw.circle(surface, (0, 200, 255), (px, py), 22, 2)

        for b in self.bullets:
            if b.get("beam"):
                pygame.draw.rect(
                    surface, (0, 255, 255), (int(b["x"]) - 2, int(b["y"]) - 10, 4, 20)
                )
            else:
                pygame.draw.rect(
                    surface,
                    (0, 255, 255),
                    (int(b["x"]) - 1, int(b["y"]), 3, 10),
                    border_radius=1,
                )

        for bug in self.bugs:
            bx, by = int(bug["x"]), int(bug["y"])
            if bug["type"] == "drone":
                pygame.draw.circle(surface, (255, 30, 100), (bx, by), 10)
                pygame.draw.circle(surface, (255, 255, 255), (bx, by), 4)
            elif bug["type"] == "speeder":
                pygame.draw.polygon(
                    surface,
                    (255, 200, 0),
                    [(bx, by - 12), (bx - 10, by + 8), (bx + 10, by + 8)],
                )
            else:
                pygame.draw.rect(
                    surface, (180, 40, 220), (bx - 12, by - 12, 24, 24), border_radius=4
                )
                pygame.draw.rect(surface, (255, 255, 255), (bx - 6, by - 6, 12, 12), 2)

        if self.game_over:
            go = self.title_font.render("SYSTEM BREACH", True, (255, 50, 80))
            surface.blit(go, (160 - go.get_width() // 2, 100))

        self.render_ui(surface)

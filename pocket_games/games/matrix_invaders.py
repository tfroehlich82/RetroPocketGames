# ==========================================
# MATRIX INVADERS v1.0
# A futuristic arcade shooter inspired by classic Space Invaders.
# Defend against marching rows of cyber invaders advancing
# row by row towards the surface. Collect weapon upgrades
# and energy shields while surviving multiple challenging
# waves featuring tactical rest breaks.
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
        self.player_hp = 5  # Spieler benötigt zu Beginn 5 Treffer
        self.bullets: list[dict] = []
        self.enemy_bullets: list[dict] = []
        self.bugs: list[dict] = []
        self.bunkers: list[dict] = []
        self.particles: list[dict] = []
        self.collectibles: list[dict] = []
        self.weapon_level = 1
        self.shield_timer = 0.0
        self.wave = 1
        self.formation_dir = 1.0
        self.formation_speed = 30.0
        self.rest_timer = 0.0
        self.matrix_chars = [
            {
                "x": random.randint(10, 310),
                "y": random.randint(0, 240),
                "speed": random.randint(40, 80),
            }
            for _ in range(15)
        ]
        self._start_wave()

    def _start_wave(self) -> None:
        self.bugs.clear()
        self.enemy_bullets.clear()

        cols = min(8, 4 + self.wave)
        rows = min(5, 3 + (self.wave // 2))
        start_x = max(20, 160 - (cols * 22))
        start_y = 45
        spacing_x = 42
        spacing_y = 26

        for r in range(rows):
            if r == 0 and self.wave >= 2:
                b_type = "elite"
            elif r == 0:
                b_type = "tank"
            elif r == 1:
                b_type = "speeder"
            else:
                b_type = "drone"

            # HP skalieren mit Level: Tanks und Elites benötigen 2-3 Treffer
            base_hp = 3 if b_type == "elite" else (2 if b_type == "tank" else 1)
            hp = min(3, base_hp + (self.wave // 2))

            for c in range(cols):
                self.bugs.append(
                    {
                        "x": float(start_x + c * spacing_x),
                        "y": float(start_y + r * spacing_y),
                        "type": b_type,
                        "hp": hp,
                        "max_hp": hp,
                        # Nur Tanks, Speeders und Elites können schiessen (Drones nicht)
                        "can_shoot": b_type in ["tank", "elite", "speeder"],
                        "shoot_cooldown": random.uniform(2.0, 5.0),
                    }
                )

        self.formation_speed = 25.0 + (self.wave * 4.0)

        self.bunkers.clear()
        if self.wave >= 2:
            bunker_xs = [70, 160, 250]
            for bx in bunker_xs:
                for bx_offset in [-12, 0, 12]:
                    self.bunkers.append(
                        {"rect": pygame.Rect(bx + bx_offset - 5, 180, 10, 10), "hp": 3}
                    )

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active or self.game_over or self.rest_timer > 0:
            return

        inp = self.engine.input
        speed = 220.0
        dt = 0.016

        if inp.is_left_pressed():
            self.px = max(20.0, self.px - speed * dt)
        if inp.is_right_pressed():
            self.px = min(300.0, self.px + speed * dt)

        if inp.is_action_just_pressed():
            if self.weapon_level == 1:
                self.bullets.append({"x": self.px, "y": 205.0})
            elif self.weapon_level == 2:
                self.bullets.append({"x": self.px - 6, "y": 205.0})
                self.bullets.append({"x": self.px + 6, "y": 205.0})
            elif self.weapon_level == 3:
                self.bullets.append({"x": self.px - 10, "y": 205.0})
                self.bullets.append({"x": self.px, "y": 205.0})
                self.bullets.append({"x": self.px + 10, "y": 205.0})
            else:
                self.bullets.append({"x": self.px, "y": 205.0, "beam": True})
                self.bullets.append({"x": self.px - 12, "y": 205.0})
                self.bullets.append({"x": self.px + 12, "y": 205.0})
            self.engine.audio.play("select")

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        if self.rest_timer > 0:
            self.rest_timer -= dt
            return

        if self.shield_timer > 0:
            self.shield_timer -= dt

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
            b["y"] -= 420.0 * dt
            if b["y"] < 10:
                self.bullets.remove(b)

        for eb in self.enemy_bullets[:]:
            eb["y"] += eb["speed"] * dt

            eb_rect = pygame.Rect(int(eb["x"]) - 2, int(eb["y"]) - 4, 4, 8)
            bunker_hit = False
            for bk in self.bunkers[:]:
                if bk["rect"].colliderect(eb_rect):
                    bk["hp"] -= 1
                    if bk["hp"] <= 0:
                        self.bunkers.remove(bk)
                    bunker_hit = True
                    break

            if bunker_hit:
                if eb in self.enemy_bullets:
                    self.enemy_bullets.remove(eb)
                continue

            if abs(eb["x"] - self.px) < 12 and abs(eb["y"] - 215.0) < 14:
                if eb in self.enemy_bullets:
                    self.enemy_bullets.remove(eb)

                if self.shield_timer > 0:
                    self.shield_timer = 0.0
                    self.engine.audio.play("confirm")
                else:
                    self.player_hp -= 1
                    self.play_sound("hit")
                    if self.player_hp <= 0:
                        self.game_over = True
                        self.play_sound("gameover")
                        return
                continue

            if eb["y"] > 240:
                self.enemy_bullets.remove(eb)

        for col in self.collectibles[:]:
            col["y"] += 70.0 * dt
            if abs(self.px - col["x"]) < 16 and abs(215.0 - col["y"]) < 16:
                if col["type"] == "weapon":
                    self.weapon_level = min(4, self.weapon_level + 1)
                    self.add_score(100)
                elif col["type"] == "shield":
                    self.shield_timer = 8.0
                    self.add_score(150)
                self.collectibles.remove(col)
                self.engine.audio.play("confirm")
            elif col["y"] > 240:
                self.collectibles.remove(col)

        edge_reached = False
        for bug in self.bugs:
            bug["x"] += self.formation_speed * self.formation_dir * dt
            if bug["x"] > 295 or bug["x"] < 25:
                edge_reached = True

            # Nur schussfähige Einheiten eröffnen das Feuer
            if bug.get("can_shoot"):
                bug["shoot_cooldown"] -= dt
                if bug["shoot_cooldown"] <= 0:
                    bug["shoot_cooldown"] = random.uniform(2.5, 6.0) - min(
                        1.5, self.wave * 0.2
                    )
                    self.enemy_bullets.append(
                        {
                            "x": bug["x"],
                            "y": bug["y"] + 8,
                            "speed": 130.0 + (self.wave * 10.0),
                        }
                    )

        if edge_reached:
            self.formation_dir *= -1.0
            for bug in self.bugs:
                bug["y"] += 10.0

        if len(self.bugs) == 0:
            self.wave += 1
            self.add_score(400 * self.wave)
            self.rest_timer = 2.0
            self.play_sound("confirm")
            self._start_wave()
            return

        for bug in self.bugs[:]:
            if bug["y"] >= 200:
                self.game_over = True
                self.play_sound("gameover")
                return

            if abs(bug["x"] - self.px) < 16 and abs(bug["y"] - 215.0) < 16:
                self.game_over = True
                self.play_sound("gameover")
                return

            for b in self.bullets[:]:
                hit_box = 12 if not b.get("beam") else 20
                if (
                    abs(b["x"] - bug["x"]) < hit_box
                    and abs(b["y"] - bug["y"]) < hit_box
                ):
                    if not b.get("beam") and b in self.bullets:
                        self.bullets.remove(b)

                    bug["hp"] -= 1
                    if bug["hp"] <= 0:
                        self.bugs.remove(bug)
                        pts = (
                            60
                            if bug["type"] == "elite"
                            else (40 if bug["type"] == "tank" else 25)
                        )
                        self.add_score(pts)
                        self.engine.audio.play("confirm")

                        if random.random() < 0.3:
                            ptype = random.choice(["weapon", "shield"])
                            self.collectibles.append(
                                {"x": bug["x"], "y": bug["y"], "type": ptype}
                            )

                        for _ in range(6):
                            angle = random.uniform(0, math.pi * 2)
                            spd = random.uniform(30, 80)
                            self.particles.append(
                                {
                                    "x": bug["x"],
                                    "y": bug["y"],
                                    "vx": math.cos(angle) * spd,
                                    "vy": math.sin(angle) * spd,
                                    "life": 0.3,
                                    "color": (0, 255, 180),
                                }
                            )
                    else:
                        self.engine.audio.play("select")
                    break

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((4, 10, 16))

        for c in self.matrix_chars:
            char_surf = self.font.render("01"[int(c["y"]) % 2], True, (0, 70, 40))
            surface.blit(char_surf, (c["x"], c["y"]))

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        for bk in self.bunkers:
            col = (
                (0, 180, 100)
                if bk["hp"] >= 3
                else ((180, 180, 0) if bk["hp"] == 2 else (180, 50, 50))
            )
            pygame.draw.rect(surface, col, bk["rect"], border_radius=2)

        for col in self.collectibles:
            cx, cy = int(col["x"]), int(col["y"])
            col_color = (0, 255, 255) if col["type"] == "weapon" else (50, 255, 100)
            pygame.draw.circle(surface, col_color, (cx, cy), 8)
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 3)

        px, py = int(self.px), 215
        pygame.draw.polygon(
            surface,
            (0, 255, 220),
            [(px, py - 15), (px - 12, py + 12), (px + 12, py + 12)],
        )
        pygame.draw.rect(surface, (255, 100, 220), (px - 3, py + 2, 6, 8))
        pygame.draw.line(surface, (255, 255, 255), (px, py - 15), (px, py - 8), 2)
        if self.shield_timer > 0:
            pygame.draw.circle(surface, (0, 200, 255), (px, py), 22, 2)

        for b in self.bullets:
            if b.get("beam"):
                pygame.draw.rect(
                    surface, (0, 255, 255), (int(b["x"]) - 2, int(b["y"]) - 10, 4, 18)
                )
            else:
                pygame.draw.rect(
                    surface,
                    (0, 255, 255),
                    (int(b["x"]) - 1, int(b["y"]), 3, 10),
                    border_radius=1,
                )

        for eb in self.enemy_bullets:
            pygame.draw.rect(
                surface,
                (255, 50, 80),
                (int(eb["x"]) - 1, int(eb["y"]), 3, 8),
                border_radius=1,
            )

        for bug in self.bugs:
            bx, by = int(bug["x"]), int(bug["y"])
            if bug["type"] == "drone":
                pygame.draw.rect(
                    surface, (255, 40, 120), (bx - 8, by - 6, 16, 12), border_radius=3
                )
                pygame.draw.rect(surface, (255, 255, 255), (bx - 4, by - 3, 2, 2))
                pygame.draw.rect(surface, (255, 255, 255), (bx + 2, by - 3, 2, 2))
            elif bug["type"] == "speeder":
                pygame.draw.polygon(
                    surface,
                    (255, 200, 0),
                    [(bx, by - 9), (bx - 10, by + 6), (bx + 10, by + 6)],
                )
                pygame.draw.circle(surface, (255, 255, 255), (bx, by), 2)
            elif bug["type"] == "elite":
                pygame.draw.polygon(
                    surface,
                    (0, 255, 180),
                    [(bx, by - 10), (bx - 12, by + 4), (bx + 12, by + 4)],
                )
                pygame.draw.rect(surface, (255, 255, 255), (bx - 3, by - 2, 6, 4))
            else:
                pygame.draw.rect(
                    surface, (180, 50, 240), (bx - 12, by - 10, 24, 20), border_radius=4
                )
                pygame.draw.rect(surface, (255, 255, 255), (bx - 6, by - 5, 4, 4))
                pygame.draw.rect(surface, (255, 255, 255), (bx + 2, by - 5, 4, 4))

        # UI: Anzeige für Welle, Waffen-Level und Spieler-HP (Leben)
        hud_txt = self.font.render(
            f"WAVE {self.wave} | HP: {self.player_hp}/5 | WPN: {self.weapon_level}",
            True,
            (0, 255, 200),
        )
        surface.blit(hud_txt, (160 - hud_txt.get_width() // 2, 5))

        if self.rest_timer > 0:
            rest_txt = self.title_font.render(
                f"PREPARE FOR WAVE {self.wave}...", True, (255, 215, 0)
            )
            surface.blit(rest_txt, (160 - rest_txt.get_width() // 2, 110))

        if self.game_over:
            go = self.title_font.render("SYSTEM BREACH", True, (255, 50, 80))
            surface.blit(go, (160 - go.get_width() // 2, 100))

        self.render_ui(surface)

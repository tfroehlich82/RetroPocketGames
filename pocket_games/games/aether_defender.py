# ==========================================
# AETHER DEFENDER v1.1
# A fast-paced action game in a cyber-core design.
# Skillfully switch between 2 distinct color states (Cyan and Magenta)
# to intercept incoming enemies of the matching color. A smoothly increasing
# difficulty curve ensure long-lasting and engaging gameplay.
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.games.base import BaseGame


class AetherDefenderGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Aether Defender")
        self.px = 160.0
        self.color_state = 0  # 0: Cyan, 1: Magenta (2 Farben reichen völlig)
        self.enemies = []
        self.particles = []
        self.spawn_timer = 0.0
        self.time_counter = 0.0
        self.lives = 3         # Spieler startet mit 3 Leben
        self.invulnerable_timer = 0.0  # Kurze Unverwundbarkeit nach Treffer

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            self.px = max(25, self.px - 190 * 0.016)
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            self.px = min(295, self.px + 190 * 0.016)
        if (
            inp.is_key_just_pressed(pygame.K_SPACE)
            or inp.mouse_clicked
            or inp.is_key_just_pressed(pygame.K_UP)
        ):
            # Nur 2 Farbzustände (0 und 1)
            self.color_state = (self.color_state + 1) % 2
            self.play_sound("bounce")
            colors_list = [(0, 255, 255), (255, 40, 150)]
            curr_col = colors_list[self.color_state]
            for _ in range(6):
                ang = random.uniform(0, math.pi * 2)
                self.particles.append(
                    {
                        "x": self.px,
                        "y": 205,
                        "vx": math.cos(ang) * 60,
                        "vy": math.sin(ang) * 60,
                        "life": 0.35,
                        "color": curr_col,
                    }
                )

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.time_counter += dt
        self.spawn_timer += dt

        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        dynamic_spawn_interval = max(0.35, 0.9 - (self.elapsed_time * 0.008))
        if self.spawn_timer > dynamic_spawn_interval:
            self.spawn_timer = 0.0
            speed_boost = min(45.0, self.elapsed_time * 0.8)
            # Nur noch Feinde in 2 Farben (0 oder 1)
            self.enemies.append(
                {
                    "x": random.randint(30, 290),
                    "y": -15,
                    "color": random.randint(0, 1),
                    "speed": random.uniform(70, 105) + speed_boost,
                }
            )

        p_rect = pygame.Rect(int(self.px) - 14, 195, 28, 20)
        for e in self.enemies[:]:
            e["y"] += e["speed"] * dt
            e_rect = pygame.Rect(e["x"] - 10, int(e["y"]) - 10, 20, 20)

            if p_rect.colliderect(e_rect):
                if e["color"] == self.color_state:
                    self.enemies.remove(e)
                    self.add_score(40)
                    self.play_sound("score")
                    for _ in range(8):
                        ang = random.uniform(0, math.pi * 2)
                        self.particles.append(
                            {
                                "x": e["x"],
                                "y": e["y"],
                                "vx": math.cos(ang) * 70,
                                "vy": math.sin(ang) * 70,
                                "life": 0.3,
                                "color": (255, 255, 255),
                            }
                        )
                else:
                    if self.invulnerable_timer <= 0:
                        self.lives -= 1
                        self.enemies.remove(e)
                        if self.lives <= 0:
                            self.game_over = True
                            self.play_sound("gameover")
                        else:
                            self.invulnerable_timer = 1.5  # 1.5s Unverwundbarkeit nach Treffer
                            self.play_sound("bounce")

            if e["y"] > 250:
                self.enemies.remove(e)

    def render_ui(self, surface: pygame.Surface) -> None:
        super().render_ui(surface)
        # Leben anzeigen
        lives_txt = self.font.render(f"LIVES: {self.lives}", True, (255, 50, 80))
        surface.blit(lives_txt, (230, 5))

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 6, 18))

        for x in range(0, 320, 40):
            pygame.draw.line(surface, (22, 16, 45), (x, 0), (x, 240), 1)
        for y in range(0, 240, 40):
            pygame.draw.line(surface, (16, 12, 35), (0, y), (320, y), 1)

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        color_map = [
            (0, 240, 255),   # Cyan
            (255, 40, 150),  # Magenta
        ]
        p_color = color_map[self.color_state]
        px, py = int(self.px), 205

        # Blinken bei Unverwundbarkeit
        if self.invulnerable_timer <= 0 or int(pygame.time.get_ticks() / 100) % 2 == 0:
            pygame.draw.polygon(
                surface, p_color, [(px, py - 14), (px - 14, py + 10), (px + 14, py + 10)]
            )
            pygame.draw.rect(
                surface, (255, 255, 255), (px - 4, py - 2, 8, 8), border_radius=2
            )
            pygame.draw.circle(surface, p_color, (px, py + 12), 5)

        for e in self.enemies:
            ex, ey = int(e["x"]), int(e["y"])
            e_color = color_map[e["color"]]
            pygame.draw.circle(surface, e_color, (ex, ey), 11)
            pygame.draw.circle(surface, (255, 255, 255), (ex, ey), 5)
            pygame.draw.circle(surface, e_color, (ex, ey), 15, 1)

        self.render_ui(surface)

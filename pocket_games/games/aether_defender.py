# ==========================================
# AETHER DEFENDER v1.0
# A fast-paced action game in a cyber-core design.
# Skillfully switch between 3 distinct color states (Cyan, Magenta, and Yellow)
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
        self.color_state = 0  # 0: Cyan, 1: Magenta, (ab 30s auch 2: Yellow)
        self.enemies = []
        self.particles = []
        self.spawn_timer = 0.0
        self.time_counter = 0.0

    @property
    def max_colors(self) -> int:
        # Nach 30 Sekunden schaltet das Spiel auf 3 Farben um
        return 3 if self.elapsed_time >= 30.0 else 2

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
            limit = self.max_colors
            self.color_state = (self.color_state + 1) % limit
            self.play_sound("bounce")
            colors_list = [(0, 255, 255), (255, 40, 150), (255, 220, 0)]
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

        # Falls der Spieler bei 3 Farben war und durch Reset/Moduswechsel außerhalb liegt, korrigieren
        if self.color_state >= self.max_colors:
            self.color_state = 0

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
            # Feinde basieren auf der aktuellen Anzahl aktiver Farben
            limit = self.max_colors
            self.enemies.append(
                {
                    "x": random.randint(30, 290),
                    "y": -15,
                    "color": random.randint(0, limit - 1),
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
                    self.game_over = True
                    self.play_sound("gameover")

            if e["y"] > 250:
                self.enemies.remove(e)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 6, 18))

        for x in range(0, 320, 40):
            pygame.draw.line(surface, (22, 16, 45), (x, 0), (x, 240), 1)
        for y in range(0, 240, 40):
            pygame.draw.line(surface, (16, 12, 35), (0, y), (320, y), 1)

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        color_map = [
            (0, 240, 255),  # Cyan
            (255, 40, 150),  # Magenta
            (255, 220, 0),  # Yellow (ab 30s)
        ]
        p_color = color_map[self.color_state]
        px, py = int(self.px), 205

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

        # Dezenten Hinweis anzeigen, wenn die 3. Farbe aktiv ist
        if self.elapsed_time >= 30.0:
            mode_txt = self.font.render("3-COLOR MODE", True, (255, 220, 0))
            surface.blit(mode_txt, (320 - mode_txt.get_width() - 10, 5))

        self.render_ui(surface)

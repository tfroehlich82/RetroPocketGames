# ==========================================
# AETHER DEFENDER (Cyber-Core Edition)
# ==========================================
import math
import random

import pygame

from pocket_games.games.base import BaseGame


class AetherDefenderGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Aether Defender")
        self.px = 160.0
        self.color_state = 0  # 0: Cyan, 1: Magenta
        self.enemies = []
        self.particles = []
        self.spawn_timer = 0.0
        self.time_counter = 0.0

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            self.px = max(25, self.px - 180 * 0.016)
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            self.px = min(295, self.px + 180 * 0.016)
        if inp.is_key_just_pressed(pygame.K_SPACE) or inp.mouse_clicked or inp.is_key_just_pressed(pygame.K_UP):
            self.color_state = 1 - self.color_state
            self.play_sound("bounce")
            for _ in range(6):
                ang = random.uniform(0, math.pi * 2)
                self.particles.append({
                    "x": self.px, "y": 205,
                    "vx": math.cos(ang) * 50, "vy": math.sin(ang) * 50,
                    "life": 0.3, "color": (0, 255, 255) if self.color_state == 0 else (255, 50, 150)
                })

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.time_counter += dt
        self.spawn_timer += dt

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        if self.spawn_timer > 0.7:
            self.spawn_timer = 0.0
            self.enemies.append({
                "x": random.randint(30, 290),
                "y": -15,
                "color": random.choice([0, 1]),
                "speed": random.uniform(80, 120)
            })

        p_rect = pygame.Rect(int(self.px) - 14, 195, 28, 20)
        for e in self.enemies[:]:
            e["y"] += e["speed"] * dt
            e_rect = pygame.Rect(e["x"] - 10, int(e["y"]) - 10, 20, 20)

            if p_rect.colliderect(e_rect):
                if e["color"] == self.color_state:
                    self.enemies.remove(e)
                    self.add_score(35)
                    self.play_sound("score")
                    for _ in range(8):
                        ang = random.uniform(0, math.pi * 2)
                        self.particles.append({
                            "x": e["x"], "y": e["y"],
                            "vx": math.cos(ang) * 60, "vy": math.sin(ang) * 60,
                            "life": 0.25, "color": (255, 255, 255)
                        })
                else:
                    self.game_over = True
                    self.play_sound("gameover")

            if e["y"] > 250:
                self.enemies.remove(e)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 6, 18))

        for x in range(0, 320, 40):
            pygame.draw.line(surface, (18, 14, 35), (x, 0), (x, 240), 1)

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        p_color = (0, 240, 255) if self.color_state == 0 else (255, 40, 150)
        px, py = int(self.px), 205
        pygame.draw.polygon(surface, p_color, [(px, py - 12), (px - 14, py + 10), (px + 14, py + 10)])
        pygame.draw.rect(surface, (255, 255, 255), (px - 4, py - 2, 8, 8), border_radius=2)
        pygame.draw.circle(surface, p_color, (px, py + 12), 4)

        for e in self.enemies:
            ex, ey = int(e["x"]), int(e["y"])
            e_color = (0, 220, 255) if e["color"] == 0 else (255, 50, 150)
            pygame.draw.circle(surface, e_color, (ex, ey), 11)
            pygame.draw.circle(surface, (255, 255, 255), (ex, ey), 5)
            pygame.draw.circle(surface, e_color, (ex, ey), 14, 1)

        self.render_ui(surface)

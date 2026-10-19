# ==========================================
# SUB ZERO MINER (Deep Ice Core Edition)
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class SubZeroMinerGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Sub-Zero Miner")
        self.px, self.py = 160.0, 30.0
        self.speed = 120.0
        self.oxygen = 100.0

        self.blocks: list[dict] = []
        self.items: list[dict] = []
        self._generate_layer(0, 240)

    def _generate_layer(self, min_y: int, max_y: int) -> None:
        for y in range(min_y, max_y, 20):
            for x in range(20, 300, 20):
                if random.random() < 0.65:
                    self.blocks.append({"rect": pygame.Rect(x, y, 18, 18), "hp": random.choice([1, 2, 3])})
                elif random.random() < 0.12:
                    self.items.append({"rect": pygame.Rect(x + 3, y + 3, 12, 12), "type": random.choice(["ice", "o2"])})

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        dt = 0.016
        dx, dy = 0.0, 0.0

        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            dx -= self.speed * dt
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            dx += self.speed * dt
        if inp.is_key_down(pygame.K_UP) or inp.is_key_down(pygame.K_w):
            dy -= self.speed * dt
        if inp.is_key_down(pygame.K_DOWN) or inp.is_key_down(pygame.K_s):
            dy += self.speed * dt

        new_rect_x = pygame.Rect(int(self.px + dx), int(self.py), 14, 14)
        if not any(new_rect_x.colliderect(b["rect"]) for b in self.blocks):
            self.px += dx

        new_rect_y = pygame.Rect(int(self.px), int(self.py + dy), 14, 14)
        if not any(new_rect_y.colliderect(b["rect"]) for b in self.blocks):
            self.py += dy

        if inp.mouse_clicked:
            mx, my = self.get_virtual_mouse_pos()
            for b in self.blocks[:]:
                if b["rect"].collidepoint(mx, my) and math_dist((self.px, self.py), (mx, my)) < 45:
                    b["hp"] -= 1
                    self.play_sound("hit")
                    if b["hp"] <= 0:
                        self.blocks.remove(b)
                        self.add_score(10)

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over or self.paused:
            return

        drain_rate = 6.0 + (self.elapsed_time * 0.35) + (self.py * 0.015)
        self.oxygen -= drain_rate * dt

        if self.oxygen <= 0:
            self.oxygen = 0
            self.game_over = True
            self.play_sound("gameover")

        p_rect = pygame.Rect(int(self.px), int(self.py), 14, 14)
        for item in self.items[:]:
            if p_rect.colliderect(item["rect"]):
                if item["type"] == "o2":
                    self.oxygen = min(100.0, self.oxygen + 25.0)
                    self.play_sound("coin")
                else:
                    self.add_score(40)
                    self.play_sound("score")
                self.items.remove(item)

        if self.py > len(self.blocks) * 2:
            self._generate_layer(240, 480)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 15, 28))

        for b in self.blocks:
            r = b["rect"]
            color = (60, 100, 140) if b["hp"] == 1 else ((40, 80, 120) if b["hp"] == 2 else (20, 60, 100))
            pygame.draw.rect(surface, color, r, border_radius=2)
            pygame.draw.rect(surface, (100, 150, 200), r, 1, border_radius=2)

        for item in self.items:
            r = item["rect"]
            color = (0, 220, 255) if item["type"] == "o2" else (255, 215, 0)
            pygame.draw.rect(surface, color, r, border_radius=3)

        pygame.draw.rect(surface, (255, 180, 0), (int(self.px), int(self.py), 14, 14), border_radius=3)

        pygame.draw.rect(surface, (30, 30, 40), (10, 224, 100, 10), border_radius=3)
        o2_w = int(100 * (self.oxygen / 100.0))
        if o2_w > 0:
            o2_color = (0, 200, 255) if self.oxygen > 30 else (255, 50, 50)
            pygame.draw.rect(surface, o2_color, (10, 224, o2_w, 10), border_radius=3)

        self.render_ui(surface)


def math_dist(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[2 if 2 < len(p2) else 1]) ** 2) ** 0.5

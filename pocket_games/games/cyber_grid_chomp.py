# ==========================================
# CYBER GRID CHOMP v1.0
# A neon-infused cyberpunk Pac-Man clone optimized for 320x240.
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.core.physics import check_circle_collision, clamp
from pocket_games.games.base import BaseGame


class CyberGridChompGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Cyber Grid Chomp")
        self.lives = 3
        self.level = 1
        self.score_in_level = 0
        self.invulnerable_timer = 0.0
        self.overclock_timer = 0.0

        self.px, self.py = 160.0, 110.0
        self.pdir_x, self.pdir_y = 0.0, 0.0
        self.next_dir_x, self.next_dir_y = 0.0, 0.0
        self.speed = 90.0

        self.bits: list[dict] = []
        self.power_pills: list[dict] = []
        self.phantoms: list[dict] = []
        self.walls: list[pygame.Rect] = []

        self._setup_level()

    def _setup_level(self) -> None:
        self.px, self.py = 160.0, 110.0
        self.pdir_x, self.pdir_y = 0.0, 0.0
        self.next_dir_x, self.next_dir_y = 0.0, 0.0
        self.overclock_timer = 0.0

        self.walls = [
            pygame.Rect(15, 15, 290, 10),
            pygame.Rect(15, 195, 290, 10),
            pygame.Rect(15, 15, 10, 190),
            pygame.Rect(295, 15, 10, 190),
            pygame.Rect(45, 45, 50, 20),
            pygame.Rect(115, 45, 90, 20),
            pygame.Rect(225, 45, 50, 20),
            pygame.Rect(45, 85, 20, 50),
            pygame.Rect(255, 85, 20, 50),
            pygame.Rect(115, 85, 90, 20),
            pygame.Rect(45, 155, 50, 20),
            pygame.Rect(115, 155, 90, 20),
            pygame.Rect(225, 155, 50, 20),
        ]

        self.bits = []
        for x in range(30, 290, 18):
            for y in range(30, 190, 18):
                bit_rect = pygame.Rect(x, y, 4, 4)
                if not any(bit_rect.colliderect(w) for w in self.walls):
                    self.bits.append({"x": x + 2, "y": y + 2})

        self.power_pills = [
            {"x": 30, "y": 30},
            {"x": 290, "y": 30},
            {"x": 30, "y": 180},
            {"x": 290, "y": 180},
        ]

        phantom_count = min(4, 2 + self.level)
        colors = [(255, 50, 80), (255, 150, 0), (0, 220, 255), (200, 50, 255)]
        self.phantoms = []
        spawns = [(160, 90), (140, 110), (180, 110), (160, 130)]
        for i in range(phantom_count):
            sx, sy = spawns[i % len(spawns)]
            self.phantoms.append({
                "x": float(sx), "y": float(sy),
                "vx": random.choice([-50.0, 50.0]),
                "vy": random.choice([-50.0, 50.0]),
                "color": colors[i % len(colors)]
            })

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.is_left_pressed():
            self.next_dir_x, self.next_dir_y = -1.0, 0.0
        elif inp.is_right_pressed():
            self.next_dir_x, self.next_dir_y = 1.0, 0.0
        elif inp.is_up_pressed():
            self.next_dir_x, self.next_dir_y = 0.0, -1.0
        elif inp.is_down_pressed():
            self.next_dir_x, self.next_dir_y = 0.0, 1.0

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over or self.paused:
            return

        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer -= dt
        if self.overclock_timer > 0.0:
            self.overclock_timer -= dt

        if self.next_dir_x != 0 or self.next_dir_y != 0:
            test_x = self.px + self.next_dir_x * self.speed * dt * 1.5
            test_y = self.py + self.next_dir_y * self.speed * dt * 1.5
            test_rect = pygame.Rect(int(test_x - 6), int(test_y - 6), 12, 12)
            if not any(test_rect.colliderect(w) for w in self.walls):
                self.pdir_x, self.pdir_y = self.next_dir_x, self.next_dir_y

        new_x = self.px + self.pdir_x * self.speed * dt
        new_y = self.py + self.pdir_y * self.speed * dt
        player_rect = pygame.Rect(int(new_x - 6), int(new_y - 6), 12, 12)

        if not any(player_rect.colliderect(w) for w in self.walls):
            self.px, self.py = new_x, new_y
        else:
            self.pdir_x, self.pdir_y = 0.0, 0.0

        if self.px < 15:
            self.px = 290.0
        elif self.px > 295:
            self.px = 20.0

        for b in self.bits[:]:
            if check_circle_collision(self.px, self.py, 6.0, float(b["x"]), float(b["y"]), 4.0):
                self.bits.remove(b)
                self.add_score(10)
                self.play_sound("score")

        for p in self.power_pills[:]:
            if check_circle_collision(self.px, self.py, 8.0, float(p["x"]), float(p["y"]), 6.0):
                self.power_pills.remove(p)
                self.overclock_timer = 7.0
                self.add_score(100)
                self.play_sound("confirm")

        phantom_speed = 60.0 if self.overclock_timer <= 0 else 35.0
        for ph in self.phantoms:
            ph["x"] += ph["vx"] * phantom_speed * dt / 50.0
            ph["y"] += ph["vy"] * phantom_speed * dt / 50.0

            ph_rect = pygame.Rect(int(ph["x"] - 6), int(ph["y"] - 6), 12, 12)
            if any(ph_rect.colliderect(w) for w in self.walls) or ph["x"] < 20 or ph["x"] > 300 or ph["y"] < 20 or ph["y"] > 200:
                ph["vx"] = random.choice([-50.0, -30.0, 30.0, 50.0])
                ph["vy"] = random.choice([-50.0, -30.0, 30.0, 50.0])
                ph["x"] = clamp(ph["x"], 25.0, 295.0)
                ph["y"] = clamp(ph["y"], 25.0, 195.0)

            if check_circle_collision(self.px, self.py, 8.0, ph["x"], ph["y"], 8.0):
                if self.overclock_timer > 0:
                    ph["x"], ph["y"] = 160.0, 110.0
                    self.add_score(300)
                    self.play_sound("confirm")
                elif self.invulnerable_timer <= 0:
                    self.lives -= 1
                    self.play_sound("hit")
                    if self.lives <= 0:
                        self.game_over = True
                        self.play_sound("gameover")
                    else:
                        self.px, self.py = 160.0, 110.0
                        self.pdir_x, self.pdir_y = 0.0, 0.0
                        self.invulnerable_timer = 2.0

        if not self.bits:
            self.level += 1
            self.add_score(1000)
            self.play_sound("confirm")
            if self.level > 3:
                self.game_won = True
            else:
                self._setup_level()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 10, 22))

        for w in self.walls:
            pygame.draw.rect(surface, (0, 150, 255), w, border_radius=3)
            pygame.draw.rect(surface, (0, 220, 255), w, 1, border_radius=3)

        for b in self.bits:
            pygame.draw.circle(surface, (255, 215, 0), (int(b["x"]), int(b["y"])), 2)

        if int(pygame.time.get_ticks() / 200) % 2 == 0:
            for p in self.power_pills:
                pygame.draw.circle(surface, (0, 255, 200), (int(p["x"]), int(p["y"])), 5)

        for ph in self.phantoms:
            p_col = (50, 100, 255) if self.overclock_timer > 0 else ph["color"]
            pygame.draw.circle(surface, p_col, (int(ph["x"]), int(ph["y"])), 7)
            pygame.draw.circle(surface, (255, 255, 255), (int(ph["x"])-2, int(ph["y"])-2), 2)
            pygame.draw.circle(surface, (255, 255, 255), (int(ph["x"])+2, int(ph["y"])-2), 2)

        if self.invulnerable_timer <= 0 or int(pygame.time.get_ticks() / 100) % 2 == 0:
            pygame.draw.circle(surface, (255, 255, 0), (int(self.px), int(self.py)), 8)
            pygame.draw.line(surface, (255, 0, 120), (int(self.px), int(self.py)-2), (int(self.px)+4, int(self.py)-2), 2)

        pygame.draw.rect(surface, (12, 15, 28), (10, 215, 300, 20), border_radius=4)
        oc_text = " | OVERCLOCK!" if self.overclock_timer > 0 else ""
        hud = self.font.render(f"LIVES: {self.lives} | SECTOR: {self.level}/3{oc_text}", True, (0, 255, 200))
        surface.blit(hud, (160 - hud.get_width() // 2, 218))

        self.render_ui(surface)

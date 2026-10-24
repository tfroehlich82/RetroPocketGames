# ==========================================
# PIXEL PLATFORMER v1.0 (CYBER RUN)
# Featuring 20 progressive levels, dynamic themes,
# expandable lives (no cap), laser weapons, and fixed jump mechanics.
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.core.physics import apply_gravity, clamp
from pocket_games.games.base import BaseGame


class PixelPlatformerGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Pixel Platformer")
        self.px = 40.0
        self.py = 140.0
        self.pvx = 0.0
        self.pvy = 0.0
        self.gravity = 950.0
        self.is_grounded = True
        self.jump_speed = -420.0
        self.lives = 3
        self.level = 1
        self.max_levels = 20
        self.has_gun = False
        self.invulnerable_timer = 0.0
        self.platforms: list[pygame.Rect] = []
        self.enemies: list[dict] = []
        self.powerups: list[dict] = []
        self.projectiles: list[dict] = []
        self._setup_level()

    def _setup_level(self) -> None:
        self.px = 40.0
        self.py = 140.0
        self.pvx = 0.0
        self.pvy = 0.0
        self.projectiles = []

        self.platforms = [pygame.Rect(0, 205, 320, 35)]
        num_plats = min(6, 3 + self.level // 4)
        for i in range(num_plats):
            w = max(40, 90 - (self.level * 2))
            x = 40 + (i * 55) % 240
            y = 160 - (i * 25) % 110
            self.platforms.append(pygame.Rect(x, y, w, 14))

        enemy_count = min(5, 1 + self.level // 4)
        self.enemies = []
        for i in range(enemy_count):
            ex = float(80 + i * 50)
            ey = self.platforms[(i + 1) % len(self.platforms)].top - 20
            self.enemies.append({
                "x": ex, "y": ey, "w": 16, "h": 20,
                "dir": 1 if i % 2 == 0 else -1,
                "alive": True,
                "speed": 45.0 + (self.level * 3.5)
            })

        self.powerups = []
        pw_type = "gun" if (random.random() < 0.5 or self.has_gun) else "life"
        self.powerups.append({"x": 150.0, "y": 60.0, "type": pw_type, "collected": False})

    def reset_position(self) -> None:
        self.px = 40.0
        self.py = 140.0
        self.pvx = 0.0
        self.pvy = 0.0
        self.invulnerable_timer = 1.5

    def handle_damage(self) -> None:
        if self.invulnerable_timer > 0.0:
            return
        self.lives -= 1
        self.play_sound("hit")
        if self.lives <= 0:
            self.game_over = True
            self.play_sound("gameover")
        else:
            self.reset_position()

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        move_speed = 160.0

        self.pvx = 0.0
        if inp.is_left_pressed():
            self.pvx = -move_speed
        if inp.is_right_pressed():
            self.pvx = move_speed

        player_rect = pygame.Rect(int(self.px), int(self.py), 16, 20)
        self.is_grounded = any(player_rect.colliderect(p) for p in self.platforms)

        if (inp.is_action_just_pressed() or inp.is_up_pressed()) and self.is_grounded:
            self.pvy = self.jump_speed
            self.is_grounded = False
            self.play_sound("jump")

        if inp.is_key_just_pressed(pygame.K_z) and self.has_gun:
            self.projectiles.append({"x": self.px + 8, "y": self.py + 8, "vx": 320.0})
            self.play_sound("select")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over or self.paused:
            return

        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer -= dt

        self.pvy = apply_gravity(self.pvy, self.gravity, dt)
        self.px += self.pvx * dt
        self.py += self.pvy * dt

        player_rect = pygame.Rect(int(self.px), int(self.py), 16, 20)
        for p in self.platforms:
            if player_rect.colliderect(p):
                if self.pvy > 0 and player_rect.bottom - self.pvy * dt <= p.top + 8:
                    self.py = p.top - 20
                    self.pvy = 0.0
                elif self.pvy < 0:
                    self.py = p.bottom
                    self.pvy = 0.0

        for pr in self.projectiles[:]:
            pr["x"] += pr["vx"] * dt
            if pr["x"] > 320 or pr["x"] < 0:
                self.projectiles.remove(pr)
                continue
            pr_rect = pygame.Rect(int(pr["x"]), int(pr["y"]), 6, 6)
            for en in self.enemies:
                if en["alive"] and pr_rect.colliderect(pygame.Rect(int(en["x"]), int(en["y"]), en["w"], en["h"])):
                    en["alive"] = False
                    self.projectiles.remove(pr)
                    self.add_score(150)
                    self.play_sound("confirm")
                    break

        for en in self.enemies:
            if not en["alive"]:
                continue
            en["x"] += en["dir"] * en["speed"] * dt
            if en["x"] < 10 or en["x"] > 295:
                en["dir"] *= -1

            en_rect = pygame.Rect(int(en["x"]), int(en["y"]), en["w"], en["h"])
            player_rect = pygame.Rect(int(self.px), int(self.py), 16, 20)

            if player_rect.colliderect(en_rect):
                if self.pvy > 0 and player_rect.bottom - self.pvy * dt <= en_rect.top + 8:
                    en["alive"] = False
                    self.pvy = -260.0
                    self.add_score(100)
                    self.play_sound("confirm")
                else:
                    self.handle_damage()
                    break

        player_rect = pygame.Rect(int(self.px), int(self.py), 16, 20)
        for pw in self.powerups:
            if not pw["collected"]:
                pw_rect = pygame.Rect(int(pw["x"]), int(pw["y"]), 12, 12)
                if player_rect.colliderect(pw_rect):
                    pw["collected"] = True
                    if pw["type"] == "gun":
                        self.has_gun = True
                        self.add_score(200)
                    else:
                        self.lives += 1
                        self.add_score(300)
                    self.play_sound("score")

        if self.px > 310:
            self.level += 1
            self.add_score(500)
            self.play_sound("confirm")
            if self.level > self.max_levels:
                self.game_won = True
            else:
                self._setup_level()

        if self.py > 240 and self.invulnerable_timer <= 0.0:
            self.handle_damage()

    def render(self, surface: pygame.Surface) -> None:
        themes = {
            1: ((15, 22, 38), (0, 180, 200)),
            2: ((38, 15, 25), (255, 80, 150)),
            3: ((20, 35, 20), (50, 220, 100)),
            4: ((35, 25, 10), (255, 180, 50)),
        }
        tier = min(4, (self.level - 1) // 5 + 1)
        bg_col, plat_col = themes[tier]

        surface.fill(bg_col)

        for p in self.platforms:
            pygame.draw.rect(surface, plat_col, p, border_radius=3)
            pygame.draw.line(surface, (255, 255, 255), (p.left, p.top), (p.right, p.top), 2)

        for pw in self.powerups:
            if not pw["collected"]:
                col = (255, 215, 0) if pw["type"] == "gun" else (255, 50, 100)
                pygame.draw.rect(surface, col, (int(pw["x"]), int(pw["y"]), 12, 12), border_radius=2)

        for en in self.enemies:
            if en["alive"]:
                pygame.draw.rect(surface, (220, 40, 60), (int(en["x"]), int(en["y"]), en["w"], en["h"]), border_radius=4)
                pygame.draw.circle(surface, (255, 255, 255), (int(en["x"])+4, int(en["y"])+6), 2)

        if self.invulnerable_timer <= 0 or int(pygame.time.get_ticks() / 100) % 2 == 0:
            px, py = int(self.px), int(self.py)
            pygame.draw.rect(surface, (0, 255, 200), (px, py, 16, 20), border_radius=4)

        for pr in self.projectiles:
            pygame.draw.circle(surface, (255, 255, 0), (int(pr["x"]), int(pr["y"])), 3)

        pygame.draw.rect(surface, (10, 12, 20), (10, 218, 300, 18), border_radius=4)
        hud = self.font.render(f"LIVES: {self.lives} | LVL: {self.level}/20 | RUN", True, (200, 220, 255))
        surface.blit(hud, (160 - hud.get_width() // 2, 220))

        self.render_ui(surface)

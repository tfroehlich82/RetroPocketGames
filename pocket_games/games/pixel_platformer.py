# ==========================================
# PIXEL PLATFORMER v2.0 (CYBER RUN)
# 20 Mario-inspired levels across four worlds, stomp enemies,
# flyers, spikes, pits, fire flowers, stars and mushrooms.
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.core.physics import apply_gravity
from pocket_games.games.base import BaseGame

MAX_LEVELS = 20
SCREEN_W = 320
SCREEN_H = 240
PLAYER_W = 16
PLAYER_H = 20
GROUND_Y = 205
GOAL_X = 300
FIRST_TIER_Y = 150
TIER_HEIGHTS = (150, 125, 100, 75)
MAX_RISE = 70
LEVEL_SEED_BASE = 7919

WORLDS = (
    {
        "name": "GRASS",
        "sky": ((92, 170, 255), (190, 230, 255)),
        "ground": (150, 88, 40),
        "top": (70, 190, 70),
        "brick": (110, 62, 28),
        "accent": (40, 150, 60),
        "decor": "hills",
    },
    {
        "name": "CAVE",
        "sky": ((18, 16, 40), (60, 50, 90)),
        "ground": (96, 86, 100),
        "top": (150, 140, 170),
        "brick": (64, 58, 74),
        "accent": (80, 74, 100),
        "decor": "stalactites",
    },
    {
        "name": "CASTLE",
        "sky": ((70, 12, 24), (150, 50, 40)),
        "ground": (120, 110, 120),
        "top": (210, 70, 60),
        "brick": (84, 74, 90),
        "accent": (60, 50, 66),
        "decor": "pillars",
    },
    {
        "name": "SKY",
        "sky": ((40, 90, 220), (170, 210, 255)),
        "ground": (235, 240, 255),
        "top": (255, 255, 255),
        "brick": (190, 205, 240),
        "accent": (255, 255, 255),
        "decor": "clouds",
    },
)

POWERUP_ORDER = ("life", "gun", "star", "life")
STAR_DURATION = 8.0
SPAWN_INVULNERABILITY = 1.5


def _star_points(cx: float, cy: float, outer: float, inner: float) -> list[tuple[int, int]]:
    points = []
    for i in range(10):
        radius = outer if i % 2 == 0 else inner
        angle = -math.pi / 2 + i * math.pi / 5
        points.append((int(cx + math.cos(angle) * radius), int(cy + math.sin(angle) * radius)))
    return points


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
        self.max_levels = MAX_LEVELS
        self.has_gun = False
        self.star_timer = 0.0
        self.invulnerable_timer = 0.0
        self.anim_time = 0.0
        self.coins_collected = 0
        self.facing = 1
        self.ground: list[pygame.Rect] = []
        self.floating: list[pygame.Rect] = []
        self.platforms: list[pygame.Rect] = []
        self.hazards: list[pygame.Rect] = []
        self.enemies: list[dict] = []
        self.coins: list[dict] = []
        self.powerups: list[dict] = []
        self.projectiles: list[dict] = []
        decor_rng = random.Random(3)
        self.decor = [(decor_rng.randint(0, SCREEN_W - 1), decor_rng.randint(20, 90)) for _ in range(5)]
        self._setup_level()

    def _player_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.px), int(self.py), PLAYER_W, PLAYER_H)

    @staticmethod
    def _enemy_rect(en: dict) -> pygame.Rect:
        return pygame.Rect(int(en["x"]), int(en["y"]), en["w"], en["h"])

    def _setup_level(self) -> None:
        self.px = 40.0
        self.py = 140.0
        self.pvx = 0.0
        self.pvy = 0.0
        self.star_timer = 0.0
        self.projectiles = []

        rng = random.Random(LEVEL_SEED_BASE + self.level)
        self._build_ground(rng)
        self._build_floating_platforms(rng)
        self._build_enemies(rng)
        self._build_hazards(rng)
        self._build_items(rng)

    def _build_ground(self, rng: random.Random) -> None:
        gaps: list[tuple[int, int]] = []
        pit_count = min(3, (self.level - 1) // 4)
        x = 60
        for _ in range(pit_count):
            width = min(56, 24 + self.level * 2)
            x += rng.randint(30, 60)
            if x + width > 250:
                break
            gaps.append((x, x + width))
            x += width

        self.ground = []
        start = 0
        for gap_start, gap_end in gaps:
            self.ground.append(pygame.Rect(start, GROUND_Y, gap_start - start, SCREEN_H - GROUND_Y))
            start = gap_end
        self.ground.append(pygame.Rect(start, GROUND_Y, SCREEN_W - start, SCREEN_H - GROUND_Y))

    def _build_floating_platforms(self, rng: random.Random) -> None:
        count = min(7, 3 + self.level // 4)
        spacing = SCREEN_W / count
        width = max(40, min(90 - self.level * 2, int(spacing) + 20))
        self.floating = []
        top = FIRST_TIER_Y
        for i in range(count):
            x = int(20 + i * spacing + rng.randint(0, 8))
            x = min(x, SCREEN_W - 20 - width)
            if i > 0:
                reachable = [h for h in TIER_HEIGHTS if top - h <= MAX_RISE]
                top = rng.choice(reachable)
            self.floating.append(pygame.Rect(x, top, width, 12))
        self.platforms = self.ground + self.floating

    def _build_enemies(self, rng: random.Random) -> None:
        self.enemies = []
        candidates = [r for r in self.platforms if r.width >= 32 and r.left >= 60]
        walker_count = min(5, 1 + self.level // 4) if candidates else 0
        walker_speed = 40.0 + self.level * 3.0
        for _ in range(walker_count):
            surface = rng.choice(candidates)
            min_x = surface.left
            max_x = surface.right - 16
            self.enemies.append({
                "kind": "walker", "x": float(rng.randint(min_x, max_x)), "y": float(surface.top - 16),
                "w": 16, "h": 16, "dir": rng.choice((-1, 1)), "speed": walker_speed,
                "min_x": float(min_x), "max_x": float(max_x), "base_y": 0.0, "phase": 0.0, "alive": True,
            })

        flyer_count = min(3, (self.level - 5) // 5 + 1) if self.level >= 6 else 0
        for _ in range(flyer_count):
            self.enemies.append({
                "kind": "flyer", "x": float(rng.randint(40, 260)), "y": 80.0,
                "w": 16, "h": 16, "dir": rng.choice((-1, 1)), "speed": 50.0 + self.level * 2.5,
                "min_x": 20.0, "max_x": 290.0, "base_y": float(rng.choice((60, 80, 100))),
                "phase": rng.random() * math.tau, "alive": True,
            })

    def _build_hazards(self, rng: random.Random) -> None:
        self.hazards = []
        spike_count = min(3, (self.level - 10) // 4 + 1) if self.level >= 11 else 0
        candidates = [r for r in self.ground if r.width >= 60 and r.left >= 80]
        for _ in range(spike_count if candidates else 0):
            surface = rng.choice(candidates)
            x = rng.randint(surface.left + 10, surface.right - 26)
            self.hazards.append(pygame.Rect(x, surface.top - 10, 16, 10))

    def _build_items(self, rng: random.Random) -> None:
        self.coins = []
        for surface in self.floating:
            for k in range(3):
                self.coins.append({"x": float(surface.left + 6 + k * 12), "y": float(surface.top - 14), "collected": False})
        for k in range(5):
            self.coins.append({"x": float(100 + k * 40), "y": float(GROUND_Y - 22), "collected": False})

        target = self.floating[1] if len(self.floating) > 1 else self.ground[0]
        kind = POWERUP_ORDER[(self.level - 1) % len(POWERUP_ORDER)]
        self.powerups = [{"x": float(target.left + 4), "y": float(target.top - 14), "type": kind, "collected": False}]

    def reset_position(self) -> None:
        self.px = 40.0
        self.py = 140.0
        self.pvx = 0.0
        self.pvy = 0.0
        self.invulnerable_timer = SPAWN_INVULNERABILITY

    def handle_damage(self) -> None:
        if self.invulnerable_timer > 0.0 or self.star_timer > 0.0:
            return
        if self.has_gun:
            self.has_gun = False
            self.invulnerable_timer = SPAWN_INVULNERABILITY
            self.play_sound("hit")
            return
        self._lose_life()

    def _lose_life(self) -> None:
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
            self.facing = -1
        if inp.is_right_pressed():
            self.pvx = move_speed
            self.facing = 1

        feet = pygame.Rect(int(self.px), int(self.py) + PLAYER_H, PLAYER_W, 2)
        self.is_grounded = self.pvy >= 0 and any(feet.colliderect(p) for p in self.platforms)

        if (inp.is_action_just_pressed() or inp.is_up_pressed()) and self.is_grounded:
            self.pvy = self.jump_speed
            self.is_grounded = False
            self.play_sound("jump")

        if inp.is_key_just_pressed(pygame.K_z) and self.has_gun:
            self.projectiles.append({"x": self.px + 8, "y": self.py + 8, "vx": 320.0 * self.facing})
            self.play_sound("select")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over or self.paused:
            return

        self.anim_time += dt
        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer -= dt
        self.star_timer = max(0.0, self.star_timer - dt)

        self.pvy = apply_gravity(self.pvy, self.gravity, dt)
        self.px += self.pvx * dt
        self.py += self.pvy * dt
        self.px = max(0.0, min(self.px, SCREEN_W - PLAYER_W))

        self._resolve_platforms(dt)
        self._update_projectiles(dt)
        self._update_enemies(dt)
        self._update_hazards()
        self._collect_items()

        if self.px > GOAL_X:
            self._complete_level()
            return

        if self.py > SCREEN_H:
            self._lose_life()

    def _resolve_platforms(self, dt: float) -> None:
        rect = self._player_rect()
        for p in self.platforms:
            if not rect.colliderect(p):
                continue
            previous_bottom = rect.bottom - self.pvy * dt
            if self.pvy >= 0 and previous_bottom <= p.top + 8:
                self.py = p.top - PLAYER_H
                self.pvy = 0.0
            elif self.pvy < 0:
                self.py = p.bottom
                self.pvy = 0.0
            elif self.pvx > 0:
                self.px = p.left - PLAYER_W
            elif self.pvx < 0:
                self.px = p.right
            rect = self._player_rect()

    def _update_projectiles(self, dt: float) -> None:
        for pr in self.projectiles[:]:
            pr["x"] += pr["vx"] * dt
            if pr["x"] > SCREEN_W or pr["x"] < 0:
                self.projectiles.remove(pr)
                continue
            pr_rect = pygame.Rect(int(pr["x"]), int(pr["y"]), 6, 6)
            for en in self.enemies:
                if en["alive"] and pr_rect.colliderect(self._enemy_rect(en)):
                    en["alive"] = False
                    self.projectiles.remove(pr)
                    self.add_score(150)
                    self.play_sound("confirm")
                    break

    def _update_enemies(self, dt: float) -> None:
        for en in self.enemies:
            if not en["alive"]:
                continue
            en["x"] += en["dir"] * en["speed"] * dt
            if en["x"] < en["min_x"]:
                en["x"] = en["min_x"]
                en["dir"] = 1
            elif en["x"] > en["max_x"]:
                en["x"] = en["max_x"]
                en["dir"] = -1
            if en["kind"] == "flyer":
                en["y"] = en["base_y"] + math.sin(self.anim_time * 2.0 + en["phase"]) * 18.0

            player_rect = self._player_rect()
            en_rect = self._enemy_rect(en)
            if not player_rect.colliderect(en_rect):
                continue
            if self.star_timer > 0.0:
                en["alive"] = False
                self.add_score(100)
                self.play_sound("confirm")
            elif self.pvy > 0 and player_rect.bottom - self.pvy * dt <= en_rect.top + 8:
                en["alive"] = False
                self.pvy = -260.0
                self.add_score(100)
                self.play_sound("confirm")
            else:
                self.handle_damage()
                break

    def _update_hazards(self) -> None:
        player_rect = self._player_rect()
        if any(player_rect.colliderect(h) for h in self.hazards):
            self.handle_damage()

    def _collect_items(self) -> None:
        player_rect = self._player_rect()
        for coin in self.coins:
            if not coin["collected"] and player_rect.colliderect(pygame.Rect(int(coin["x"]), int(coin["y"]), 8, 10)):
                coin["collected"] = True
                self.coins_collected += 1
                self.add_score(10)
                self.play_sound("score")

        for pw in self.powerups:
            if pw["collected"]:
                continue
            if player_rect.colliderect(pygame.Rect(int(pw["x"]), int(pw["y"]), 12, 12)):
                pw["collected"] = True
                if pw["type"] == "gun":
                    self.has_gun = True
                    self.add_score(200)
                elif pw["type"] == "star":
                    self.star_timer = STAR_DURATION
                    self.add_score(250)
                else:
                    self.lives += 1
                    self.add_score(300)
                self.play_sound("score")

    def _complete_level(self) -> None:
        self.level += 1
        self.add_score(500)
        self.play_sound("confirm")
        if self.level > self.max_levels:
            self.game_won = True
        else:
            self._setup_level()

    def render(self, surface: pygame.Surface) -> None:
        world_index = min(len(WORLDS) - 1, (self.level - 1) // 5)
        theme = WORLDS[world_index]
        self._draw_background(surface, theme)

        for p in self.platforms:
            self._draw_block(surface, p, theme)

        for h in self.hazards:
            pts = [(h.left, h.bottom), (h.left + h.width // 2, h.top), (h.right, h.bottom)]
            pygame.draw.polygon(surface, (200, 200, 215), pts)
            pygame.draw.polygon(surface, (255, 60, 60), pts, 2)

        self._draw_flag(surface)

        for coin in self.coins:
            if coin["collected"]:
                continue
            squash = abs(math.cos(self.anim_time * 5.0 + coin["x"] * 0.1))
            w = max(2, int(8 * squash))
            cx, cy = int(coin["x"]) + 4, int(coin["y"]) + 5
            pygame.draw.ellipse(surface, (255, 200, 40), (cx - w // 2, cy - 5, w, 10))
            pygame.draw.ellipse(surface, (255, 240, 150), (cx - w // 2 + 1, cy - 4, max(1, w // 3), 4))

        for pw in self.powerups:
            if not pw["collected"]:
                self._draw_powerup(surface, pw)

        for en in self.enemies:
            if en["alive"]:
                self._draw_enemy(surface, en)

        self._draw_player(surface)

        for pr in self.projectiles:
            pygame.draw.circle(surface, (255, 160, 40), (int(pr["x"]), int(pr["y"])), 3)
            pygame.draw.circle(surface, (255, 240, 120), (int(pr["x"]), int(pr["y"])), 1)

        self._draw_hud(surface, theme, world_index)
        self.render_ui(surface)

    def _draw_background(self, surface: pygame.Surface, theme: dict) -> None:
        top, bottom = theme["sky"]
        for y in range(0, SCREEN_H, 2):
            t = y / SCREEN_H
            color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
            pygame.draw.rect(surface, color, (0, y, SCREEN_W, 2))

        decor = theme["decor"]
        accent = theme["accent"]
        if decor == "hills":
            for x in (-30, 100, 220):
                pygame.draw.ellipse(surface, accent, (x, 160, 120, 90))
        elif decor == "stalactites":
            for x in range(0, SCREEN_W, 40):
                pygame.draw.polygon(surface, accent, [(x, 0), (x + 20, 0), (x + 10, 20 + (x * 7) % 20)])
        elif decor == "pillars":
            for x in (30, 150, 260):
                pygame.draw.rect(surface, accent, (x, 60, 20, 150))
                pygame.draw.rect(surface, accent, (x - 4, 56, 28, 6))
        elif decor == "clouds":
            for base_x, y in self.decor:
                x = (base_x + self.anim_time * 8.0) % (SCREEN_W + 40) - 20
                pygame.draw.circle(surface, (245, 248, 255), (int(x), y), 10)
                pygame.draw.circle(surface, (245, 248, 255), (int(x + 10), y - 4), 12)
                pygame.draw.circle(surface, (245, 248, 255), (int(x + 20), y), 10)

    def _draw_block(self, surface: pygame.Surface, rect: pygame.Rect, theme: dict) -> None:
        surface.set_clip(rect)
        pygame.draw.rect(surface, theme["ground"], rect)
        for y in range(rect.top + 6, rect.bottom, 6):
            pygame.draw.line(surface, theme["brick"], (rect.left, y), (rect.right, y))
        for row, y in enumerate(range(rect.top, rect.bottom, 6)):
            offset = 8 if row % 2 else 0
            for x in range(rect.left + offset, rect.right, 16):
                pygame.draw.line(surface, theme["brick"], (x, y), (x, y + 6))
        pygame.draw.rect(surface, theme["top"], (rect.left, rect.top, rect.width, 4))
        surface.set_clip(None)

    def _draw_flag(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (220, 220, 230), (GOAL_X, 118, 3, GROUND_Y - 118))
        pygame.draw.circle(surface, (255, 215, 0), (GOAL_X + 1, 116), 3)
        pygame.draw.polygon(surface, (255, 70, 70), [(GOAL_X + 3, 120), (GOAL_X + 16, 126), (GOAL_X + 3, 132)])

    def _draw_powerup(self, surface: pygame.Surface, pw: dict) -> None:
        x, y = int(pw["x"]), int(pw["y"])
        if pw["type"] == "gun":
            pygame.draw.circle(surface, (255, 120, 40), (x + 6, y + 4), 5)
            pygame.draw.circle(surface, (255, 230, 60), (x + 6, y + 4), 3)
            pygame.draw.rect(surface, (40, 200, 80), (x + 5, y + 8, 2, 6))
        elif pw["type"] == "star":
            pygame.draw.polygon(surface, (255, 230, 60), _star_points(x + 6, y + 6, 7, 3))
        else:
            pygame.draw.ellipse(surface, (235, 40, 50), (x, y, 12, 8))
            pygame.draw.rect(surface, (250, 235, 210), (x + 3, y + 6, 6, 6))
            pygame.draw.circle(surface, (255, 255, 255), (x + 3, y + 3), 1)
            pygame.draw.circle(surface, (255, 255, 255), (x + 8, y + 3), 1)

    def _draw_enemy(self, surface: pygame.Surface, en: dict) -> None:
        x, y = int(en["x"]), int(en["y"])
        if en["kind"] == "flyer":
            flap = 4 if int(self.anim_time * 10) % 2 else -2
            pygame.draw.ellipse(surface, (170, 90, 255), (x - 4, y + flap, 24, 8))
            pygame.draw.ellipse(surface, (110, 40, 200), (x + 2, y + 3, 12, 11))
            pygame.draw.rect(surface, (255, 255, 255), (x + 4, y + 5, 3, 3))
            pygame.draw.rect(surface, (255, 255, 255), (x + 9, y + 5, 3, 3))
        else:
            pygame.draw.ellipse(surface, (150, 80, 40), (x, y, 16, 12))
            pygame.draw.rect(surface, (90, 50, 25), (x, y + 12, 16, 4))
            pygame.draw.rect(surface, (255, 255, 255), (x + 3, y + 4, 4, 4))
            pygame.draw.rect(surface, (255, 255, 255), (x + 9, y + 4, 4, 4))
            pygame.draw.rect(surface, (0, 0, 0), (x + 4, y + 5, 2, 2))
            pygame.draw.rect(surface, (0, 0, 0), (x + 10, y + 5, 2, 2))

    def _draw_player(self, surface: pygame.Surface) -> None:
        visible = self.invulnerable_timer <= 0 or (pygame.time.get_ticks() // 100) % 2 == 0
        if not visible:
            return
        x, y = int(self.px), int(self.py)
        if self.star_timer > 0.0:
            palette = ((255, 60, 60), (255, 220, 40), (60, 255, 120), (60, 200, 255))
            cap = palette[int(self.anim_time * 12) % len(palette)]
            body = (40, 40, 60)
        elif self.has_gun:
            cap = (220, 60, 40)
            body = (250, 250, 250)
        else:
            cap = (220, 40, 40)
            body = (40, 80, 220)
        pygame.draw.rect(surface, cap, (x + 2, y, 12, 4), border_radius=2)
        pygame.draw.rect(surface, (255, 200, 160), (x + 3, y + 4, 10, 6))
        pygame.draw.rect(surface, (0, 0, 0), (x + 5, y + 6, 2, 2))
        pygame.draw.rect(surface, (0, 0, 0), (x + 10, y + 6, 2, 2))
        pygame.draw.rect(surface, cap, (x + 2, y + 10, 12, 4))
        pygame.draw.rect(surface, body, (x + 3, y + 14, 10, 6))
        pygame.draw.rect(surface, (90, 50, 20), (x + 1, y + 17, 5, 3))
        pygame.draw.rect(surface, (90, 50, 20), (x + 10, y + 17, 5, 3))

    def _draw_hud(self, surface: pygame.Surface, theme: dict, world_index: int) -> None:
        pygame.draw.rect(surface, (10, 12, 20), (0, 0, SCREEN_W, 14))
        stage = ((self.level - 1) % 5) + 1
        text = f"LIVES {self.lives}  {theme['name']} {world_index + 1}-{stage}  COINS {self.coins_collected}  LVL {self.level}/{self.max_levels}"
        hud = self.font.render(text, True, (200, 220, 255))
        surface.blit(hud, (4, 2))
        if self.star_timer > 0.0:
            star = self.font.render("STAR", True, (255, 230, 60))
            surface.blit(star, (SCREEN_W - star.get_width() - 4, 2))
        elif self.has_gun:
            gun = self.font.render("FIRE", True, (255, 120, 40))
            surface.blit(gun, (SCREEN_W - gun.get_width() - 4, 2))

# ==========================================
# NEON DASH v1.3
# A fast-paced cyberpunk endless runner featuring 5 challenging stages and distinct visual scenarios
# (Cyber Neon, Matrix Grid, Sunset Highway, Deep Abyss, Quantum Core). Each level is tuned for an
# engaging run. The game starts with easy obstacles. As you advance through levels,
# speed and obstacle density increase progressively, introducing advanced elements such as tall
# double blocks and complex pattern combinations remains thrilling all the way to the final level.
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.core.physics import apply_gravity, clamp
from pocket_games.games.base import BaseGame


class NeonDashGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Neon Dash")
        self.player_y = 180.0
        self.player_vy = 0.0
        self.gravity = 880.0
        self.jump_speed = -390.0

        self.level_duration = random.uniform(30.0, 40.0)
        self.density = 2.0

        self.background_particles = [
            {
                "x": random.randint(0, 320),
                "y": random.randint(0, 160),
                "speed": random.randint(10, 25),
            }
            for _ in range(25)
        ]

        self.scenarios = {
            1: {
                "name": "Cyber Neon",
                "bg": (8, 5, 18),
                "floor": (0, 240, 255),
                "obs": (255, 180, 0),
            },
            2: {
                "name": "Matrix Grid",
                "bg": (4, 15, 10),
                "floor": (0, 255, 120),
                "obs": (180, 50, 255),
            },
            3: {
                "name": "Sunset Highway",
                "bg": (25, 10, 20),
                "floor": (255, 100, 150),
                "obs": (255, 220, 0),
            },
            4: {
                "name": "Deep Abyss",
                "bg": (15, 8, 8),
                "floor": (255, 50, 50),
                "obs": (0, 255, 200),
            },
            5: {
                "name": "Quantum Core",
                "bg": (5, 15, 30),
                "floor": (100, 200, 255),
                "obs": (255, 50, 200),
            },
            6: {
                "name": "Neon Void",
                "bg": (20, 5, 30),
                "floor": (255, 0, 255),
                "obs": (0, 255, 150),
            },
            7: {
                "name": "Cyber Storm",
                "bg": (10, 20, 35),
                "floor": (50, 150, 255),
                "obs": (255, 100, 50),
            },
            8: {
                "name": "Hyper Warp",
                "bg": (30, 5, 5),
                "floor": (255, 255, 0),
                "obs": (255, 0, 100),
            },
        }
        self.level = 1
        self.max_levels = len(self.scenarios)
        self.is_grounded = True
        self.level_timer = 0.0
        self.distance = 0.0
        self.obstacles: list[dict] = []
        self.spawn_timer = 0.0
        self.next_spawn_delay = 1.8

        self._spawn_obstacle()

    def _get_current_speed(self) -> float:
        base = 180.0 + (self.level - 1) * 18.0
        return base + (self.level_timer * 0.08)

    def _spawn_obstacle(self) -> None:
        group_x = 330.0

        # Hilfsfunktion zur Bestimmung der erlaubten Elementtypen (Spike, Block, Tall Block)
        def get_random_element(allow_tall: bool = True) -> str:
            possible_types = ["spike", "block"]
            if allow_tall:
                possible_types.append("tall_block")
            return random.choice(possible_types)

        if self.level >= 2:
            if self.level >= 7:
                combo_choices = ["single", "pair", "triple", "quad"]
            elif self.level >= 5:
                combo_choices = ["single", "pair", "triple"]
            else:
                combo_choices = ["single", "pair"]

            combo_type = random.choice(combo_choices)

            if combo_type == "pair":
                # Bei 2er-Blöcken dürfen tall blocks an beliebiger Position stehen
                for i in range(2):
                    t = get_random_element(allow_tall=True)
                    w = 18 if t == "spike" else 22
                    h = 38 if t == "tall_block" else 22
                    self.obstacles.append(
                        {
                            "x": group_x + (i * 38),
                            "y": 200.0 - h,
                            "w": w,
                            "h": h,
                            "type": t,
                        }
                    )
                return
            elif combo_type == "triple" and self.level >= 5:
                # Bei 3er-Blöcken dürfen tall blocks nur in der Mitte (Index 1) stehen
                for i in range(3):
                    allow_tall = i == 1
                    t = get_random_element(allow_tall=allow_tall)
                    w = 18 if t == "spike" else 22
                    h = 38 if t == "tall_block" else 22
                    self.obstacles.append(
                        {
                            "x": group_x + (i * 35),
                            "y": 200.0 - h,
                            "w": w,
                            "h": h,
                            "type": t,
                        }
                    )
                return
            elif combo_type == "quad" and self.level >= 7:
                # Bei 4er-Blöcken dürfen tall blocks nur in der Mitte (Index 1 und 2) stehen
                for i in range(4):
                    allow_tall = i in (1, 2)
                    t = get_random_element(allow_tall=allow_tall)
                    w = 18 if t == "spike" else 22
                    h = 38 if t == "tall_block" else 22
                    self.obstacles.append(
                        {
                            "x": group_x + (i * 32),
                            "y": 200.0 - h,
                            "w": w,
                            "h": h,
                            "type": t,
                        }
                    )
                return

        # Löcher erst ab Level 3
        if self.level >= 3 and random.random() < 0.25:
            self.obstacles.append(
                {"x": group_x, "y": 200.0, "w": 45, "h": 10, "type": "gap"}
            )
        else:
            obs_type = random.choice(["spike", "block", "tall_block"])
            w = 18 if obs_type == "spike" else 22
            h = 38 if obs_type == "tall_block" else 22
            self.obstacles.append(
                {
                    "x": group_x,
                    "y": 200.0 - h,
                    "w": w,
                    "h": h,
                    "type": obs_type,
                }
            )

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if (inp.is_action_just_pressed() or inp.is_up_pressed()) and self.is_grounded:
            self.player_vy = self.jump_speed
            self.is_grounded = False
            self.play_sound("jump")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over or self.paused:
            return

        current_speed = self._get_current_speed()
        self.distance += current_speed * dt
        self.level_timer += dt

        if self.level_timer >= self.level_duration:
            if self.level < self.max_levels:
                self.level += 1
                self.level_timer = 0.0
                self.level_duration = random.uniform(30.0, 40.0)
                self.play_sound("confirm")
            else:
                self.game_won = True

        for p in self.background_particles:
            p["x"] -= p["speed"] * dt
            if p["x"] < 0:
                p["x"] = 320
                p["y"] = random.randint(0, 160)

        self.player_vy = apply_gravity(self.player_vy, self.gravity, dt)
        self.player_y += self.player_vy * dt
        self.player_y = clamp(self.player_y, 0.0, 195.0)

        player_cx = 50
        in_gap = False
        if self.player_y >= 180.0:
            for obs in self.obstacles:
                if (
                    obs["type"] == "gap"
                    and obs["x"] <= player_cx <= obs["x"] + obs["w"]
                ):
                    in_gap = True
                    break

        if in_gap:
            self.is_grounded = False
            if self.player_y > 210.0:
                self.game_over = True
                self.play_sound("crash")
        else:
            if self.player_y >= 180.0:
                self.player_y = 180.0
                self.player_vy = 0.0
                self.is_grounded = True

        self.spawn_timer += dt
        if self.spawn_timer >= self.next_spawn_delay:
            self.spawn_timer = 0.0
            self.next_spawn_delay = random.uniform(1.3, 2.2) - (self.level * 0.05)
            self._spawn_obstacle()

        player_rect = pygame.Rect(40, int(self.player_y), 20, 20)

        for obs in self.obstacles[:]:
            obs["x"] -= current_speed * dt
            if obs["type"] == "gap":
                obs_rect = pygame.Rect(int(obs["x"]), 200, obs["w"], 40)
            else:
                obs_rect = pygame.Rect(int(obs["x"]), int(obs["y"]), obs["w"], obs["h"])

            if obs_rect.right < 0:
                self.obstacles.remove(obs)
                if obs["type"] != "gap":
                    self.add_score(15)
                    self.play_sound("score")

            if player_rect.colliderect(obs_rect) and obs["type"] != "gap":
                self.game_over = True
                self.play_sound("crash")

    def render(self, surface: pygame.Surface) -> None:
        scenario = self.scenarios.get(self.level, self.scenarios[1])
        surface.fill(scenario["bg"])

        for p in self.background_particles:
            surface.set_at((int(p["x"]), int(p["y"])), scenario["floor"])

        floor_color = scenario["floor"]
        last_x = 0
        active_gaps = sorted(
            [o for o in self.obstacles if o["type"] == "gap"], key=lambda o: o["x"]
        )

        for gap in active_gaps:
            g_start = int(gap["x"])
            g_end = int(gap["x"] + gap["w"])
            if g_start > last_x:
                pygame.draw.line(surface, floor_color, (last_x, 200), (g_start, 200), 2)

            abyss_rect = pygame.Rect(g_start, 201, gap["w"], 39)
            pygame.draw.rect(surface, (5, 3, 10), abyss_rect)
            pygame.draw.line(surface, (255, 50, 100), (g_start, 200), (g_start, 210), 2)
            pygame.draw.line(surface, (255, 50, 100), (g_end, 200), (g_end, 210), 2)
            for lx in range(g_start + 6, g_end, 10):
                pygame.draw.line(surface, (30, 15, 30), (lx, 205), (lx, 235), 1)

            last_x = max(last_x, g_end)

        if last_x < 320:
            pygame.draw.line(surface, floor_color, (last_x, 200), (320, 200), 2)

        offset = int(self.distance) % 35
        for i in range(0, 320, 35):
            x_pos = i - offset
            if x_pos >= 0:
                in_any_gap = any(
                    g["x"] <= x_pos <= g["x"] + g["w"] for g in active_gaps
                )
                if not in_any_gap:
                    pygame.draw.line(
                        surface, floor_color, (x_pos, 200), (x_pos, 240), 1
                    )

        px, py = 40, int(self.player_y)
        pygame.draw.rect(
            surface, (255, 0, 150), (px - 2, py - 2, 24, 24), border_radius=4
        )
        pygame.draw.rect(surface, floor_color, (px, py, 20, 20), border_radius=3)
        pygame.draw.rect(
            surface, (255, 255, 255), (px + 4, py + 4, 12, 12), border_radius=2
        )

        obs_color = scenario["obs"]
        for obs in self.obstacles:
            if obs["type"] == "gap":
                continue
            ox, oy, ow, oh = int(obs["x"]), int(obs["y"]), obs["w"], obs["h"]
            if obs["type"] == "spike":
                pygame.draw.polygon(
                    surface,
                    obs_color,
                    [(ox, oy + oh), (ox + ow // 2, oy), (ox + ow, oy + oh)],
                )
            else:
                pygame.draw.rect(surface, obs_color, (ox, oy, ow, oh), border_radius=3)

        lvl_txt = self.font.render(
            f"LVL {self.level}: {scenario['name']}", True, (255, 255, 255)
        )
        surface.blit(lvl_txt, (160 - lvl_txt.get_width() // 2, 5))
        self.render_ui(surface)

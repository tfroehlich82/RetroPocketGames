# ==========================================
# NEON DASH v1.0
# A fast-paced cyberpunk endless runner featuring 5 challenging stages and distinct visual scenarios
# (Cyber Neon, Matrix Grid, Sunset Highway, Deep Abyss, Quantum Core). Each level is tuned for an
# engaging 30-second run. The game starts with easy obstacles. As you advance through levels,
# speed and obstacle density increase progressively, introducing advanced elements such as tall
# double blocks and complex pattern combinations (1x1-1x2-1x2-1x1). Featuring optimized gravity and
# perfectly synchronous floor scrolling, the game remains thrilling all the way to the final level.
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
        self.gravity = 850.0
        self.jump_speed = -380.0
        self.level_duration = 30.0
        self.density = 2.0

        self.background_particles = [
            {
                "x": random.randint(0, 320),
                "y": random.randint(0, 160),
                "speed": random.randint(10, 25)
            } for _ in range(25)
        ]

        # 5 different scenes, one per level
        self.scenarios = {
            1: {"name": "Cyber Neon", "bg": (8, 5, 18), "floor": (0, 240, 255), "obs": (255, 180, 0)},
            2: {"name": "Matrix Grid", "bg": (4, 15, 10), "floor": (0, 255, 120), "obs": (180, 50, 255)},
            3: {"name": "Sunset Highway", "bg": (25, 10, 20), "floor": (255, 100, 150), "obs": (255, 220, 0)},
            4: {"name": "Deep Abyss", "bg": (15, 8, 8), "floor": (255, 50, 50), "obs": (0, 255, 200)},
            5: {"name": "Quantum Core", "bg": (5, 15, 30), "floor": (100, 200, 255), "obs": (255, 50, 200)},
        }
        self.level = 1
        self.max_levels = len(self.scenarios)
        self.is_grounded = True
        self.level_timer = 0.0
        self.distance = 0.0
        self.obstacles: list[dict] = []
        self.spawn_timer = 0.0

        self._spawn_obstacle()

    def _get_current_speed(self) -> float:
        # Geschwindigkeit steigt vor allem stufenbasiert pro Level, minimal innerhalb des Levels
        base = 150.0 + (self.level - 1) * 15.0
        return base + (self.level_timer * 0.1)

    def _spawn_obstacle(self) -> None:
        r = random.random()
        group_x = 330.0

        # Hindernis-Vielfalt und Schwierigkeit steigern sich streng nach Level
        if self.level >= 5 and r < 0.3:
            # Level 5 Muster: 1x1 - 1x2 - 1x2 - 1x1 Kombination
            pattern_heights = [22, 38, 38, 22]
            pattern_widths = [18, 20, 20, 18]
            pattern_types = ["spike", "tall_block", "tall_block", "spike"]
            for i in range(4):
                w = pattern_widths[i]
                h = pattern_heights[i]
                self.obstacles.append({
                    "x": group_x + (i * 26),
                    "y": 200.0 - h,
                    "w": w,
                    "h": h,
                    "type": pattern_types[i]
                })
        elif self.level >= 4 and r < 0.35:
            # Level 4+: 3-er / 4-er Blöcke
            count = 4 if self.level == 5 else 3
            for i in range(count):
                self.obstacles.append({
                    "x": group_x + (i * 24),
                    "y": 178,
                    "w": 20,
                    "h": 22,
                    "type": "block"
                })
        elif self.level >= 3 and r < 0.4:
            # Level 3+: Hohe Doppelblöcke oder 2-er Blöcke
            if r < 0.2:
                for i in range(2):
                    self.obstacles.append({
                        "x": group_x + (i * 26),
                        "y": 200.0 - 38,
                        "w": 22,
                        "h": 38,
                        "type": "tall_block"
                    })
            else:
                for i in range(2):
                    self.obstacles.append({
                        "x": group_x + (i * 24),
                        "y": 178,
                        "w": 20,
                        "h": 22,
                        "type": "block"
                    })
        elif self.level >= 2 and r < 0.35:
            # Level 2+: Hohe Blöcke
            self.obstacles.append({
                "x": group_x,
                "y": 200.0 - 38,
                "w": 22,
                "h": 38,
                "type": "tall_block"
            })
        else:
            # Level 1 und Standard-Fallback: Sehr leicht zu überwindende Einzelhindernisse
            obs_type = random.choice(["spike", "block"])
            w = 18 if obs_type == "spike" else 22
            h = 22
            self.obstacles.append({
                "x": group_x,
                "y": 200.0 - h,
                "w": w,
                "h": h,
                "type": obs_type
            })

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
                self.play_sound("confirm")
            else:
                self.game_over = True  # Sieg

        for p in self.background_particles:
            p["x"] -= p["speed"] * dt
            if p["x"] < 0:
                p["x"] = 320
                p["y"] = random.randint(0, 160)

        self.player_vy = apply_gravity(self.player_vy, self.gravity, dt)
        self.player_y += self.player_vy * dt
        self.player_y = clamp(self.player_y, 0.0, 180.0)

        if self.player_y >= 180.0:
            self.player_y = 180.0
            self.player_vy = 0.0
            self.is_grounded = True

        self.spawn_timer += dt
        # Dichte steigt mit jedem Level und minimal im Verlauf des Levels
        base_spawn_delay = max(1.2, self.density - (self.level * 0.15) - (self.level_timer * 0.02))
        if self.spawn_timer >= base_spawn_delay:
            self.spawn_timer = 0.0
            self._spawn_obstacle()

        player_rect = pygame.Rect(40, int(self.player_y), 20, 20)

        for obs in self.obstacles[:]:
            obs["x"] -= current_speed * dt
            obs_rect = pygame.Rect(int(obs["x"]), int(obs["y"]), obs["w"], obs["h"])

            if obs_rect.right < 0:
                self.obstacles.remove(obs)
                self.add_score(15)
                self.play_sound("score")

            if player_rect.colliderect(obs_rect):
                self.game_over = True
                self.play_sound("crash")

    def render(self, surface: pygame.Surface) -> None:
        scenario = self.scenarios.get(self.level, self.scenarios[1])
        surface.fill(scenario["bg"])

        for p in self.background_particles:
            surface.set_at((int(p["x"]), int(p["y"])), scenario["floor"])

        floor_color = scenario["floor"]
        pygame.draw.line(surface, floor_color, (0, 200), (320, 200), 2)
        pygame.draw.line(surface, (100, 100, 100), (0, 201), (320, 201), 1)

        # 100% synchroner Boden-Scroll basierend auf dem exakten Distanz-Offset
        offset = int(self.distance) % 35
        for i in range(0, 320, 35):
            x_pos = i - offset
            if x_pos >= 0:
                pygame.draw.line(surface, floor_color, (x_pos, 200), (x_pos, 240), 1)

        px, py = 40, int(self.player_y)
        pygame.draw.rect(surface, (255, 0, 150), (px - 2, py - 2, 24, 24), border_radius=4)
        pygame.draw.rect(surface, floor_color, (px, py, 20, 20), border_radius=3)
        pygame.draw.rect(surface, (255, 255, 255), (px + 4, py + 4, 12, 12), border_radius=2)

        obs_color = scenario["obs"]
        for obs in self.obstacles:
            ox, oy, ow, oh = int(obs["x"]), int(obs["y"]), obs["w"], obs["h"]
            if obs["type"] == "spike":
                pygame.draw.polygon(surface, obs_color, [(ox, oy + oh), (ox + ow // 2, oy), (ox + ow, oy + oh)])
                pygame.draw.polygon(surface, (255, 255, 255), [(ox + 4, oy + oh), (ox + ow // 2, oy + 4), (ox + ow - 4, oy + oh)], 1)
            else:
                pygame.draw.rect(surface, obs_color, (ox, oy, ow, oh), border_radius=3)
                pygame.draw.rect(surface, (255, 255, 255), (ox + 2, oy + 2, ow - 4, oh - 4), 1, border_radius=2)

        lvl_txt = self.font.render(f"LVL {self.level}: {scenario['name']}", True, (255, 255, 255))
        surface.blit(lvl_txt, (160 - lvl_txt.get_width() // 2, 5))

        self.render_ui(surface)

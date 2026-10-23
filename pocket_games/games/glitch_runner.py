# ==========================================
# GLITCH RUNNER v1.1
# A tactical cyber puzzle game against the clock.
# Navigate your data cursor across a digital grid to reach
# the stable core exit node while beating the countdown timer
# and avoiding unpredictable expanding system glitches.
# Master multiple escalating sectors featuring strategic system rest breaks.
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.games.base import BaseGame


class GlitchRunnerGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Glitch Runner")
        self.grid_w = 6
        self.grid_h = 6
        self.player_pos = [0, 0]
        self.exit_pos = [5, 5]
        self.glitched_tiles: set[tuple[int, int]] = set()
        self.particles: list[dict] = []
        self.level = 1
        self.sectors_cleared = 0
        self.glitch_timer = 0.0
        self.time_limit = 15.0
        self.time_remaining = 15.0
        self.setup_level()

    def setup_level(self) -> None:
        self.grid_w = min(8, 5 + self.level)
        self.grid_h = min(7, 5 + (self.level // 2))
        self.player_pos = [0, 0]

        self.time_limit = max(10.0, 18.0 - (self.level * 2.0))
        self.time_remaining = self.time_limit

        while True:
            ex = random.randint(2, self.grid_w - 1)
            ey = random.randint(2, self.grid_h - 1)
            if [ex, ey] != self.player_pos:
                self.exit_pos = [ex, ey]
                break

        self.glitched_tiles.clear()
        glitch_count = self.level + 2
        for _ in range(glitch_count):
            gx = random.randint(0, self.grid_w - 1)
            gy = random.randint(0, self.grid_h - 1)
            if [gx, gy] != self.player_pos and [gx, gy] != self.exit_pos:
                self.glitched_tiles.add((gx, gy))

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        moved = False
        nx, ny = self.player_pos

        if inp.is_key_just_pressed(pygame.K_LEFT) or inp.is_key_just_pressed(
            pygame.K_a
        ):
            nx = max(0, nx - 1)
            moved = True
        elif inp.is_key_just_pressed(pygame.K_RIGHT) or inp.is_key_just_pressed(
            pygame.K_d
        ):
            nx = min(self.grid_w - 1, nx + 1)
            moved = True
        elif inp.is_key_just_pressed(pygame.K_UP) or inp.is_key_just_pressed(
            pygame.K_w
        ):
            ny = max(0, ny - 1)
            moved = True
        elif inp.is_key_just_pressed(pygame.K_DOWN) or inp.is_key_just_pressed(
            pygame.K_s
        ):
            ny = min(self.grid_h - 1, ny + 1)
            moved = True

        if moved:
            if (nx, ny) in self.glitched_tiles:
                self.game_over = True
                self.play_sound("gameover")
                return

            self.player_pos = [nx, ny]
            self.play_sound("select")

            if self.player_pos == self.exit_pos:
                self.add_score(150 * self.level + int(self.time_remaining * 10))
                self.sectors_cleared += 1
                self.play_sound("confirm")

                cell_size = 32
                board_w = self.grid_w * cell_size
                start_x = (320 - board_w) // 2
                start_y = 50
                ex_px = start_x + self.exit_pos[0] * cell_size + cell_size // 2
                ex_py = start_y + self.exit_pos[1] * cell_size + cell_size // 2
                for _ in range(12):
                    ang = random.uniform(0, math.pi * 2)
                    spd = random.uniform(40, 100)
                    self.particles.append(
                        {
                            "x": ex_px,
                            "y": ex_py,
                            "vx": math.cos(ang) * spd,
                            "vy": math.sin(ang) * spd,
                            "life": 0.4,
                            "color": (0, 255, 180),
                        }
                    )

                # Pausen/Rest-Timer komplett entfernt – Level steigt direkt und ohne Verzögerung
                if self.sectors_cleared >= 3 and self.level < 3:
                    self.level += 1
                    self.sectors_cleared = 0

                self.setup_level()
                return

            self._trigger_system_glitch()

    def _trigger_system_glitch(self) -> None:
        gx = random.randint(0, self.grid_w - 1)
        gy = random.randint(0, self.grid_h - 1)
        if [gx, gy] != self.player_pos and [gx, gy] != self.exit_pos:
            self.glitched_tiles.add((gx, gy))
            if len(self.glitched_tiles) > (self.level + 3):
                self.glitched_tiles.pop()

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.time_remaining -= dt
        if self.time_remaining <= 0:
            self.game_over = True
            self.play_sound("gameover")
            return

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        self.glitch_timer += dt
        if self.glitch_timer > max(1.5, 4.0 - (self.level * 0.8)):
            self.glitch_timer = 0.0
            self._trigger_system_glitch()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((6, 10, 18))

        for x in range(0, 320, 20):
            pygame.draw.line(surface, (10, 18, 30), (x, 0), (x, 240), 1)
        for y in range(0, 240, 20):
            pygame.draw.line(surface, (10, 18, 30), (0, y), (320, y), 1)

        cell_size = 32
        board_w = self.grid_w * cell_size
        start_x = (320 - board_w) // 2
        start_y = 50

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        for r in range(self.grid_h):
            for c in range(self.grid_w):
                rx = start_x + c * cell_size
                ry = start_y + r * cell_size
                rect = pygame.Rect(rx + 2, ry + 2, cell_size - 4, cell_size - 4)

                if [c, r] == self.exit_pos:
                    pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 40)
                    pygame.draw.rect(
                        surface, (0, 200 + pulse, 150 + pulse), rect, border_radius=4
                    )
                    pygame.draw.circle(
                        surface,
                        (255, 255, 255),
                        (rx + cell_size // 2, ry + cell_size // 2),
                        5,
                    )
                elif (c, r) in self.glitched_tiles:
                    glitch_col = (
                        (255, 40, 90)
                        if int(pygame.time.get_ticks() / 150) % 2 == 0
                        else (160, 20, 50)
                    )
                    pygame.draw.rect(surface, glitch_col, rect, border_radius=4)
                    pygame.draw.rect(surface, (255, 100, 150), rect, 1, border_radius=4)
                else:
                    pygame.draw.rect(surface, (15, 28, 45), rect, border_radius=4)
                    pygame.draw.rect(surface, (35, 60, 95), rect, 1, border_radius=4)

        px = start_x + self.player_pos[0] * cell_size + cell_size // 2
        py = start_y + self.player_pos[1] * cell_size + cell_size // 2
        pygame.draw.circle(surface, (255, 215, 0), (px, py), 11)
        pygame.draw.circle(surface, (255, 140, 0), (px, py), 11, 2)
        pygame.draw.circle(surface, (255, 255, 255), (px, py), 4)

        lvl_txt = self.font.render(
            f"SECTOR {self.level} | TARGETS: {self.sectors_cleared}/3",
            True,
            (0, 255, 200),
        )
        surface.blit(lvl_txt, (160 - lvl_txt.get_width() // 2, 6))

        pygame.draw.rect(surface, (20, 10, 15), (35, 222, 250, 10), border_radius=4)
        timer_ratio = max(0.0, self.time_remaining / self.time_limit)
        bar_w = int(250 * timer_ratio)
        if bar_w > 0:
            bar_col = (0, 255, 150) if timer_ratio > 0.3 else (255, 50, 80)
            pygame.draw.rect(surface, bar_col, (35, 222, bar_w, 10), border_radius=4)

        time_txt = (
            self.code_font.render(
                f"TIME: {int(self.time_remaining)}s", True, (255, 255, 255)
            )
            if hasattr(self, "code_font")
            else self.font.render(
                f"TIME: {int(self.time_remaining)}s", True, (255, 255, 255)
            )
        )
        surface.blit(time_txt, (160 - time_txt.get_width() // 2, 201))

        self.render_ui(surface)

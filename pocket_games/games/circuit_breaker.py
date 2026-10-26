# ==========================================
# CIRCUIT BREAKER v1.1
# A gripping puzzle and logic game set on a futuristic cybernetic circuit board.
# Connect the start and end nodes by toggling microchip states to activate the
# data stream before the timer runs out.
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class CircuitBreakerGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Circuit Breaker")
        self.grid_w, self.grid_h = 5, 4
        self.level = 1
        self.solved_count = 0
        self.nodes = []
        self.timer = 18.0
        self._generate_circuit()

    def _generate_circuit(self) -> None:
        # Adjust grid size per level (more nodes from Lvl 5 and Lvl 15)
        self.grid_w = min(7, 5 + (self.level // 5))
        self.grid_h = min(5, 4 + (self.level // 15))

        # Increase the number of possible values/states from level 10
        num_states = min(5, 3 + (self.level // 10))

        self.nodes.clear()
        for r in range(self.grid_h):
            row = []
            for c in range(self.grid_w):
                row.append({"state": random.randint(0, num_states - 1), "active": False})
            self.nodes.append(row)
        self.nodes[0][0]["active"] = True
        self._update_flow()

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        board_w_px = min(280, self.grid_w * 52)
        board_h_px = min(160, self.grid_h * 42)
        start_x = (320 - board_w_px) // 2
        start_y = 35
        cell_w = board_w_px // self.grid_w
        cell_h = board_h_px // self.grid_h
        chip_w = cell_w - 8
        chip_h = cell_h - 6

        inp = self.engine.input
        if inp.mouse_clicked:
            mx, my = self.get_virtual_mouse_pos()
            for r in range(self.grid_h):
                for c in range(self.grid_w):
                    rx = start_x + c * cell_w + 4
                    ry = start_y + r * cell_h + 3
                    if pygame.Rect(rx, ry, chip_w, chip_h).collidepoint(mx, my):
                        num_states = min(5, 3 + (self.level // 10))
                        self.nodes[r][c]["state"] = (self.nodes[r][c]["state"] + 1) % num_states
                        self.play_sound("hit")
                        self._update_flow()

    def _update_flow(self) -> None:
        for r in range(self.grid_h):
            for c in range(self.grid_w):
                self.nodes[r][c]["active"] = False

        self.nodes[0][0]["active"] = True
        queue = [(0, 0)]

        while queue:
            cr, cc = queue.pop(0)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = cr + dr, cc + dc
                if (
                    0 <= nr < self.grid_h
                    and 0 <= nc < self.grid_w
                    and (
                        not self.nodes[nr][nc]["active"]
                        and self.nodes[nr][nc]["state"] == self.nodes[cr][cc]["state"]
                    )
                ):
                    self.nodes[nr][nc]["active"] = True
                    queue.append((nr, nc))

        if self.nodes[self.grid_h - 1][self.grid_w - 1]["active"]:
            self.add_score(250 + (self.level * 50))
            self.play_sound("score")
            self.solved_count += 1

            if self.solved_count % 3 == 0:
                self.level += 1

            bonus_time = max(3.0, 6.0 - (self.level * 0.4))
            self.timer = min(18.0, self.timer + bonus_time)
            self._generate_circuit()

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        drain_multiplier = 1.0 + (self.level - 1) * 0.12
        self.timer -= dt * drain_multiplier
        if self.timer <= 0:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 14, 24))
        for x in range(0, 320, 20):
            pygame.draw.line(surface, (12, 22, 36), (x, 0), (x, 240), 1)
        for y in range(0, 240, 20):
            pygame.draw.line(surface, (12, 22, 36), (0, y), (320, y), 1)

        board_w_px = min(280, self.grid_w * 52)
        board_h_px = min(160, self.grid_h * 42)
        start_x = (320 - board_w_px) // 2
        start_y = 35
        cell_w = board_w_px // self.grid_w
        cell_h = board_h_px // self.grid_h
        chip_w = cell_w - 8
        chip_h = cell_h - 6

        # Leiterbahnen
        for r in range(self.grid_h):
            for c in range(self.grid_w):
                rx = start_x + c * cell_w + 4
                ry = start_y + r * cell_h + 3
                x1, y1 = rx + chip_w // 2, ry + chip_h // 2

                if c + 1 < self.grid_w:
                    next_rx = start_x + (c + 1) * cell_w + 4
                    x2 = next_rx + chip_w // 2
                    active_line = (
                        self.nodes[r][c]["active"]
                        and self.nodes[r][c + 1]["active"]
                        and self.nodes[r][c]["state"] == self.nodes[r][c + 1]["state"]
                    )
                    color = (0, 255, 200) if active_line else (24, 42, 64)
                    pygame.draw.line(surface, color, (x1, y1), (x2, y1), 4)
                    pygame.draw.line(
                        surface,
                        (255, 255, 255) if active_line else (15, 28, 45),
                        (x1, y1),
                        (x2, y1),
                        1,
                    )

                if r + 1 < self.grid_h:
                    next_ry = start_y + (r + 1) * cell_h + 3
                    y2 = next_ry + chip_h // 2
                    active_line = (
                        self.nodes[r][c]["active"]
                        and self.nodes[r + 1][c]["active"]
                        and self.nodes[r][c]["state"] == self.nodes[r + 1][c]["state"]
                    )
                    color = (0, 255, 200) if active_line else (24, 42, 64)
                    pygame.draw.line(surface, color, (x1, y1), (x1, y2), 4)
                    pygame.draw.line(
                        surface,
                        (255, 255, 255) if active_line else (15, 28, 45),
                        (x1, y1),
                        (x1, y2),
                        1,
                    )

        # Mikrochip-Knotenpunkte
        for r in range(self.grid_h):
            for c in range(self.grid_w):
                node = self.nodes[r][c]
                rx = start_x + c * cell_w + 4
                ry = start_y + r * cell_h + 3

                is_start = r == 0 and c == 0
                is_end = r == self.grid_h - 1 and c == self.grid_w - 1

                if is_start:
                    border_color = (255, 215, 0)
                    fill_color = (45, 35, 10)
                elif is_end:
                    border_color = (255, 50, 150)
                    fill_color = (45, 15, 30)
                else:
                    border_color = (0, 255, 200) if node["active"] else (60, 80, 110)
                    fill_color = (15, 35, 50) if node["active"] else (18, 28, 42)

                pygame.draw.rect(surface, fill_color, (rx, ry, chip_w, chip_h), border_radius=5)
                pygame.draw.rect(
                    surface, border_color, (rx, ry, chip_w, chip_h), 2, border_radius=5
                )

                led_col = (0, 255, 100) if node["active"] else (100, 40, 40)
                pygame.draw.circle(surface, led_col, (rx + 8, ry + 8), 2)

                lbl = self.title_font.render(
                    str(node["state"]),
                    True,
                    (255, 255, 255) if node["active"] else (160, 180, 200),
                )
                surface.blit(
                    lbl,
                    (rx + chip_w // 2 - lbl.get_width() // 2, ry + chip_h // 2 - lbl.get_height() // 2),
                )

        # Level display and timer bar
        lvl_info = self.font.render(f"CIRCUIT LEVEL {self.level} ({self.grid_w}x{self.grid_h})", True, (0, 255, 200))
        surface.blit(lvl_info, (160 - lvl_info.get_width() // 2, 8))

        pygame.draw.rect(surface, (15, 25, 40), (20, 222, 280, 10), border_radius=4)
        timer_w = int(280 * (max(0.0, self.timer) / 18.0))
        if timer_w > 0:
            timer_color = (0, 255, 150) if self.timer > 6.0 else (255, 50, 80)
            pygame.draw.rect(
                surface, timer_color, (20, 222, timer_w, 10), border_radius=4
            )
            pygame.draw.line(
                surface, (255, 255, 255), (20, 223), (20 + timer_w, 223), 1
            )

        self.render_ui(surface)

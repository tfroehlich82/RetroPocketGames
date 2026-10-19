# ==========================================
# CIRCUIT BREAKER (Cybernetic Circuit Board)
# ==========================================
import random

import pygame

from pocket_games.games.base import BaseGame


class CircuitBreakerGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Circuit Breaker")
        self.grid_w, self.grid_h = 5, 4
        self.nodes = []
        self.timer = 18.0
        self._generate_circuit()

    def _generate_circuit(self) -> None:
        self.nodes.clear()
        for r in range(self.grid_h):
            row = []
            for c in range(self.grid_w):
                row.append({"state": random.choice([0, 1, 2]), "active": False})
            self.nodes.append(row)
        self.nodes[0][0]["active"] = True
        self._update_flow()

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.mouse_clicked:
            mx, my = inp.mouse_pos
            for r in range(self.grid_h):
                for c in range(self.grid_w):
                    rx, ry = 40 + c * 50, 45 + r * 42
                    if pygame.Rect(rx, ry, 42, 36).collidepoint(mx, my):
                        self.nodes[r][c]["state"] = (self.nodes[r][c]["state"] + 1) % 3
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
            self.add_score(250)
            self.play_sound("score")
            self.timer = min(18.0, self.timer + 5.0)
            self._generate_circuit()

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((6, 12, 18))

        for r in range(self.grid_h):
            for c in range(self.grid_w):
                x1, y1 = 40 + c * 50 + 21, 45 + r * 42 + 18
                if c + 1 < self.grid_w:
                    x2 = 40 + (c + 1) * 50 + 21
                    active_line = (
                        self.nodes[r][c]["active"]
                        and self.nodes[r][c + 1]["active"]
                        and self.nodes[r][c]["state"] == self.nodes[r][c + 1]["state"]
                    )
                    color = (0, 220, 255) if active_line else (30, 50, 70)
                    pygame.draw.line(surface, color, (x1, y1), (x2, y1), 3)
                if r + 1 < self.grid_h:
                    y2 = 45 + (r + 1) * 42 + 18
                    active_line = (
                        self.nodes[r][c]["active"]
                        and self.nodes[r + 1][c]["active"]
                        and self.nodes[r][c]["state"] == self.nodes[r + 1][c]["state"]
                    )
                    color = (0, 220, 255) if active_line else (30, 50, 70)
                    pygame.draw.line(surface, color, (x1, y1), (x1, y2), 3)

        for r in range(self.grid_h):
            for c in range(self.grid_w):
                node = self.nodes[r][c]
                rx, ry = 40 + c * 50, 45 + r * 42

                is_endpoint = (r == 0 and c == 0) or (
                    r == self.grid_h - 1 and c == self.grid_w - 1
                )
                border_color = (
                    (255, 215, 0)
                    if is_endpoint
                    else ((0, 255, 200) if node["active"] else (70, 90, 110))
                )
                fill_color = (15, 30, 45) if not node["active"] else (20, 60, 80)

                pygame.draw.rect(surface, fill_color, (rx, ry, 42, 36), border_radius=6)
                pygame.draw.rect(
                    surface, border_color, (rx, ry, 42, 36), 2, border_radius=6
                )

                lbl = self.font.render(
                    str(node["state"]),
                    True,
                    (255, 255, 255) if node["active"] else (150, 160, 170),
                )
                surface.blit(
                    lbl,
                    (rx + 21 - lbl.get_width() // 2, ry + 18 - lbl.get_height() // 2),
                )

        pygame.draw.rect(surface, (20, 10, 15), (20, 222, 280, 10), border_radius=4)
        timer_w = int(280 * (max(0.0, self.timer) / 18.0))
        if timer_w > 0:
            timer_color = (0, 255, 150) if self.timer > 6.0 else (255, 50, 80)
            pygame.draw.rect(
                surface, timer_color, (20, 222, timer_w, 10), border_radius=4
            )

        self.render_ui(surface)

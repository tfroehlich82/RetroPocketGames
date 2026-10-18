# ==========================================
# CIRCUIT BREAKER (Dynamic Logic Flow Puzzle)
# ==========================================
import random

import pygame

from pocket_games.games.base import BaseGame


class CircuitBreakerGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Circuit Breaker")
        self.grid_w, self.grid_h = 5, 4
        self.nodes = []
        self.timer = 15.0
        self._generate_circuit()

    def _generate_circuit(self) -> None:
        self.nodes.clear()
        for r in range(self.grid_h):
            row = []
            for c in range(self.grid_w):
                row.append({"state": random.choice([0, 1, 2]), "active": False})

            self.nodes.append(row)
        self.nodes[0][0]["active"] = True

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.mouse_clicked:
            mx, my = inp.mouse_pos
            for r in range(self.grid_h):
                for c in range(self.grid_w):
                    rx, ry = 50 + c * 48, 50 + r * 40
                    if pygame.Rect(rx, ry, 36, 30).collidepoint(mx, my):
                        self.nodes[r][c]["state"] = (self.nodes[r][c]["state"] + 1) % 3
                        self.play_sound("hit")
                        self._update_flow()

    def _update_flow(self) -> None:
        for r in range(self.grid_h):
            for c in range(self.grid_w):
                self.nodes[r][c]["active"] = False

        self.nodes[0][0]["active"] = True
        queue = [(0, 0)]
        connected = 0

        while queue:
            cr, cc = queue.pop(0)
            connected += 1
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = cr + dr, cc + dc
                if 0 <= nr < self.grid_h and 0 <= nc < self.grid_w and (
                        not self.nodes[nr][nc]["active"]
                        and self.nodes[nr][nc]["state"] == self.nodes[cr][cc]["state"]
                ):
                    self.nodes[nr][nc]["active"] = True
                    queue.append((nr, nc))

        if self.nodes[self.grid_h - 1][self.grid_w - 1]["active"]:
            self.add_score(200)
            self.play_sound("score")
            self.timer = max(5.0, 15.0 - self.elapsed_time * 0.2)
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
        surface.fill((10, 25, 20))

        for r in range(self.grid_h):
            for c in range(self.grid_w):
                node = self.nodes[r][c]
                rx, ry = 50 + c * 48, 50 + r * 40
                color = (0, 255, 100) if node["active"] else (80, 80, 90)
                pygame.draw.rect(surface, color, (rx, ry, 36, 30), border_radius=4)

                lbl = self.font.render(str(node["state"]), True, (0, 0, 0))
                surface.blit(lbl, (rx + 14, ry + 8))

        # Render Timer Bar
        pygame.draw.rect(
            surface, (255, 50, 50), (10, 220, int(300 * (self.timer / 15.0)), 8)
        )
        self.render_ui(surface)

# ==========================================
# CIRCUIT BREAKER v1.0
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
        self.nodes = []
        self.timer = 18.0
        self.particles: list[dict] = []
        self._generate_circuit()

    def _generate_circuit(self) -> None:
        self.nodes.clear()
        for r in range(self.grid_h):
            row = []
            for c in range(self.grid_w):
                # Symbole oder Hex-Zahlen für die Chips (0, 1, 2)
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
            mx, my = self.get_virtual_mouse_pos()
            for r in range(self.grid_h):
                for c in range(self.grid_w):
                    rx, ry = 38 + c * 52, 40 + r * 42
                    if pygame.Rect(rx, ry, 44, 36).collidepoint(mx, my):
                        self.nodes[r][c]["state"] = (self.nodes[r][c]["state"] + 1) % 3
                        self.play_sound("hit")
                        # Kleine Funken-Partikel beim Schalten
                        for _ in range(4):
                            self.particles.append({
                                "x": rx + 22, "y": ry + 18,
                                "vx": random.uniform(-40, 40), "vy": random.uniform(-40, 40),
                                "life": 0.2, "color": (0, 255, 200)
                            })
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

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

    def render(self, surface: pygame.Surface) -> None:
        # Tech-Hintergrund mit Platinen-Rastermuster
        surface.fill((8, 14, 24))
        for x in range(0, 320, 20):
            pygame.draw.line(surface, (12, 22, 36), (x, 0), (x, 240), 1)
        for y in range(0, 240, 20):
            pygame.draw.line(surface, (12, 22, 36), (0, y), (320, y), 1)

        # Leiterbahnen (Verbindungen zwischen Nodes)
        for r in range(self.grid_h):
            for c in range(self.grid_w):
                x1, y1 = 38 + c * 52 + 22, 40 + r * 42 + 18
                if c + 1 < self.grid_w:
                    x2 = 38 + (c + 1) * 52 + 22
                    active_line = (
                        self.nodes[r][c]["active"]
                        and self.nodes[r][c + 1]["active"]
                        and self.nodes[r][c]["state"] == self.nodes[r][c + 1]["state"]
                    )
                    color = (0, 255, 200) if active_line else (24, 42, 64)
                    pygame.draw.line(surface, color, (x1, y1), (x2, y1), 4)
                    # Doppelte Leiterbahn für High-Tech-Look
                    pygame.draw.line(surface, (255, 255, 255) if active_line else (15, 28, 45), (x1, y1), (x2, y1), 1)

                if r + 1 < self.grid_h:
                    y2 = 40 + (r + 1) * 42 + 18
                    active_line = (
                        self.nodes[r][c]["active"]
                        and self.nodes[r + 1][c]["active"]
                        and self.nodes[r][c]["state"] == self.nodes[r + 1][c]["state"]
                    )
                    color = (0, 255, 200) if active_line else (24, 42, 64)
                    pygame.draw.line(surface, color, (x1, y1), (x1, y2), 4)
                    pygame.draw.line(surface, (255, 255, 255) if active_line else (15, 28, 45), (x1, y1), (x1, y2), 1)

        # Mikrochip-Knotenpunkte (Nodes)
        for r in range(self.grid_h):
            for c in range(self.grid_w):
                node = self.nodes[r][c]
                rx, ry = 38 + c * 52, 40 + r * 42

                is_start = (r == 0 and c == 0)
                is_end = (r == self.grid_h - 1 and c == self.grid_w - 1)

                if is_start:
                    border_color = (255, 215, 0)
                    fill_color = (45, 35, 10)
                elif is_end:
                    border_color = (255, 50, 150)
                    fill_color = (45, 15, 30)
                else:
                    border_color = (0, 255, 200) if node["active"] else (60, 80, 110)
                    fill_color = (15, 35, 50) if node["active"] else (18, 28, 42)

                # Chip-Gehäuse mit abgerundeten Ecken und technischen Pins
                pygame.draw.rect(surface, fill_color, (rx, ry, 44, 36), border_radius=5)
                pygame.draw.rect(surface, border_color, (rx, ry, 44, 36), 2, border_radius=5)

                # Kleine Mikrochip-Pins an den Seiten
                pygame.draw.line(surface, border_color, (rx - 3, ry + 10), (rx, ry + 10), 2)
                pygame.draw.line(surface, border_color, (rx - 3, ry + 26), (rx, ry + 26), 2)
                pygame.draw.line(surface, border_color, (rx + 44, ry + 10), (rx + 47, ry + 10), 2)
                pygame.draw.line(surface, border_color, (rx + 44, ry + 26), (rx + 47, ry + 26), 2)

                # Status-LED in der Ecke des Chips
                led_col = (0, 255, 100) if node["active"] else (100, 40, 40)
                pygame.draw.circle(surface, led_col, (rx + 8, ry + 8), 2)

                # Zustandswert (Chip-Zahl)
                lbl = self.title_font.render(
                    str(node["state"]),
                    True,
                    (255, 255, 255) if node["active"] else (160, 180, 200),
                )
                surface.blit(
                    lbl,
                    (rx + 22 - lbl.get_width() // 2, ry + 18 - lbl.get_height() // 2),
                )

        # Partikel rendern
        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        # Sci-Fi Timer-Leiste am unteren Bildschirmrand
        pygame.draw.rect(surface, (15, 25, 40), (20, 222, 280, 10), border_radius=4)
        timer_w = int(280 * (max(0.0, self.timer) / 18.0))
        if timer_w > 0:
            timer_color = (0, 255, 150) if self.timer > 6.0 else (255, 50, 80)
            pygame.draw.rect(
                surface, timer_color, (20, 222, timer_w, 10), border_radius=4
            )
            # Glanzstrich
            pygame.draw.line(surface, (255, 255, 255), (20, 223), (20 + timer_w, 223), 1)

        self.render_ui(surface)

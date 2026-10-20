# ==========================================
# KERNEL PANIC (Terminal Glitch Edition)
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class KernelPanicGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Kernel Panic")
        self.leaks: list[dict] = []
        self.spawn_timer = 0.0
        self.memory_used = 0.0  # 0% to 100%

        # Unabhängige Scanline, die sich fließend von oben nach unten und zurück bewegt
        self.scanline_y = 0.0
        self.scanline_dir = 1.0
        self.scanline_speed = 75.0

        # Kleinere, dedizierte Schriftart für den Text innerhalb der Blöcke
        try:
            self.code_font = pygame.font.Font(None, 13)
        except Exception:  # noqa: BLE001
            self.code_font = pygame.font.SysFont("sans-serif", 11)

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active:
            return

        inp = self.engine.input
        if inp.mouse_clicked:
            vx, vy = self.get_virtual_mouse_pos()
            for l in self.leaks[:]:
                if abs(l["x"] - vx) < 20 and abs(l["y"] - vy) < 20:
                    self.leaks.remove(l)
                    self.add_score(25)
                    self.memory_used = max(0.0, self.memory_used - 6.0)
                    self.engine.audio.play("confirm")
                    return

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        # Scanline-Bewegung von oben nach unten und wieder zurück
        self.scanline_y += self.scanline_speed * self.scanline_dir * dt
        if self.scanline_y > 240:
            self.scanline_y = 240
            self.scanline_dir = -1.0
        elif self.scanline_y < 0:
            self.scanline_y = 0
            self.scanline_dir = 1.0

        # Schwierigkeit steigt dynamisch mit zunehmender Punktzahl
        score_multiplier = 1.0 + (self.score / 150.0)
        spawn_interval = max(0.25, 0.7 - (self.score * 0.004))

        self.spawn_timer += dt
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0.0
            base_speed = random.uniform(65.0, 110.0)
            self.leaks.append(
                {
                    "x": random.randint(35, 285),
                    "y": -15.0,
                    "speed": base_speed * score_multiplier,
                    "size": random.randint(20, 26),
                    "code": random.choice(["0x0", "ERR", "NULL", "SEG", "BUF"]),
                }
            )

        for l in self.leaks[:]:
            l["y"] += l["speed"] * dt
            if l["y"] > 240:
                self.leaks.remove(l)
                self.memory_used += 14.0
                self.engine.audio.play("hit")

        if self.memory_used >= 100.0:
            self.game_over = True

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((12, 18, 14))

        for y in range(0, 240, 20):
            pygame.draw.line(surface, (18, 28, 20), (0, y), (320, y), 1)

        # Unabhängige Scanline-Linie
        pygame.draw.line(
            surface,
            (40, 180, 90),
            (0, int(self.scanline_y)),
            (320, int(self.scanline_y)),
            2,
        )

        for l in self.leaks:
            lx, ly = int(l["x"]), int(l["y"])
            s = l["size"]
            rect = pygame.Rect(lx - s // 2, ly - s // 2, s, s)
            pygame.draw.rect(surface, (255, 30, 80), rect, border_radius=3)
            pygame.draw.rect(surface, (255, 200, 220), rect, 2, border_radius=3)

            # Code-Beschriftung mit angepasster kleiner Schrift innerhalb des Blocks
            txt = self.code_font.render(l["code"], True, (255, 255, 255))
            surface.blit(txt, (lx - txt.get_width() // 2, ly - txt.get_height() // 2))

        pygame.draw.rect(surface, (20, 35, 25), (15, 220, 290, 12), border_radius=4)
        mem_w = int(290 * (min(100.0, self.memory_used) / 100.0))
        mem_color = (
            (0, 255, 120)
            if self.memory_used < 50
            else ((255, 180, 0) if self.memory_used < 80 else (255, 30, 50))
        )
        if mem_w > 0:
            pygame.draw.rect(surface, mem_color, (15, 220, mem_w, 12), border_radius=4)

        mem_txt = self.font.render(
            f"RAM USAGE: {int(self.memory_used)}%", True, (255, 255, 255)
        )
        surface.blit(mem_txt, (160 - mem_txt.get_width() // 2, 201))

        if self.game_over:
            go = self.title_font.render("KERNEL PANIC!", True, (255, 40, 40))
            surface.blit(go, (160 - go.get_width() // 2, 100))

        self.render_ui(surface)

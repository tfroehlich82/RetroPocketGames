# ==========================================
# KERNEL PANIC v1.0
# A fast-paced terminal defense game.
# Click on falling memory leaks and critical system errors
# before they completely exhaust your RAM.
# Increasing speeds driven by your score ensure a continuous and escalating challenge.
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
                if abs(l["x"] - vx) < 22 and abs(l["y"] - vy) < 22:
                    self.leaks.remove(l)
                    points = 40 if l.get("fatal") else 25
                    self.add_score(points)
                    reduction = 10.0 if l.get("fatal") else 6.0
                    self.memory_used = max(0.0, self.memory_used - reduction)
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

        # Sanft ansteigende Schwierigkeit für eine deutlich längere, angenehmere Spieldauer
        score_factor = self.score / 400.0
        spawn_interval = max(0.6, 1.4 - (score_factor * 0.4))

        self.spawn_timer += dt
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0.0
            is_fatal = self.score > 250 and random.random() < 0.2
            base_speed = random.uniform(45.0, 75.0)  # Deutlich entspannterer Start
            speed_multiplier = 1.0 + (self.score / 500.0)  # Sehr sanfter Anstieg
            code_str = (
                "FATAL"
                if is_fatal
                else random.choice(["0x0", "ERR", "NULL", "SEG", "BUF"])
            )

            self.leaks.append(
                {
                    "x": random.randint(35, 285),
                    "y": -15.0,
                    "speed": base_speed * speed_multiplier,
                    "size": 24 if is_fatal else random.randint(20, 25),
                    "code": code_str,
                    "fatal": is_fatal,
                }
            )

        for l in self.leaks[:]:
            l["y"] += l["speed"] * dt
            if l["y"] > 240:
                self.leaks.remove(l)
                penalty = 18.0 if l.get("fatal") else 12.0
                self.memory_used += penalty
                self.engine.audio.play("hit")

        if self.memory_used >= 100.0:
            self.game_over = True

    def render(self, surface: pygame.Surface) -> None:
        bg_color = (25, 12, 14) if self.memory_used >= 80 else (12, 18, 14)
        surface.fill(bg_color)

        for y in range(0, 240, 20):
            pygame.draw.line(surface, (18, 28, 20), (0, y), (320, y), 1)

        # Scanline-Linie mit Glow-Effekt
        scan_y = int(self.scanline_y)
        pygame.draw.line(surface, (20, 100, 50), (0, scan_y - 1), (320, scan_y - 1), 1)
        pygame.draw.line(surface, (50, 220, 110), (0, scan_y), (320, scan_y), 2)
        pygame.draw.line(surface, (20, 100, 50), (0, scan_y + 1), (320, scan_y + 1), 1)

        for l in self.leaks:
            lx, ly = int(l["x"]), int(l["y"])
            s = l["size"]
            rect = pygame.Rect(lx - s // 2, ly - s // 2, s, s)

            box_color = (255, 20, 60) if l.get("fatal") else (255, 40, 90)
            border_color = (255, 200, 220) if not l.get("fatal") else (255, 255, 0)

            pygame.draw.rect(surface, box_color, rect, border_radius=3)
            pygame.draw.rect(surface, border_color, rect, 2, border_radius=3)

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

from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class KernelPanicGame(BaseGame):
    """Refactored Kernel Panic game with BaseGame architecture."""

    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Kernel Panic")
        self.leaks: list[dict] = []
        self.spawn_timer = 0.0
        self.spawn_interval = 0.75
        self.memory_used = 0.0  # 0% to 100%

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active:
            return

        inp = self.engine.input
        if inp.mouse_clicked:
            vx, vy = self.get_virtual_mouse_pos()
            for l in self.leaks[:]:
                if abs(l["x"] - vx) < 18 and abs(l["y"] - vy) < 18:
                    self.leaks.remove(l)
                    self.add_score(20)
                    self.memory_used = max(0.0, self.memory_used - 5.0)
                    self.engine.audio.play("confirm")
                    return

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self.leaks.append(
                {
                    "x": random.randint(30, 290),
                    "y": -15.0,
                    "speed": random.uniform(60.0, 110.0),
                    "size": random.randint(16, 24),
                }
            )

        for l in self.leaks[:]:
            l["y"] += l["speed"] * dt
            if l["y"] > 240:
                self.leaks.remove(l)
                self.memory_used += 15.0
                self.engine.audio.play("hit")

        if self.memory_used >= 100.0:
            self.game_over = True

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((25, 10, 15))

        # Leaks
        for l in self.leaks:
            lx, ly = int(l["x"]), int(l["y"])
            s = l["size"]
            pygame.draw.rect(surface, (255, 40, 60), (lx - s // 2, ly - s // 2, s, s), border_radius=4)
            pygame.draw.rect(surface, (255, 200, 200), (lx - s // 2, ly - s // 2, s, s), 1, border_radius=4)

        # Memory Meter at the bottom
        pygame.draw.rect(surface, (40, 20, 20), (20, 225, 280, 10), border_radius=3)
        mem_w = int(280 * (min(100.0, self.memory_used) / 100.0))
        mem_color = (0, 255, 100) if self.memory_used < 50 else ((255, 200, 0) if self.memory_used < 80 else (255, 0, 0))
        if mem_w > 0:
            pygame.draw.rect(surface, mem_color, (20, 225, mem_w, 10), border_radius=3)

        if self.game_over:
            go = self.title_font.render("KERNEL PANIC!", True, (255, 0, 0))
            surface.blit(go, (160 - go.get_width() // 2, 110))

        self.render_ui(surface)

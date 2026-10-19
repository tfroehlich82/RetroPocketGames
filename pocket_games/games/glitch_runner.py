# ==========================================
# GLITCH RUNNER (Fast-Paced Snappy Edition)
# ==========================================
from __future__ import annotations

import pygame

from pocket_games.games.base import BaseGame


class GlitchRunnerGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Glitch Runner")
        self.px, self.py = 40.0, 150.0
        self.vy = 0.0
        self.glitch_phase = False
        self.timer = 0.0
        self.score_count = 0

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if (
            inp.is_key_just_pressed(pygame.K_SPACE)
            or inp.mouse_clicked
            or inp.is_key_just_pressed(pygame.K_UP)
            or inp.is_key_just_pressed(pygame.K_w)
        ) and self.py >= 148:
            self.vy = -160  # Sehr kurzer, schneller Sprung (minimale Air-Time)
            self.play_sound("bounce")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.timer += dt

        # Sanft ansteigende Schwierigkeit
        interval = max(1.4, 4.5 - (self.score_count * 0.1))

        if self.timer > interval:
            self.timer = 0.0
            self.glitch_phase = not self.glitch_phase

        # Hohe Schwerkraft für extrem schnelles Landen
        self.vy += 650 * dt
        self.py += self.vy * dt

        if self.py > 150:
            if self.glitch_phase:
                self.game_over = True
                self.play_sound("gameover")
            else:
                self.py = 150
                self.vy = 0
                self.score_count += 1
                self.add_score(1)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((12, 15, 22))

        interval = max(1.4, 4.5 - (self.score_count * 0.1))
        warning = self.timer > (interval - 0.6)

        floor_color = (
            (255, 200, 50)
            if warning and int(self.timer * 18) % 2 == 0
            else ((255, 40, 100) if self.glitch_phase else (0, 255, 160))
        )

        pygame.draw.rect(surface, floor_color, (0, 162, 320, 20), border_radius=4)
        pygame.draw.rect(surface, (255, 220, 0), (int(self.px), int(self.py), 14, 14), border_radius=3)

        if warning:
            warn_txt = self.font.render("GLITCH WARNING!", True, (255, 200, 0))
            surface.blit(warn_txt, (160 - warn_txt.get_width() // 2, 25))

        self.render_ui(surface)

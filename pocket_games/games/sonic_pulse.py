# ==========================================
# 17: SONIC PULSE (Rhythm Collapsing Ring)
# ==========================================
import random

import pygame

from pocket_games.games.base import BaseGame


class SonicPulseGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Sonic Pulse")
        self.pulse_radius = 5.0
        self.target_radius = 50.0
        self.expanding = False

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if (inp.is_key_pressed(pygame.K_SPACE) or inp.mouse_clicked) and not self.expanding:
            self.expanding = True

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        if self.expanding:
            self.pulse_radius += 120.0 * dt
            if abs(self.pulse_radius - self.target_radius) < 8.0:
                self.add_score(50)
                self.play_sound("score")
                self._reset_ring()
            elif self.pulse_radius > self.target_radius + 15:
                self.game_over = True
                self.play_sound("gameover")

    def _reset_ring(self) -> None:
        self.pulse_radius = 5.0
        self.target_radius = float(random.randint(30, 80))
        self.expanding = False

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 20, 25))
        pygame.draw.circle(surface, (255, 0, 120), (160, 120), int(self.target_radius), 3)
        pygame.draw.circle(surface, (0, 220, 255), (160, 120), int(self.pulse_radius), 2)
        self.render_ui(surface)

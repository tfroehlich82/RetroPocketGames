# ==========================================
# 18: GRAVITY SLING (Planetary Gravity Wells)
# ==========================================
import math

import pygame

from pocket_games.games.base import BaseGame


class GravitySlingGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Gravity Sling")
        self.px, self.py = 50.0, 120.0
        self.vx, self.vy = 80.0, -40.0
        self.planet = (160, 120, 25)

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.is_key_just_pressed(pygame.K_SPACE) or inp.mouse_clicked:
            # Thrust Pulse
            self.vy -= 60
            self.play_sound("bounce")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        # Gravity pull toward planet
        dx = self.planet[0] - self.px
        dy = self.planet[1] - self.py
        dist = math.hypot(dx, dy)

        if dist < self.planet[2]:
            self.game_over = True
            self.play_sound("gameover")
            return

        force = 15000.0 / (dist ** 2)
        self.vx += (dx / dist) * force * dt
        self.vy += (dy / dist) * force * dt

        self.px += self.vx * dt
        self.py += self.vy * dt

        if 0 <= self.px <= 320 and 0 <= self.py <= 240:
            self.add_score(1)

        if self.px < 0 or self.px > 320 or self.py < 0 or self.py > 240:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((5, 10, 20))
        pygame.draw.circle(surface, (100, 150, 255), (self.planet[0], self.planet[1]), self.planet[2])
        pygame.draw.circle(surface, (255, 215, 0), (int(self.px), int(self.py)), 4)
        self.render_ui(surface)

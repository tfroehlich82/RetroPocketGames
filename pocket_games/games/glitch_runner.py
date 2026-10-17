# ==========================================
# 19: GLITCH RUNNER (Phase-shifting Platforms)
# ==========================================
import pygame

from pocket_games.games.base import BaseGame


class GlitchRunnerGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Glitch Runner")
        self.px, self.py = 40.0, 150.0
        self.vy = 0.0
        self.glitch_phase = False
        self.timer = 0.0

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if (inp.is_key_pressed(pygame.K_SPACE) or inp.mouse_clicked) and self.py >= 150:
            self.vy = -220
            self.play_sound("bounce")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.timer += dt
        if self.timer > 1.2:
            self.timer = 0.0
            self.glitch_phase = not self.glitch_phase

        self.vy += 500 * dt
        self.py += self.vy * dt

        if self.py > 150:
            if self.glitch_phase:
                self.game_over = True  # Fell through glitched floor
                self.play_sound("gameover")
            else:
                self.py = 150
                self.vy = 0
                self.add_score(2)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 15, 20))
        floor_color = (255, 50, 100) if self.glitch_phase else (0, 255, 150)
        pygame.draw.rect(surface, floor_color, (0, 162, 320, 20))
        pygame.draw.rect(surface, (255, 200, 0), (int(self.px), int(self.py), 12, 12))
        self.render_ui(surface)

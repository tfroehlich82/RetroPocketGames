# ==========================================
# 20: AETHER DEFENDER (Color-matching Shoot 'em up)
# ==========================================
import random

import pygame

from pocket_games.games.base import BaseGame


class AetherDefenderGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Aether Defender")
        self.px = 160.0
        self.color_state = 0  # 0: Blue, 1: Red
        self.enemies = []
        self.spawn_timer = 0.0

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.is_key_down(pygame.K_LEFT):
            self.px = max(20, self.px - 140 * 0.016)
        if inp.is_key_down(pygame.K_RIGHT):
            self.px = min(300, self.px + 140 * 0.016)
        if inp.is_key_just_pressed(pygame.K_SPACE) or inp.mouse_clicked:
            self.color_state = 1 - self.color_state
            self.play_sound("bounce")

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.spawn_timer += dt
        if self.spawn_timer > 0.8:
            self.spawn_timer = 0.0
            self.enemies.append({"x": random.randint(20, 300), "y": -10, "color": random.choice([0, 1])})

        p_rect = pygame.Rect(int(self.px) - 10, 200, 20, 15)
        for e in self.enemies[:]:
            e["y"] += 90 * dt
            e_rect = pygame.Rect(e["x"] - 8, int(e["y"]), 16, 16)

            if p_rect.colliderect(e_rect):
                if e["color"] == self.color_state:
                    self.enemies.remove(e)
                    self.add_score(30)
                    self.play_sound("score")
                else:
                    self.game_over = True
                    self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 10, 15))
        p_color = (0, 200, 255) if self.color_state == 0 else (255, 50, 50)
        pygame.draw.rect(surface, p_color, (int(self.px) - 10, 200, 20, 15), border_radius=3)

        for e in self.enemies:
            e_color = (0, 200, 255) if e["color"] == 0 else (255, 50, 50)
            pygame.draw.circle(surface, e_color, (e["x"], int(e["y"])), 8)

        self.render_ui(surface)

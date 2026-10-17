# ==========================================
# 16: CHRONO SHIFT (Time Anomaly Field)
# ==========================================
import math
import random

import pygame

from pocket_games.games.base import BaseGame


class ChronoShiftGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Chrono Shift")
        self.px, self.py = 160.0, 120.0
        self.fragments = []
        self.anomalies = []
        self.spawn_timer = 0.0

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        spd = 120.0
        if inp.is_key_down(pygame.K_LEFT):
            self.px = max(10, self.px - spd * 0.016)
        if inp.is_key_down(pygame.K_RIGHT):
            self.px = min(310, self.px + spd * 0.016)
        if inp.is_key_down(pygame.K_UP):
            self.py = max(10, self.py - spd * 0.016)
        if inp.is_key_down(pygame.K_DOWN):
            self.py = min(230, self.py + spd * 0.016)

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.spawn_timer += dt
        if self.spawn_timer > 1.0:
            self.spawn_timer = 0.0
            self.fragments.append(pygame.Rect(random.randint(20, 300), random.randint(20, 220), 10, 10))
            if len(self.anomalies) < 5:
                self.anomalies.append({"x": random.randint(30, 290), "y": random.randint(30, 210), "r": 15})

        player_rect = pygame.Rect(int(self.px), int(self.py), 12, 12)
        for f in self.fragments[:]:
            if player_rect.colliderect(f):
                self.fragments.remove(f)
                self.add_score(35)
                self.play_sound("score")

        for a in self.anomalies:
            if math.hypot(self.px - a["x"], self.py - a["y"]) < a["r"]:
                self.game_over = True
                self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((20, 15, 30))
        for a in self.anomalies:
            pygame.draw.circle(surface, (180, 0, 255), (a["x"], a["y"]), a["r"], 2)
        for f in self.fragments:
            pygame.draw.rect(surface, (255, 215, 0), f)

        pygame.draw.rect(surface, (0, 255, 150), (int(self.px), int(self.py), 12, 12))
        self.render_ui(surface)

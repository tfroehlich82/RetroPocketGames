from __future__ import annotations

import random

import pygame


class NeonDashGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.lanes = [80, 160, 240]
        self.player_lane = 1
        self.obstacles = [{"lane": random.randint(0, 2), "y": -50}]
        self.spawn_timer = 0.0
        self.game_over = False

    def handle_input(self) -> None:
        inp = self.engine.input
        if inp.is_key_pressed(pygame.K_ESCAPE):
            self.active = False
        if self.game_over:
            if inp.is_key_pressed(pygame.K_RETURN) or inp.mouse_clicked:
                self.__init__(self.engine)
            return
        if inp.is_key_pressed(pygame.K_LEFT) and self.player_lane > 0:
            self.player_lane -= 1
        if inp.is_key_pressed(pygame.K_RIGHT) and self.player_lane < 2:
            self.player_lane += 1

        if inp.mouse_clicked:
            if inp.mouse_pos[0] < 160 and self.player_lane > 0:
                self.player_lane -= 1
            elif inp.mouse_pos[0] >= 160 and self.player_lane < 2:
                self.player_lane += 1

    def update(self, dt: float) -> None:
        if self.game_over:
            return
        self.score += int(dt * 50)
        self.engine.highscores.submit_score("Neon Dash", self.score)
        self.spawn_timer += dt
        if self.spawn_timer > 1.2:
            self.spawn_timer = 0.0
            self.obstacles.append({"lane": random.randint(0, 2), "y": -30})

        for obs in self.obstacles:
            obs["y"] += 150 * dt
            if obs["lane"] == self.player_lane and abs(obs["y"] - 190) < 15:
                self.game_over = True

        self.obstacles = [o for o in self.obstacles if o["y"] < 260]

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((25, 10, 30))
        for l in self.lanes:
            pygame.draw.line(surface, (60, 30, 80), (l, 0), (l, 240), 2)

        # Player
        px = self.lanes[self.player_lane]
        pygame.draw.rect(surface, (0, 255, 200), (px - 10, 180, 20, 25), border_radius=4)

        # Obstacles
        for obs in self.obstacles:
            ox = self.lanes[obs["lane"]]
            pygame.draw.rect(surface, (255, 0, 100), (ox - 12, int(obs["y"]), 24, 15), border_radius=3)

        sc = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))
        if self.game_over:
            go = self.font.render("CRASH! Tap/Enter to restart", True, (255, 50, 50))
            surface.blit(go, (70, 110))

from __future__ import annotations

import random

import pygame

# from pocket_games.core.engine import VIRTUAL_HEIGHT, VIRTUAL_WIDTH


class PixelDropGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.cols, self.rows = 10, 16
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.block_y = 0.0
        self.block_x = 4
        self.block_color = 1
        self.drop_timer = 0.0
        self.drop_speed = 0.5
        self.game_over = False

    def handle_input(self) -> None:
        inp = self.engine.input
        if (
            inp.is_key_pressed(pygame.K_ESCAPE)
            or inp.is_key_pressed(pygame.K_BACKSPACE)
            or self.engine.input.is_back_pressed()
        ):
            self.active = False
        if self.game_over:
            if inp.is_key_pressed(pygame.K_RETURN) or inp.mouse_clicked:
                self.__init__(self.engine)
            return

        if inp.is_key_pressed(pygame.K_LEFT) and self.block_x > 0:  # noqa: SIM102
            if self.grid[int(self.block_y)][self.block_x - 1] == 0:
                self.block_x -= 1
        if inp.is_key_pressed(pygame.K_RIGHT) and self.block_x < self.cols - 1:  # noqa: SIM102
            if self.grid[int(self.block_y)][self.block_x + 1] == 0:
                self.block_x += 1
        if inp.is_key_pressed(pygame.K_DOWN):
            self.drop_speed = 0.1

    def update(self, dt: float) -> None:
        if self.game_over:
            return
        self.drop_timer += dt
        if self.drop_timer >= self.drop_speed:
            self.drop_timer = 0.0
            next_y = int(self.block_y) + 1
            if next_y >= self.rows or self.grid[next_y][self.block_x] != 0:
                # Lock block
                self.grid[int(self.block_y)][self.block_x] = self.block_color
                self.score += 10
                self.engine.highscores.submit_score("Pixel Drop", self.score)
                # Reset new block
                self.block_x = random.randint(0, self.cols - 1)
                self.block_y = 0.0
                self.block_color = random.randint(1, 4)
                self.drop_speed = 0.5
                if self.grid[0][self.block_x] != 0:
                    self.game_over = True
            else:
                self.block_y += 1.0

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((20, 20, 30))
        ox, oy = 80, 20
        cw, ch = 12, 12

        # Draw grid
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(ox + c * cw, oy + r * ch, cw - 1, ch - 1)
                val = self.grid[r][c]
                color = (60, 60, 80) if val == 0 else (0, 200, 255)
                pygame.draw.rect(surface, color, rect)

        # Draw active block
        if not self.game_over:
            act_rect = pygame.Rect(ox + self.block_x * cw, oy + int(self.block_y) * ch, cw - 1, ch - 1)
            pygame.draw.rect(surface, (255, 100, 100), act_rect)

        # UI
        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(score_surf, (10, 10))
        if self.game_over:
            go_surf = self.font.render("GAME OVER! Tap/Enter", True, (255, 0, 0))
            surface.blit(go_surf, (85, 100))

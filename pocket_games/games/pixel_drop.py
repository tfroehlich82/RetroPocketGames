# ==========================================
# PIXEL DROP v1.0
# A classic block puzzle game featuring refined progression mechanics.
# Every 10 successfully cleared lines advance the player to the next level.
# The falling speed remains constant throughout each level and increases
# only upon leveling up.
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame

SHAPES = [
    [[1, 1, 1, 1]],          # I
    [[1, 1], [1, 1]],        # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
    [[0, 1, 1], [1, 0, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
]
SHAPE_COLORS = [
    (0, 240, 240),
    (240, 240, 0),
    (160, 0, 240),
    (240, 160, 0),
    (0, 0, 240),
    (0, 240, 0),
    (240, 0, 0),
]


class PixelDropGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Pixel Drop")
        self.cols, self.rows = 10, 18
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.next_shape_idx = random.randint(0, len(SHAPES) - 1)
        self.total_cleared_lines = 0
        self.level = 1
        self._spawn_piece()
        self.drop_timer = 0.0
        self.lock_timer = 0.0
        self.is_locking = False

    def _spawn_piece(self) -> None:
        self.current_shape_idx = self.next_shape_idx
        self.next_shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.current_shape_idx]
        self.color = SHAPE_COLORS[self.current_shape_idx]
        self.px = self.cols // 2 - len(self.shape[0]) // 2
        self.py = 0
        self.lock_timer = 0.0
        self.is_locking = False

        if self._check_collision(self.px, self.py, self.shape):
            self.game_over = True
            self.play_sound("gameover")

    def _check_collision(self, px: int, py: int, shape: list[list[int]]) -> bool:
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    gx, gy = px + c, py + r
                    if gx < 0 or gx >= self.cols or gy >= self.rows:
                        return True
                    if gy >= 0 and self.grid[gy][gx] is not None:
                        return True
        return False

    def _rotate_shape(self) -> list[list[int]]:
        return [list(row) for row in zip(*self.shape[::-1])]

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input

        if inp.is_key_just_pressed(pygame.K_LEFT) and not self._check_collision(
            self.px - 1, self.py, self.shape
        ):
            self.px -= 1
            if self.is_locking:
                self.lock_timer = 0.0
        elif inp.is_key_just_pressed(pygame.K_RIGHT) and not self._check_collision(
            self.px + 1, self.py, self.shape
        ):
            self.px += 1
            if self.is_locking:
                self.lock_timer = 0.0

        if inp.is_key_just_pressed(pygame.K_UP):
            rotated = self._rotate_shape()
            if not self._check_collision(self.px, self.py, rotated):
                self.shape = rotated
                self.play_sound("bounce")
                if self.is_locking:
                    self.lock_timer = 0.0

        if inp.is_key_down(pygame.K_DOWN) and not self._check_collision(
            self.px, self.py + 1, self.shape
        ):
            self.py += 1
            self.drop_timer = 0.0

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        # The falling speed remains constant throughout each level
        # and increases only upon leveling up
        drop_speed = max(0.12, 0.70 - ((self.level - 1) * 0.1))
        self.drop_timer += dt

        touching_ground = self._check_collision(self.px, self.py + 1, self.shape)

        if touching_ground:
            self.is_locking = True
            self.lock_timer += dt
            if self.lock_timer >= 0.45:
                self._lock_piece()
        else:
            self.is_locking = False
            self.lock_timer = 0.0
            if self.drop_timer >= drop_speed:
                self.drop_timer = 0.0
                self.py += 1

    def _lock_piece(self) -> None:
        for r, row in enumerate(self.shape):
            for c, val in enumerate(row):
                if val and self.py + r >= 0:
                    self.grid[self.py + r][self.px + c] = self.color
        self._clear_lines()
        self._spawn_piece()

    def _clear_lines(self) -> None:
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = self.rows - len(new_grid)
        for _ in range(cleared):
            new_grid.insert(0, [None for _ in range(self.cols)])
        self.grid = new_grid

        if cleared > 0:
            self.total_cleared_lines += cleared
            # Level up after 10 cleared rows
            self.level = (self.total_cleared_lines // 10) + 1

            bonus_multipliers = {1: 100, 2: 300, 3: 500, 4: 800}
            points = bonus_multipliers.get(cleared, cleared * 250) * self.level

            self.add_score(points)
            self.play_sound("score")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 15, 25))
        ox, oy, cw, ch = 25, 20, 11, 11

        # Render Grid
        pygame.draw.rect(
            surface,
            (40, 40, 60),
            (ox - 2, oy - 2, self.cols * cw + 4, self.rows * ch + 4),
            2,
        )
        for r in range(self.rows):
            for c in range(self.cols):
                color = self.grid[r][c] or (25, 25, 35)
                pygame.draw.rect(
                    surface, color, (ox + c * cw, oy + r * ch, cw - 1, ch - 1)
                )

        # Render Active Block
        if not self.game_over:
            for r, row in enumerate(self.shape):
                for c, val in enumerate(row):
                    if val:
                        pygame.draw.rect(
                            surface,
                            self.color,
                            (
                                ox + (self.px + c) * cw,
                                oy + (self.py + r) * ch,
                                cw - 1,
                                ch - 1,
                            ),
                        )

        # Render Level Info
        level_txt = self.font.render(f"LEVEL: {self.level}", True, (255, 220, 0))
        surface.blit(level_txt, (150, 20))

        # Render Next Preview
        preview_txt = self.font.render("NEXT", True, (200, 200, 200))
        surface.blit(preview_txt, (150, 50))
        next_shape = SHAPES[self.next_shape_idx]
        next_color = SHAPE_COLORS[self.next_shape_idx]
        for r, row in enumerate(next_shape):
            for c, val in enumerate(row):
                if val:
                    pygame.draw.rect(
                        surface, next_color, (150 + c * cw, 70 + r * ch, cw - 1, ch - 1)
                    )

        self.render_ui(surface)

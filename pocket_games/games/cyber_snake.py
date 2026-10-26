# ==========================================
# CYBER SNAKE v1.0
# A futuristic cyberpunk-themed retro classic.
# Navigate the snake through the grid, collect data nodes to score points,
# and increase your speed with every snack.
# Avoid crashing into boundaries or your own tail.
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class CyberSnakeGame(BaseGame):
    """Refactored Cyber Snake utilizing BaseGame framework."""

    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Cyber Snake")
        self.grid_size = 10
        self.cols = 32
        self.rows = 24  # Total rows; the top area (0-2) is reserved for the HUD
        self.reset_snake()

    def reset_snake(self) -> None:
        self.snake = [{"x": 16, "y": 12}, {"x": 15, "y": 12}, {"x": 14, "y": 12}]
        self.dir = (1, 0)
        self.next_dir = (1, 0)
        self.food = self.spawn_food()
        self.move_timer = 0.0
        self.speed = 0.11
        self.game_over = False

    def spawn_food(self) -> dict[str, int]:
        while True:
            fx = random.randint(1, self.cols - 2)
            fy = random.randint(3, self.rows - 2)
            if not any(s["x"] == fx and s["y"] == fy for s in self.snake):
                return {"x": fx, "y": fy}

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active:
            return

        inp = self.engine.input
        if self.game_over:
            if inp.is_key_just_pressed(pygame.K_RETURN) or inp.is_key_just_pressed(pygame.K_SPACE) or inp.mouse_clicked:
                self.reset_snake()
            return

        if (inp.is_key_just_pressed(pygame.K_UP) or inp.is_key_just_pressed(pygame.K_w)) and self.dir != (0, 1):
            self.next_dir = (0, -1)
        elif (inp.is_key_just_pressed(pygame.K_DOWN) or inp.is_key_just_pressed(pygame.K_s)) and self.dir != (0, -1):
            self.next_dir = (0, 1)
        elif (inp.is_key_just_pressed(pygame.K_LEFT) or inp.is_key_just_pressed(pygame.K_a)) and self.dir != (1, 0):
            self.next_dir = (-1, 0)
        elif (inp.is_key_just_pressed(pygame.K_RIGHT) or inp.is_key_just_pressed(pygame.K_d)) and self.dir != (-1, 0):
            self.next_dir = (1, 0)

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        self.move_timer += dt
        if self.move_timer >= self.speed:
            self.move_timer = 0.0
            self.dir = self.next_dir

            head = {"x": self.snake[0]["x"] + self.dir[0], "y": self.snake[0]["y"] + self.dir[1]}

            # Wall collision (taking the HUD in rows 0-2 into account) or self-collision
            if (
                head["x"] < 0
                or head["x"] >= self.cols
                or head["y"] < 3
                or head["y"] >= self.rows
                or any(s["x"] == head["x"] and s["y"] == head["y"] for s in self.snake)
            ):
                self.game_over = True
                self.engine.audio.play("hit")
                return

            self.snake.insert(0, head)

            if head["x"] == self.food["x"] and head["y"] == self.food["y"]:
                self.add_score(15)
                self.food = self.spawn_food()
                self.speed = max(0.05, self.speed - 0.002)
                self.engine.audio.play("confirm")
            else:
                self.snake.pop()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 12, 10))

        # Grid lines background
        for x in range(0, 320, 20):
            pygame.draw.line(surface, (15, 25, 20), (x, 30), (x, 240), 1)
        for y in range(30, 240, 20):
            pygame.draw.line(surface, (15, 25, 20), (0, y), (320, y), 1)

        # Render Food
        fx, fy = self.food["x"] * self.grid_size, self.food["y"] * self.grid_size
        pygame.draw.rect(surface, (255, 0, 100), (fx + 1, fy + 1, 8, 8), border_radius=2)

        # Render Snake
        for idx, s in enumerate(self.snake):
            sx, sy = s["x"] * self.grid_size, s["y"] * self.grid_size
            color = (0, 255, 150) if idx == 0 else (0, 180, 100)
            pygame.draw.rect(surface, color, (sx + 1, sy + 1, 8, 8), border_radius=2)

        if self.game_over:
            go = self.title_font.render("GAME OVER", True, (255, 50, 50))
            sub = self.font.render("Press Enter or Tap to Restart", True, (200, 200, 200))
            surface.blit(go, (160 - go.get_width() // 2, 100))
            surface.blit(sub, (160 - sub.get_width() // 2, 130))

        self.render_ui(surface)

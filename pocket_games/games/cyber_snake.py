from __future__ import annotations

import random

import pygame


class CyberSnakeGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.snake = [{"x": 10, "y": 10}, {"x": 9, "y": 10}, {"x": 8, "y": 10}]
        self.dir = (1, 0)
        self.food = {"x": random.randint(2, 28), "y": random.randint(2, 18)}
        self.timer = 0.0
        self.game_over = False

    def handle_input(self) -> None:
        inp = self.engine.input
        if inp.is_key_pressed(pygame.K_ESCAPE):
            self.active = False
        if self.game_over:
            if inp.is_key_pressed(pygame.K_RETURN) or inp.mouse_clicked:
                self.__init__(self.engine)
            return
        if (inp.is_key_pressed(pygame.K_UP) or inp.is_key_pressed(pygame.K_w)) and self.dir != (0, 1):
            self.dir = (0, -1)
        elif (inp.is_key_pressed(pygame.K_DOWN) or inp.is_key_pressed(pygame.K_s)) and self.dir != (0, -1):
            self.dir = (0, 1)
        elif (inp.is_key_pressed(pygame.K_LEFT) or inp.is_key_pressed(pygame.K_a)) and self.dir != (1, 0):
            self.dir = (-1, 0)
        elif (inp.is_key_pressed(pygame.K_RIGHT) or inp.is_key_pressed(pygame.K_d)) and self.dir != (-1, 0):
            self.dir = (1, 0)

    def update(self, dt: float) -> None:
        if self.game_over:
            return
        self.timer += dt
        if self.timer >= 0.12:
            self.timer = 0.0
            head = {"x": self.snake[0]["x"] + self.dir[0], "y": self.snake[0]["y"] + self.dir[1]}
            if head["x"] < 0 or head["x"] >= 32 or head["y"] < 0 or head["y"] >= 24 or head in self.snake:
                self.game_over = True
                return
            self.snake.insert(0, head)
            if head["x"] == self.food["x"] and head["y"] == self.food["y"]:
                self.score += 15
                self.engine.highscores.submit_score("Cyber Snake", self.score)
                self.food = {"x": random.randint(2, 28), "y": random.randint(2, 18)}
            else:
                self.snake.pop()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 15, 10))
        for s in self.snake:
            pygame.draw.rect(surface, (0, 255, 100), (s["x"] * 10, s["y"] * 10, 9, 9), border_radius=2)
        pygame.draw.rect(surface, (255, 0, 100), (self.food["x"] * 10, self.food["y"] * 10, 9, 9), border_radius=2)
        sc = self.font.render(f"Cyber Snake: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))
        if self.game_over:
            go = self.font.render("GAME OVER - Tap/Enter", True, (255, 0, 0))
            surface.blit(go, (80, 110))

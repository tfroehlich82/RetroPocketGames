# ==========================================
# BIT BLASTER v1.0
# An action-packed brick breaker featuring 20 progressively challenging levels.
# With each cleared level, the ball speed increases slightly, the paddle becomes
# narrower, and higher stages introduce tougher multi-hit bricks.
# Conquer all 20 levels to beat the system.
# ==========================================
from __future__ import annotations

import pygame

from pocket_games.core.physics import clamp, handle_paddle_collision
from pocket_games.games.base import BaseGame


class Paddle:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.rect = pygame.Rect(x, y, width, height)


class Ball:
    def __init__(self, x: float, y: float, radius: int, vx: float, vy: float) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = vx
        self.vy = vy
        self.rect = pygame.Rect(
            int(x - radius), int(y - radius), radius * 2, radius * 2
        )

    def update_rect(self) -> None:
        self.rect.center = (int(self.x), int(self.y))


class BitBlasterGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Bit Blaster")
        self.px = 160.0
        self.level = 1
        self.max_levels = 20

        # Paddle in Level 1 ca. doppelt so groß (100px), verringert sich progressiv bis Level 20 auf 45px
        paddle_w = max(45, 100 - (self.level - 1) * 3)
        self.paddle = Paddle(int(self.px) - paddle_w // 2, 215, paddle_w, 8)

        # Ballgeschwindigkeit steigt pro Level an
        initial_speed = 100.0 + (self.level - 1) * 7.0
        self.ball = Ball(160.0, 120.0, 5, initial_speed, -initial_speed)

        self.blocks = []
        self._init_blocks()

    def _init_blocks(self) -> None:
        self.blocks.clear()
        rows = min(6, 4 + (self.level - 1) // 5)
        cols = 7

        colors = [
            (255, 80, 80),
            (255, 180, 0),
            (0, 220, 255),
            (180, 100, 255),
            (255, 50, 150),
            (50, 255, 100),
        ]

        for r in range(rows):
            for c in range(cols):
                hp = 2 if (self.level >= 10 and r == 0 and c % 2 == 0) else 1
                color = colors[r % len(colors)]
                self.blocks.append(
                    {
                        "rect": pygame.Rect(c * 42 + 13, r * 16 + 30, 38, 12),
                        "color": color,
                        "hp": hp,
                        "max_hp": hp,
                        "alive": True,
                    }
                )

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        half_w = self.paddle.rect.width // 2

        # Exakte Begrenzung an den Wänden (Wände bei x=5 und x=315), damit kein Ball durchrutschen kann
        min_x = 5 + half_w
        max_x = 315 - half_w

        if inp.is_left_pressed():
            self.px = max(min_x, self.px - 7)
        if inp.is_right_pressed():
            self.px = min(max_x, self.px + 7)
        if inp.mouse_clicked:
            vx, _vy = self.get_virtual_mouse_pos()
            self.px = clamp(vx, float(min_x), float(max_x))

        self.paddle.rect.x = int(self.px) - half_w

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        speed_mod = min(1.6, 1.0 + (self.elapsed_time * 0.004))
        self.ball.x += self.ball.vx * dt * speed_mod
        self.ball.y += self.ball.vy * dt * speed_mod
        self.ball.update_rect()

        if self.ball.rect.left <= 5:
            self.ball.rect.left = 5
            self.ball.vx = abs(self.ball.vx)
            self.play_sound("bounce")
        elif self.ball.rect.right >= 315:
            self.ball.rect.right = 315
            self.ball.vx = -abs(self.ball.vx)
            self.play_sound("bounce")

        if self.ball.rect.top <= 5:
            self.ball.rect.top = 5
            self.ball.vy = abs(self.ball.vy)
            self.play_sound("bounce")

        if self.ball.rect.colliderect(self.paddle.rect):
            handle_paddle_collision(self.ball, self.paddle)
            self.ball.x, self.ball.y = (
                float(self.ball.rect.centerx),
                float(self.ball.rect.centery),
            )
            self.play_sound("hit")

        all_cleared = True
        for blk in self.blocks:
            if blk["alive"]:
                all_cleared = False
                if self.ball.rect.colliderect(blk["rect"]):
                    blk["hp"] -= 1
                    if blk["hp"] <= 0:
                        blk["alive"] = False
                        self.add_score(25 * self.level)
                        self.play_sound("score")
                    else:
                        self.play_sound("hit")
                    self.ball.vy *= -1
                    break

        if all_cleared:
            if self.level < self.max_levels:
                self.level += 1
                paddle_w = max(45, 100 - (self.level - 1) * 3)
                self.paddle.rect.width = paddle_w
                speed = 120.0 + (self.level - 1) * 7.0
                self.ball.x, self.ball.y = 160.0, 120.0
                self.ball.vx = speed if self.ball.vx > 0 else -speed
                self.ball.vy = -abs(speed)
                self.play_sound("confirm")
                self._init_blocks()
            else:
                self.game_won = True
                self.play_sound("confirm")

        if self.ball.rect.top > 240:
            self.game_over = True
            self.play_sound("gameover")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 10, 25))
        pygame.draw.rect(surface, (0, 200, 255), self.paddle.rect, border_radius=3)
        pygame.draw.circle(surface, (255, 255, 0), self.ball.rect.center, 5)

        for blk in self.blocks:
            if blk["alive"]:
                color = (
                    blk["color"]
                    if blk["hp"] == max(1, blk["max_hp"])
                    else (120, 120, 140)
                )
                pygame.draw.rect(surface, color, blk["rect"], border_radius=2)
                pygame.draw.rect(
                    surface, (255, 255, 255), blk["rect"], 1, border_radius=2
                )

        lvl_txt = self.font.render(f"LVL {self.level}/20", True, (0, 255, 200))
        surface.blit(lvl_txt, (150, 5))

        self.render_ui(surface)

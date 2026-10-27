# ==========================================
# BIT BLASTER v1.1
# An action-packed brick breaker featuring 20 progressively challenging levels.
# With each cleared level, the ball speed increases slightly, the paddle becomes
# narrower, and higher stages introduce tougher multi-hit bricks.
# Conquer all 20 levels to beat the system.
# ==========================================
from __future__ import annotations

import pygame

from pocket_games.core.physics import clamp, handle_paddle_collision
from pocket_games.core.settings import BIT_BLASTER_TUNING_FILE
from pocket_games.core.tuning import get_number, get_section
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
        super().__init__(engine, "Bit Blaster", tuning_file=BIT_BLASTER_TUNING_FILE)
        self._game = get_section(self.tuning, "game")
        self._paddle_cfg = get_section(self.tuning, "paddle")
        self._ball_cfg = get_section(self.tuning, "ball")
        self._brick_cfg = get_section(self.tuning, "bricks")
        self.px = 160.0
        self.lives = int(get_number(self._game, "lives", 3))
        self.level = 1
        self.max_levels = int(get_number(self._game, "max_levels", 20))

        paddle_w = self._paddle_width()
        self.paddle = Paddle(
            int(self.px) - paddle_w // 2,
            int(get_number(self._paddle_cfg, "y", 215)),
            paddle_w,
            int(get_number(self._paddle_cfg, "height", 8)),
        )

        initial_speed = self._ball_speed()
        self.ball = Ball(
            160.0,
            120.0,
            int(get_number(self._ball_cfg, "radius", 5)),
            initial_speed,
            -initial_speed,
        )

        self.blocks = []
        self._init_blocks()

    def _paddle_width(self) -> int:
        base = get_number(self._paddle_cfg, "base_width", 100)
        minimum = get_number(self._paddle_cfg, "min_width", 45)
        shrink = get_number(self._paddle_cfg, "shrink_per_level", 3)
        return int(max(minimum, base - (self.level - 1) * shrink))

    def _ball_speed(self) -> float:
        base = get_number(self._ball_cfg, "base_speed", 100.0)
        per_level = get_number(self._ball_cfg, "speed_per_level", 7.0)
        return base + (self.level - 1) * per_level

    def _init_blocks(self) -> None:
        self.blocks.clear()
        base_rows = int(get_number(self._brick_cfg, "base_rows", 4))
        max_rows = int(get_number(self._brick_cfg, "max_rows", 6))
        rows_step = int(get_number(self._brick_cfg, "rows_step_levels", 5))
        tough_from = int(get_number(self._brick_cfg, "tough_from_level", 10))
        rows = min(max_rows, base_rows + (self.level - 1) // rows_step)
        cols = int(get_number(self._brick_cfg, "cols", 7))

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
                hp = 2 if (self.level >= tough_from and r == 0 and c % 2 == 0) else 1
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

    def _reset_ball_position(self) -> None:
        speed = self._ball_speed()
        self.ball.x, self.ball.y = 160.0, 120.0
        self.ball.vx = speed if self.ball.vx > 0 else -speed
        self.ball.vy = -abs(speed)

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        half_w = self.paddle.rect.width // 2

        min_x = 5 + half_w
        max_x = 315 - half_w

        step = get_number(self._paddle_cfg, "move_step", 7)
        if inp.is_left_pressed():
            self.px = max(min_x, self.px - step)
        if inp.is_right_pressed():
            self.px = min(max_x, self.px + step)
        if inp.mouse_clicked:
            vx, _vy = self.get_virtual_mouse_pos()
            self.px = clamp(vx, float(min_x), float(max_x))

        self.paddle.rect.x = int(self.px) - half_w

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        speed_mod = min(
            get_number(self._ball_cfg, "max_speed_mod", 1.6),
            1.0 + (self.elapsed_time * get_number(self._ball_cfg, "speed_ramp", 0.004)),
        )
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
                        self.add_score(int(get_number(self._brick_cfg, "score_per_level", 25)) * self.level)
                        self.play_sound("score")
                    else:
                        self.play_sound("hit")
                    self.ball.vy *= -1
                    break

        if all_cleared:
            if self.level < self.max_levels:
                self.level += 1
                self.paddle.rect.width = self._paddle_width()
                self.play_sound("confirm")
                self._reset_ball_position()
                self._init_blocks()
            else:
                self.game_won = True
                self.play_sound("confirm")

        if self.ball.rect.top > 240:
            self.lives -= 1
            self.play_sound("hit")
            if self.lives <= 0:
                self.game_over = True
                self.play_sound("gameover")
            else:
                self._reset_ball_position()

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

        lvl_txt = self.font.render(f"LIVES: {self.lives} | LVL {self.level}/20", True, (0, 255, 200))
        surface.blit(lvl_txt, (120, 5))

        self.render_ui(surface)

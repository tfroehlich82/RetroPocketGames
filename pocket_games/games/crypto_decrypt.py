# ==========================================
# CRYPTO DECRYPT v1.2
# A masterminds-style logical deduction game.
# Crack the secret 4-digit code within 8 attempts.
# After each guess, feedback indicators show correct
# digits and position matches.
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.games.base import BaseGame


class CryptoDecryptGame(BaseGame):
    """Mastermind-style vault cracking game with manual acknowledgment on failure."""

    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Crypto Decrypt")
        self.code_length = 4
        self.max_attempts = 8
        self.target_code: list[int] = []
        self.current_guess = [0, 0, 0, 0]
        self.cursor = 0
        self.history: list[dict] = []
        self.attempts_left = self.max_attempts
        self.revealing_code = False
        self.input_lockout_timer = 3.0
        self.reset_game()

    def reset_game(self) -> None:
        self.target_code = [random.randint(0, 9) for _ in range(self.code_length)]
        self.current_guess = [0, 0, 0, 0]
        self.cursor = 0
        self.history = []
        self.attempts_left = self.max_attempts
        self.game_over = False
        self.revealing_code = False
        self.input_lockout_timer = 3.0
        self.elapsed_time = 0.0

    def submit_guess(self) -> None:
        if (
            self.game_over
            or self.revealing_code
            or self.attempts_left <= 0
        ):
            return

        target_copy = list(self.target_code)
        guess_copy = list(self.current_guess)

        exact = 0
        near = 0

        for i in range(self.code_length):
            if guess_copy[i] == target_copy[i]:
                exact += 1
                target_copy[i] = -1
                guess_copy[i] = -2

        for i in range(self.code_length):
            if guess_copy[i] >= 0 and guess_copy[i] in target_copy:
                near += 1
                target_copy[target_copy.index(guess_copy[i])] = -1

        self.history.append(
            {"guess": list(self.current_guess), "exact": exact, "near": near}
        )
        self.attempts_left -= 1

        if exact == self.code_length:
            time_spent = max(0.1, self.elapsed_time)
            score_gained = max(100, int(10000 / time_spent) + (self.attempts_left * 200))
            self.add_score(score_gained)
            self.engine.audio.play("confirm")
            self.reset_game()
        elif self.attempts_left <= 0:
            self.revealing_code = True
            self.engine.audio.play("hit")
        else:
            self.engine.audio.play("select")

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused:
            return

        if self.input_lockout_timer > 0.0:
            self.input_lockout_timer -= dt

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active:
            return

        inp = self.engine.input
        if self.game_over:
            if (
                inp.is_key_just_pressed(pygame.K_RETURN)
                or inp.is_key_just_pressed(pygame.K_SPACE)
                or inp.mouse_clicked
            ):
                self.reset_game()
            return

        # Wait for the player's confirmation when the code is revealed
        if self.revealing_code:
            if (
                inp.is_key_just_pressed(pygame.K_RETURN)
                or inp.is_key_just_pressed(pygame.K_SPACE)
                or inp.mouse_clicked
            ):
                self.revealing_code = False
                self.game_over = True
                self.play_sound("confirm")
                if inp.mouse_clicked:
                    inp.mouse_clicked = False
            return

        if inp.is_key_just_pressed(pygame.K_LEFT) or inp.is_key_just_pressed(
            pygame.K_a
        ):
            self.cursor = (self.cursor - 1) % self.code_length
            self.engine.audio.play("select")
        elif inp.is_key_just_pressed(pygame.K_RIGHT) or inp.is_key_just_pressed(
            pygame.K_d
        ):
            self.cursor = (self.cursor + 1) % self.code_length
            self.engine.audio.play("select")
        elif inp.is_key_just_pressed(pygame.K_UP) or inp.is_key_just_pressed(
            pygame.K_w
        ):
            self.current_guess[self.cursor] = (self.current_guess[self.cursor] + 1) % 10
            self.engine.audio.play("select")
        elif inp.is_key_just_pressed(pygame.K_DOWN) or inp.is_key_just_pressed(
            pygame.K_s
        ):
            self.current_guess[self.cursor] = (self.current_guess[self.cursor] - 1) % 10
            self.engine.audio.play("select")
        elif inp.is_key_just_pressed(pygame.K_RETURN) or inp.is_key_just_pressed(
            pygame.K_SPACE
        ):
            if self.input_lockout_timer <= 0.0:
                self.submit_guess()

        if inp.mouse_clicked:
            vx, vy = self.get_virtual_mouse_pos()
            for i in range(self.code_length):
                bx = 65 + i * 44
                by = 180
                if bx <= vx <= bx + 36 and by <= vy <= by + 38:
                    self.cursor = i
                    self.current_guess[i] = (self.current_guess[i] + 1) % 10
                    self.engine.audio.play("select")
                    return
            if 242 <= vx <= 310 and 180 <= vy <= 218 and self.input_lockout_timer <= 0.0:
                self.submit_guess()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((12, 16, 24))

        for x in range(0, 320, 32):
            pygame.draw.line(surface, (18, 24, 36), (x, 0), (x, 240), 1)
        for y in range(0, 240, 32):
            pygame.draw.line(surface, (18, 24, 36), (0, y), (320, y), 1)

        pygame.draw.rect(surface, (22, 10, 14), (10, 15, 300, 28), border_radius=4)
        pygame.draw.rect(surface, (180, 40, 50), (10, 15, 300, 28), 2, border_radius=4)

        alarm_on = int(pygame.time.get_ticks() / 250) % 2 == 0
        led_color = (255, 50, 50) if alarm_on else (100, 20, 20)
        pygame.draw.circle(surface, led_color, (24, 29), 6)
        pygame.draw.circle(surface, (255, 200, 200), (22, 27), 2)

        status_txt = self.font.render(
            f"VAULT SECURE | TIME: {round(self.elapsed_time, 1)}s",
            True,
            (255, 220, 100),
        )
        surface.blit(status_txt, (38, 22))

        if self.input_lockout_timer > 0.0:
            lock_txt = self.font.render(
                f"SECURITY LOCKOUT: {math.ceil(self.input_lockout_timer)}s",
                True,
                (255, 100, 100),
            )
            surface.blit(lock_txt, (110, 46))

        pygame.draw.rect(surface, (8, 12, 18), (15, 62, 290, 108), border_radius=4)
        pygame.draw.rect(surface, (40, 60, 90), (15, 62, 290, 108), 1, border_radius=4)

        visible_history = self.history[-6:]
        for idx, entry in enumerate(visible_history):
            hy = 68 + idx * 16
            g_str = " ".join(map(str, entry["guess"]))
            txt = self.font.render(
                f"LOG #{self.history.index(entry) + 1}: [{g_str}]",
                True,
                (200, 210, 225),
            )
            surface.blit(txt, (22, hy))

            for e in range(entry["exact"]):
                pygame.draw.circle(surface, (0, 255, 120), (220 + e * 12, hy + 6), 4)
            for n in range(entry["near"]):
                pygame.draw.circle(
                    surface, (255, 200, 0), (220 + (entry["exact"] + n) * 12, hy + 6), 4
                )

        if self.revealing_code:
            code_str = " ".join(map(str, self.target_code))
            reveal_txt = self.font.render(
                f"VAULT BREACHED! CODE: {code_str}", True, (255, 200, 0)
            )
            surface.blit(reveal_txt, (35, 185))

            cont_txt = self.font.render(
                "PRESS ENTER / TOUCH TO CONTINUE", True, (150, 180, 220)
            )
            surface.blit(cont_txt, (45, 205))
        elif not self.game_over:
            for i in range(self.code_length):
                bx = 65 + i * 44
                by = 180
                is_sel = i == self.cursor

                box_bg = (30, 45, 65) if is_sel else (16, 26, 40)
                border_col = (0, 255, 200) if is_sel else (70, 100, 130)

                pygame.draw.rect(surface, box_bg, (bx, by, 36, 38), border_radius=4)
                pygame.draw.rect(
                    surface, border_col, (bx, by, 36, 38), 2, border_radius=4
                )
                pygame.draw.rect(
                    surface, (8, 14, 22), (bx + 4, by + 4, 28, 30), border_radius=2
                )

                val_surf = self.title_font.render(
                    str(self.current_guess[i]),
                    True,
                    (255, 255, 255) if is_sel else (210, 230, 255),
                )
                surface.blit(val_surf, (bx + 12, by + 8))

            btn_bg = (180, 40, 50) if self.input_lockout_timer > 0.0 else (0, 160, 100)
            pygame.draw.rect(surface, btn_bg, (242, 180, 68, 38), border_radius=4)
            pygame.draw.rect(
                surface, (255, 255, 255), (242, 180, 68, 38), 1, border_radius=4
            )
            btn_txt = self.font.render("UNLOCK", True, (255, 255, 255))
            surface.blit(btn_txt, (250, 192))
        else:
            code_str = " ".join(map(str, self.target_code))
            go_txt = self.font.render(f"ALARM! CODE: {code_str}", True, (255, 60, 60))
            surface.blit(go_txt, (55, 185))

            restart_txt = self.font.render(
                "PRESS ENTER TO RESET VAULT", True, (150, 180, 220)
            )
            surface.blit(restart_txt, (65, 205))

        self.render_ui(surface)

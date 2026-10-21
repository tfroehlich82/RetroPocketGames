# ==========================================
# CRYPTO DECRYPT v1.0
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
    """Complete overhaul of Crypto Decrypt with Mastermind-style deduction gameplay."""

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
        self.reveal_timer = 0.0
        self.reset_game()

    def reset_game(self) -> None:
        self.target_code = [random.randint(0, 9) for _ in range(self.code_length)]
        self.current_guess = [0, 0, 0, 0]
        self.cursor = 0
        self.history = []
        self.attempts_left = self.max_attempts
        self.game_over = False
        self.revealing_code = False
        self.reveal_timer = 0.0

    def submit_guess(self) -> None:
        if self.game_over or self.revealing_code or self.attempts_left <= 0:
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
            score_gained = 100 + (self.attempts_left * 50)
            self.add_score(score_gained)
            self.engine.audio.play("confirm")
            self.reset_game()
        elif self.attempts_left <= 0:
            # Letzter Versuch aufgebraucht: Code für 3 Sekunden anzeigen
            self.revealing_code = True
            self.reveal_timer = 3.0
            self.engine.audio.play("hit")
        else:
            self.engine.audio.play("select")

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused:
            return

        # 3 Sekunden Wartezeit beim Aufdecken des Codes abarbeiten
        if self.revealing_code:
            self.reveal_timer -= dt
            if self.reveal_timer <= 0.0:
                self.revealing_code = False
                self.game_over = True

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

        # Warten, während der Code aufgedeckt wird, keine Eingaben erlauben
        if self.revealing_code:
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
            self.submit_guess()

        if inp.mouse_clicked:
            vx, vy = self.get_virtual_mouse_pos()
            for i in range(self.code_length):
                bx = 70 + i * 40
                by = 180
                if bx <= vx <= bx + 32 and by <= vy <= by + 36:
                    self.cursor = i
                    self.current_guess[i] = (self.current_guess[i] + 1) % 10
                    self.engine.audio.play("select")
                    return
            if 240 <= vx <= 305 and 180 <= vy <= 216:
                self.submit_guess()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 16, 24))

        # Title / Terminal Header
        pygame.draw.rect(surface, (15, 30, 45), (10, 25, 300, 20), border_radius=3)
        lbl = self.font.render(
            f"ATTEMPTS REMAINING: {self.attempts_left}/{self.max_attempts}",
            True,
            (0, 255, 200),
        )
        surface.blit(lbl, (15, 28))

        # Render History
        visible_history = self.history[-7:]
        for idx, entry in enumerate(visible_history):
            hy = 50 + idx * 18
            g_str = " ".join(map(str, entry["guess"]))
            txt = self.font.render(
                f"TRY {self.history.index(entry) + 1}:  {g_str}", True, (210, 210, 210)
            )
            surface.blit(txt, (20, hy))

            for e in range(entry["exact"]):
                pygame.draw.circle(surface, (0, 255, 100), (160 + e * 12, hy + 6), 4)
            for n in range(entry["near"]):
                pygame.draw.circle(
                    surface, (255, 200, 0), (160 + (entry["exact"] + n) * 12, hy + 6), 4
                )

        # Zustand während des Aufdeckens oder Eingabe
        if self.revealing_code:
            code_str = " ".join(map(str, self.target_code))
            reveal_txt = self.font.render(
                f"CORRECT CODE WAS: {code_str}", True, (255, 200, 0)
            )
            surface.blit(reveal_txt, (50, 185))

            time_txt = self.font.render(
                f"REVEALING IN {math.ceil(self.reveal_timer)}s...",
                True,
                (150, 180, 220),
            )
            surface.blit(time_txt, (95, 205))
        elif not self.game_over:
            for i in range(self.code_length):
                bx = 70 + i * 40
                by = 180
                is_sel = i == self.cursor

                box_bg = (25, 50, 75) if is_sel else (18, 32, 48)
                border_col = (0, 255, 220) if is_sel else (90, 120, 150)

                pygame.draw.rect(surface, box_bg, (bx, by, 32, 36), border_radius=4)
                pygame.draw.rect(
                    surface, border_col, (bx, by, 32, 36), 2, border_radius=4
                )

                val_surf = self.title_font.render(
                    str(self.current_guess[i]),
                    True,
                    (255, 255, 255) if is_sel else (200, 220, 240),
                )
                surface.blit(val_surf, (bx + 10, by + 6))

            # Submit Button
            pygame.draw.rect(
                surface, (0, 180, 100), (240, 180, 65, 36), border_radius=4
            )
            btn_txt = self.font.render("DECRYPT", True, (255, 255, 255))
            surface.blit(btn_txt, (244, 192))
        else:
            code_str = " ".join(map(str, self.target_code))
            go_txt = self.font.render(
                f"FAILED! CODE WAS: {code_str}", True, (255, 50, 50)
            )
            surface.blit(go_txt, (45, 185))

            restart_txt = self.font.render(
                "PRESS ENTER TO RETRY", True, (150, 180, 220)
            )
            surface.blit(restart_txt, (80, 205))

        self.render_ui(surface)

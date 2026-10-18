from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class CryptoDecryptGame(BaseGame):
    """Complete overhaul of Crypto Decrypt with Mastermind-style deduction gameplay."""

    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Crypto Decrypt")
        self.code_length = 4
        self.max_attempts = 6
        self.target_code: list[int] = []
        self.current_guess = [0, 0, 0, 0]
        self.cursor = 0
        self.history: list[dict] = []
        self.attempts_left = self.max_attempts
        self.reset_game()

    def reset_game(self) -> None:
        self.target_code = [random.randint(0, 9) for _ in range(self.code_length)]
        self.current_guess = [0, 0, 0, 0]
        self.cursor = 0
        self.history = []
        self.attempts_left = self.max_attempts
        self.game_over = False

    def submit_guess(self) -> None:
        if self.game_over or self.attempts_left <= 0:
            return

        # Calculate exact matches (correct digit & position) and near matches (correct digit, wrong position)
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

        self.history.append({"guess": list(self.current_guess), "exact": exact, "near": near})
        self.attempts_left -= 1

        if exact == self.code_length:
            score_gained = 100 + (self.attempts_left * 50)
            self.add_score(score_gained)
            self.engine.audio.play("confirm")
            self.reset_game()
        elif self.attempts_left <= 0:
            self.game_over = True
            self.engine.audio.play("hit")
        else:
            self.engine.audio.play("select")

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active:
            return

        inp = self.engine.input
        if self.game_over:
            if inp.is_key_just_pressed(pygame.K_RETURN) or inp.is_key_just_pressed(pygame.K_SPACE) or inp.mouse_clicked:
                self.reset_game()
            return

        if inp.is_key_just_pressed(pygame.K_LEFT) or inp.is_key_just_pressed(pygame.K_a):
            self.cursor = (self.cursor - 1) % self.code_length
            self.engine.audio.play("select")
        elif inp.is_key_just_pressed(pygame.K_RIGHT) or inp.is_key_just_pressed(pygame.K_d):
            self.cursor = (self.cursor + 1) % self.code_length
            self.engine.audio.play("select")
        elif inp.is_key_just_pressed(pygame.K_UP) or inp.is_key_just_pressed(pygame.K_w):
            self.current_guess[self.cursor] = (self.current_guess[self.cursor] + 1) % 10
            self.engine.audio.play("select")
        elif inp.is_key_just_pressed(pygame.K_DOWN) or inp.is_key_just_pressed(pygame.K_s):
            self.current_guess[self.cursor] = (self.current_guess[self.cursor] - 1) % 10
            self.engine.audio.play("select")
        elif inp.is_key_just_pressed(pygame.K_RETURN) or inp.is_key_just_pressed(pygame.K_SPACE):
            self.submit_guess()

        if inp.mouse_clicked:
            vx, vy = self.get_virtual_mouse_pos()
            # Check digit box click
            for i in range(self.code_length):
                bx = 70 + i * 40
                by = 180
                if bx <= vx <= bx + 30 and by <= vy <= by + 35:
                    self.cursor = i
                    self.current_guess[i] = (self.current_guess[i] + 1) % 10
                    self.engine.audio.play("select")
                    return
            # Submit button click
            if 240 <= vx <= 300 and 180 <= vy <= 215:
                self.submit_guess()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 16, 24))

        # Title / Terminal Header
        pygame.draw.rect(surface, (15, 30, 45), (10, 25, 300, 20), border_radius=3)
        lbl = self.font.render(f"ATTEMPTS REMAINING: {self.attempts_left}/{self.max_attempts}", True, (0, 255, 200))
        surface.blit(lbl, (15, 28))

        # Render History
        for idx, entry in enumerate(self.history):
            hy = 50 + idx * 20
            g_str = " ".join(map(str, entry["guess"]))
            txt = self.font.render(f"TRY {idx+1}:  {g_str}", True, (200, 200, 200))
            surface.blit(txt, (20, hy))

            # Render indicators: Green = Exact, Yellow = Near
            for e in range(entry["exact"]):
                pygame.draw.circle(surface, (0, 255, 100), (160 + e * 12, hy + 8), 4)
            for n in range(entry["near"]):
                pygame.draw.circle(surface, (255, 200, 0), (160 + (entry["exact"] + n) * 12, hy + 8), 4)

        # Active Guess Controls
        if not self.game_over:
            for i in range(self.code_length):
                bx = 70 + i * 40
                by = 180
                is_sel = (i == self.cursor)
                color = (0, 255, 200) if is_sel else (40, 60, 80)
                pygame.draw.rect(surface, color, (bx, by, 32, 36), border_radius=4)
                pygame.draw.rect(surface, (0, 255, 250) if is_sel else (100, 100, 100), (bx, by, 32, 36), 2, border_radius=4)

                val_surf = self.title_font.render(str(self.current_guess[i]), True, (255, 255, 255) if is_sel else (180, 180, 180))
                surface.blit(val_surf, (bx + 10, by + 6))

            # Submit Button
            pygame.draw.rect(surface, (0, 180, 100), (240, 180, 65, 36), border_radius=4)
            btn_txt = self.font.render("DECRYPT", True, (255, 255, 255))
            surface.blit(btn_txt, (244, 192))
        else:
            code_str = " ".join(map(str, self.target_code))
            go_txt = self.font.render(f"FAILED! CODE WAS: {code_str}", True, (255, 50, 50))
            surface.blit(go_txt, (60, 190))

        self.render_ui(surface)

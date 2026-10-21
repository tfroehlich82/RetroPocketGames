from __future__ import annotations

import pygame

from pocket_games.core.logger import logger
from pocket_games.games.base import GAME_METADATA, t


class HighScoreScreen:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.font = pygame.font.SysFont(None, 18)
        self.title_font = pygame.font.SysFont(None, 24)
        self.scroll_offset = 0
        self.max_visible = 8
        logger.info("Highscore-Bildschirm geöffnet.")

    def handle_input(self) -> None:
        inp = self.engine.input
        if not inp:
            return

        # Verwende is_key_just_pressed statt get_pressed(), um ein sofortiges 
        # Schließen durch den Menü-Auswahlklick (Enter/Space) zu verhindern.
        if (
            inp.is_key_just_pressed(pygame.K_ESCAPE)
            or inp.is_key_just_pressed(pygame.K_BACKSPACE)
            or inp.is_key_just_pressed(pygame.K_RETURN)
            or inp.is_key_just_pressed(pygame.K_SPACE)
        ):
            self.active = False
            return

        game_keys = list(GAME_METADATA.keys())
        max_scroll = max(0, len(game_keys) - self.max_visible)

        # Präzises, ereignisbasiertes Scrollen
        if inp.is_key_just_pressed(pygame.K_UP) or inp.is_key_just_pressed(pygame.K_w):
            self.scroll_offset = max(0, self.scroll_offset - 1)
            self.engine.audio.play("select")
        elif inp.is_key_just_pressed(pygame.K_DOWN) or inp.is_key_just_pressed(pygame.K_s):
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
            self.engine.audio.play("select")

        for event in inp.events:
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif event.y < 0:
                    self.scroll_offset = min(max_scroll, self.scroll_offset + 1)

        if getattr(inp, "mouse_clicked", False):
            mw, mh = self.engine.screen.get_size()
            _vx = int(inp.mouse_pos[0] * (320 / mw))
            vy = int(inp.mouse_pos[1] * (240 / mh))
            if vy > 210:
                self.active = False

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 15, 25))
        title_text = t(self.engine, "hall_of_fame")
        title = self.title_font.render(title_text, True, (255, 215, 0))
        surface.blit(title, (16, 10))

        game_keys = list(GAME_METADATA.keys())
        scores = self.engine.highscores.scores if hasattr(self.engine, "highscores") and self.engine.highscores else {}

        start_y = 38
        item_h = 21
        visible_keys = game_keys[self.scroll_offset : self.scroll_offset + self.max_visible]

        for i, game_name in enumerate(visible_keys):
            score = scores.get(game_name, 0)
            text_str = f"{game_name}: {score}"
            text = self.font.render(text_str, True, (200, 220, 255))
            surface.blit(text, (20, start_y + i * item_h))

        # Scrollbar / Indicator
        if len(game_keys) > self.max_visible:
            bar_x = 305
            bar_y = 38
            bar_h = self.max_visible * item_h
            pygame.draw.rect(surface, (40, 40, 60), (bar_x, bar_y, 4, bar_h), border_radius=2)
            handle_h = max(10, bar_h * (self.max_visible / len(game_keys)))
            handle_y = bar_y + (bar_h - handle_h) * (self.scroll_offset / max(1, len(game_keys) - self.max_visible))
            pygame.draw.rect(surface, (0, 200, 255), (bar_x, handle_y, 4, handle_h), border_radius=2)

        hint_text = t(self.engine, "back_hint")
        hint = self.font.render(hint_text, True, (120, 120, 160))
        surface.blit(hint, (20, 218))

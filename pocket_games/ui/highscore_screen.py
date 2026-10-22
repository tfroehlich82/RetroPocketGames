from __future__ import annotations

import pygame

from pocket_games.core.logger import logger
from pocket_games.games.base import GAME_METADATA, t


class HighScoreScreen:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.font = pygame.font.SysFont(None, 18)
        self.title_font = pygame.font.SysFont(None, 22)
        self.scroll_offset = 0
        self.max_visible = 7
        logger.info("Highscore-Bildschirm geöffnet.")

    def handle_input(self) -> None:
        inp = self.engine.input
        if not inp:
            return

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
        elif inp.is_key_just_pressed(pygame.K_DOWN) or inp.is_key_just_pressed(
            pygame.K_s
        ):
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

        # Titel
        title_text = t(self.engine, "hall_of_fame")
        title = self.title_font.render(title_text, True, (255, 215, 0))
        surface.blit(title, (16, 8))

        # Tabellen-Header
        header_game = self.font.render("GAME", True, (140, 160, 200))
        header_score = self.font.render("SCORE", True, (140, 160, 200))
        surface.blit(header_game, (20, 32))
        surface.blit(header_score, (230, 32))
        pygame.draw.line(surface, (40, 50, 80), (16, 48), (295, 48), 1)

        game_keys = list(GAME_METADATA.keys())
        highscores_mgr = (
            self.engine.highscores
            if hasattr(self.engine, "highscores") and self.engine.highscores
            else None
        )

        start_y = 52
        item_h = 22
        visible_keys = game_keys[
            self.scroll_offset : self.scroll_offset + self.max_visible
        ]

        # Tabellenzeilen rendern
        for i, game_name in enumerate(visible_keys):
            row_y = start_y + i * item_h

            # Alternierende Zeilenhintergründe für bessere Lesbarkeit
            if i % 2 == 0:
                pygame.draw.rect(
                    surface,
                    (20, 22, 35),
                    (16, row_y - 2, 280, item_h - 1),
                    border_radius=3,
                )

            score = 0
            if highscores_mgr:
                if hasattr(highscores_mgr, "get_score"):
                    score = highscores_mgr.get_score(game_name)
                elif hasattr(highscores_mgr, "scores"):
                    val = highscores_mgr.scores.get(game_name, 0)
                    score = (
                        val.get("all_time", 0) if isinstance(val, dict) else int(val)
                    )
                elif isinstance(highscores_mgr, dict):
                    val = highscores_mgr.get(game_name, 0)
                    score = (
                        val.get("all_time", 0) if isinstance(val, dict) else int(val)
                    )

            # Linke Spalte: Spielname (Trunkierung falls zu lang)
            display_name = game_name if len(game_name) <= 22 else f"{game_name[:20]}.."
            name_txt = self.font.render(display_name, True, (220, 230, 255))
            surface.blit(name_txt, (20, row_y))

            # Rechte Spalte: Score (rechtsbündig an Position x = 285)
            score_txt = self.font.render(
                f"{score}", True, (0, 255, 180) if score > 0 else (120, 130, 150)
            )
            score_x = 285 - score_txt.get_width()
            surface.blit(score_txt, (score_x, row_y))

        # Scrollbar
        if len(game_keys) > self.max_visible:
            bar_x = 302
            bar_y = 50
            bar_h = self.max_visible * item_h
            pygame.draw.rect(
                surface, (30, 35, 50), (bar_x, bar_y, 4, bar_h), border_radius=2
            )
            handle_h = max(12, bar_h * (self.max_visible / len(game_keys)))
            max_scroll = max(1, len(game_keys) - self.max_visible)
            handle_y = bar_y + (bar_h - handle_h) * (self.scroll_offset / max_scroll)
            pygame.draw.rect(
                surface, (0, 200, 255), (bar_x, handle_y, 4, handle_h), border_radius=2
            )

        # Bottom Hint
        hint_text = t(self.engine, "back_hint")
        hint = self.font.render(hint_text, True, (120, 120, 160))
        surface.blit(hint, (20, 218))

from __future__ import annotations

import pygame

from pocket_games.core.logger import logger


class HighScoreScreen:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.font = pygame.font.SysFont(None, 20)
        self.title_font = pygame.font.SysFont(None, 26)
        logger.info("Highscore-Bildschirm geöffnet.")

    def handle_input(self) -> None:
        inp = self.engine.input
        keys = pygame.key.get_pressed()

        if (
            keys[pygame.K_ESCAPE]
            or keys[pygame.K_BACKSPACE]
            or keys[pygame.K_RETURN]
            or keys[pygame.K_SPACE]
            or getattr(inp, "mouse_clicked", False)
        ):
            self.active = False

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 15, 25))

        # Titel
        title = self.title_font.render(
            "🏆 HALL OF FAME (Highscores)", True, (255, 215, 0)
        )
        surface.blit(title, (16, 12))

        # Highscores auflisten
        scores = self.engine.highscores.scores
        y = 45
        if not scores:
            empty_text = self.font.render(
                "Noch keine Highscores vorhanden.", True, (150, 150, 180)
            )
            surface.blit(empty_text, (24, y))
        else:
            for game_name, score in scores.items():
                if y > 200:
                    break  # Platzlimit auf dem 320x240 Bildschirm
                text = self.font.render(f"{game_name}: {score}", True, (200, 220, 255))
                surface.blit(text, (24, y))
                y += 18

        # Zurück-Hinweis
        hint = self.font.render("[Esc / Enter] Zurück zum Menü", True, (120, 120, 160))
        surface.blit(hint, (24, 215))

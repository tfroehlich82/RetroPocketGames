from __future__ import annotations

import pygame

from pocket_games.core.engine import VIRTUAL_HEIGHT, VIRTUAL_WIDTH


class BaseGame:
    """Base class for all Pocket Games with standardized interface, sound, difficulty tracking, and helper methods."""

    def __init__(self, engine, game_name: str) -> None:
        self.engine = engine
        self.game_name = game_name
        self.active: bool = True
        self.game_over: bool = False
        self.paused: bool = False
        self.score: int = 0
        self.elapsed_time: float = 0.0
        self.difficulty_factor: float = 1.0
        self.font = pygame.font.SysFont(None, 18)
        self.title_font = pygame.font.SysFont(None, 22)

    def play_sound(self, sound_type: str) -> None:
        """Helper to trigger sound events safely through the engine audio manager."""
        if hasattr(self.engine, "audio") and self.engine.audio:
            self.engine.audio.play(sound_type)

    def add_score(self, points: int) -> None:
        """Adds points and persists score to highscore manager."""
        self.score += int(points * self.difficulty_factor)
        if hasattr(self.engine, "highscores") and self.engine.highscores:
            self.engine.highscores.submit_score(self.game_name, self.score)

    def get_virtual_mouse_pos(self) -> tuple[int, int]:
        """Transforms physical window mouse coordinates to virtual 320x240 canvas space."""
        if not hasattr(self.engine, "screen") or not self.engine.screen:
            return pygame.mouse.get_pos()
        mw, mh = self.engine.screen.get_size()
        mx, my = pygame.mouse.get_pos()
        vx = int(mx * (VIRTUAL_WIDTH / max(1, mw)))
        vy = int(my * (VIRTUAL_HEIGHT / max(1, mh)))
        return (vx, vy)

    def handle_input(self) -> None:
        """Base input handling for exit, pause, and game over restart."""
        inp = self.engine.input

        if (
            inp.is_key_pressed(pygame.K_ESCAPE)
            or inp.is_key_pressed(pygame.K_BACKSPACE)
            or (hasattr(inp, "is_back_pressed") and inp.is_back_pressed())
        ):
            self.active = False
            return

        # Pause-Toggle via Taste P
        if inp.is_key_pressed(pygame.K_p):
            self.paused = not self.paused

        if self.game_over and (
                inp.is_key_pressed(pygame.K_RETURN) or inp.mouse_clicked or inp.is_key_pressed(pygame.K_SPACE)):
            self.__init__(self.engine, self.game_name)  # Re-initialize game state

    def update(self, dt: float) -> None:
        """Update difficulty scaling and game time if not paused or game over."""
        if not self.game_over and not self.paused:
            self.elapsed_time += dt
            self.difficulty_factor = 1.0 + (self.elapsed_time / 30.0)  # Escalates every 30s

    def render_ui(self, surface: pygame.Surface) -> None:
        """Draw score, pause screen, and overlay game over screens."""
        score_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(score_surf, (10, 8))

        if self.paused:
            overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            surface.blit(overlay, (0, 0))

            pause_txt = self.title_font.render("PAUSED", True, (255, 255, 0))
            surface.blit(pause_txt, (VIRTUAL_WIDTH // 2 - pause_txt.get_width() // 2, VIRTUAL_HEIGHT // 2 - 10))

        if self.game_over:
            overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            go_txt = self.title_font.render("GAME OVER", True, (255, 60, 60))
            surface.blit(go_txt, (VIRTUAL_WIDTH // 2 - go_txt.get_width() // 2, 90))

            sub_txt = self.font.render("Press Enter / Click to Restart", True, (200, 200, 200))
            surface.blit(sub_txt, (VIRTUAL_WIDTH // 2 - sub_txt.get_width() // 2, 125))

            final_txt = self.font.render(f"Final Score: {self.score}", True, (255, 215, 0))
            surface.blit(final_txt, (VIRTUAL_WIDTH // 2 - final_txt.get_width() // 2, 150))

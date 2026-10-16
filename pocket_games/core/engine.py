from __future__ import annotations
import pygame
from pocket_games.core.input import InputManager
from pocket_games.core.settings import Settings
from pocket_games.core.highscore import HighScoreManager

VIRTUAL_WIDTH = 320
VIRTUAL_HEIGHT = 240

class Engine:
    def __init__(self, title: str = "PocketTerm35 Games") -> None:
        pygame.init()
        pygame.font.init()

        self.settings = Settings()
        self.highscores = HighScoreManager()
        self.input = InputManager()

        flags = pygame.FULLSCREEN if self.settings.fullscreen else 0
        self.screen = pygame.display.set_mode((480, 320), flags)
        pygame.display.set_caption(title)

        self.virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

    def render_to_screen(self) -> None:
        scaled = pygame.transform.smoothscale(self.virtual_surface, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def run_scene(self, scene_cls) -> None:
        scene = scene_cls(self)
        while self.running and scene.active:
            dt = self.clock.tick(60) / 1000.0
            self.input.update()
            scene.handle_input()
            scene.update(dt)
            self.virtual_surface.fill((15, 15, 25))
            scene.render(self.virtual_surface)
            self.render_to_screen()

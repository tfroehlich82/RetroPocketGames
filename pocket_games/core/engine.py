from __future__ import annotations

import sys

import pygame

from pocket_games.core.audio import AudioManager
from pocket_games.core.highscore import HighScoreManager
from pocket_games.core.input import InputManager
from pocket_games.core.logger import logger
from pocket_games.core.settings import Settings

VIRTUAL_WIDTH = 320
VIRTUAL_HEIGHT = 240


class Engine:
    def __init__(self, title: str = "RetroPocket Games") -> None:
        logger.info("Initializing Pygame and Engine...")
        pygame.init()
        pygame.font.init()

        self.settings = Settings()
        self.highscores = HighScoreManager()
        self.input = InputManager()
        self.audio = AudioManager(enabled=self.settings.sound_enabled)
        self.audio.set_volume(self.settings.master_volume)

        is_windows = sys.platform == "win32"
        if is_windows:
            window_width = 960
            window_height = 720
            flags = 0
            logger.info(
                "Windows-System detected: Run windowed mode with 960x720px."
            )
        else:
            window_width = 480
            window_height = 320
            flags = pygame.FULLSCREEN if self.settings.fullscreen else 0

        self.screen = pygame.display.set_mode((window_width, window_height), flags)
        pygame.display.set_caption(title)

        self.virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

    def render_to_screen(self) -> None:
        scaled = pygame.transform.smoothscale(
            self.virtual_surface, self.screen.get_size()
        )
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def run_scene(self, scene_cls) -> None:
        scene_name = scene_cls.__name__
        logger.info(f"Selected Game: {scene_name}")
        scene = scene_cls(self)

        try:
            while self.running and scene.active:
                dt = self.clock.tick(60) / 1000.0
                self.input.update()
                scene.handle_input()
                scene.update(dt)
                self.virtual_surface.fill((15, 15, 25))
                scene.render(self.virtual_surface)
                self.render_to_screen()
        except Exception as e:  # noqa: BLE001
            logger.error(f"Unexpected Error in {scene_name}: {e}", exc_info=True)
            raise Exception  # noqa: TRY002

        logger.info(f"Leaving Game: {scene_name}")

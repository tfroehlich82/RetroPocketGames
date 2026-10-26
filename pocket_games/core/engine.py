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
    """Main game engine that manages the application lifecycle and rendering.

    Initializes Pygame, configures the display window based on the detected
    operating system, sets up a virtual-resolution surface for consistent
    rendering across different screen sizes, and provides the main-loop
    infrastructure for running game scenes. On Windows the engine defaults to
    a 640x480 windowed display; on other platforms it supports fullscreen
    mode at 480x320 depending on user preferences.

    :ivar settings: Application configuration including sound, fullscreen,
        and other user preferences.
    :type settings: Settings
    :ivar highscores: Manager responsible for tracking and persisting player
        scores.
    :type highscores: HighScoreManager
    :ivar input: Manager that processes and routes player input events.
    :type input: InputManager
    :ivar audio: Audio subsystem controller for sound playback and volume
        management.
    :type audio: AudioManager
    :ivar screen: The Pygame display surface that the final frame is
        presented to.
    :type screen: pygame.Surface
    :ivar virtual_surface: A fixed-resolution surface that all game scenes
        render into before being scaled to the display.
    :type virtual_surface: pygame.Surface
    :ivar clock: The Pygame clock used to regulate the frame rate.
    :type clock: pygame.time.Clock
    :ivar running: Flag indicating whether the main game loop should
        continue.
    :type running: bool

    def __init__(self, title: str = "RetroPocket Games") -> None:
        """
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
            window_width = 640
            window_height = 480
            flags = 0
            logger.info(
                "Windows-System detected: Run windowed mode with 640x480px."
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
        """
        Render the virtual surface to the display screen.

        Scales the virtual surface to match the current screen
        resolution using smooth scaling, blits the result to the
        top-left corner of the screen, and updates the display
        buffer to present the new frame.

        :return: No return value
        """
        scaled = pygame.transform.smoothscale(
            self.virtual_surface, self.screen.get_size()
        )
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def run_scene(self, scene_cls) -> None:
        """
        Run a game scene in a continuous loop, processing input, updates, and
        rendering each frame until the scene deactivates or the game loop stops.

        :param scene_cls: A class (type) representing the game scene to instantiate
            and execute. The resulting instance is expected to provide
            ``handle_input``, ``update``, and ``render`` methods along with an
            ``active`` attribute. If the instance exposes ``game_name`` and
            ``score`` attributes and the owning object holds a non-empty
            ``highscores`` collection, the score will be submitted upon scene
            completion.
        :return: None
        """
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

        if (
            hasattr(scene, "game_name")
            and hasattr(scene, "score")
            and hasattr(self, "highscores")
            and self.highscores
        ):
            self.highscores.submit_score(scene.game_name, scene.score)

        logger.info(f"Leaving Game: {scene_name}")

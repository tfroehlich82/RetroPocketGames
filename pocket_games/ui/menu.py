from __future__ import annotations

import sys

import pygame

from pocket_games.core.engine import VIRTUAL_WIDTH
from pocket_games.ui.highscore_screen import HighScoreScreen
from pocket_games.ui.settings_screen import SettingsScreen


class MainMenu:
    """

    Summary of what the MainMenu class does.

    The MainMenu class serves as the central controller for the main game selection interface, managing navigation between game titles and system menus like settings and highscores, handling input for scrolling and selection, and launching chosen game classes or exiting the application. It initializes with a provided engine instance and populates a list of games and menu items for display.

    Detailed description of the class, its purpose, and usage.

    This class handles the initial state of the arcade interface, initializing fonts, rendering surfaces, tracking selection state via index and scroll offset, and managing the game entry point lifecycle by delegating scene execution to the engine when a selection is confirmed. It maintains an internal list of item rectangles for rendering and tracks the active state before potential suspension.

    :ivar engine: The core Game Engine instance used for audio playback, input handling, and scene running.
    :type engine: object

    :ivar active: Boolean flag indicating whether the main menu state is currently active and handling input updates.
    :type active: bool

    :ivar games: A static list of tuples pairing game display names with their respective Game class constructors or instances.
    :type games: list[tuple[str, type]]

    :ivar menu_items: A dynamic list combining the available game entries with system menus like settings, highscores, and exit actions.
    :type menu_items: list[tuple[str, Union[type, None]]]

    :ivar selected_index: The integer index of the currently selected menu item for rendering and interaction logic.
    :type selected_index: int

    :ivar scroll_offset: The integer offset applied to the vertical scrolling view to show items above or below the initial viewport.
    :type scroll_offset: int

    :ivar item_rects: A list of pygame Rect objects generated to define the display area boundaries for each visible menu item during rendering.
    :item_rects: list[pygame.Rect]
    """
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True

        from pocket_games.games.aether_defender import AetherDefenderGame
        from pocket_games.games.bit_blaster import BitBlasterGame
        from pocket_games.games.bug_hunter import BugHunterGame
        from pocket_games.games.byte_hopper import ByteHopperGame
        from pocket_games.games.chrono_shift import ChronoShiftGame
        from pocket_games.games.circuit_breaker import CircuitBreakerGame
        from pocket_games.games.crypto_decrypt import CryptoDecryptGame
        from pocket_games.games.cyber_grid_chomp import CyberGridChompGame
        from pocket_games.games.cyber_snake import CyberSnakeGame
        from pocket_games.games.glitch_runner import GlitchRunnerGame
        from pocket_games.games.gravity_sling import GravitySlingGame
        from pocket_games.games.kernel_panic import KernelPanicGame
        from pocket_games.games.matrix_invaders import MatrixInvadersGame
        from pocket_games.games.neon_dash import NeonDashGame
        from pocket_games.games.orbital_defense import OrbitalDefenseGame
        from pocket_games.games.pixel_drop import PixelDropGame
        from pocket_games.games.pixel_platformer import PixelPlatformerGame
        from pocket_games.games.pulse_racer import PulseRacerGame
        from pocket_games.games.quantum_maze import QuantumMazeGame
        from pocket_games.games.retro_pong import RetroPongGame
        from pocket_games.games.sonic_pulse import SonicPulseGame
        from pocket_games.games.sub_zero_miner import SubZeroMinerGame

        self.games = [
            ("Pixel Drop", PixelDropGame),
            ("Circuit Breaker", CircuitBreakerGame),
            ("Neon Dash", NeonDashGame),
            ("Byte Hopper", ByteHopperGame),
            ("Quantum Maze", QuantumMazeGame),
            ("Sub-Zero Miner", SubZeroMinerGame),
            ("Retro Pong 2077", RetroPongGame),
            ("Bug Hunter", BugHunterGame),
            ("Cyber Snake", CyberSnakeGame),
            ("Matrix Invaders", MatrixInvadersGame),
            ("Bit Blaster", BitBlasterGame),
            ("Pulse Racer", PulseRacerGame),
            ("Crypto Decrypt", CryptoDecryptGame),
            ("Kernel Panic", KernelPanicGame),
            ("Orbital Defense", OrbitalDefenseGame),
            ("Chrono Shift", ChronoShiftGame),
            ("Sonic Pulse", SonicPulseGame),
            ("Gravity Sling", GravitySlingGame),
            ("Glitch Runner", GlitchRunnerGame),
            ("Aether Defender", AetherDefenderGame),
            ("Cyber Grid Chomp", CyberGridChompGame),
            ("Pixel Platformer", PixelPlatformerGame),
        ]

        self.menu_items = self.games + [
            ("Settings", SettingsScreen),
            ("Highscores", HighScoreScreen),
            ("Exit", None),
        ]

        self.selected_index = 0
        self.scroll_offset = 0
        self.font = pygame.font.SysFont(None, 18)
        self.title_font = pygame.font.SysFont(None, 24)
        self.item_rects: list[pygame.Rect] = []

    def handle_input(self) -> None:
        """
        Handles keyboard input events for menu navigation and selection actions. Processes directional keys (Up/Down) to adjust the selected item index and scroll offset, wrapping around list boundaries as necessary. Plays audio feedback for interaction navigation. Triggers the launch action when confirmation keys (Enter/Space) are pressed.

        :return: None"""
        visible_count = 8
        inp = self.engine.input

        if inp.is_key_just_pressed(pygame.K_UP) or inp.is_key_just_pressed(pygame.K_w):
            self.engine.audio.play("select")
            self.selected_index -= 1
            if self.selected_index < 0:
                self.selected_index = len(self.menu_items) - 1
                self.scroll_offset = max(0, len(self.menu_items) - visible_count)
            elif self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index

        elif inp.is_key_just_pressed(pygame.K_DOWN) or inp.is_key_just_pressed(
            pygame.K_s
        ):
            self.engine.audio.play("select")
            self.selected_index += 1
            if self.selected_index >= len(self.menu_items):
                self.selected_index = 0
                self.scroll_offset = 0
            elif self.selected_index >= self.scroll_offset + visible_count:
                self.scroll_offset = self.selected_index - visible_count + 1

        elif inp.is_key_just_pressed(pygame.K_RETURN) or inp.is_key_just_pressed(
            pygame.K_SPACE
        ):
            self.engine.audio.play("confirm")
            self.launch_selected()

    def launch_selected(self) -> None:
        """Launches the scene corresponding to the currently selected menu item or exits the application.

        :param self: The instance of the class containing the menu and engine state.
        :return: None.

        """
        name, cls = self.menu_items[self.selected_index]
        if name.lower() == "exit":
            self.engine.running = False
            sys.exit(0)
        if cls:
            self.engine.run_scene(cls)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        """
        Renders the complete game menu interface onto the provided surface by clearing background, drawing a centered title, and iterating through available menu items to draw their graphical representations with selection highlighting.

        :param surface: The pygame Surface object used as the destination for rendering UI elements.
        :return: None after all graphical drawing operations have been completed.
        """
        surface.fill((10, 10, 20))
        title_surf = self.title_font.render("POCKET ARCADE", True, (0, 255, 200))
        surface.blit(title_surf, (VIRTUAL_WIDTH // 2 - title_surf.get_width() // 2, 6))

        self.item_rects = []
        start_y = 30
        item_h = 23
        visible_count = 8

        for i in range(visible_count):
            idx = self.scroll_offset + i
            if idx >= len(self.menu_items):
                break
            name, _ = self.menu_items[idx]
            rect = pygame.Rect(15, start_y + i * item_h, VIRTUAL_WIDTH - 30, 20)
            self.item_rects.append(rect)

            is_sel = (idx == self.selected_index)
            bg_color = (50, 40, 80) if idx >= len(self.games) else ((40, 40, 80) if is_sel else (20, 20, 35))
            text_color = (255, 255, 0) if is_sel else (200, 200, 200)

            pygame.draw.rect(surface, bg_color, rect, border_radius=4)
            pygame.draw.rect(surface, (0, 150, 200) if is_sel else (50, 50, 80), rect, 1, border_radius=4)

            display_text = f"{idx+1}. {name}" if idx < len(self.games) else f"⚙ {name}"
            t_surf = self.font.render(display_text, True, text_color)
            surface.blit(t_surf, (rect.x + 8, rect.y + 3))

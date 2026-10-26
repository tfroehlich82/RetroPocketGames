from __future__ import annotations

import pygame

from pocket_games.core.engine import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from pocket_games.games.base import t


class SettingsScreen:
    """Manage game settings and user interface interactions.

    This class handles the display and logic for the settings menu screen, including
    option selection, value adjustments (toggles/sliders), and application of changes
    to the engine configuration. It manages rendering text based on translations and
    updates visual feedback for selected items.

    :ivar engine: The game engine instance providing audio, input, and storage capabilities.
    :type engine: Engine or similar object containing audio, settings, screen, and input modules.
    :ivar active: Indicates whether the settings screen is currently visible and processing events.
    :type active: bool
    :ivar selected_index: The index of the currently highlighted option in the list.
    :type selected_index: int
    :ivar font: The pygame font object used for rendering main label text.
    :type font: pygame.font.Font
    :ivar title_font: The pygame font object used for rendering the main title.
    :type title_font: pygame.font.Font
    :ivar options: A list of tuples containing translation keys and associated action names.
    :type options: list[tuple[str, str]]
    :ivar item_rects: A list of pygame Rect objects representing the bounding boxes for clickable items.
    :type item_rects: list[pygame.Rect]

    def __init__(self, engine) -> None:
        """
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.selected_index = 0
        self.font = pygame.font.SysFont(None, 18)
        self.title_font = pygame.font.SysFont(None, 24)

        # Options list: (Translation Key, Action)
        self.options = [
            ("sound_effects", "toggle_sound"),
            ("master_volume", "slider_volume"),
            ("fullscreen_mode", "toggle_fullscreen"),
            ("language", "toggle_language"),
            ("back_menu", "back")
        ]
        self.item_rects: list[pygame.Rect] = []

    def handle_input(self) -> None:
        """
        Handles user input events to manage menu navigation and interaction execution within the application environment. This function processes keyboard inputs such as WASD or arrow keys to navigate selection lists, adjust values associated with options, and confirm action execution via ENTER or SPACE. It also handles mouse click events relative to screen size coordinates to interact with visual items defined by bounding rectangles. The method updates the internal selected index based on input state and triggers corresponding audio feedback through the engine's audio system when navigating options. All input processing is mapped to specific actions stored within the options list without exposing internal engine implementation details or private attributes starting with an underscore.

        :param self: An instance of the class containing this method.
        :return: None.
        """
        inp = self.engine.input

        if inp.is_key_just_pressed(pygame.K_UP) or inp.is_key_just_pressed(pygame.K_w):
            self.selected_index = (self.selected_index - 1) % len(self.options)
            self.engine.audio.play("select")
        elif inp.is_key_just_pressed(pygame.K_DOWN) or inp.is_key_just_pressed(pygame.K_s):
            self.selected_index = (self.selected_index + 1) % len(self.options)
            self.engine.audio.play("select")

        _key, action = self.options[self.selected_index]

        if inp.is_key_just_pressed(pygame.K_LEFT) or inp.is_key_just_pressed(pygame.K_a):
            self.adjust_value(action, -1)
        elif inp.is_key_just_pressed(pygame.K_RIGHT) or inp.is_key_just_pressed(pygame.K_d):
            self.adjust_value(action, 1)
        elif inp.is_key_just_pressed(pygame.K_RETURN) or inp.is_key_just_pressed(pygame.K_SPACE):
            self.execute_action(action)

        if inp.mouse_clicked:
            mw, mh = self.engine.screen.get_size()
            vx = int(inp.mouse_pos[0] * (VIRTUAL_WIDTH / mw))
            vy = int(inp.mouse_pos[1] * (VIRTUAL_HEIGHT / mh))
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(vx, vy):
                    self.selected_index = i
                    _, act = self.options[i]
                    if act in ("back", "toggle_sound", "toggle_fullscreen", "toggle_language"):
                        self.execute_action(act)
                    else:
                        self.adjust_value(act, 1)

    def adjust_value(self, action: str, direction: int) -> None:
        """
        Adjusts engine settings by processing a specific action command to toggle features like sound, volume, fullscreen mode, or language preference.

        :param action: Specifies the operation to perform such as toggling sound, adjusting volume slider, changing fullscreen state, or swapping language.
        :param direction: Provides an integer offset applied to the master volume when the slider_volume action is executed.
        :return: None since this method modifies internal engine configuration directly and saves changes persistently.
        """
        settings = self.engine.settings
        match action:
            case "toggle_sound":
                settings.sound_enabled = not settings.sound_enabled
                self.engine.audio.enabled = settings.sound_enabled
                settings.save()
                self.engine.audio.play("confirm")
            case "slider_volume":
                settings.master_volume = max(0.0, min(1.0, settings.master_volume + (direction * 0.1)))
                self.engine.audio.set_volume(settings.master_volume)
                settings.save()
                self.engine.audio.play("select")
            case "toggle_fullscreen":
                settings.fullscreen = not settings.fullscreen
                settings.save()
                flags = pygame.FULLSCREEN if settings.fullscreen else 0
                self.engine.screen = pygame.display.set_mode((480, 320), flags)
                self.engine.audio.play("confirm")
            case "toggle_language":
                settings.language = "English" if settings.language == "Deutsch" else "Deutsch"
                settings.save()
                self.engine.audio.play("confirm")

    def execute_action(self, action: str) -> None:
        """
        Executes a specific action based on the provided command string, handling logic for toggling audio and fullscreen states, volume adjustments, language changes, and returning from active state or triggering engine feedback.

        :param action: The command string determining the specific operation to perform (e.g., 'toggle_sound', 'back').
        :return: None.

        """
        match action:
            case "toggle_sound" | "toggle_fullscreen" | "toggle_language" | "slider_volume":
                self.adjust_value(action, 1)
            case "back":
                self.engine.audio.play("confirm")
                self.active = False

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        """
        Renders the configuration settings interface onto the provided Pygame Surface. The method clears the surface, draws a title element, and iterates through defined options to render labels and values such as sound toggles, volume sliders, fullscreen status, or language selection. It utilizes current engine settings to update text values and calculates positions relative to the surface size.

        :param surface: The target Pygame Surface instance where the UI graphics are rendered.
        :return: None. This method performs side effects only and renders directly to the provided object without returning a value.
        """
        surface.fill((15, 15, 25))
        title_text = t(self.engine, "settings_title")
        title_surf = self.title_font.render(title_text, True, (0, 255, 200))
        surface.blit(title_surf, (VIRTUAL_WIDTH // 2 - title_surf.get_width() // 2, 12))

        self.item_rects = []
        start_y = 50
        item_h = 32
        settings = self.engine.settings

        for i, (key, action) in enumerate(self.options):
            label = t(self.engine, key)
            rect = pygame.Rect(20, start_y + i * item_h, VIRTUAL_WIDTH - 40, 26)
            self.item_rects.append(rect)

            is_sel = (i == self.selected_index)
            bg_color = (40, 40, 80) if is_sel else (25, 25, 40)
            border_color = (0, 200, 255) if is_sel else (60, 60, 90)

            pygame.draw.rect(surface, bg_color, rect, border_radius=6)
            pygame.draw.rect(surface, border_color, rect, 1, border_radius=6)

            val_str = ""
            match action:
                case "toggle_sound":
                    val_str = t(self.engine, "enabled") if settings.sound_enabled else t(self.engine, "disabled")
                case "slider_volume":
                    val_str = f"{int(settings.master_volume * 100)}%"
                case "toggle_fullscreen":
                    val_str = t(self.engine, "on") if settings.fullscreen else t(self.engine, "off")
                case "toggle_language":
                    val_str = settings.language
                case "back":
                    val_str = "-->"

            text_surf = self.font.render(f"{label}: {val_str}", True, (255, 255, 255) if is_sel else (180, 180, 180))
            surface.blit(text_surf, (rect.x + 12, rect.y + 5))

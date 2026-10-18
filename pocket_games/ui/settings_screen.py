from __future__ import annotations

import pygame

from pocket_games.core.engine import VIRTUAL_HEIGHT, VIRTUAL_WIDTH


class SettingsScreen:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.selected_index = 0
        self.font = pygame.font.SysFont(None, 18)
        self.title_font = pygame.font.SysFont(None, 24)

        # Options list: (Label, Type)
        self.options = [
            ("Sound Effect Audio", "toggle_sound"),
            ("Master Volume", "slider_volume"),
            ("Fullscreen Mode", "toggle_fullscreen"),
            ("Back to Main Menu", "back")
        ]
        self.item_rects: list[pygame.Rect] = []

    def handle_input(self) -> None:
        inp = self.engine.input

        # Navigation
        if inp.is_key_just_pressed(pygame.K_UP) or inp.is_key_just_pressed(pygame.K_w):
            self.selected_index = (self.selected_index - 1) % len(self.options)
            self.engine.audio.play("select")
        elif inp.is_key_just_pressed(pygame.K_DOWN) or inp.is_key_just_pressed(pygame.K_s):
            self.selected_index = (self.selected_index + 1) % len(self.options)
            self.engine.audio.play("select")

        # Value adjustments or selection
        _current_label, action = self.options[self.selected_index]

        if inp.is_key_just_pressed(pygame.K_LEFT) or inp.is_key_just_pressed(pygame.K_a):
            self.adjust_value(action, -1)
        elif inp.is_key_just_pressed(pygame.K_RIGHT) or inp.is_key_just_pressed(pygame.K_d):
            self.adjust_value(action, 1)
        elif inp.is_key_just_pressed(pygame.K_RETURN) or inp.is_key_just_pressed(pygame.K_SPACE):
            self.execute_action(action)

        # Touchscreen clicks
        if inp.mouse_clicked:
            mw, mh = self.engine.screen.get_size()
            vx = int(inp.mouse_pos[0] * (VIRTUAL_WIDTH / mw))
            vy = int(inp.mouse_pos[1] * (VIRTUAL_HEIGHT / mh))
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(vx, vy):
                    self.selected_index = i
                    _, act = self.options[i]
                    if act in ("back", "toggle_sound", "toggle_fullscreen"):
                        self.execute_action(act)
                    else:
                        # Toggle / Cycle value on click
                        self.adjust_value(act, 1)

    def adjust_value(self, action: str, direction: int) -> None:
        settings = self.engine.settings
        match action:
            case "toggle_sound":
                settings.sound_enabled = not settings.sound_enabled
                self.engine.audio.enabled = settings.sound_enabled
                settings.save()
                self.engine.audio.play("confirm")
            case "slider_volume":
                settings.master_volume = max(0.0, min(1.0, settings.master_volume + (direction * 0.1)))
                self.engine.audio.volume = settings.master_volume
                settings.save()
                self.engine.audio.play("select")
            case "toggle_fullscreen":
                settings.fullscreen = not settings.fullscreen
                settings.save()
                flags = pygame.FULLSCREEN if settings.fullscreen else 0
                self.engine.screen = pygame.display.set_mode((480, 320), flags)
                self.engine.audio.play("confirm")

    def execute_action(self, action: str) -> None:
        match action:
            case "toggle_sound" | "toggle_fullscreen" | "slider_volume":
                self.adjust_value(action, 1)
            case "back":
                self.engine.audio.play("confirm")
                self.active = False

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 15, 25))
        title_surf = self.title_font.render("SYSTEM SETTINGS", True, (0, 255, 200))
        surface.blit(title_surf, (VIRTUAL_WIDTH // 2 - title_surf.get_width() // 2, 15))

        self.item_rects = []
        start_y = 65
        item_h = 35
        settings = self.engine.settings

        for i, (label, action) in enumerate(self.options):
            rect = pygame.Rect(20, start_y + i * item_h, VIRTUAL_WIDTH - 40, 28)
            self.item_rects.append(rect)

            is_sel = (i == self.selected_index)
            bg_color = (40, 40, 80) if is_sel else (25, 25, 40)
            border_color = (0, 200, 255) if is_sel else (60, 60, 90)

            pygame.draw.rect(surface, bg_color, rect, border_radius=6)
            pygame.draw.rect(surface, border_color, rect, 1, border_radius=6)

            # Format value display string
            val_str = ""
            match action:
                case "toggle_sound":
                    val_str = "ENABLED" if settings.sound_enabled else "DISABLED"
                case "slider_volume":
                    val_str = f"{int(settings.master_volume * 100)}%"
                case "toggle_fullscreen":
                    val_str = "ON" if settings.fullscreen else "OFF"
                case "back":
                    val_str = "-->"

            text_surf = self.font.render(f"{label}: {val_str}", True, (255, 255, 255) if is_sel else (180, 180, 180))
            surface.blit(text_surf, (rect.x + 12, rect.y + 7))

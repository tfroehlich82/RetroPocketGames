from __future__ import annotations

import pygame


class InputManager:
    def __init__(self) -> None:
        self.events: list[pygame.event.Event] = []
        self.keys_just_pressed: set[int] = set()
        self.mouse_pos: tuple[int, int] = (0, 0)
        self.mouse_clicked: bool = False

    def update(self) -> None:
        self.mouse_clicked = False
        self.events = pygame.event.get()
        self.keys_just_pressed.clear()

        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_clicked = True
                self.mouse_pos = event.pos
            elif event.type == pygame.KEYDOWN:
                self.keys_just_pressed.add(event.key)

    def is_key_just_pressed(self, key: int) -> bool:
        """Löst NUR EINMAL im Frame aus, in dem die Taste gedrückt wurde (für Menüs)."""
        return key in self.keys_just_pressed

    def is_key_down(self, key: int) -> bool:
        """Liefert True, SOLANGE die Taste gehalten wird (für flüssige Bewegung in Spielen)."""
        pressed = pygame.key.get_pressed()
        return bool(pressed[key])

    def is_back_pressed(self) -> bool:
        """Prüft, ob Escape oder Backspace in diesem Frame neu gedrückt wurde."""
        return (
            self.is_key_just_pressed(pygame.K_ESCAPE)
            or self.is_key_just_pressed(pygame.K_BACKSPACE)
        )

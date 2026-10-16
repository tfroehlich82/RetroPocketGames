from __future__ import annotations

import pygame


class InputManager:
    def __init__(self) -> None:
        self.events: list[pygame.event.Event] = []
        self.keys_pressed: set[int] = set()
        self.mouse_pos: tuple[int, int] = (0, 0)
        self.mouse_clicked: bool = False

    def update(self) -> None:
        self.mouse_clicked = False
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_clicked = True
                self.mouse_pos = event.pos

        self.keys_pressed = {
            event.key for event in self.events if event.type == pygame.KEYDOWN
        }

    def is_key_down(self, key: int) -> bool:
        return key in self.keys_pressed

    def is_key_pressed(self, key: int) -> bool:
        pressed = pygame.key.get_pressed()
        return bool(pressed[key])

    def is_back_pressed(self) -> bool:
        keys = pygame.key.get_pressed()
        return bool(keys[pygame.K_ESCAPE] or keys[pygame.K_BACKSPACE])

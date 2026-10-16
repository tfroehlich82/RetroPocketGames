from __future__ import annotations

import pygame


class InputManager:
    def __init__(self) -> None:
        self.keys_pressed: dict[int, bool] = {}
        self.keys_down: dict[int, bool] = {}
        self.mouse_pos: tuple[int, int] = (0, 0)
        self.mouse_clicked: bool = False
        self.mouse_released: bool = False
        self.touch_active: bool = False

    def update(self) -> None:
        self.keys_pressed.clear()
        self.mouse_clicked = False
        self.mouse_released = False

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    raise SystemExit
                case pygame.KEYDOWN:
                    self.keys_down[event.key] = True
                    self.keys_pressed[event.key] = True
                case pygame.KEYUP:
                    self.keys_down[event.key] = False
                case pygame.MOUSEBUTTONDOWN:
                    self.mouse_pos = event.pos
                    self.mouse_clicked = True
                    self.touch_active = True
                case pygame.MOUSEBUTTONUP:
                    self.mouse_pos = event.pos
                    self.mouse_released = True
                case pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos

    def is_key_down(self, key: int) -> bool:
        return self.keys_down.get(key, False)

    def is_key_pressed(self, key: int) -> bool:
        return self.keys_pressed.get(key, False)

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
            elif event.type == pygame.FINGERDOWN:
                self.mouse_clicked = True
                surf = pygame.display.get_surface()
                if surf:
                    sw, sh = surf.get_size()
                    self.mouse_pos = (int(event.x * sw), int(event.y * sh))
                else:
                    self.mouse_pos = (0, 0)
            elif event.type == pygame.KEYDOWN:
                self.keys_just_pressed.add(event.key)

    def is_key_just_pressed(self, key: int) -> bool:
        return key in self.keys_just_pressed

    def is_key_down(self, key: int) -> bool:
        pressed = pygame.key.get_pressed()
        return bool(pressed[key])

    def is_back_pressed(self) -> bool:
        return (
            self.is_key_just_pressed(pygame.K_ESCAPE)
            or self.is_key_just_pressed(pygame.K_BACKSPACE)
        )

    def is_left_pressed(self) -> bool:
        return self.is_key_down(pygame.K_LEFT) or self.is_key_down(pygame.K_a)

    def is_right_pressed(self) -> bool:
        return self.is_key_down(pygame.K_RIGHT) or self.is_key_down(pygame.K_d)

    def is_up_pressed(self) -> bool:
        return self.is_key_down(pygame.K_UP) or self.is_key_down(pygame.K_w)

    def is_down_pressed(self) -> bool:
        return self.is_key_down(pygame.K_DOWN) or self.is_key_down(pygame.K_s)

    def is_action_pressed(self) -> bool:
        return (
            self.is_key_down(pygame.K_SPACE)
            or self.is_key_down(pygame.K_RETURN)
            or self.is_key_down(pygame.K_z)
            or self.mouse_clicked
        )

    def is_action_just_pressed(self) -> bool:
        return (
            self.is_key_just_pressed(pygame.K_SPACE)
            or self.is_key_just_pressed(pygame.K_RETURN)
            or self.is_key_just_pressed(pygame.K_z)
            or self.is_key_just_pressed(pygame.K_UP)
            or self.is_key_just_pressed(pygame.K_w)
            or self.mouse_clicked
        )

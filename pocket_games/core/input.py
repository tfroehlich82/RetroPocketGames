from __future__ import annotations

import pygame

# Action               Keyboard                    Touchscreen
# ---------------------------------------------------------------------------
# Menu Navigation      D-Pad Up/Down               Tap or swipe list items
# Confirm/Action       Button A/Enter/Space        Single tap
# Back                 Button B/Esc/Backspace      tap button on screen
# Global Exit          Start (Hold >3s)/Esc        tap button on screen


class InputManager:
    def __init__(self) -> None:
        self.events: list[pygame.event.Event] = []
        self.keys_just_pressed: set[int] = set()
        self.joystick_buttons_pressed: set[int] = set()
        self.joystick_buttons_just_pressed: set[int] = set()
        self.mouse_pos: tuple[int, int] = (0, 0)
        self.mouse_clicked: bool = False
        self._start_press_start_time: int | None = None

        # Joysticks / Gamepads für Handhelds wie PocketTerm35 initialisieren
        try:
            if not pygame.joystick.get_init():
                pygame.joystick.init()
            self.joysticks = [
                pygame.joystick.Joystick(i)
                for i in range(pygame.joystick.get_count())
            ]
            for js in self.joysticks:
                js.init()
        except Exception:  # noqa: BLE001
            self.joysticks = []

    def update(self) -> None:
        self.mouse_clicked = False
        self.events = pygame.event.get()
        self.keys_just_pressed.clear()
        self.joystick_buttons_just_pressed.clear()

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
            elif event.type == pygame.JOYBUTTONDOWN:
                self.joystick_buttons_pressed.add(event.button)
                self.joystick_buttons_just_pressed.add(event.button)
            elif event.type == pygame.JOYBUTTONUP:
                self.joystick_buttons_pressed.discard(event.button)

    def is_key_just_pressed(self, key: int) -> bool:
        return key in self.keys_just_pressed

    def is_key_down(self, key: int) -> bool:
        pressed = pygame.key.get_pressed()
        return bool(pressed[key])

    def is_joy_button_down(self, button: int) -> bool:
        return button in self.joystick_buttons_pressed

    def is_joy_button_just_pressed(self, button: int) -> bool:
        return button in self.joystick_buttons_just_pressed

    def is_back_pressed(self) -> bool:
        # Button B / X / Esc / Backspace
        return (
            self.is_key_just_pressed(pygame.K_ESCAPE)
            or self.is_key_just_pressed(pygame.K_BACKSPACE)
            or self.is_key_just_pressed(pygame.K_x)
            or self.is_joy_button_just_pressed(1)
            or self.is_joy_button_just_pressed(3)
        )

    def is_global_exit_pressed(self) -> bool:
        # Global Exit: Start (Hold >3s) / Esc
        if self.is_key_just_pressed(pygame.K_ESCAPE):
            return True

        start_held = (
            self.is_key_down(pygame.K_RETURN)
            or self.is_key_down(pygame.K_KP_ENTER)
            or self.is_key_down(pygame.K_TAB)
            or self.is_joy_button_down(7)
            or self.is_joy_button_down(8)
            or self.is_joy_button_down(9)
        )

        if start_held:
            current_time = pygame.time.get_ticks()
            if self._start_press_start_time is None:
                self._start_press_start_time = current_time
            else:
                elapsed = (current_time - self._start_press_start_time) / 1000.0
                if elapsed >= 3.0:
                    self._start_press_start_time = None
                    return True
        else:
            self._start_press_start_time = None
        return False

    def is_left_pressed(self) -> bool:
        return self.is_key_down(pygame.K_LEFT) or self.is_key_down(pygame.K_a)

    def is_right_pressed(self) -> bool:
        return self.is_key_down(pygame.K_RIGHT) or self.is_key_down(pygame.K_d)

    def is_up_pressed(self) -> bool:
        return self.is_key_down(pygame.K_UP) or self.is_key_down(pygame.K_w)

    def is_down_pressed(self) -> bool:
        return self.is_key_down(pygame.K_DOWN) or self.is_key_down(pygame.K_s)

    def is_action_pressed(self) -> bool:
        # Button A / Enter / Space
        return (
            self.is_key_down(pygame.K_SPACE)
            or self.is_key_down(pygame.K_RETURN)
            or self.is_key_down(pygame.K_KP_ENTER)
            or self.is_key_down(pygame.K_z)
            or self.is_key_down(pygame.K_LALT)
            or self.is_joy_button_down(0)
            or self.mouse_clicked
        )

    def is_action_just_pressed(self) -> bool:
        return (
            self.is_key_just_pressed(pygame.K_SPACE)
            or self.is_key_just_pressed(pygame.K_RETURN)
            or self.is_key_just_pressed(pygame.K_KP_ENTER)
            or self.is_key_just_pressed(pygame.K_z)
            or self.is_key_just_pressed(pygame.K_LALT)
            or self.is_key_just_pressed(pygame.K_UP)
            or self.is_key_just_pressed(pygame.K_w)
            or self.is_joy_button_just_pressed(0)
            or self.mouse_clicked
        )

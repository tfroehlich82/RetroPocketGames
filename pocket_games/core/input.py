from __future__ import annotations

import pygame


class InputManager:
    """
    Summary of what the class does.
    The InputManager class handles centralized input processing for game loops, managing events from keyboard, mouse, and joystick devices using pygame. It encapsulates state tracking for pressed keys, held buttons, and mouse position to provide convenient methods for checking specific input conditions like actions or navigation directions.

    Detailed description of the class, its purpose, and usage.
    This class is designed to abstract raw pygame event polling into manageable boolean checks. It initializes internal buffers for events, key states, and joystick mappings within its constructor. The update method processes the current frame's events to refresh input flags such as newly pressed keys or joystick buttons. Methods like is_key_just_pressed allow checking for new input states in a single frame cycle without processing stale data. Global exit and action states are handled by combining multiple potential inputs (e.g., Escape key, Enter key, or mouse click) into unified boolean responses suitable for game state transitions. The internal timer logic used for hold-to-exit functionality remains hidden from the public interface to prevent external dependencies on private timing mechanisms.

    """
    def __init__(self) -> None:
        self.events: list[pygame.event.Event] = []
        self.keys_pressed: set[int] = set()
        self.keys_just_pressed: set[int] = set()
        self.joystick_buttons_pressed: set[int] = set()
        self.joystick_buttons_just_pressed: set[int] = set()
        self.mouse_pos: tuple[int, int] = (0, 0)
        self.mouse_clicked: bool = False
        self._start_press_start_time: int | None = None

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
        """
        Updates the game loop event processing state based on input device events. Processes pygame event queue to handle mouse clicks, finger touches, key presses, and joystick button states, clearing previous temporary input sets and updating internal flags accordingly.

        Parameters
        ----------
        self : instance
            The instance of the class containing the game loop state and event buffers.

        Returns
        -------
        None
        """
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
                self.keys_pressed.add(event.key)
                self.keys_just_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            elif event.type == pygame.JOYBUTTONDOWN:
                self.joystick_buttons_pressed.add(event.button)
                self.joystick_buttons_just_pressed.add(event.button)
            elif event.type == pygame.JOYBUTTONUP:
                self.joystick_buttons_pressed.discard(event.button)

    def is_key_just_pressed(self, key: int) -> bool:
        return key in self.keys_just_pressed

    def is_key_down(self, key: int) -> bool:
        if key in self.keys_pressed:
            return True
        try:
            pressed = pygame.key.get_pressed()
            if pressed and pressed[key]:
                return True
        except Exception:  # noqa: S110 BLE001
            pass
        return False

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
            or self.is_key_just_pressed(pygame.K_b)
        )

    def is_global_exit_pressed(self) -> bool:
        # Global Exit: Start (Hold >3s) / Esc
        if self.is_key_just_pressed(pygame.K_ESCAPE):
            return True

        start_held = self.is_key_down(pygame.K_BREAK)
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
            or self.is_key_just_pressed(pygame.K_RETURN)
            or self.is_key_down(pygame.K_RETURN)
            or self.is_key_down(pygame.K_KP_ENTER)
            or self.is_key_down(pygame.K_a)
            or self.mouse_clicked
        )

    def is_action_just_pressed(self) -> bool:
        return (
            self.is_key_just_pressed(pygame.K_SPACE)
            or self.is_key_just_pressed(pygame.K_RETURN)
            or self.is_key_just_pressed(pygame.K_KP_ENTER)
            or self.is_key_just_pressed(pygame.K_a)
            or self.mouse_clicked
        )

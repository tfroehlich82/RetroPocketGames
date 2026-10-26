# core/input.py

## InputManager

`class InputManager`

Summary of what the class does.
The InputManager class handles centralized input processing for game loops, managing events from keyboard, mouse, and joystick devices using pygame. It encapsulates state tracking for pressed keys, held buttons, and mouse position to provide convenient methods for checking specific input conditions like actions or navigation directions.

Detailed description of the class, its purpose, and usage.
This class is designed to abstract raw pygame event polling into manageable boolean checks. It initializes internal buffers for events, key states, and joystick mappings within its constructor. The update method processes the current frame's events to refresh input flags such as newly pressed keys or joystick buttons. Methods like is_key_just_pressed allow checking for new input states in a single frame cycle without processing stale data. Global exit and action states are handled by combining multiple potential inputs (e.g., Escape key, Enter key, or mouse click) into unified boolean responses suitable for game state transitions. The internal timer logic used for hold-to-exit functionality remains hidden from the public interface to prevent external dependencies on private timing mechanisms.

### __init__

`def __init__(self) -> None`

### update

`def update(self) -> None`

Updates the game loop event processing state based on input device events. Processes pygame event queue to handle mouse clicks, finger touches, key presses, and joystick button states, clearing previous temporary input sets and updating internal flags accordingly.

Parameters
----------
self : instance
    The instance of the class containing the game loop state and event buffers.

Returns
-------
None

### is_key_just_pressed

`def is_key_just_pressed(self, key: int) -> bool`

### is_key_down

`def is_key_down(self, key: int) -> bool`

### is_joy_button_down

`def is_joy_button_down(self, button: int) -> bool`

### is_joy_button_just_pressed

`def is_joy_button_just_pressed(self, button: int) -> bool`

### is_back_pressed

`def is_back_pressed(self) -> bool`

### is_global_exit_pressed

`def is_global_exit_pressed(self) -> bool`

### is_left_pressed

`def is_left_pressed(self) -> bool`

### is_right_pressed

`def is_right_pressed(self) -> bool`

### is_up_pressed

`def is_up_pressed(self) -> bool`

### is_down_pressed

`def is_down_pressed(self) -> bool`

### is_action_pressed

`def is_action_pressed(self) -> bool`

### is_action_just_pressed

`def is_action_just_pressed(self) -> bool`

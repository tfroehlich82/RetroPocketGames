# ui/settings_screen.py

## SettingsScreen

`class SettingsScreen`

Manage game settings and user interface interactions.

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
    

### __init__

`def __init__(self, engine) -> None`

### handle_input

`def handle_input(self) -> None`

Handles user input events to manage menu navigation and interaction execution within the application environment. This function processes keyboard inputs such as WASD or arrow keys to navigate selection lists, adjust values associated with options, and confirm action execution via ENTER or SPACE. It also handles mouse click events relative to screen size coordinates to interact with visual items defined by bounding rectangles. The method updates the internal selected index based on input state and triggers corresponding audio feedback through the engine's audio system when navigating options. All input processing is mapped to specific actions stored within the options list without exposing internal engine implementation details or private attributes starting with an underscore.

:param self: An instance of the class containing this method.
:return: None.

### adjust_value

`def adjust_value(self, action: str, direction: int) -> None`

Adjusts engine settings by processing a specific action command to toggle features like sound, volume, fullscreen mode, or language preference.

:param action: Specifies the operation to perform such as toggling sound, adjusting volume slider, changing fullscreen state, or swapping language.
:param direction: Provides an integer offset applied to the master volume when the slider_volume action is executed.
:return: None since this method modifies internal engine configuration directly and saves changes persistently.

### execute_action

`def execute_action(self, action: str) -> None`

Executes a specific action based on the provided command string, handling logic for toggling audio and fullscreen states, volume adjustments, language changes, and returning from active state or triggering engine feedback.

:param action: The command string determining the specific operation to perform (e.g., 'toggle_sound', 'back').
:return: None.

### update

`def update(self, dt: float) -> None`

### render

`def render(self, surface: pygame.Surface) -> None`

Renders the configuration settings interface onto the provided Pygame Surface. The method clears the surface, draws a title element, and iterates through defined options to render labels and values such as sound toggles, volume sliders, fullscreen status, or language selection. It utilizes current engine settings to update text values and calculates positions relative to the surface size.

:param surface: The target Pygame Surface instance where the UI graphics are rendered.
:return: None. This method performs side effects only and renders directly to the provided object without returning a value.

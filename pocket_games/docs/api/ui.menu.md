# ui/menu.py

## MainMenu

`class MainMenu`

Summary of what the MainMenu class does.

The MainMenu class serves as the central controller for the main game selection interface, managing navigation between game titles and system menus like settings and highscores, handling input for scrolling and selection, and launching chosen game classes or exiting the application. It initializes with a provided engine instance and populates a list of games and menu items for display.

Detailed description of the class, its purpose, and usage.

This class handles the initial state of the arcade interface, initializing fonts, rendering surfaces, tracking selection state via index and scroll offset, and managing the game entry point lifecycle by delegating scene execution to the engine when a selection is confirmed. It maintains an internal list of item rectangles for rendering and tracks the active state before potential suspension.

:ivar engine: The core Game Engine instance used for audio playback, input handling, and scene running.
:type engine: object

:ivar active: Boolean flag indicating whether the main menu state is currently active and handling input updates.
:type active: bool

:ivar games: A static list of tuples pairing game display names with their respective Game class constructors or instances.
:type games: list[tuple[str, type]]

:ivar menu_items: A dynamic list combining the available game entries with system menus like settings, highscores, and exit actions.
:type menu_items: list[tuple[str, Union[type, None]]]

:ivar selected_index: The integer index of the currently selected menu item for rendering and interaction logic.
:type selected_index: int

:ivar scroll_offset: The integer offset applied to the vertical scrolling view to show items above or below the initial viewport.
:type scroll_offset: int

:ivar item_rects: A list of pygame Rect objects generated to define the display area boundaries for each visible menu item during rendering.
:item_rects: list[pygame.Rect]

### __init__

`def __init__(self, engine) -> None`

### handle_input

`def handle_input(self) -> None`

Handles keyboard input events for menu navigation and selection actions. Processes directional keys (Up/Down) to adjust the selected item index and scroll offset, wrapping around list boundaries as necessary. Plays audio feedback for interaction navigation. Triggers the launch action when confirmation keys (Enter/Space) are pressed.

:return: None

### launch_selected

`def launch_selected(self) -> None`

Launches the scene corresponding to the currently selected menu item or exits the application.

:param self: The instance of the class containing the menu and engine state.
:return: None.

### update

`def update(self, dt: float) -> None`

### render

`def render(self, surface: pygame.Surface) -> None`

Renders the complete game menu interface onto the provided surface by clearing background, drawing a centered title, and iterating through available menu items to draw their graphical representations with selection highlighting.

:param surface: The pygame Surface object used as the destination for rendering UI elements.
:return: None after all graphical drawing operations have been completed.

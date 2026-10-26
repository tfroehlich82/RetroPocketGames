# games/base.py

## t

`def t(engine, key: str) -> str`

Translates a specific key based on the language preference found in engine settings or defaults to English. Returns the localized value if available, otherwise returns the original key.

:param engine: The object that may contain settings determining the translation language.
:param key: The string identifier to look up in the translations dictionary.
:return: The translated string for the key or the original key string itself.

## BaseGame

`class BaseGame`

BaseGame provides fundamental functionality and state management for game applications within a generic engine framework. It initializes the core attributes required for rendering, input handling, and lifecycle tracking including intro screens, pause states, win/loss conditions, and basic UI elements. Subclasses should override specific update, render, or handle_input methods to define unique gameplay logic while inheriting standardized checks for game state transitions to prevent processing during inactive phases like the intro or ending.

.. py:attribute:: CONTROLS
   :type: dict[str, list[typing.Any]]
   A dictionary mapping action strings (e.g., 'left', 'action') to lists of pygame key constants.

.. py:attribute:: engine
   :type: Any
   The parent game engine instance providing access to audio, screen, and input systems.

.. py:attribute:: game_name
   :type: str
   Unique identifier string assigned during initialization for highscore and logging purposes.

.. py:attribute:: active
   :type: bool
   Flag indicating whether the main game loop is currently running or stopped.

.. py:attribute:: paused
   :type: bool
   Flag indicating whether the update logic is suspended.

.. py:attribute:: game_over
   :type: bool
   Boolean state set when the player loses or the game session ends via failure condition.

.. py:attribute:: game_won
   :type: bool
   Boolean state set when the primary objective of the game has been successfully completed.

.. py:attribute:: score
   :type: int
   The current accumulated points tracked throughout the gameplay session.

.. py:attribute:: elapsed_time
   :type: float
   Total duration in seconds that the game has been running actively since start.

.. py:attribute:: showing_intro
   :type: bool
   Boolean flag used to determine if the rendering logic should display the introduction screen instead of gameplay content.

.. py:attribute:: description
   :type: str
   Detailed textual explanation describing the specific game rules or narrative provided in metadata.

.. py:attribute:: goal
   :type: str
   String defining the primary objective the player needs to achieve to win the game.

.. py:attribute:: gameplay
   :type: str
   Instructions describing the mechanics and style of play expected from the user.

.. py:attribute:: controls
   :type: str
   Brief hint text indicating the default input scheme used for interacting with the game.

### __init__

`def __init__(self, engine, game_name: str) -> None`

### is_control_pressed

`def is_control_pressed(self, action: str) -> bool`

Verifies whether a specific control action is currently active within the engine input system.

:param action: The name of the action string representing a user input control to be checked.
:return: A boolean value indicating if the associated input state corresponds to the specified action being pressed or clicked.
:rtype: bool

### is_control_just_pressed

`def is_control_just_pressed(self, action: str) -> bool`

This method evaluates whether the provided control action has been triggered by the engine input state.

:param action: The name of the control action to verify for key or mouse press events.
:return: True if the action corresponds to a just-pressed input, False otherwise.

### difficulty_factor

`def difficulty_factor(self) -> float`

This property calculates and returns the current difficulty factor based on the elapsed time of the instance. The calculation starts at a base value of 1.0 and increases linearly with respect to time passed.

:return: The computed difficulty multiplier derived from the elapsed time attribute without type restrictions.

### get_virtual_mouse_pos

`def get_virtual_mouse_pos(self) -> tuple[int, int]`

Returns the scaled virtual mouse position mapped to a fixed resolution of 320 by 240 pixels. The calculation utilizes the input engine mouse position if available, otherwise falling back to pygame defaults, and scales coordinates relative to the current screen dimensions or default surface size.

:param self: The instance of the class containing the active engine context and screen reference.
:return: A tuple of two integers representing the normalized x and y coordinates within the scaled viewport.

### add_score

`def add_score(self, amount: int) -> None`

Updates the internal score attribute by adding the provided value to it.

:param amount: The quantity to increase the score by.
:return: None once the score has been updated.

### play_sound

`def play_sound(self, sound_name: str) -> None`

Play a sound using the engine's audio system if available.

:param sound_name: The name of the audio clip to play.
:type sound_name: str
:return: None
:rtype: NoneType

### render_ui

`def render_ui(self, surface: pygame.Surface) -> None`

Renders the user interface score text onto the provided display surface using the configured font and color settings. The method creates a score string representation based on the current instance score attribute and blits it at the top-left position (10, 5) of the surface.

:param surface: A pygame.Surface object where the score text is to be rendered.
:return: None

### handle_input

`def handle_input(self) -> None`

Handles user input processing for the game engine logic and state management. This method
evaluates active input sources to detect quit commands via escape or back keys, which
immediately deactivates the engine. It also monitors the introductory sequence phase
where pressing action or up keys transitions out of intro mode and triggers sound effects.
For game over or win scenarios, it waits for a specific timer duration before responding
to exit or action inputs to deactivate the application accordingly. Updates internal
flags and mouse input states based on control events.

:return: None

### update

`def update(self, dt: float) -> None`

Updates game state based on the time delta, handles game end conditions and score submission, checks for intro visibility, and advances elapsed time if not paused.

:param dt: Delta time step in seconds for the current frame.
:return: None (void).

### render

`def render(self, surface: pygame.Surface) -> None`

Renders the appropriate visual representation of the current game state onto the specified drawing surface based on internal application flags. This method determines whether to render an introduction sequence or a game over screen depending on the active status variables, executing the corresponding rendering logic without modifying private attributes or exposing internal state details in its documentation.

:param surface: The target PyGame Surface object intended to receive the rendered graphical content for the current frame.
:return: None after completing the drawing operations and returning control to the caller.

### render_intro

`def render_intro(self, surface: pygame.Surface) -> None`

Renders the introductory screen interface onto the provided surface, applying background colors and positioning game metadata including title, description, goals, gameplay mechanics, control instructions, and a toggle start prompt.

:param surface: The pygame.Surface object used as the canvas for all UI rendering operations.
:return: None after successfully drawing all elements to the specified surface.

### render_game_over

`def render_game_over(self, surface: pygame.Surface) -> None`

Render the game over interface overlay onto the specified surface, displaying current score, elapsed time, level, best run statistics, and top 3 historical runs.

:param surface: The destination surface to blit the game over UI content onto.
:return: None

### render_game_finished

`def render_game_finished(self, surface: pygame.Surface) -> None`

Renders the game finished overlay on the provided surface, displaying final scores and countdown or exit hints based on internal timers.

:param surface: The pygame.Surface instance to draw the finished state onto.
:return: None

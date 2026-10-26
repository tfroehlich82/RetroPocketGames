# ui/highscore_screen.py

## HighScoreScreen

`class HighScoreScreen`

High Score Screen Management and Rendering Class.

This class encapsulates the logic for displaying the high score hall of fame.
It manages user interaction for scrolling through the list of available games
including keyboard navigation, mouse wheel input, and click detection for
deactivation. The rendering logic handles drawing titles, scoreboard tables
with alternating row backgrounds, scrollbars, and localized navigation hints
on the target pygame surface.

:ivar engine: The active game engine instance providing audio, screen, and input access.
:ivar active: Flag indicating if the high score menu is currently displayed to the user.
:ivar font: Font object used for rendering standard text on the scoreboard.
:ivar title_font: Font object used for rendering the hall of fame title.
:ivar scroll_offset: Integer representing the current vertical scroll index of the game list.
:ivar max_visible: Maximum number of high score entries visible at one time without scrolling.

### __init__

`def __init__(self, engine) -> None`

### handle_input

`def handle_input(self) -> None`

Handle user input for the game selection menu, processing key presses
for deactivation, keyboard and mouse wheel scrolling through the list
of available games, and mouse click detection in the bottom region to
close the menu.

The method first checks for deactivation keys (ESCAPE, BACKSPACE,
RETURN, SPACE) and disables the menu if any are detected. If the menu
remains active, it processes scrolling via UP/DOWN arrow keys, W/S
keys, or mouse wheel events, clamping the scroll offset within the
valid range determined by the total number of games and the maximum
visible count. An audio select cue is played for each
keyboard-based scroll step. A mouse click detected in the lower
portion of the screen (below the y=210 line in a 240 pixel tall
coordinate space) also deactivates the menu.

:return: None

### update

`def update(self, dt: float) -> None`

### render

`def render(self, surface: pygame.Surface) -> None`

Render the hall of fame screen displaying high scores for all registered
games on the provided surface.

The screen features a localized title, a two-column scoreboard table
listing each game name alongside its all-time high score, alternating
row backgrounds for improved readability, a vertical scrollbar indicator
when the entry list exceeds the visible window, and a localized
navigation hint at the bottom of the layout.

Game names exceeding 22 characters are truncated with an ellipsis
suffix. Score values are retrieved from the engine's highscore manager,
with fallback support for multiple interface conventions (dedicated
getter method, scores attribute, or plain dictionary mapping).

:param surface: Target surface on which the hall of fame is drawn
:return: None

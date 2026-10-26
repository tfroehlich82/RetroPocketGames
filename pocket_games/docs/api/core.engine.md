# core/engine.py

## Engine

`class Engine`

Main game engine that manages the application lifecycle and rendering.

Initializes Pygame, configures the display window based on the detected
operating system, sets up a virtual-resolution surface for consistent
rendering across different screen sizes, and provides the main-loop
infrastructure for running game scenes. On Windows the engine defaults to
a 640x480 windowed display; on other platforms it supports fullscreen
mode at 480x320 depending on user preferences.

:ivar settings: Application configuration including sound, fullscreen,
    and other user preferences.
:type settings: Settings
:ivar highscores: Manager responsible for tracking and persisting player
    scores.
:type highscores: HighScoreManager
:ivar input: Manager that processes and routes player input events.
:type input: InputManager
:ivar audio: Audio subsystem controller for sound playback and volume
    management.
:type audio: AudioManager
:ivar screen: The Pygame display surface that the final frame is
    presented to.
:type screen: pygame.Surface
:ivar virtual_surface: A fixed-resolution surface that all game scenes
    render into before being scaled to the display.
:type virtual_surface: pygame.Surface
:ivar clock: The Pygame clock used to regulate the frame rate.
:type clock: pygame.time.Clock
:ivar running: Flag indicating whether the main game loop should
    continue.
:type running: bool

def __init__(self, title: str = "RetroPocket Games") -> None:
    

### __init__

`def __init__(self, title: str='RetroPocket Games') -> None`

### render_to_screen

`def render_to_screen(self) -> None`

Render the virtual surface to the display screen.

Scales the virtual surface to match the current screen
resolution using smooth scaling, blits the result to the
top-left corner of the screen, and updates the display
buffer to present the new frame.

:return: No return value

### run_scene

`def run_scene(self, scene_cls) -> None`

Run a game scene in a continuous loop, processing input, updates, and
rendering each frame until the scene deactivates or the game loop stops.

:param scene_cls: A class (type) representing the game scene to instantiate
    and execute. The resulting instance is expected to provide
    ``handle_input``, ``update``, and ``render`` methods along with an
    ``active`` attribute. If the instance exposes ``game_name`` and
    ``score`` attributes and the owning object holds a non-empty
    ``highscores`` collection, the score will be submitted upon scene
    completion.
:return: None

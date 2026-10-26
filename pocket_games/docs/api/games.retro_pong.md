# games/retro_pong.py

## Paddle

`class Paddle`

### __init__

`def __init__(self, x: int, y: int, width: int, height: int) -> None`

## Ball

`class Ball`

### __init__

`def __init__(self, x: float, y: float, radius: int, vx: float, vy: float) -> None`

### update_rect

`def update_rect(self) -> None`

## RetroPongGame

`class RetroPongGame(BaseGame)`

### __init__

`def __init__(self, engine) -> None`

### handle_input

`def handle_input(self) -> None`

### update

`def update(self, dt: float) -> None`

### render

`def render(self, surface: pygame.Surface) -> None`

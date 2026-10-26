# core/physics.py

## handle_paddle_collision

`def handle_paddle_collision(ball, paddle, paddle_vy: float=0.0) -> None`

This function handles collision between the ball and the paddle in a paddle-ball game. When a collision is detected, it calculates appropriate bounce physics based on impact position, adjusts velocity with rubber elasticity effects, clips speed to maximum limits, and repositions the ball accordingly. It supports both vertical and horizontal paddle orientations and applies additional velocity from moving paddles.

:param ball: The ball object containing rect (for collision detection), vx, vy (velocity components)
:param paddle: The paddle object containing rect with height and width dimensions
:param paddle_vy: Vertical velocity of the paddle for adding momentum transfer effects when non-zero

The function processes collision by calculating offset based on impact position relative to paddle center. A rubber bounce effect applies where bounce angle scales with offset magnitude from -1.0 to 1.0. Speed multipliers consider both rubber factor and paddle vertical movement. The ball is repositioned to prevent immediate re-collision after bounce.

The function logs debug information about the bounce including final speed in meters per second and angle in degrees for physics verification during development.
:return: None

## check_circle_collision

`def check_circle_collision(x1: float, y1: float, r1: float, x2: float, y2: float, r2: float) -> bool`

This function evaluates whether two circular shapes intersect or touch in a two-dimensional coordinate system by comparing their geometric properties. It calculates the squared distance between centers and compares it to the squared sum of radii.

:param x1: The horizontal position of the center point for the first circle.
:param y1: The vertical position of the center point for the first circle.
:param r1: The radius length of the first circle.
:param x2: The horizontal position of the center point for the second circle.
:param y2: The vertical position of the center point for the second circle.
:param r2: The radius length of the second circle.
:return: A boolean value indicating whether a collision occurs between the two circles.

## clamp

`def clamp(val: float, min_val: float, max_val: float) -> float`

Clamps a value to be within a specified minimum and maximum limit.

:param val: The input numeric value that will be clamped.
:param min_val: The lower boundary of the valid range.
:param max_val: The upper boundary of the valid range.
:return: A float representing the clamped value within the bounds.

## apply_gravity

`def apply_gravity(vy: float, gravity: float, dt: float) -> float`

Applies gravitational acceleration to a vertical velocity vector over a given time step.

:param vy: Vertical velocity value before the application of gravity.
:param gravity: Gravitational acceleration value acting on the velocity.
:param dt: Time duration for the calculation interval.
:return: Updated vertical velocity after applying the gravitational effect over the time step.

## update_velocity_damping

`def update_velocity_damping(vx: float, vy: float, damping: float) -> tuple[float, float]`

Update velocity vectors by scaling them with a damping factor to simulate friction or decay.

:param vx: The current x-axis velocity component (float).
:param vy: The current y-axis velocity component (float).
:param damping: A scalar value representing the friction coefficient applied to both components (float).
:return: A tuple containing the damped x and y velocities after applying the factor (tuple[float, float]).

## calculate_orbital_pull

`def calculate_orbital_pull(px: float, py: float, cx: float, cy: float, strength: float, min_dist: float=10.0) -> tuple[float, float]`

Calculate the orbital pull force components acting on an object at a specified position relative to a central attractor. This function computes the x and y components of the force exerted based on the distance between the current position and the orbital center, applying a strength scaling factor while enforcing a minimum distance constraint to prevent singularity.

:param px: The x-coordinate of the particle's current position.
:param py: The y-coordinate of the particle's current position.
:param cx: The x-coordinate of the central attractor or orbit center.
:param cy: The y-coordinate of the central attractor or orbit center.
:param strength: The scalar magnitude defining the intensity of the pull force applied.
:param min_dist: The minimum distance threshold enforced to prevent infinite forces when the particle is too close to the center, defaulting to 10.0.
:return: A tuple containing the x-component (fx) and y-component (fy) of the calculated orbital pull force.

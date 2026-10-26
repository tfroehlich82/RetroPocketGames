from __future__ import annotations

import math

from pocket_games.core.logger import logger


def handle_paddle_collision(ball, paddle, paddle_vy: float = 0.0) -> None:
    """
    This function handles collision between the ball and the paddle in a paddle-ball game. When a collision is detected, it calculates appropriate bounce physics based on impact position, adjusts velocity with rubber elasticity effects, clips speed to maximum limits, and repositions the ball accordingly. It supports both vertical and horizontal paddle orientations and applies additional velocity from moving paddles.

    :param ball: The ball object containing rect (for collision detection), vx, vy (velocity components)
    :param paddle: The paddle object containing rect with height and width dimensions
    :param paddle_vy: Vertical velocity of the paddle for adding momentum transfer effects when non-zero

    The function processes collision by calculating offset based on impact position relative to paddle center. A rubber bounce effect applies where bounce angle scales with offset magnitude from -1.0 to 1.0. Speed multipliers consider both rubber factor and paddle vertical movement. The ball is repositioned to prevent immediate re-collision after bounce.

    The function logs debug information about the bounce including final speed in meters per second and angle in degrees for physics verification during development.
    :return: None

    """
    if ball.rect.colliderect(paddle.rect):
        if paddle.rect.height > paddle.rect.width:
            paddle_center = paddle.rect.centery
            ball_center = ball.rect.centery
            half_extent = paddle.rect.height / 2.0
            is_vertical_paddle = True
        else:
            paddle_center = paddle.rect.centerx
            ball_center = ball.rect.centerx
            half_extent = paddle.rect.width / 2.0
            is_vertical_paddle = False

        offset = (ball_center - paddle_center) / max(1.0, half_extent)
        offset = max(-1.0, min(1.0, offset))

        max_bounce_angle = math.radians(60)
        bounce_angle = offset * max_bounce_angle

        rubber_bounce_factor = 1.05 + (abs(offset) * 0.08)
        current_speed = math.hypot(ball.vx, ball.vy) * rubber_bounce_factor

        if paddle_vy != 0.0:
            current_speed += abs(paddle_vy) * 0.15

        max_speed = 450.0
        current_speed = min(current_speed, max_speed)

        if is_vertical_paddle:
            direction = -1 if ball.vx > 0 else 1
            ball.vx = direction * current_speed * math.cos(bounce_angle)
            ball.vy = current_speed * math.sin(bounce_angle)

            if direction > 0:
                ball.rect.left = paddle.rect.right
            else:
                ball.rect.right = paddle.rect.left
        else:
            direction = -1 if ball.vy > 0 else 1
            ball.vx = current_speed * math.sin(bounce_angle)
            ball.vy = direction * current_speed * math.cos(bounce_angle)

            if direction > 0:
                ball.rect.top = paddle.rect.bottom
            else:
                ball.rect.bottom = paddle.rect.top

        ball.x, ball.y = ball.rect.centerx, ball.rect.centery

        logger.debug(
            f"Rubber Ball Bounce: Speed={current_speed:.2f}, Angle={math.degrees(bounce_angle):.1f}°"
        )


def check_circle_collision(
    x1: float, y1: float, r1: float, x2: float, y2: float, r2: float
) -> bool:
    """
    This function evaluates whether two circular shapes intersect or touch in a two-dimensional coordinate system by comparing their geometric properties. It calculates the squared distance between centers and compares it to the squared sum of radii.

    :param x1: The horizontal position of the center point for the first circle.
    :param y1: The vertical position of the center point for the first circle.
    :param r1: The radius length of the first circle.
    :param x2: The horizontal position of the center point for the second circle.
    :param y2: The vertical position of the center point for the second circle.
    :param r2: The radius length of the second circle.
    :return: A boolean value indicating whether a collision occurs between the two circles.
    """
    dist_sq = (x1 - x2) ** 2 + (y1 - y2) ** 2
    return dist_sq <= (r1 + r2) ** 2


def clamp(val: float, min_val: float, max_val: float) -> float:
    """
    Clamps a value to be within a specified minimum and maximum limit.

    :param val: The input numeric value that will be clamped.
    :param min_val: The lower boundary of the valid range.
    :param max_val: The upper boundary of the valid range.
    :return: A float representing the clamped value within the bounds."""
    return max(min_val, min(max_val, val))


def apply_gravity(vy: float, gravity: float, dt: float) -> float:
    """
    Applies gravitational acceleration to a vertical velocity vector over a given time step.

    :param vy: Vertical velocity value before the application of gravity.
    :param gravity: Gravitational acceleration value acting on the velocity.
    :param dt: Time duration for the calculation interval.
    :return: Updated vertical velocity after applying the gravitational effect over the time step.
    """
    return vy + gravity * dt


def update_velocity_damping(
    vx: float, vy: float, damping: float
) -> tuple[float, float]:
    """
    Update velocity vectors by scaling them with a damping factor to simulate friction or decay.

    :param vx: The current x-axis velocity component (float).
    :param vy: The current y-axis velocity component (float).
    :param damping: A scalar value representing the friction coefficient applied to both components (float).
    :return: A tuple containing the damped x and y velocities after applying the factor (tuple[float, float]).

    """
    return vx * damping, vy * damping


def calculate_orbital_pull(
    px: float, py: float, cx: float, cy: float, strength: float, min_dist: float = 10.0
) -> tuple[float, float]:
    """
    Calculate the orbital pull force components acting on an object at a specified position relative to a central attractor. This function computes the x and y components of the force exerted based on the distance between the current position and the orbital center, applying a strength scaling factor while enforcing a minimum distance constraint to prevent singularity.

    :param px: The x-coordinate of the particle's current position.
    :param py: The y-coordinate of the particle's current position.
    :param cx: The x-coordinate of the central attractor or orbit center.
    :param cy: The y-coordinate of the central attractor or orbit center.
    :param strength: The scalar magnitude defining the intensity of the pull force applied.
    :param min_dist: The minimum distance threshold enforced to prevent infinite forces when the particle is too close to the center, defaulting to 10.0.
    :return: A tuple containing the x-component (fx) and y-component (fy) of the calculated orbital pull force."""
    dx = cx - px
    dy = cy - py
    dist_sq = dx * dx + dy * dy
    dist = math.sqrt(dist_sq)
    dist = max(dist, min_dist)

    force = strength / max(1.0, dist_sq)
    fx = force * (dx / dist)
    fy = force * (dy / dist)
    return fx, fy

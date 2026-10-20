from __future__ import annotations

import math

from pocket_games.core.logger import logger


def handle_paddle_collision(ball, paddle, paddle_vy: float = 0.0) -> None:
    """Berechnet die Gummi-Ball-Elastizitätsphysik bei Paddle-Kollisionen (für Pong & Bit Blaster)."""
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
    """Prüft eine distanzbasierte Kreis-Kollision (für Miner, Bugs, Chrono Shift etc.)."""
    dist_sq = (x1 - x2) ** 2 + (y1 - y2) ** 2
    return dist_sq <= (r1 + r2) ** 2


def clamp(val: float, min_val: float, max_val: float) -> float:
    """Begrenzt einen Wert auf definierte Min/Max-Grenzen."""
    return max(min_val, min(max_val, val))


def apply_gravity(vy: float, gravity: float, dt: float) -> float:
    """Wendet Gravitationsbeschleunigung auf die vertikale Geschwindigkeit an."""
    return vy + gravity * dt


def update_velocity_damping(
    vx: float, vy: float, damping: float
) -> tuple[float, float]:
    """Wendet Reibung / Dämpfung auf Geschwindigkeitsvektoren an (z. B. Chrono Shift)."""
    return vx * damping, vy * damping


def calculate_orbital_pull(
    px: float, py: float, cx: float, cy: float, strength: float, min_dist: float = 10.0
) -> tuple[float, float]:
    """Berechnet die Anziehungskraft für Gravitationsquellen / Planeten (Gravity Sling)."""
    dx = cx - px
    dy = cy - py
    dist_sq = dx * dx + dy * dy
    dist = math.sqrt(dist_sq)
    dist = max(dist, min_dist)

    force = strength / max(1.0, dist_sq)
    fx = force * (dx / dist)
    fy = force * (dy / dist)
    return fx, fy

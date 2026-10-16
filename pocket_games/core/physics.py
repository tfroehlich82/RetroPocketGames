import math

from pocket_games.core.logger import logger


def handle_paddle_collision(ball, paddle):
    if ball.rect.colliderect(paddle.rect):
        paddle_center_y = paddle.rect.centery
        ball_center_y = ball.rect.centery
        offset = (ball_center_y - paddle_center_y) / (paddle.rect.height / 2)
        offset = max(-1.0, min(1.0, offset))
        max_bounce_angle = math.radians(45)
        bounce_angle = offset * max_bounce_angle
        current_speed = (
            math.hypot(ball.vx, ball.vy) * 1.04
        )  # 4% Acceleration
        max_speed = 400.0
        current_speed = min(current_speed, max_speed)
        direction = -1 if ball.vx > 0 else 1
        ball.vx = direction * current_speed * math.cos(bounce_angle)
        ball.vy = current_speed * math.sin(bounce_angle)
        if direction > 0:
            ball.rect.left = paddle.rect.right
        else:
            ball.rect.right = paddle.rect.left
        logger.debug(
            f"Calculated forces for rubber ball: Speed={current_speed:.2f}, Angle={math.degrees(bounce_angle):.1f}°"
        )

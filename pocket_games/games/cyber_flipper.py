# ==========================================
# CYBER FLIPPER v1.0
# A virtual pinball table with five themed levels.
# Each level has its own palette, gravity, bumper
# layout, wall layout, raised decks and ramps.
# Flippers, launcher and bumpers are simulated with
# segment physics on two height layers.
# ==========================================
from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from pocket_games.core.settings import CYBER_FLIPPER_TUNING_FILE
from pocket_games.core.tuning import get_number, get_section, load_tuning_file
from pocket_games.games.base import BaseGame

Color = tuple[int, int, int]
Segment = tuple[tuple[float, float], tuple[float, float]]
BumperSpec = tuple[float, float, float, int, Color]
LAYER_LOW = 0
LAYER_HIGH = 1
BANNER_DURATION = 2.0
GRID_STEP = 20


@dataclass(frozen=True)
class RampZone:
    """
    A rectangular ramp area. While the ball center is inside it, the ball moves
    to the height layer `to_layer` (0 for the playfield, 1 for the raised deck).
    """

    x: float
    y: float
    w: float
    h: float
    to_layer: int


@dataclass(frozen=True)
class FlipperLevel:
    """
    Static description of one pinball table: theme colors, physics values,
    the score needed to clear it, and the bumper, wall, ramp and raised deck layout.
    """

    name: str
    background: Color
    grid: Color
    wall: Color
    accent: Color
    gravity: float
    wall_restitution: float
    score_target: int
    bumpers: tuple[BumperSpec, ...]
    walls: tuple[Segment, ...]
    ramps: tuple[RampZone, ...] = ()
    upper_walls: tuple[Segment, ...] = ()
    upper_bumpers: tuple[BumperSpec, ...] = ()


def _pair(value: object, default: tuple[float, float]) -> tuple[float, float]:
    """
    Converts a two-element JSON array into a float tuple.

    :param value: Parsed JSON value, expected to be a list of two numbers.
    :param default: Tuple returned when the value is missing or malformed.
    :return: The coordinate pair as floats.
    """
    if isinstance(value, list) and len(value) == 2:
        return float(value[0]), float(value[1])
    return default


def _segment(value: object) -> Segment:
    """
    Converts a JSON wall entry of the form [[x1, y1], [x2, y2]] into a segment.

    :param value: Parsed JSON wall entry.
    :return: The segment as a pair of coordinate pairs.
    """
    start, end = value
    return _pair(start, (0.0, 0.0)), _pair(end, (0.0, 0.0))


def _color(value: object, default: Color) -> Color:
    """
    Converts a JSON color array into an RGB tuple.

    :param value: Parsed JSON value, expected to be a list of three integers.
    :param default: Color returned when the value is missing or malformed.
    :return: The RGB color as a tuple.
    """
    if isinstance(value, list) and len(value) == 3:
        return int(value[0]), int(value[1]), int(value[2])
    return default


def _bumper(value: object) -> BumperSpec:
    """
    Converts a JSON bumper entry [x, y, radius, points, color] into a bumper specification.

    :param value: Parsed JSON bumper entry.
    :return: The bumper specification tuple.
    """
    x, y, r, pts, color = value
    return float(x), float(y), float(r), int(pts), _color(color, (255, 255, 255))


def _ramp(value: dict) -> RampZone:
    """
    Converts a JSON ramp object into a RampZone.

    :param value: Parsed JSON ramp object with x, y, w, h and to_layer keys.
    :return: The ramp zone.
    """
    return RampZone(
        float(value["x"]),
        float(value["y"]),
        float(value["w"]),
        float(value["h"]),
        int(value["to_layer"]),
    )


def _frame_walls(data: dict) -> tuple[Segment, ...]:
    """
    Reads the static frame walls shared by every table.

    :param data: The loaded tuning dictionary.
    :return: The frame wall segments.
    """
    return tuple(_segment(entry) for entry in data.get("frame_walls", []))


def _build_level(entry: dict) -> FlipperLevel:
    """
    Builds one FlipperLevel from its JSON object.

    :param entry: Parsed JSON object describing a single table.
    :return: The table definition.
    """
    bumpers = tuple(_bumper(b) for b in entry.get("bumpers", []))
    ring = entry.get("ring_bumpers")
    if ring:
        bumpers = _ring_bumpers(
            float(ring["cx"]),
            float(ring["cy"]),
            float(ring["radius"]),
            int(ring["count"]),
            int(ring["pts"]),
            _color(ring["color"], (255, 255, 255)),
        ) + bumpers
    return FlipperLevel(
        name=str(entry["name"]),
        background=_color(entry.get("background"), (8, 10, 20)),
        grid=_color(entry.get("grid"), (18, 26, 48)),
        wall=_color(entry.get("wall"), (0, 200, 255)),
        accent=_color(entry.get("accent"), (0, 255, 200)),
        gravity=float(entry.get("gravity", 450.0)),
        wall_restitution=float(entry.get("wall_restitution", 0.7)),
        score_target=int(entry.get("score_target", 1500)),
        bumpers=bumpers,
        walls=tuple(_segment(w) for w in entry.get("walls", [])),
        ramps=tuple(_ramp(r) for r in entry.get("ramps", [])),
        upper_walls=tuple(_segment(w) for w in entry.get("upper_walls", [])),
        upper_bumpers=tuple(_bumper(b) for b in entry.get("upper_bumpers", [])),
    )


def _build_levels(data: dict) -> tuple[FlipperLevel, ...]:
    """
    Builds all table definitions from the tuning dictionary.

    :param data: The loaded tuning dictionary.
    :return: The ordered tuple of tables.
    """
    return tuple(_build_level(entry) for entry in data.get("levels", []))


def _ring_bumpers(
    cx: float, cy: float, radius: float, count: int, pts: int, color: Color
) -> tuple[BumperSpec, ...]:
    """
    Builds a circle of bumpers around a center point.

    :param cx: Center x coordinate of the ring.
    :param cy: Center y coordinate of the ring.
    :param radius: Distance of each bumper from the center.
    :param count: Number of bumpers in the ring.
    :param pts: Score awarded per bumper hit.
    :param color: Neon color of the bumpers.
    :return: Tuple of bumper specifications.
    """
    specs: list[BumperSpec] = []
    for i in range(count):
        ang = (math.pi * 2 / count) * i
        specs.append((cx + math.cos(ang) * radius, cy + math.sin(ang) * radius, 9.0, pts, color))
    return tuple(specs)


TUNING_FILE = CYBER_FLIPPER_TUNING_FILE
_TUNING = load_tuning_file(TUNING_FILE)
_PHYSICS = get_section(_TUNING, "physics")
_PLAYFIELD = get_section(_TUNING, "playfield")

PLAYFIELD_LEFT = get_number(_PLAYFIELD, "left", 20.0)
PLAYFIELD_RIGHT = get_number(_PLAYFIELD, "right", 300.0)
PLAYFIELD_TOP = get_number(_PLAYFIELD, "top", 22.0)
LANE_X = get_number(_PLAYFIELD, "lane_x", 280.0)
DRAIN_Y = get_number(_PLAYFIELD, "drain_y", 236.0)
FLIPPER_LENGTH = get_number(_PHYSICS, "flipper_length", 48.0)
FLIPPER_THICKNESS = get_number(_PHYSICS, "flipper_thickness", 3.0)
FLIPPER_SPEED = get_number(_PHYSICS, "flipper_speed", 18.0)
FLIPPER_REST_ANGLE = get_number(_PHYSICS, "flipper_rest_angle", 0.5)
FLIPPER_ACTIVE_ANGLE = get_number(_PHYSICS, "flipper_active_angle", -0.45)
FLIPPER_KICK = get_number(_PHYSICS, "flipper_kick", 260.0)
LEFT_PIVOT = _pair(_PLAYFIELD.get("left_pivot"), (95.0, 200.0))
RIGHT_PIVOT = _pair(_PLAYFIELD.get("right_pivot"), (225.0, 200.0))
BALL_RADIUS = get_number(_PHYSICS, "ball_radius", 5.0)
BALLS_PER_GAME = int(get_number(_PHYSICS, "balls_per_game", 3))
SUBSTEPS = int(get_number(_PHYSICS, "substeps", 4))
MAX_BALL_SPEED = get_number(_PHYSICS, "max_ball_speed", 700.0)
BUMPER_BOOST = get_number(_PHYSICS, "bumper_boost", 1.08)
BUMPER_RESTITUTION = get_number(_PHYSICS, "bumper_restitution", 0.9)
LAUNCH_BASE_SPEED = get_number(_PHYSICS, "launch_base_speed", 260.0)
LAUNCH_SPEED_PER_CHARGE = get_number(_PHYSICS, "launch_speed_per_charge", 10.0)
MAX_CHARGE = get_number(_PHYSICS, "max_charge", 30.0)
PLUNGER_START = _pair(_PLAYFIELD.get("plunger_start"), (290.0, 190.0))
FRAME_WALLS = _frame_walls(_TUNING)
LEVELS = _build_levels(_TUNING)


def _clamp_channel(value: float) -> int:
    """
    Clamps a color channel to the valid 0-255 range.

    :param value: Channel value, possibly out of range.
    :return: Integer channel value between 0 and 255.
    """
    return max(0, min(255, int(value)))


def shade(color: Color, factor: float) -> Color:
    """
    Scales the brightness of a color by a factor.

    :param color: RGB color to scale.
    :param factor: Multiplier applied to every channel.
    :return: The darkened or brightened RGB color.
    """
    r, g, b = color
    return _clamp_channel(r * factor), _clamp_channel(g * factor), _clamp_channel(b * factor)


def brighten(color: Color, amount: int) -> Color:
    """
    Adds a fixed amount of brightness to every channel of a color.

    :param color: RGB color to brighten.
    :param amount: Value added to each channel, may be negative.
    :return: The adjusted RGB color.
    """
    r, g, b = color
    return _clamp_channel(r + amount), _clamp_channel(g + amount), _clamp_channel(b + amount)


def closest_point_on_segment(
    px: float, py: float, ax: float, ay: float, bx: float, by: float
) -> tuple[float, float]:
    """
    Returns the point on the segment A-B that is closest to point P.

    :param px: X coordinate of the point.
    :param py: Y coordinate of the point.
    :param ax: X coordinate of the segment start.
    :param ay: Y coordinate of the segment start.
    :param bx: X coordinate of the segment end.
    :param by: Y coordinate of the segment end.
    :return: The closest (x, y) point on the segment.
    """
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0.0:
        return ax, ay
    t = ((px - ax) * dx + (py - ay) * dy) / length_sq
    t = max(0.0, min(1.0, t))
    return ax + dx * t, ay + dy * t


def point_in_rect(px: float, py: float, x: float, y: float, w: float, h: float) -> bool:
    """
    Checks whether a point lies inside an axis-aligned rectangle.

    :param px: X coordinate of the point.
    :param py: Y coordinate of the point.
    :param x: Left edge of the rectangle.
    :param y: Top edge of the rectangle.
    :param w: Width of the rectangle.
    :param h: Height of the rectangle.
    :return: True if the point is inside or on the rectangle.
    """
    return x <= px <= x + w and y <= py <= y + h


def layer_at(ramps: tuple[RampZone, ...], px: float, py: float) -> int:
    """
    Determines the height layer at a position. The first zone that contains the
    position decides the layer. Outside every zone the ball is on the low layer,
    so leaving a raised deck makes the ball fall back to the playfield.

    :param ramps: Ramp and deck zones of the active table.
    :param px: X coordinate of the ball center.
    :param py: Y coordinate of the ball center.
    :return: LAYER_HIGH or LAYER_LOW.
    """
    for ramp in ramps:
        if point_in_rect(px, py, ramp.x, ramp.y, ramp.w, ramp.h):
            return ramp.to_layer
    return LAYER_LOW


def reflect_velocity(
    vx: float, vy: float, nx: float, ny: float, restitution: float
) -> tuple[float, float]:
    """
    Reflects a velocity off a surface with the given unit normal. Velocities
    that already move away from the surface are returned unchanged.

    :param vx: Velocity along x.
    :param vy: Velocity along y.
    :param nx: X component of the unit surface normal.
    :param ny: Y component of the unit surface normal.
    :param restitution: Bounciness factor, 0 absorbs and 1 is perfectly elastic.
    :return: The reflected (vx, vy) velocity.
    """
    dot = vx * nx + vy * ny
    if dot >= 0.0:
        return vx, vy
    return vx - (1.0 + restitution) * dot * nx, vy - (1.0 + restitution) * dot * ny


def flipper_tip(side: int, angle: float) -> tuple[float, float]:
    """
    Computes the tip position of a flipper for a given swing angle.

    :param side: -1 for the left flipper, 1 for the right flipper.
    :param angle: Swing angle in radians, see FLIPPER_REST_ANGLE and FLIPPER_ACTIVE_ANGLE.
    :return: The (x, y) position of the flipper tip.
    """
    px, py = LEFT_PIVOT if side < 0 else RIGHT_PIVOT
    return px - side * FLIPPER_LENGTH * math.cos(angle), py + FLIPPER_LENGTH * math.sin(angle)


def advance_flipper_angle(angle: float, active: bool, dt: float) -> float:
    """
    Moves a flipper angle towards its active or rest target at a fixed speed.

    :param angle: Current swing angle in radians.
    :param active: True if the flipper button is held.
    :param dt: Elapsed time in seconds.
    :return: The new swing angle.
    """
    target = FLIPPER_ACTIVE_ANGLE if active else FLIPPER_REST_ANGLE
    step = FLIPPER_SPEED * dt
    if angle < target:
        return min(target, angle + step)
    return max(target, angle - step)


class CyberFlipperGame(BaseGame):
    """
    Pinball game with five themed tables. The player controls two flippers and
    a plunger, and must reach the score target of each table to advance.
    """

    def __init__(self, engine, rng: random.Random | None = None) -> None:
        super().__init__(engine, game_name="Cyber Flipper", tuning_file=TUNING_FILE)
        self.rng = rng if rng is not None else random.Random(2077)
        self.level_index = 0
        self.level = 1
        self.level_score = 0
        self.balls_left = BALLS_PER_GAME
        self.ball_radius = BALL_RADIUS
        self.bx, self.by = PLUNGER_START
        self.bvx, self.bvy = 0.0, 0.0
        self.ball_on_plunger = True
        self.launcher_pulled = 0.0
        self.flipper_left_active = False
        self.flipper_right_active = False
        self.left_angle = FLIPPER_REST_ANGLE
        self.right_angle = FLIPPER_REST_ANGLE
        self.left_rising = False
        self.right_rising = False
        self.particles: list[dict] = []
        self.banner_timer = BANNER_DURATION
        self.bumpers: list[dict] = []
        self.upper_bumpers: list[dict] = []
        self.walls: list[Segment] = []
        self.upper_walls: list[Segment] = []
        self.ramps: tuple[RampZone, ...] = ()
        self.ball_layer = LAYER_LOW
        self.gravity = 0.0
        self.wall_restitution = 0.7
        self.load_level(0)

    @property
    def table(self) -> FlipperLevel:
        """
        Returns the table definition of the current level.

        :return: The active FlipperLevel.
        """
        return LEVELS[self.level_index]

    def load_level(self, index: int) -> None:
        """
        Loads the table layout, physics and palette of a level and resets the ball.

        :param index: Zero-based index into LEVELS.
        """
        self.level_index = index
        self.level = index + 1
        level = LEVELS[index]
        self.gravity = level.gravity
        self.wall_restitution = level.wall_restitution
        self.bumpers = self._make_bumpers(level.bumpers)
        self.upper_bumpers = self._make_bumpers(level.upper_bumpers)
        self.walls = list(FRAME_WALLS) + list(level.walls)
        self.upper_walls = list(level.upper_walls)
        self.ramps = level.ramps
        self.level_score = 0
        self.particles = []
        self.banner_timer = BANNER_DURATION
        self.reset_ball()

    @staticmethod
    def _make_bumpers(specs: tuple[BumperSpec, ...]) -> list[dict]:
        """
        Converts bumper specifications into mutable bumper state dictionaries.

        :param specs: Bumper specifications of a table layer.
        :return: List of bumper state dictionaries with flash timers.
        """
        return [
            {
                "x": x,
                "y": y,
                "r": r,
                "pts": pts,
                "color": color,
                "flash": 0.0,
            }
            for x, y, r, pts, color in specs
        ]

    def active_bumpers(self) -> list[dict]:
        """
        Returns the bumpers on the height layer the ball currently occupies.

        :return: Bumpers of the ball's layer.
        """
        return self.upper_bumpers if self.ball_layer == LAYER_HIGH else self.bumpers

    def active_walls(self) -> list[Segment]:
        """
        Returns the frame walls plus the table walls of the ball's height layer.

        :return: Wall segments that can collide with the ball right now.
        """
        if self.ball_layer == LAYER_HIGH:
            return list(FRAME_WALLS) + list(self.upper_walls)
        return list(FRAME_WALLS) + list(self.walls[len(FRAME_WALLS):])

    def reset_ball(self) -> None:
        """
        Places a fresh ball in the plunger lane, ready to be launched.
        """
        self.bx, self.by = PLUNGER_START
        self.bvx = 0.0
        self.bvy = 0.0
        self.launcher_pulled = 0.0
        self.ball_on_plunger = True
        self.ball_layer = LAYER_LOW

    def handle_input(self) -> None:
        """
        Reads flipper and plunger input. Holding the plunger charges it, releasing
        it launches the ball from the plunger lane.
        """
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        self.flipper_left_active = inp.is_left_pressed() or inp.is_key_down(pygame.K_z)
        self.flipper_right_active = inp.is_right_pressed() or inp.is_key_down(pygame.K_x)

        if not self.ball_on_plunger:
            return
        if inp.is_down_pressed() or inp.is_action_pressed():
            self.launcher_pulled = min(MAX_CHARGE, self.launcher_pulled + 40.0 * 0.016)
        elif (inp.is_action_just_pressed() or inp.is_up_pressed()) and self.launcher_pulled > 0:
            self.bvy = -LAUNCH_BASE_SPEED - self.launcher_pulled * LAUNCH_SPEED_PER_CHARGE
            self.launcher_pulled = 0.0
            self.ball_on_plunger = False
            self.play_sound("confirm")

    def update(self, dt: float) -> None:
        """
        Advances flippers, particles, bumper flashes and the ball physics.

        :param dt: Elapsed time in seconds.
        """
        super().update(dt)
        if self.game_over or self.paused:
            return

        if self.banner_timer > 0:
            self.banner_timer -= dt
        self._update_particles(dt)
        for b in self.bumpers:
            if b["flash"] > 0:
                b["flash"] -= dt

        self._update_flippers(dt)

        if not self.ball_on_plunger:
            step = dt / SUBSTEPS
            for _ in range(SUBSTEPS):
                self._step_ball(step)

        if self.by - self.ball_radius > DRAIN_Y:
            self._drain_ball()
        self._check_level_complete()

    def _update_particles(self, dt: float) -> None:
        """
        Moves particles and removes the ones whose lifetime has expired.

        :param dt: Elapsed time in seconds.
        """
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

    def _spawn_particles(self, x: float, y: float, color: Color, count: int, speed: float, life: float) -> None:
        """
        Spawns a burst of particles at a position with random directions.

        :param x: Origin x coordinate.
        :param y: Origin y coordinate.
        :param color: Particle color.
        :param count: Number of particles to spawn.
        :param speed: Maximum particle speed in px/s.
        :param life: Lifetime of each particle in seconds.
        """
        for _ in range(count):
            ang = self.rng.uniform(0, math.pi * 2)
            spd = self.rng.uniform(speed * 0.4, speed)
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(ang) * spd,
                    "vy": math.sin(ang) * spd,
                    "life": life,
                    "color": color,
                }
            )

    def _update_flippers(self, dt: float) -> None:
        """
        Swings both flippers towards their target angles and records the rising state.

        :param dt: Elapsed time in seconds.
        """
        new_left = advance_flipper_angle(self.left_angle, self.flipper_left_active, dt)
        new_right = advance_flipper_angle(self.right_angle, self.flipper_right_active, dt)
        self.left_rising = new_left < self.left_angle
        self.right_rising = new_right < self.right_angle
        self.left_angle = new_left
        self.right_angle = new_right

    def _step_ball(self, dt: float) -> None:
        """
        Runs one physics substep: gravity, movement, then all collisions.

        :param dt: Substep length in seconds.
        """
        self.bvy += self.gravity * dt
        self.bx += self.bvx * dt
        self.by += self.bvy * dt
        self.ball_layer = layer_at(self.ramps, self.bx, self.by)

        speed = math.hypot(self.bvx, self.bvy)
        if speed > MAX_BALL_SPEED:
            scale = MAX_BALL_SPEED / speed
            self.bvx *= scale
            self.bvy *= scale

        self._collide_walls()
        self._collide_flippers()
        self._collide_bumpers()

    def _collide_segment(
        self,
        ax: float,
        ay: float,
        bx_: float,
        by_: float,
        min_dist: float,
        restitution: float,
        kick: float = 0.0,
    ) -> bool:
        """
        Pushes the ball out of a segment if it overlaps and reflects its velocity.

        :param ax: X coordinate of the segment start.
        :param ay: Y coordinate of the segment start.
        :param bx_: X coordinate of the segment end.
        :param by_: Y coordinate of the segment end.
        :param min_dist: Minimum allowed distance between ball center and segment.
        :param restitution: Bounciness of the surface.
        :param kick: Extra speed added along the surface normal, used by flippers.
        :return: True if a collision happened.
        """
        cx, cy = closest_point_on_segment(self.bx, self.by, ax, ay, bx_, by_)
        dx, dy = self.bx - cx, self.by - cy
        dist = math.hypot(dx, dy)
        if dist >= min_dist:
            return False
        if dist < 1e-6:
            nx, ny = 0.0, -1.0
        else:
            nx, ny = dx / dist, dy / dist
        self.bx = cx + nx * min_dist
        self.by = cy + ny * min_dist
        self.bvx, self.bvy = reflect_velocity(self.bvx, self.bvy, nx, ny, restitution)
        if kick:
            self.bvx += nx * kick
            self.bvy += ny * kick
        return True

    def _collide_walls(self) -> None:
        """
        Bounces the ball off all frame and table walls.
        """
        for (ax, ay), (bx_, by_) in self.active_walls():
            if self._collide_segment(ax, ay, bx_, by_, self.ball_radius, self.wall_restitution):
                self.play_sound("hit")

    def _collide_flippers(self) -> None:
        """
        Bounces the ball off both flippers. A flipper that is swinging up adds a kick.
        """
        for side, angle, rising in (
            (-1, self.left_angle, self.left_rising),
            (1, self.right_angle, self.right_rising),
        ):
            px, py = LEFT_PIVOT if side < 0 else RIGHT_PIVOT
            tx, ty = flipper_tip(side, angle)
            kick = FLIPPER_KICK if rising else 0.0
            if self._collide_segment(
                px, py, tx, ty, self.ball_radius + FLIPPER_THICKNESS, 0.6, kick
            ):
                self.play_sound("select")
                color = self.table.accent
                self._spawn_particles(self.bx, self.by, color, 5, 80.0, 0.3)

    def _collide_bumpers(self) -> None:
        """
        Handles ball collisions with round bumpers, awarding points and boosting speed.
        """
        for b in self.active_bumpers():
            dist = math.hypot(self.bx - b["x"], self.by - b["y"])
            min_dist = self.ball_radius + b["r"]
            if dist >= min_dist:
                continue
            nx = (self.bx - b["x"]) / dist if dist > 0 else 0.0
            ny = (self.by - b["y"]) / dist if dist > 0 else -1.0
            self.bx = b["x"] + nx * min_dist
            self.by = b["y"] + ny * min_dist
            self.bvx, self.bvy = reflect_velocity(self.bvx, self.bvy, nx, ny, BUMPER_RESTITUTION)
            self.bvx *= BUMPER_BOOST
            self.bvy *= BUMPER_BOOST
            self._award(b["pts"])
            b["flash"] = 0.2
            self.play_sound("score")
            self._spawn_particles(b["x"], b["y"], b["color"], 8, 120.0, 0.4)

    def _award(self, points: int) -> None:
        """
        Adds points to the total score and to the current level score.

        :param points: Points to award.
        """
        self.add_score(points)
        self.level_score += points

    def _drain_ball(self) -> None:
        """
        Handles a ball falling off the bottom of the table. Costs one ball, and
        ends the game when no balls are left.
        """
        self.balls_left -= 1
        self.play_sound("gameover")
        if self.balls_left <= 0:
            self.game_over = True
        else:
            self.reset_ball()

    def _check_level_complete(self) -> None:
        """
        Advances to the next table once the level score target is reached. Clearing
        the last table wins the game.
        """
        if self.level_score < self.table.score_target:
            return
        if self.level_index + 1 >= len(LEVELS):
            self.game_won = True
            return
        self.balls_left = BALLS_PER_GAME
        self.load_level(self.level_index + 1)
        self.play_sound("confirm")

    def render(self, surface: pygame.Surface) -> None:
        """
        Draws the themed table in layers: playfield, low walls and bumpers, the
        ball if it is on the low layer, the raised deck, upper walls and bumpers,
        the ball if it is on the high layer, flippers, plunger, particles and HUD.

        :param surface: The surface to draw on.
        """
        level = self.table
        self._draw_playfield(surface, level)

        self._draw_plunger(surface, level)
        for segment in self.walls:
            self._draw_wall(surface, segment, level)
        for b in self.bumpers:
            self._draw_bumper(surface, b, level)
        if self.ball_layer == LAYER_LOW:
            self._draw_ball(surface, level)

        self._draw_deck(surface, level)
        for segment in self.upper_walls:
            self._draw_wall(surface, segment, level)
        for b in self.upper_bumpers:
            self._draw_bumper(surface, b, level)
        if self.ball_layer == LAYER_HIGH:
            self._draw_ball(surface, level)

        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

        self._draw_flipper(surface, -1, self.left_angle, self.flipper_left_active)
        self._draw_flipper(surface, 1, self.right_angle, self.flipper_right_active)

        self._draw_hud(surface)
        if self.banner_timer > 0:
            banner = self.font.render(level.name.upper(), True, level.accent)
            surface.blit(banner, (160 - banner.get_width() // 2, 110))

        self.render_ui(surface)

    def _draw_playfield(self, surface: pygame.Surface, level: FlipperLevel) -> None:
        """
        Draws the playfield with a lit top-to-bottom gradient and a grid pattern.

        :param surface: The surface to draw on.
        :param level: The active table, providing the theme colors.
        """
        surface.fill(level.background)
        span = DRAIN_Y - PLAYFIELD_TOP
        for y in range(int(PLAYFIELD_TOP), int(DRAIN_Y), 2):
            lift = int(24 * (1.0 - (y - PLAYFIELD_TOP) / span))
            pygame.draw.line(
                surface, brighten(level.background, lift), (PLAYFIELD_LEFT, y), (PLAYFIELD_RIGHT, y)
            )
        for x in range(int(PLAYFIELD_LEFT), int(PLAYFIELD_RIGHT), GRID_STEP):
            pygame.draw.line(surface, level.grid, (x, PLAYFIELD_TOP), (x, DRAIN_Y), 1)
        for y in range(int(PLAYFIELD_TOP), int(DRAIN_Y), GRID_STEP):
            pygame.draw.line(surface, level.grid, (PLAYFIELD_LEFT, y), (PLAYFIELD_RIGHT, y), 1)
        self._draw_table_edge(surface, level)

    def _draw_table_edge(self, surface: pygame.Surface, level: FlipperLevel) -> None:
        """
        Draws the thick front edge of the table at the drain side, giving the
        playfield the look of a tilted glass cabinet seen from above.

        :param surface: The surface to draw on.
        :param level: The active table, providing the theme colors.
        """
        edge = pygame.Rect(int(PLAYFIELD_LEFT), int(DRAIN_Y), int(PLAYFIELD_RIGHT - PLAYFIELD_LEFT), 6)
        pygame.draw.rect(surface, shade(level.background, 0.25), edge)
        pygame.draw.line(surface, brighten(level.wall, 30), edge.topleft, edge.topright, 1)

    def _draw_wall(self, surface: pygame.Surface, segment: Segment, level: FlipperLevel) -> None:
        """
        Draws a rail as a metal guide with a drop shadow, a neon core and a highlight.

        :param surface: The surface to draw on.
        :param segment: The (start, end) points of the rail.
        :param level: The active table, providing the theme colors.
        """
        (ax, ay), (bx_, by_) = segment
        pygame.draw.line(surface, shade(level.background, 0.4), (ax + 2, ay + 3), (bx_ + 2, by_ + 3), 6)
        pygame.draw.line(surface, shade(level.wall, 0.3), (ax, ay), (bx_, by_), 5)
        pygame.draw.line(surface, level.wall, (ax, ay), (bx_, by_), 3)
        pygame.draw.line(surface, brighten(level.wall, 90), (ax, ay - 1), (bx_, by_ - 1), 1)

    def _draw_bumper(self, surface: pygame.Surface, b: dict, level: FlipperLevel) -> None:
        """
        Draws a pop bumper as a domed cap with a shadow, a rim and a specular highlight.

        :param surface: The surface to draw on.
        :param b: Bumper state dictionary.
        :param level: The active table, providing the theme colors.
        """
        x, y, r = int(b["x"]), int(b["y"]), b["r"]
        cap = (255, 255, 255) if b["flash"] > 0 else b["color"]
        pygame.draw.circle(surface, shade(level.background, 0.4), (x + 2, y + 3), r + 2)
        pygame.draw.circle(surface, shade(b["color"], 0.35), (x, y + 2), r + 2)
        pygame.draw.circle(surface, shade(cap, 0.7), (x, y + 1), r + 1)
        pygame.draw.circle(surface, cap, (x, y), r)
        pygame.draw.circle(surface, shade(cap, 0.3), (x, y), max(2, r - 4))
        pygame.draw.circle(surface, brighten(cap, 110), (x - r // 3, y - r // 3), max(1, r // 4))

    def _draw_deck(self, surface: pygame.Surface, level: FlipperLevel) -> None:
        """
        Draws every raised deck zone as a panel with a cast shadow on the playfield.

        :param surface: The surface to draw on.
        :param level: The active table, providing the theme colors.
        """
        for ramp in self.ramps:
            if ramp.to_layer != LAYER_HIGH:
                continue
            rect = pygame.Rect(int(ramp.x), int(ramp.y), int(ramp.w), int(ramp.h))
            pygame.draw.rect(surface, shade(level.background, 0.3), rect.move(4, 5))
            pygame.draw.rect(surface, brighten(level.background, 22), rect)
            pygame.draw.rect(surface, shade(level.wall, 0.5), rect, 1)
            pygame.draw.line(surface, brighten(level.wall, 40), rect.topleft, rect.topright, 2)

    def _draw_ball(self, surface: pygame.Surface, level: FlipperLevel) -> None:
        """
        Draws the steel ball with a glow, a floor shadow and a specular highlight.

        :param surface: The surface to draw on.
        :param level: The active table, providing the accent color.
        """
        x, y = int(self.bx), int(self.by)
        r = self.ball_radius
        pygame.draw.circle(surface, shade(level.accent, 0.35), (x, y), r + 2)
        pygame.draw.circle(surface, (150, 160, 175), (x, y), r)
        pygame.draw.circle(surface, (215, 222, 232), (x - 1, y - 1), r - 2)
        pygame.draw.circle(surface, (255, 255, 255), (x - 2, y - 2), 1)

    def _draw_plunger(self, surface: pygame.Surface, level: FlipperLevel) -> None:
        """
        Draws the plunger channel with its spring coils and the charge meter.

        :param surface: The surface to draw on.
        :param level: The active table, providing the accent color.
        """
        pygame.draw.rect(surface, (30, 34, 44), (282, 120, 16, 104))
        pygame.draw.rect(surface, (90, 96, 110), (282, 120, 16, 104), 1)
        for y in range(124, 220, 6):
            pygame.draw.line(surface, (120, 126, 140), (284, y), (296, y), 1)
        if self.ball_on_plunger and self.launcher_pulled > 0:
            charge_h = int(60 * self.launcher_pulled / MAX_CHARGE)
            pygame.draw.rect(surface, level.accent, (286, 214 - charge_h, 8, charge_h))

    def _draw_flipper(self, surface: pygame.Surface, side: int, angle: float, active: bool) -> None:
        """
        Draws one flipper arm, brighter while the button is held.

        :param surface: The surface to draw on.
        :param side: -1 for the left flipper, 1 for the right flipper.
        :param angle: Current swing angle in radians.
        :param active: Whether the flipper button is held.
        """
        px, py = LEFT_PIVOT if side < 0 else RIGHT_PIVOT
        tip = flipper_tip(side, angle)
        if side < 0:
            color = (0, 255, 255) if active else (80, 130, 160)
        else:
            color = (255, 0, 150) if active else (160, 80, 130)
        pygame.draw.line(surface, (5, 5, 10), (px + 2, py + 3), (tip[0] + 2, tip[1] + 3), 7)
        pygame.draw.line(surface, shade(color, 0.5), (px, py), tip, 7)
        pygame.draw.line(surface, color, (px, py), tip, 5)
        pygame.draw.line(surface, brighten(color, 90), (px, py - 1), (tip[0], tip[1] - 1), 1)
        pygame.draw.circle(surface, (20, 20, 28), (int(tip[0]), int(tip[1])), 3)
        pygame.draw.circle(surface, (60, 64, 74), (int(px), int(py)), 5)
        pygame.draw.circle(surface, (230, 230, 240), (int(px), int(py)), 3)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        """
        Draws the status line with the table number and balls at the top right and
        the table progress along the bottom edge. The total score is drawn by the base class.

        :param surface: The surface to draw on.
        """
        status = self.font.render(
            f"TABLE {self.level}/{len(LEVELS)}  BALLS {self.balls_left}", True, self.table.accent
        )
        surface.blit(status, (310 - status.get_width(), 5))
        progress = self.font.render(
            f"TABLE SCORE {self.level_score}/{self.table.score_target}", True, (200, 200, 220)
        )
        surface.blit(progress, (160 - progress.get_width() // 2, 226))

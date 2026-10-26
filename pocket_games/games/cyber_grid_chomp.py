# ==========================================
# CYBER GRID CHOMP v1.1
# A neon-infused cyberpunk Pac-Man clone optimized for 320x240.
# Five escalating sectors on a fixed single-lane maze, phantoms that hunt
# the player with breadth-first pathfinding, and an overclock mode that
# flips the chase. Every sector is deterministic and reproducible.
# ==========================================
from __future__ import annotations

import math
import random
from collections import deque

import pygame

from pocket_games.core.physics import check_circle_collision
from pocket_games.games.base import BaseGame

MAX_LEVELS = 5
TILE_SIZE = 20
ORIGIN_X = 10
ORIGIN_Y = 10
LAYOUT = (
    "###############",
    "#........#....#",
    "#.#.#.#.#.#.#.#",
    "#..#..........#",
    "#.#.#.#.#.#.#.#",
    "#..........#..#",
    "#.#.#.#.#.#.#.#",
    "#....#........#",
    "###############",
)
GRID_COLS = len(LAYOUT[0])
GRID_ROWS = len(LAYOUT)
DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))
PLAYER_SPAWN_TILE = (7, 7)
PLAYER_SPAWN = (160.0, 160.0)
POWER_PILL_TILES = ((1, 1), (13, 1), (1, 7), (13, 7))
SPAWN_INVULNERABILITY = 2.0
LEVEL_SEED_BASE = 4242
PHANTOM_COUNTS = (3, 3, 4, 4, 5)
PHANTOM_SPAWNS = ((7, 1), (1, 4), (13, 4), (7, 5), (11, 7))
PHANTOM_COLORS = ((255, 50, 80), (255, 150, 0), (0, 220, 255), (200, 50, 255), (120, 255, 60))


def _tile_of(x: float, y: float) -> tuple[int, int]:
    col = min(GRID_COLS - 1, max(0, int((x - ORIGIN_X) // TILE_SIZE)))
    row = min(GRID_ROWS - 1, max(0, int((y - ORIGIN_Y) // TILE_SIZE)))
    return col, row


def _tile_center(tile: tuple[int, int]) -> tuple[float, float]:
    return (
        ORIGIN_X + tile[0] * TILE_SIZE + TILE_SIZE / 2,
        ORIGIN_Y + tile[1] * TILE_SIZE + TILE_SIZE / 2,
    )


def _build_blocked_tiles() -> frozenset[tuple[int, int]]:
    return frozenset(
        (col, row)
        for row, line in enumerate(LAYOUT)
        for col, cell in enumerate(line)
        if cell == "#"
    )


def _build_wall_rects() -> tuple[pygame.Rect, ...]:
    return tuple(
        pygame.Rect(ORIGIN_X + col * TILE_SIZE, ORIGIN_Y + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        for col, row in sorted(BLOCKED_TILES, key=lambda t: (t[1], t[0]))
    )


BLOCKED_TILES = _build_blocked_tiles()
WALL_RECTS = _build_wall_rects()
_GLOW_CACHE: dict[tuple[int, tuple[int, int, int]], pygame.Surface] = {}


def _open_neighbors(tile: tuple[int, int]) -> list[tuple[int, int]]:
    col, row = tile
    neighbors = []
    for dx, dy in DIRECTIONS:
        nxt = (col + dx, row + dy)
        if 0 <= nxt[0] < GRID_COLS and 0 <= nxt[1] < GRID_ROWS and nxt not in BLOCKED_TILES:
            neighbors.append(nxt)
    return neighbors


def _distance_map(start: tuple[int, int]) -> dict[tuple[int, int], int]:
    distances = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in _open_neighbors(current):
            if nxt not in distances:
                distances[nxt] = distances[current] + 1
                queue.append(nxt)
    return distances


def _step_towards(x: float, y: float, tx: float, ty: float, step: float) -> tuple[float, float, bool]:
    dx, dy = tx - x, ty - y
    dist = math.hypot(dx, dy)
    if dist <= step:
        return tx, ty, True
    return x + dx / dist * step, y + dy / dist * step, False


class CyberGridChompGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Cyber Grid Chomp")
        self.lives = 3
        self.level = 1
        self.invulnerable_timer = SPAWN_INVULNERABILITY
        self.overclock_timer = 0.0
        self.banner_timer = 0.0
        self.chomp_timer = 0.0
        self.facing = 0.0
        self.speed = 80.0

        self.px, self.py = PLAYER_SPAWN
        self.ptile = PLAYER_SPAWN_TILE
        self.ptarget: tuple[int, int] | None = None
        self.pdir_x, self.pdir_y = 0.0, 0.0
        self.next_dir_x, self.next_dir_y = 0.0, 0.0

        self.bits: list[dict] = []
        self.power_pills: list[dict] = []
        self.phantoms: list[dict] = []
        self.walls: list[pygame.Rect] = list(WALL_RECTS)
        self.phantom_speed = 62.0
        self.chase_chance = 0.6
        self.pill_duration = 7.0
        self.rng = random.Random(LEVEL_SEED_BASE)
        self._player_dist: dict[tuple[int, int], int] = {}
        self._player_dist_tile: tuple[int, int] | None = None

        self._setup_level()

    def _setup_level(self) -> None:
        idx = self.level - 1
        self.phantom_speed = 62.0 + 8.0 * idx
        self.chase_chance = min(1.0, 0.6 + 0.1 * idx)
        self.pill_duration = max(4.0, 7.0 - 0.75 * idx)
        self.rng = random.Random(LEVEL_SEED_BASE + self.level)
        self._player_dist_tile = None

        self._reset_player()
        self.overclock_timer = 0.0

        self.bits = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                tile = (col, row)
                if tile in BLOCKED_TILES or tile in POWER_PILL_TILES:
                    continue
                x, y = _tile_center(tile)
                self.bits.append({"x": x, "y": y})

        self.power_pills = []
        for tile in POWER_PILL_TILES:
            x, y = _tile_center(tile)
            self.power_pills.append({"x": x, "y": y})

        count = PHANTOM_COUNTS[min(idx, len(PHANTOM_COUNTS) - 1)]
        self.phantoms = [self._make_phantom(i) for i in range(count)]

    def _reset_player(self) -> None:
        self.px, self.py = PLAYER_SPAWN
        self.ptile = PLAYER_SPAWN_TILE
        self.ptarget = None
        self.pdir_x, self.pdir_y = 0.0, 0.0
        self.next_dir_x, self.next_dir_y = 0.0, 0.0

    def _make_phantom(self, index: int) -> dict:
        x, y = _tile_center(PHANTOM_SPAWNS[index % len(PHANTOM_SPAWNS)])
        return {
            "x": x,
            "y": y,
            "target": None,
            "dx": 0,
            "dy": 0,
            "color": PHANTOM_COLORS[index % len(PHANTOM_COLORS)],
        }

    def _reset_phantoms(self) -> None:
        self.phantoms = [self._make_phantom(i) for i in range(len(self.phantoms))]

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        if inp.is_left_pressed():
            self.next_dir_x, self.next_dir_y = -1.0, 0.0
        elif inp.is_right_pressed():
            self.next_dir_x, self.next_dir_y = 1.0, 0.0
        elif inp.is_up_pressed():
            self.next_dir_x, self.next_dir_y = 0.0, -1.0
        elif inp.is_down_pressed():
            self.next_dir_x, self.next_dir_y = 0.0, 1.0

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over or self.paused:
            return

        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer -= dt
        if self.overclock_timer > 0.0:
            self.overclock_timer -= dt
        if self.banner_timer > 0.0:
            self.banner_timer -= dt

        self._move_player(dt)
        self._collect_items()
        self._update_phantoms(dt)

        if not self.bits and not self.game_over:
            self._advance_level()

    def _steer_player(self) -> None:
        nx, ny = self.next_dir_x, self.next_dir_y
        if self.ptarget is not None:
            if (nx, ny) != (0.0, 0.0) and (nx, ny) == (-self.pdir_x, -self.pdir_y):
                self.ptarget = self.ptile
                self.pdir_x, self.pdir_y = nx, ny
            return

        col, row = self.ptile
        for dx, dy in ((nx, ny), (self.pdir_x, self.pdir_y)):
            if (dx, dy) == (0.0, 0.0):
                continue
            nxt = (col + int(dx), row + int(dy))
            if nxt in _open_neighbors(self.ptile):
                self.pdir_x, self.pdir_y = dx, dy
                self.ptarget = nxt
                return
        self.pdir_x, self.pdir_y = 0.0, 0.0

    def _move_player(self, dt: float) -> None:
        self._steer_player()
        if self.ptarget is None:
            return

        if self.pdir_x != 0 or self.pdir_y != 0:
            self.facing = math.atan2(self.pdir_y, self.pdir_x)
        tx, ty = _tile_center(self.ptarget)
        self.px, self.py, arrived = _step_towards(self.px, self.py, tx, ty, self.speed * dt)
        self.chomp_timer += dt
        if arrived:
            self.ptile = self.ptarget
            self.ptarget = None

    def _collect_items(self) -> None:
        for b in self.bits[:]:
            if check_circle_collision(self.px, self.py, 6.0, float(b["x"]), float(b["y"]), 4.0):
                self.bits.remove(b)
                self.add_score(10)
                self.play_sound("score")

        for p in self.power_pills[:]:
            if check_circle_collision(self.px, self.py, 8.0, float(p["x"]), float(p["y"]), 6.0):
                self.power_pills.remove(p)
                self.overclock_timer = self.pill_duration
                self.add_score(100)
                self.play_sound("confirm")

    def _player_distances(self) -> dict[tuple[int, int], int]:
        tile = self.ptile
        if tile != self._player_dist_tile:
            self._player_dist = _distance_map(tile)
            self._player_dist_tile = tile
        return self._player_dist

    def _choose_next_tile(self, ph: dict) -> tuple[int, int] | None:
        current = _tile_of(ph["x"], ph["y"])
        options = _open_neighbors(current)
        if not options:
            return None

        distances = self._player_distances()
        known = [t for t in options if t in distances]
        fleeing = self.overclock_timer > 0
        hunting = not fleeing and self.rng.random() < self.chase_chance

        if fleeing and known:
            best = max(distances[t] for t in known)
            pool = [t for t in known if distances[t] == best]
        elif hunting and known:
            best = min(distances[t] for t in known)
            pool = [t for t in known if distances[t] == best]
        else:
            reverse = (current[0] - ph["dx"], current[1] - ph["dy"])
            pool = [t for t in options if t != reverse] or options
        return self.rng.choice(pool)

    def _move_phantom(self, ph: dict, step: float) -> None:
        if ph["target"] is None:
            target = self._choose_next_tile(ph)
            if target is None:
                return
            current = _tile_of(ph["x"], ph["y"])
            ph["dx"], ph["dy"] = target[0] - current[0], target[1] - current[1]
            ph["target"] = target

        tx, ty = _tile_center(ph["target"])
        remaining = step
        for axis, goal in (("x", tx), ("y", ty)):
            diff = goal - ph[axis]
            if abs(diff) > 1e-6:
                move = min(abs(diff), remaining)
                ph[axis] += math.copysign(move, diff)
                remaining -= move

        if abs(tx - ph["x"]) < 1e-6 and abs(ty - ph["y"]) < 1e-6:
            ph["x"], ph["y"] = tx, ty
            ph["target"] = None

    def _update_phantoms(self, dt: float) -> None:
        fleeing = self.overclock_timer > 0
        speed = 30.0 if fleeing else self.phantom_speed
        for index, ph in enumerate(self.phantoms):
            self._move_phantom(ph, speed * dt)
            if not check_circle_collision(self.px, self.py, 8.0, ph["x"], ph["y"], 8.0):
                continue
            if fleeing:
                self.phantoms[index] = self._make_phantom(index)
                self.add_score(300)
                self.play_sound("confirm")
            elif self.invulnerable_timer <= 0:
                self._lose_life()
                break

    def _lose_life(self) -> None:
        self.lives -= 1
        self.play_sound("hit")
        if self.lives <= 0:
            self.game_over = True
            self.play_sound("gameover")
            return
        self._reset_player()
        self.invulnerable_timer = SPAWN_INVULNERABILITY
        self._reset_phantoms()

    def _advance_level(self) -> None:
        self.add_score(1000)
        self.play_sound("confirm")
        if self.level >= MAX_LEVELS:
            self.game_won = True
            return
        self.level += 1
        self._setup_level()
        self.banner_timer = 2.0

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 10, 22))
        self._draw_grid(surface)
        self._draw_walls(surface)

        for b in self.bits:
            pygame.draw.circle(surface, (255, 215, 0), (int(b["x"]), int(b["y"])), 2)

        self._draw_power_pills(surface)
        for ph in self.phantoms:
            self._draw_phantom(surface, ph)
        self._draw_player(surface)
        self._draw_hud(surface)

        if self.banner_timer > 0:
            banner = self.title_font.render(f"SECTOR {self.level} ONLINE", True, (255, 215, 0))
            surface.blit(banner, (160 - banner.get_width() // 2, 110))

        self.render_ui(surface)

    def _draw_glow(self, surface: pygame.Surface, center: tuple[int, int], radius: int, color: tuple[int, int, int]) -> None:
        key = (radius, color)
        glow = _GLOW_CACHE.get(key)
        if glow is None:
            glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*color, 55), (radius, radius), radius)
            _GLOW_CACHE[key] = glow
        surface.blit(glow, (center[0] - radius, center[1] - radius))

    def _draw_grid(self, surface: pygame.Surface) -> None:
        grid_color = (14, 18, 36)
        left, top = ORIGIN_X, ORIGIN_Y
        right = ORIGIN_X + GRID_COLS * TILE_SIZE
        bottom = ORIGIN_Y + GRID_ROWS * TILE_SIZE
        for col in range(GRID_COLS + 1):
            x = left + col * TILE_SIZE
            pygame.draw.line(surface, grid_color, (x, top), (x, bottom))
        for row in range(GRID_ROWS + 1):
            y = top + row * TILE_SIZE
            pygame.draw.line(surface, grid_color, (left, y), (right, y))

    def _draw_walls(self, surface: pygame.Surface) -> None:
        pulse = (math.sin(pygame.time.get_ticks() / 400.0) + 1.0) / 2.0
        edge = (0, int(190 + 65 * pulse), 255)
        for w in self.walls:
            pygame.draw.rect(surface, (0, 90, 170), w, border_radius=3)
            pygame.draw.rect(surface, edge, w, 1, border_radius=3)

    def _draw_power_pills(self, surface: pygame.Surface) -> None:
        pulse = (math.sin(pygame.time.get_ticks() / 150.0) + 1.0) / 2.0
        radius = 4 + int(2 * pulse)
        for p in self.power_pills:
            center = (int(p["x"]), int(p["y"]))
            self._draw_glow(surface, center, 10, (0, 255, 200))
            pygame.draw.circle(surface, (0, 255, 200), center, radius)
            pygame.draw.circle(surface, (255, 255, 255), center, max(1, radius - 3))

    def _draw_phantom(self, surface: pygame.Surface, ph: dict) -> None:
        fleeing = self.overclock_timer > 0
        if fleeing:
            flashing = self.overclock_timer < 2.0 and int(pygame.time.get_ticks() / 150) % 2 == 0
            color = (255, 255, 255) if flashing else (50, 100, 255)
        else:
            color = ph["color"]

        cx, cy = int(ph["x"]), int(ph["y"])
        self._draw_glow(surface, (cx, cy), 11, color)
        pygame.draw.circle(surface, color, (cx, cy - 1), 7)
        pygame.draw.rect(surface, color, (cx - 7, cy - 1, 14, 8))
        for i in range(3):
            pygame.draw.circle(surface, color, (cx - 5 + i * 5, cy + 7), 2)

        pupil_dx, pupil_dy = ph["dx"], ph["dy"]
        for ex in (cx - 3, cx + 3):
            pygame.draw.circle(surface, (255, 255, 255), (ex, cy - 2), 3)
            pygame.draw.circle(surface, (20, 20, 60), (ex + pupil_dx, cy - 2 + pupil_dy), 1)

    def _draw_player(self, surface: pygame.Surface) -> None:
        if self.invulnerable_timer > 0 and int(pygame.time.get_ticks() / 100) % 2 == 1:
            return

        cx, cy = int(self.px), int(self.py)
        moving = self.ptarget is not None
        mouth = 0.15 + 0.5 * abs(math.sin(self.chomp_timer * 10.0)) if moving else 0.12
        radius = 8

        self._draw_glow(surface, (cx, cy), 12, (255, 255, 0))
        start = self.facing + mouth
        end = self.facing + 2 * math.pi - mouth
        points = [(cx, cy)]
        steps = 14
        for i in range(steps + 1):
            angle = start + (end - start) * i / steps
            points.append((int(cx + radius * math.cos(angle)), int(cy + radius * math.sin(angle))))
        pygame.draw.polygon(surface, (255, 255, 0), points)

        eye_angle = self.facing - math.pi / 2
        eye = (int(cx + 3.5 * math.cos(eye_angle)), int(cy + 3.5 * math.sin(eye_angle)))
        pygame.draw.circle(surface, (20, 20, 0), eye, 1)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (12, 15, 28), (10, 215, 300, 20), border_radius=4)
        oc_text = " | OVERCLOCK!" if self.overclock_timer > 0 else ""
        hud = self.font.render(
            f"LIVES: {self.lives} | SECTOR: {self.level}/{MAX_LEVELS} | DATA: {len(self.bits)}{oc_text}",
            True,
            (0, 255, 200),
        )
        surface.blit(hud, (160 - hud.get_width() // 2, 218))

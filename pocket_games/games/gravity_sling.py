# ==========================================
# GRAVITY SLING v1.3
# Actively pilot your space probe through gravity-dense star systems.
# Utilize full 4-way vector thrusters for precision control while
# leveraging planetary gravitational pull to perform slingshot maneuvers.
# Levels, planets, crystals and starfields are seeded, so every run is identical.
# ==========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.core.physics import calculate_orbital_pull, check_circle_collision
from pocket_games.games.base import BaseGame

MAX_LEVELS = 3
LEVEL_TIME = 40.0
SPAWN_POS = (50.0, 120.0)
LEVEL_SEED_BASE = 4099
BACKGROUND_SEED = 2024
EFFECT_SEED = 77
NEBULA_COLORS = ((70, 25, 120), (25, 55, 120), (120, 35, 75))


def _planet(
    x: int,
    y: int,
    r: int,
    gravity_r: int,
    color: tuple[int, int, int],
    strength: float,
    kind: str,
    seed: int,
    ring: bool = False,
) -> dict:
    return {
        "x": x,
        "y": y,
        "r": r,
        "gravity_r": gravity_r,
        "color": color,
        "strength": strength,
        "kind": kind,
        "seed": seed,
        "ring": ring,
    }


PLANET_CONFIGS = (
    (
        _planet(160, 125, 24, 74, (60, 130, 230), 9000.0, "ocean", 11),
    ),
    (
        _planet(100, 92, 14, 52, (170, 160, 150), 6000.0, "rocky", 23),
        _planet(218, 150, 21, 76, (230, 120, 70), 10500.0, "gas", 37, ring=True),
    ),
    (
        _planet(82, 78, 12, 46, (190, 230, 255), 5200.0, "ice", 41),
        _planet(236, 84, 17, 62, (235, 170, 90), 8800.0, "gas", 53),
        _planet(160, 168, 26, 86, (180, 70, 200), 14000.0, "volcanic", 67),
    ),
)


def _clamp_channel(value: float) -> int:
    return max(0, min(255, int(value)))


class GravitySlingGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Gravity Sling")
        self.px, self.py = SPAWN_POS
        self.vx, self.vy = 0.0, 0.0
        self.thrust_x, self.thrust_y = 0.0, 0.0
        self.lives = 3
        self.level = 1
        self.crystals_collected = 0
        self.rest_timer = 0.0
        self.invulnerable_timer = 0.0
        self.time_left = LEVEL_TIME
        self.planets: list[dict] = []
        self.crystals: list[dict] = []
        self.particles: list[dict] = []
        self.stars: list[tuple[int, int, float]] = []
        self.background: pygame.Surface | None = None
        self.effect_rng = random.Random(EFFECT_SEED)
        self._probe_glow = self._make_probe_glow()
        self._setup_level()

    def _setup_level(self) -> None:
        self.time_left = LEVEL_TIME
        self.particles = []
        cfg_idx = min(self.level - 1, len(PLANET_CONFIGS) - 1)
        self.planets = [dict(p) for p in PLANET_CONFIGS[cfg_idx]]
        self._build_background(self.level)
        self._spawn_crystal()

    def _spawn_crystal(self) -> None:
        rng = random.Random(LEVEL_SEED_BASE + self.level * 100 + self.crystals_collected)
        self.crystals = []
        while True:
            cx = rng.randint(40, 280)
            cy = rng.randint(50, 190)
            if check_circle_collision(cx, cy, 0.0, SPAWN_POS[0], SPAWN_POS[1], 40.0):
                continue
            valid = True
            for p in self.planets:
                if check_circle_collision(
                    cx, cy, 0.0, float(p["x"]), float(p["y"]), float(p["r"] + 25)
                ):
                    valid = False
                    break
            if valid:
                self.crystals.append({"x": cx, "y": cy})
                break

    def _build_background(self, level: int) -> None:
        rng = random.Random(BACKGROUND_SEED + level)
        bg = pygame.Surface((320, 240))
        for y in range(240):
            t = y / 239.0
            pygame.draw.line(bg, (4 + int(10 * t), 6 + int(6 * t), 20 + int(18 * t)), (0, y), (319, y))

        nebula = pygame.Surface((320, 240), pygame.SRCALPHA)
        for _ in range(4):
            cx, cy = rng.randint(0, 319), rng.randint(0, 239)
            radius = rng.randint(45, 95)
            col = rng.choice(NEBULA_COLORS)
            for k in range(radius, 0, -5):
                alpha = int(3 + 34 * (1 - k / radius))
                pygame.draw.circle(nebula, (*col, alpha), (cx, cy), k)
        bg.blit(nebula, (0, 0))

        big_x = rng.choice((rng.randint(-40, 10), rng.randint(310, 350)))
        big_y = rng.randint(30, 210)
        big_r = rng.randint(50, 80)
        big_col = rng.choice(PLANET_CONFIGS[0])["color"]
        pygame.draw.circle(bg, tuple(int(c * 0.2) for c in big_col), (big_x, big_y), big_r)
        pygame.draw.circle(bg, tuple(int(c * 0.35) for c in big_col), (big_x, big_y), big_r, 1)

        self.stars = []
        for count, low, high in ((80, 40, 90), (40, 100, 160), (14, 190, 255)):
            for _ in range(count):
                x, y = rng.randrange(320), rng.randrange(240)
                b = rng.randint(low, high)
                color = (b, b, min(255, b + 25))
                if high > 180:
                    pygame.draw.circle(bg, color, (x, y), 1)
                    pygame.draw.line(bg, (b // 3, b // 3, b // 2), (x - 3, y), (x + 3, y))
                    self.stars.append((x, y, rng.uniform(0.0, 6.28)))
                else:
                    bg.set_at((x, y), color)
        self.background = bg

    def _make_probe_glow(self) -> pygame.Surface:
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        for k in range(14, 0, -1):
            alpha = int(110 * (1 - (k - 1) / 14) ** 1.5)
            pygame.draw.circle(surf, (255, 200, 60, alpha), (16, 16), k)
        return surf

    def handle_damage(self) -> None:
        if self.invulnerable_timer > 0.0:
            return
        self.lives -= 1
        self.play_sound("hit")
        self._burst(self.px, self.py, (255, 110, 70), 18, speed=110.0)
        if self.lives <= 0:
            self.game_over = True
            self.play_sound("gameover")
        else:
            self.px, self.py = SPAWN_POS
            self.vx, self.vy = 0.0, 0.0
            self.invulnerable_timer = 1.5

    def _burst(self, x: float, y: float, color: tuple[int, int, int], count: int, speed: float = 60.0) -> None:
        for _ in range(count):
            angle = self.effect_rng.uniform(0.0, 2 * math.pi)
            magnitude = self.effect_rng.uniform(0.3, 1.0) * speed
            life = self.effect_rng.uniform(0.35, 0.7)
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(angle) * magnitude,
                    "vy": math.sin(angle) * magnitude,
                    "life": life,
                    "max_life": life,
                    "color": color,
                    "size": self.effect_rng.choice((1, 2, 2, 3)),
                }
            )

    def handle_input(self) -> None:
        super().handle_input()
        self.thrust_x, self.thrust_y = 0.0, 0.0
        if self.game_over or self.rest_timer > 0:
            return

        inp = self.engine.input
        thrust = 190.0
        dt = 0.016

        if inp.is_left_pressed():
            self.thrust_x -= 1.0
        if inp.is_right_pressed():
            self.thrust_x += 1.0
        if inp.is_up_pressed():
            self.thrust_y -= 1.0
        if inp.is_down_pressed():
            self.thrust_y += 1.0

        self.vx += self.thrust_x * thrust * dt
        self.vy += self.thrust_y * thrust * dt

        if (self.thrust_x != 0 or self.thrust_y != 0) and self.effect_rng.random() < 0.6:
            self.particles.append(
                {
                    "x": self.px,
                    "y": self.py,
                    "vx": -self.thrust_x * 90.0 + self.effect_rng.uniform(-15, 15),
                    "vy": -self.thrust_y * 90.0 + self.effect_rng.uniform(-15, 15),
                    "life": 0.3,
                    "max_life": 0.3,
                    "color": (255, self.effect_rng.randint(160, 220), 50),
                    "size": 2,
                }
            )

    def _update_particles(self, dt: float) -> None:
        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vx"] *= max(0.0, 1.0 - 2.5 * dt)
            p["vy"] *= max(0.0, 1.0 - 2.5 * dt)
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        if self.rest_timer > 0:
            self.rest_timer -= dt
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self.handle_damage()
            self.time_left = LEVEL_TIME
            return

        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer -= dt

        self._update_particles(dt)

        for p in self.planets:
            if self.invulnerable_timer <= 0.0 and check_circle_collision(
                self.px, self.py, 3.0, float(p["x"]), float(p["y"]), float(p["r"] - 2)
            ):
                self.handle_damage()
                return

            fx, fy = calculate_orbital_pull(
                self.px, self.py, float(p["x"]), float(p["y"]), strength=p["strength"]
            )
            self.vx += fx * dt
            self.vy += fy * dt

        self.vx *= 0.985
        self.vy *= 0.985

        self.px += self.vx * dt
        self.py += self.vy * dt

        for c in self.crystals[:]:
            if check_circle_collision(
                self.px, self.py, 6.0, float(c["x"]), float(c["y"]), 10.0
            ):
                self.crystals.remove(c)
                self.add_score(50 * self.level)
                self.crystals_collected += 1
                self._burst(c["x"], c["y"], (0, 255, 200), 14, speed=80.0)
                self.play_sound("score")

                if self.crystals_collected >= 4 and self.level < MAX_LEVELS:
                    self.level += 1
                    self.crystals_collected = 0
                    self.rest_timer = 2.0
                    self.play_sound("confirm")
                    self.px, self.py = SPAWN_POS
                    self.vx, self.vy = 0.0, 0.0
                    self._setup_level()
                else:
                    self._spawn_crystal()

        if (
            self.px < 5 or self.px > 315 or self.py < 25 or self.py > 235
        ) and self.invulnerable_timer <= 0.0:
            self.handle_damage()

    def _planet_surface_color(
        self,
        kind: str,
        color: tuple[int, int, int],
        dx: float,
        dy: float,
        phases: tuple[float, float, float],
        craters: list[tuple[float, float, float]],
    ) -> tuple[int, int, int, bool]:
        ph1, ph2, ph3 = phases
        r, g, b = color
        if kind == "gas":
            band = 0.5 + 0.5 * math.sin(dy * 7.0 + ph1 + 0.6 * math.sin(dx * 3.0 + ph2))
            f = 0.72 + 0.4 * band
            return _clamp_channel(r * f), _clamp_channel(g * f), _clamp_channel(b * f), False
        if kind == "ocean":
            if abs(dy) > 0.82:
                return 235, 242, 255, False
            land = math.sin(dx * 4.2 + ph1) * math.cos(dy * 3.7 + ph2) + 0.45 * math.sin(dx * 9.0 + dy * 7.0 + ph3)
            if land > 0.45:
                return 70, 150, 80, False
            return r, g, b, False
        if kind == "rocky":
            for cx, cy, cr in craters:
                if (dx - cx) ** 2 + (dy - cy) ** 2 < cr * cr:
                    return int(r * 0.55), int(g * 0.55), int(b * 0.55), False
            return r, g, b, False
        if kind == "ice":
            f = 0.92 + 0.08 * math.sin(dx * 11.0 + ph1) * math.sin(dy * 9.0 + ph2)
            mix = min(1.0, max(0.0, (abs(dy) - 0.6) * 2.5))
            return (
                _clamp_channel(r * f + (255 - r * f) * mix),
                _clamp_channel(g * f + (255 - g * f) * mix),
                _clamp_channel(b * f + (255 - b * f) * mix),
                False,
            )
        crack = abs(math.sin(dx * 6.0 + dy * 4.0 + ph1) + 0.7 * math.cos(dy * 5.0 + ph2))
        if crack < 0.12:
            return 255, 150, 50, True
        return int(r * 0.6), int(g * 0.6), int(b * 0.6), False

    def _build_planet_sprite(self, p: dict) -> pygame.Surface:
        r = p["r"]
        color = p["color"]
        ring = p.get("ring", False)
        extent = int(r * 1.9) + 6 if ring else r + 7
        size = extent * 2
        center = extent
        surf = pygame.Surface((size, size), pygame.SRCALPHA)

        for k in range(7, 0, -1):
            alpha = int(60 * (1 - (k - 1) / 7))
            pygame.draw.circle(surf, (*color, alpha), (center, center), r + k)

        rng = random.Random(p["seed"])
        phases = (rng.uniform(0, 2 * math.pi), rng.uniform(0, 2 * math.pi), rng.uniform(0, 2 * math.pi))
        craters = [
            (rng.uniform(-0.55, 0.55), rng.uniform(-0.55, 0.55), rng.uniform(0.07, 0.16))
            for _ in range(6)
        ]
        light = (-0.4767, -0.5722, 0.6677)
        for iy in range(size):
            for ix in range(size):
                dx = (ix - center + 0.5) / r
                dy = (iy - center + 0.5) / r
                d2 = dx * dx + dy * dy
                if d2 > 1.0:
                    continue
                nz = math.sqrt(1.0 - d2)
                diffuse = max(0.0, dx * light[0] + dy * light[1] + nz * light[2])
                shade = 0.14 + 0.86 * diffuse
                red, green, blue, emissive = self._planet_surface_color(
                    p["kind"], color, dx, dy, phases, craters
                )
                if not emissive:
                    red, green, blue = (_clamp_channel(red * shade), _clamp_channel(green * shade), _clamp_channel(blue * shade))
                surf.set_at((ix, iy), (red, green, blue, 255))

        if ring:
            rx, ry = int(r * 1.9), int(r * 0.42)
            rect = pygame.Rect(center - rx, center - ry, rx * 2, ry * 2)
            pygame.draw.ellipse(surf, (230, 210, 170, 150), rect, 2)
            pygame.draw.ellipse(surf, (200, 180, 150, 90), rect.inflate(-6, -4), 1)
        return surf

    def _build_field(self, p: dict) -> pygame.Surface:
        gr = p["gravity_r"]
        surf = pygame.Surface((gr * 2 + 4, gr * 2 + 4), pygame.SRCALPHA)
        rect = pygame.Rect(2, 2, gr * 2, gr * 2)
        segments = 24
        for i in range(0, segments, 2):
            start = i * 2 * math.pi / segments
            pygame.draw.arc(surf, (*p["color"], 55), rect, start, start + 2 * math.pi / segments, 1)
        return surf

    def _draw_planet(self, surface: pygame.Surface, p: dict) -> None:
        if "field" not in p:
            p["field"] = self._build_field(p)
        if "sprite" not in p:
            p["sprite"] = self._build_planet_sprite(p)
        center = (int(p["x"]), int(p["y"]))
        surface.blit(p["field"], p["field"].get_rect(center=center))
        surface.blit(p["sprite"], p["sprite"].get_rect(center=center))

    def _draw_crystal(self, surface: pygame.Surface, c: dict) -> None:
        ticks = pygame.time.get_ticks() / 1000.0
        pulse = 0.5 + 0.5 * math.sin(ticks * 4.0 + c["x"] * 0.1)
        cx, cy = int(c["x"]), int(c["y"])
        pygame.draw.circle(surface, (0, int(60 + 50 * pulse), int(70 + 50 * pulse)), (cx, cy), int(9 + 3 * pulse))
        diamond = [(cx, cy - 7), (cx + 6, cy), (cx, cy + 7), (cx - 6, cy)]
        pygame.draw.polygon(surface, (0, 255, 200), diamond)
        pygame.draw.polygon(surface, (200, 255, 245), diamond, 1)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 2, cy - 2), 1)

    def _draw_flame(self, surface: pygame.Surface, px: int, py: int) -> None:
        dx, dy = -self.thrust_x, -self.thrust_y
        norm = math.hypot(dx, dy) or 1.0
        dx, dy = dx / norm, dy / norm
        nx, ny = -dy, dx
        length = 12 + 4 * abs(math.sin(pygame.time.get_ticks() / 60.0))
        base_x, base_y = px + dx * 6, py + dy * 6
        outer = [
            (base_x + nx * 3, base_y + ny * 3),
            (base_x + dx * length, base_y + dy * length),
            (base_x - nx * 3, base_y - ny * 3),
        ]
        inner_len = length * 0.6
        inner = [
            (base_x + nx * 1.5, base_y + ny * 1.5),
            (base_x + dx * inner_len, base_y + dy * inner_len),
            (base_x - nx * 1.5, base_y - ny * 1.5),
        ]
        pygame.draw.polygon(surface, (255, 120, 30), [(int(x), int(y)) for x, y in outer])
        pygame.draw.polygon(surface, (255, 240, 160), [(int(x), int(y)) for x, y in inner])

    def _draw_probe(self, surface: pygame.Surface) -> None:
        if self.invulnerable_timer > 0 and int(pygame.time.get_ticks() / 100) % 2 == 1:
            return
        px, py = int(self.px), int(self.py)
        if self.thrust_x != 0 or self.thrust_y != 0:
            self._draw_flame(surface, px, py)
        surface.blit(self._probe_glow, self._probe_glow.get_rect(center=(px, py)))
        pygame.draw.circle(surface, (255, 215, 0), (px, py), 6)
        pygame.draw.circle(surface, (255, 245, 200), (px - 1, py - 1), 3)
        pygame.draw.circle(surface, (255, 255, 255), (px, py), 2)

    def _draw_particle(self, surface: pygame.Surface, p: dict) -> None:
        fade = max(0.0, p["life"] / p["max_life"])
        color = tuple(int(c * fade) for c in p["color"])
        size = max(1, int(p["size"] * fade + 0.5))
        pygame.draw.circle(surface, color, (int(p["x"]), int(p["y"])), size)

    def _draw_twinkle(self, surface: pygame.Surface) -> None:
        ticks = pygame.time.get_ticks() / 1000.0
        for x, y, phase in self.stars:
            b = int(150 + 105 * (0.5 + 0.5 * math.sin(ticks * 2.0 + phase)))
            surface.set_at((x, y), (b, b, min(255, b + 25)))

    def render(self, surface: pygame.Surface) -> None:
        if self.background is None:
            self._build_background(self.level)
        surface.blit(self.background, (0, 0))
        self._draw_twinkle(surface)

        for p in self.planets:
            self._draw_planet(surface, p)

        for c in self.crystals:
            self._draw_crystal(surface, c)

        for p in self.particles:
            self._draw_particle(surface, p)

        self._draw_probe(surface)

        panel = pygame.Surface((300, 20), pygame.SRCALPHA)
        panel.fill((10, 14, 30, 200))
        pygame.draw.line(panel, (0, 255, 200, 90), (0, 0), (299, 0))
        surface.blit(panel, (10, 215))

        info_txt = self.font.render(
            f"L: {self.lives} | SEC: {self.level} | GEMS: {self.crystals_collected}/4 | TIME: {max(0, int(self.time_left))}s",
            True,
            (0, 255, 200),
        )
        surface.blit(info_txt, (160 - info_txt.get_width() // 2, 218))

        if self.rest_timer > 0:
            rest_txt = self.title_font.render(
                f"ENTERING SECTOR {self.level}...", True, (255, 215, 0)
            )
            shadow = self.title_font.render(
                f"ENTERING SECTOR {self.level}...", True, (0, 0, 0)
            )
            x = 160 - rest_txt.get_width() // 2
            surface.blit(shadow, (x + 1, 111))
            surface.blit(rest_txt, (x, 110))

        self.render_ui(surface)

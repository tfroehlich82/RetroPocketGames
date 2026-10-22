# ==========================================
# SUB ZERO MINER v1.1
# An immersive survival adventure in freezing depths.
# Navigate the miner through frosty ice caves, collect valuable diamonds
# and oxygen bubbles while avoiding treacherous ice hazards and toxic spores.
# Atmospheric ice cave visuals with stalactites and a continuously
# depleting oxygen supply deliver engaging survival gameplay.
# =========================================
from __future__ import annotations

import math
import random

import pygame

from pocket_games.core.physics import check_circle_collision, clamp
from pocket_games.games.base import BaseGame


class SubZeroMinerGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Sub-Zero Miner")
        self.rx, self.ry = 160.0, 120.0
        self.oxygen = 100.0
        self.level = 1
        self.gems: list[dict] = []
        self.hazards: list[dict] = []
        self.toxic_spores: list[dict] = []
        self.reset_level()

    def reset_level(self) -> None:
        self.rx, self.ry = 160.0, 120.0
        safety_margin = 14.0  # Mindestabstand zwischen den Objekten

        # Ice Hazards mit Kollisions- und Mindestabstandsprüfung generieren
        self.hazards = []
        while len(self.hazards) < 3:
            hx = random.randint(50, 270)
            hy = random.randint(50, 190)
            hr = 16

            # Abstand zum Startbereich (160, 120) einhalten
            if (hx - 160) ** 2 + (hy - 120) ** 2 <= (hr + 40) ** 2:
                continue

            # Abstand zu bereits platzierten Hazards prüfen
            valid = True
            for h in self.hazards:
                if (hx - h["x"]) ** 2 + (hy - h["y"]) ** 2 < (
                    hr + h["r"] + safety_margin
                ) ** 2:
                    valid = False
                    break

            if valid:
                self.hazards.append({"x": hx, "y": hy, "r": hr})

        # Toxic Spores Hazards
        self.toxic_spores = []
        while len(self.toxic_spores) < 2 + min(self.level, 3):
            tx = random.randint(40, 280)
            ty = random.randint(40, 200)
            tr = 12

            if (tx - 160) ** 2 + (ty - 120) ** 2 <= (tr + 35) ** 2:
                continue

            valid = True
            for obj in self.hazards + self.toxic_spores:
                if (tx - obj["x"]) ** 2 + (ty - obj["y"]) ** 2 < (
                    tr + obj["r"] + safety_margin
                ) ** 2:
                    valid = False
                    break

            if valid:
                self.toxic_spores.append(
                    {"x": tx, "y": ty, "r": tr, "pulse": random.uniform(0, math.pi)}
                )

        # Gems / O2 Bubbles
        self.gems = []
        gem_radius = 6
        for _ in range(4):
            while True:
                gx = random.randint(40, 280)
                gy = random.randint(40, 200)

                valid = True
                for h in self.hazards + self.toxic_spores:
                    if check_circle_collision(
                        float(gx),
                        float(gy),
                        float(gem_radius),
                        float(h["x"]),
                        float(h["y"]),
                        float(h["r"] + 6),
                    ):
                        valid = False
                        break

                if valid:
                    self.gems.append({"x": gx, "y": gy, "val": 30})
                    break

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active or self.game_over:
            return

        inp = self.engine.input
        speed = 110.0
        dt = 0.016

        dx, dy = 0.0, 0.0
        if inp.is_left_pressed():
            dx -= speed * dt
        if inp.is_right_pressed():
            dx += speed * dt
        if inp.is_up_pressed():
            dy -= speed * dt
        if inp.is_down_pressed():
            dy += speed * dt

        new_x = clamp(self.rx + dx, 25.0, 295.0)
        new_y = clamp(self.ry + dy, 40.0, 215.0)

        collides = False
        for h in self.hazards:
            if check_circle_collision(
                new_x, new_y, 8.0, float(h["x"]), float(h["y"]), float(h["r"])
            ):
                collides = True
                self.oxygen -= dt * 12.0
                break

        for ts in self.toxic_spores:
            if check_circle_collision(
                new_x, new_y, 8.0, float(ts["x"]), float(ts["y"]), float(ts["r"])
            ):
                collides = True
                self.oxygen -= dt * 35.0
                break

        if not collides:
            self.rx, self.ry = new_x, new_y

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        drain_rate = 5.0 + (self.level * 1.8)
        self.oxygen -= dt * drain_rate

        if self.oxygen <= 0:
            self.game_over = True
            self.play_sound("gameover")
            return

        for ts in self.toxic_spores:
            ts["pulse"] += dt * 5

        for g in self.gems[:]:
            if check_circle_collision(
                self.rx, self.ry, 6.0, float(g["x"]), float(g["y"]), 6.0
            ):
                self.gems.remove(g)
                self.add_score(g["val"])
                self.oxygen = min(100.0, self.oxygen + 22.0)
                self.play_sound("score")

        if not self.gems:
            self.level += 1
            self.reset_level()

    def render(self, surface: pygame.Surface) -> None:
        # Eishöhlen-Hintergrund mit eisigen Farbverläufen und Fels-/Eisstrukturen
        surface.fill((12, 22, 38))

        # Dekorative Eiszapfen / Stalaktiten an der Decke
        pygame.draw.rect(surface, (20, 35, 55), (0, 0, 320, 32))
        for x in range(0, 320, 16):
            peak_h = 16 + (x % 3) * 6
            pygame.draw.polygon(
                surface, (30, 50, 75), [(x, 0), (x + 8, peak_h), (x + 16, 0)]
            )
            pygame.draw.polygon(
                surface,
                (150, 210, 255),
                [(x + 2, 0), (x + 8, peak_h - 4), (x + 6, 0)],
                1,
            )

        # Dekorative Eiszapfen / Stalagmiten am Boden
        pygame.draw.rect(surface, (20, 35, 55), (0, 212, 320, 28))
        for x in range(8, 320, 20):
            peak_h = 212 - (x % 4) * 5
            pygame.draw.polygon(
                surface, (30, 50, 75), [(x, 240), (x + 10, peak_h), (x + 20, 240)]
            )
            pygame.draw.polygon(
                surface,
                (150, 210, 255),
                [(x + 4, 240), (x + 10, peak_h + 4), (x + 16, 240)],
                1,
            )

        # Kristallstrukturen / Risse im Hintergrund
        pygame.draw.line(surface, (22, 42, 68), (60, 40), (100, 90), 2)
        pygame.draw.line(surface, (22, 42, 68), (100, 90), (80, 140), 2)
        pygame.draw.line(surface, (22, 42, 68), (240, 50), (200, 110), 2)
        pygame.draw.line(surface, (22, 42, 68), (200, 110), (230, 170), 2)

        # Eis-Hazards (mit funkelnden Eiskristallen)
        for h in self.hazards:
            pygame.draw.circle(
                surface, (110, 200, 255), (int(h["x"]), int(h["y"])), h["r"]
            )
            pygame.draw.circle(
                surface, (200, 240, 255), (int(h["x"]), int(h["y"])), h["r"] - 4, 1
            )
            hx, hy = int(h["x"]), int(h["y"])
            pygame.draw.line(surface, (255, 255, 255), (hx - 6, hy), (hx + 6, hy), 1)
            pygame.draw.line(surface, (255, 255, 255), (hx, hy - 6), (hx, hy + 6), 1)

        # Giftige Sporen
        for ts in self.toxic_spores:
            tx, ty = int(ts["x"]), int(ts["y"])
            glow = int(4 + math.sin(ts["pulse"]) * 3)
            pygame.draw.circle(surface, (160, 30, 200), (tx, ty), ts["r"] + glow)
            pygame.draw.circle(surface, (220, 100, 255), (tx, ty), ts["r"])
            pygame.draw.circle(surface, (255, 255, 255), (tx, ty), 3)

        # Diamanten / Kristalle
        for g in self.gems:
            gx, gy = int(g["x"]), int(g["y"])
            pygame.draw.polygon(
                surface,
                (0, 240, 255),
                [(gx, gy - 7), (gx + 6, gy), (gx, gy + 7), (gx - 6, gy)],
            )
            pygame.draw.polygon(
                surface,
                (255, 255, 255),
                [(gx, gy - 5), (gx + 4, gy), (gx, gy + 5), (gx - 4, gy)],
                1,
            )

        # Spieler (Minenarbeiter)
        mx, my = int(self.rx), int(self.ry)
        pygame.draw.rect(
            surface, (255, 130, 0), (mx - 8, my - 8, 16, 16), border_radius=3
        )
        pygame.draw.rect(surface, (255, 255, 255), (mx - 3, my - 3, 6, 6))

        # UI & O2-Leiste mit neutralen Hintergründen für exzellente Lesbarkeit
        # Hintergrund für O2-Balken
        pygame.draw.rect(surface, (10, 15, 25, 200), (8, 221, 126, 16), border_radius=3)
        pygame.draw.rect(surface, (30, 40, 50), (10, 225, 120, 8), border_radius=2)
        o2_w = int(120 * (min(100.0, max(0.0, self.oxygen)) / 100.0))
        o2_col = (0, 220, 255) if self.oxygen > 30 else (255, 50, 50)
        if o2_w > 0:
            pygame.draw.rect(surface, o2_col, (10, 225, o2_w, 8), border_radius=2)

        # Neutraler Hintergrund für Depth Level (unten rechts)
        lvl_txt = self.font.render(f"DEPTH LVL {self.level}", True, (200, 220, 255))
        pygame.draw.rect(
            surface,
            (10, 15, 25, 200),
            (215, 218, lvl_txt.get_width() + 10, lvl_txt.get_height() + 6),
            border_radius=3,
        )
        surface.blit(lvl_txt, (220, 222))

        # Neutraler Hintergrund für Score (oben links über Basis-UI)
        score_bg_w = 90
        score_bg_h = 18
        pygame.draw.rect(
            surface, (10, 15, 25, 200), (6, 3, score_bg_w, score_bg_h), border_radius=3
        )

        self.render_ui(surface)

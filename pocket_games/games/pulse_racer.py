# ==========================================
# PULSE RACER (Highway Pursuit Edition)
# ==========================================
from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class PulseRacerGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Pulse Racer")
        self.rx = 160.0
        self.traffic: list[dict] = []
        self.spawn_timer = 0.0
        self.base_speed = 210.0
        self.distance_float = 0.0
        self.last_dist = 0
        self.road_scroll = 0.0

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active or self.game_over:
            return

        inp = self.engine.input
        dt = 0.016
        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            self.rx = max(80.0, self.rx - 180.0 * dt)
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            self.rx = min(240.0, self.rx + 180.0 * dt)

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        self.distance_float += self.base_speed * dt
        current_dist = int(self.distance_float)
        if current_dist > self.last_dist:
            diff = current_dist - self.last_dist
            self.last_dist = current_dist
            self.add_score(diff)

        self.road_scroll = (self.road_scroll + self.base_speed * dt) % 40

        self.spawn_timer += dt
        if self.spawn_timer > 0.75:
            self.spawn_timer = 0.0
            # Decide if it's an oncoming car or a slower vehicle ahead
            v_type = random.choice(["slower", "blocker", "fast_oncoming"])
            lane_x = float(random.choice([95, 160, 225]))

            if v_type == "fast_oncoming":
                # Spawns ahead and drives towards player faster
                self.traffic.append(
                    {
                        "x": lane_x,
                        "y": -30.0,
                        "speed": 130.0,
                        "type": "oncoming",
                        "color": (255, 50, 50),
                    }
                )
            elif v_type == "blocker":
                self.traffic.append(
                    {
                        "x": lane_x,
                        "y": -40.0,
                        "speed": 40.0,
                        "type": "blocker",
                        "color": (255, 180, 0),
                    }
                )
            else:
                self.traffic.append(
                    {
                        "x": lane_x,
                        "y": -40.0,
                        "speed": 80.0,
                        "type": "cruiser",
                        "color": (0, 200, 255),
                    }
                )

        # Update traffic
        for veh in self.traffic[:]:
            if veh["type"] == "oncoming":
                veh["y"] += (self.base_speed + veh["speed"]) * dt
            else:
                veh["y"] += (self.base_speed - veh["speed"]) * dt

            # Collision check with player (player at y = 185)
            if abs(veh["x"] - self.rx) < 14 and abs(veh["y"] - 185.0) < 18:
                self.game_over = True
                self.play_sound("gameover")

            if veh["y"] > 260 or veh["y"] < -60:
                self.traffic.remove(veh)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 12, 25))
        road_rect = pygame.Rect(70, 0, 180, 240)
        pygame.draw.rect(surface, (25, 25, 35), road_rect)

        # Lane dividers
        pygame.draw.line(surface, (255, 255, 255), (72, 0), (72, 240), 2)
        pygame.draw.line(surface, (255, 255, 255), (248, 0), (248, 240), 2)
        pygame.draw.line(surface, (100, 100, 120), (130, 0), (130, 240), 1)
        pygame.draw.line(surface, (100, 100, 120), (190, 0), (190, 240), 1)

        for y_pos in range(int(-40 + self.road_scroll), 240, 40):
            pygame.draw.line(
                surface, (255, 255, 255), (160, y_pos), (160, y_pos + 20), 2
            )

        # Player Car
        px, py = int(self.rx), 185
        pygame.draw.rect(
            surface, (0, 255, 180), (px - 10, py - 14, 20, 28), border_radius=5
        )
        pygame.draw.rect(
            surface, (255, 255, 255), (px - 6, py - 6, 12, 10), border_radius=2
        )
        # Tail lights
        pygame.draw.circle(surface, (255, 0, 0), (px - 7, py + 12), 2)
        pygame.draw.circle(surface, (255, 0, 0), (px + 7, py + 12), 2)

        # Traffic Vehicles
        for veh in self.traffic:
            vx, vy = int(veh["x"]), int(veh["y"])
            pygame.draw.rect(
                surface, veh["color"], (vx - 10, vy - 14, 20, 28), border_radius=5
            )
            pygame.draw.rect(surface, (50, 50, 50), (vx - 6, vy - 4, 12, 8))

        self.render_ui(surface)

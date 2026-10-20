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
        self.base_speed = (
            180.0  # Etwas angenehmere Startgeschwindigkeit für perfekte Synchronität
        )
        self.distance_float = 0.0
        self.last_dist = 0
        self.road_scroll = 0.0
        self.lanes = [100.0, 160.0, 220.0]

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active or self.game_over:
            return

        inp = self.engine.input
        dt = 0.016
        if inp.is_left_pressed():
            self.rx = max(80.0, self.rx - 190.0 * dt)
        if inp.is_right_pressed():
            self.rx = min(240.0, self.rx + 190.0 * dt)

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        # Sanfterer, synchroner Geschwindigkeitsanstieg
        current_base_speed = self.base_speed + (self.elapsed_time * 3.0)

        self.distance_float += current_base_speed * dt
        current_dist = int(self.distance_float)
        if current_dist > self.last_dist:
            diff = current_dist - self.last_dist
            self.last_dist = current_dist
            self.add_score(diff)

        # Straßen-Scrollen exakt synchron zur Fahrzeug-Vorwärtsgeschwindigkeit
        self.road_scroll = (self.road_scroll + current_base_speed * dt) % 40

        self.spawn_timer += dt
        spawn_interval = max(0.45, 2.2 - (self.elapsed_time * 0.03))

        if self.spawn_timer > spawn_interval:
            self.spawn_timer = 0.0
            v_type = random.choice(["slower", "blocker", "fast_oncoming", "speedy"])
            lane_idx = random.randint(0, 2)
            lane_x = self.lanes[lane_idx]

            if v_type == "fast_oncoming":
                self.traffic.append(
                    {
                        "lane": lane_idx,
                        "x": lane_x,
                        "target_x": lane_x,
                        "y": -30.0,
                        "speed": 110.0 + self.elapsed_time * 2.0,
                        "type": "oncoming",
                        "color": (255, 50, 50),
                    }
                )
            elif v_type == "blocker":
                self.traffic.append(
                    {
                        "lane": lane_idx,
                        "x": lane_x,
                        "target_x": lane_x,
                        "y": -40.0,
                        "speed": 30.0,
                        "type": "blocker",
                        "color": (255, 180, 0),
                    }
                )
            elif v_type == "speedy":
                self.traffic.append(
                    {
                        "lane": lane_idx,
                        "x": lane_x,
                        "target_x": lane_x,
                        "y": -40.0,
                        "speed": 95.0 + self.elapsed_time * 2.5,
                        "type": "cruiser",
                        "color": (50, 255, 120),
                    }
                )
            else:
                self.traffic.append(
                    {
                        "lane": lane_idx,
                        "x": lane_x,
                        "target_x": lane_x,
                        "y": -40.0,
                        "speed": 65.0,
                        "type": "cruiser",
                        "color": (0, 200, 255),
                    }
                )

        for veh in self.traffic[:]:
            if veh["type"] != "oncoming":
                for other in self.traffic:
                    if other != veh and other["type"] != "oncoming":
                        dist = other["y"] - veh["y"]
                        if 0 < dist < 90 and abs(other["x"] - veh["x"]) < 22:
                            candidates = [
                                veh["x"] - 30.0,
                                veh["x"] + 30.0,
                                veh["x"] - 60.0,
                                veh["x"] + 60.0,
                            ]
                            valid_candidates = []
                            for cand in candidates:
                                if 80.0 <= cand <= 240.0:
                                    path_blocked = False
                                    for t_check in self.traffic:
                                        if (
                                            t_check != veh
                                            and abs(t_check["x"] - cand) < 20
                                            and abs(t_check["y"] - veh["y"]) < 45
                                        ):
                                            path_blocked = True
                                            break
                                    if not path_blocked:
                                        valid_candidates.append(cand)

                            if valid_candidates:
                                veh["target_x"] = random.choice(valid_candidates)
                            else:
                                veh["speed"] = max(10.0, other["speed"] - 2.0)

            if "target_x" not in veh:
                veh["target_x"] = veh["x"]

            if veh["x"] < veh["target_x"]:
                veh["x"] = min(veh["target_x"], veh["x"] + 140.0 * dt)
            elif veh["x"] > veh["target_x"]:
                veh["x"] = max(veh["target_x"], veh["x"] - 140.0 * dt)

            if veh["type"] == "oncoming":
                veh["y"] += (current_base_speed + veh["speed"]) * dt
            else:
                veh["y"] += (current_base_speed - veh["speed"]) * dt

            for other in self.traffic:
                if other != veh and (
                    abs(veh["x"] - other["x"]) < 18
                    and abs(veh["y"] - other["y"]) < 28
                ):
                    if veh["y"] < other["y"]:
                        veh["y"] = other["y"] - 30.0
                    else:
                        veh["y"] = other["y"] + 30.0

            if abs(veh["x"] - self.rx) < 14 and abs(veh["y"] - 185.0) < 18:
                self.game_over = True
                self.play_sound("gameover")

            if veh["y"] > 260 or veh["y"] < -60:
                self.traffic.remove(veh)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 12, 25))
        road_rect = pygame.Rect(70, 0, 180, 240)
        pygame.draw.rect(surface, (25, 25, 35), road_rect)

        pygame.draw.line(surface, (255, 255, 255), (70, 0), (70, 240), 2)
        pygame.draw.line(surface, (255, 255, 255), (250, 0), (250, 240), 2)

        # Fahrstreifen-Trennlinien bewegen sich exakt synchron mit road_scroll
        for y_pos in range(int(-40 + self.road_scroll), 240, 40):
            pygame.draw.line(
                surface, (255, 255, 255), (130, y_pos), (130, y_pos + 20), 2
            )
            pygame.draw.line(
                surface, (255, 255, 255), (190, y_pos), (190, y_pos + 20), 2
            )

        # Player Car
        px, py = int(self.rx), 185
        pygame.draw.rect(
            surface, (0, 255, 180), (px - 10, py - 14, 20, 28), border_radius=5
        )
        pygame.draw.rect(
            surface, (255, 255, 255), (px - 6, py - 6, 12, 10), border_radius=2
        )
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

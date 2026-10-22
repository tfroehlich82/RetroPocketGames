# ==========================================
# PULSE RACER v1.2
# A high-speed highway racing game featuring dynamic traffic.
# Dodge oncoming vehicles and road blockers, maintain your lane,
# and chase the ultimate highscore.
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
        self.pylons: list[dict] = []
        self.spawn_timer = 0.0
        self.pylon_spawn_timer = 0.0
        self.barrier_spawn_timer = 0.0
        self.base_speed = 180.0
        self.distance_float = 0.0
        self.last_dist = 0
        self.road_scroll = 0.0
        self.lanes = [100.0, 160.0, 220.0]
        self.dividers = [130.0, 190.0]

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

        current_base_speed = self.base_speed + (self.elapsed_time * 3.0)

        self.distance_float += current_base_speed * dt
        current_dist = int(self.distance_float)
        if current_dist > self.last_dist:
            diff = current_dist - self.last_dist
            self.last_dist = current_dist
            self.add_score(diff)

        self.road_scroll = (self.road_scroll + current_base_speed * dt) % 40

        self.pylon_spawn_timer += dt
        if self.pylon_spawn_timer >= 3.0:
            self.pylon_spawn_timer = 0.0
            p_x = random.choice(self.dividers)
            self.pylons.append({"x": p_x, "y": -20.0})

        for p in self.pylons[:]:
            p["y"] += current_base_speed * dt
            if abs(p["x"] - self.rx) < 12 and abs(p["y"] - 185.0) < 16:
                self.game_over = True
                self.play_sound("crash")
            if p["y"] > 260:
                self.pylons.remove(p)

        self.spawn_timer += dt
        spawn_interval = max(0.45, 2.2 - (self.elapsed_time * 0.03))

        if self.spawn_timer > spawn_interval:
            self.spawn_timer = 0.0
            v_type = random.choice(["slower", "blocker", "fast_oncoming", "speedy"])
            lane_idx = random.randint(0, 2)
            lane_x = self.lanes[lane_idx]

            base_veh = {
                "lane": lane_idx,
                "x": lane_x,
                "target_x": lane_x,
                "blinking": False,
                "blink_timer": 0.0,
                "decision_timer": random.uniform(1.0, 2.5),
            }

            if v_type == "fast_oncoming":
                base_veh.update({"y": -30.0, "speed": 110.0 + self.elapsed_time * 2.0, "type": "oncoming", "color": (255, 50, 50)})
            elif v_type == "blocker":
                base_veh.update({"y": -40.0, "net_speed_offset": 10.0, "type": "blocker", "color": (255, 180, 0)})
            elif v_type == "speedy":
                base_veh.update({"y": -65.0, "net_speed_offset": 25.0, "type": "speedy", "color": (50, 255, 120), "decision_timer": random.uniform(0.8, 1.8)})
            else:
                base_veh.update({"y": -40.0, "net_speed_offset": 70.0, "type": "cruiser", "color": (0, 200, 255)})

            self.traffic.append(base_veh)

        for veh in self.traffic[:]:
            if veh["type"] not in ["oncoming", "barrier"]:
                veh["decision_timer"] -= dt
                if veh["decision_timer"] <= 0:
                    veh["decision_timer"] = random.uniform(1.0, 2.0)
                    for other in self.traffic:
                        if other != veh and other["type"] not in ["oncoming", "barrier"] and (
                            abs(other["x"] - veh["x"]) < 12
                            and veh["y"] < other["y"]
                            and (other["y"] - veh["y"]) < 130
                        ) and veh.get("net_speed_offset", 50) < other.get("net_speed_offset", 50):
                            current_lane_idx = self.lanes.index(veh["x"]) if veh["x"] in self.lanes else 1
                            possible_lanes = []
                            if current_lane_idx > 0:
                                possible_lanes.append(current_lane_idx - 1)
                            if current_lane_idx < 2:
                                possible_lanes.append(current_lane_idx + 1)

                            if possible_lanes:
                                target_lane_idx = random.choice(possible_lanes)
                                target_x = self.lanes[target_lane_idx]

                                pylon_blocked = False
                                for p in self.pylons:
                                    if abs(p["y"] - veh["y"]) < 60 and (
                                        (veh["x"] < p["x"] < target_x) or (target_x < p["x"] < veh["x"])
                                    ):
                                        pylon_blocked = True
                                        break

                                lane_free = not pylon_blocked
                                for t_check in self.traffic:
                                    if abs(t_check["x"] - target_x) < 18 and abs(t_check["y"] - veh["y"]) < 90:
                                        lane_free = False
                                        break

                                if lane_free:
                                    veh["target_x"] = target_x
                                    veh["blinking"] = True
                                    veh["blink_timer"] = 1.0

            if veh["blinking"]:
                veh["blink_timer"] -= dt
                if veh["blink_timer"] <= 0 and abs(veh["x"] - veh["target_x"]) < 2:
                    veh["blinking"] = False

            if veh["x"] < veh["target_x"]:
                veh["x"] = min(veh["target_x"], veh["x"] + 130.0 * dt)
            elif veh["x"] > veh["target_x"]:
                veh["x"] = max(veh["target_x"], veh["x"] - 130.0 * dt)

            if veh["type"] == "oncoming":
                veh["y"] += (current_base_speed + veh["speed"]) * dt
            elif veh["type"] == "barrier":
                veh["y"] += current_base_speed * dt
            else:
                offset = veh.get("net_speed_offset", 50.0)
                veh["y"] += (current_base_speed - offset) * dt

            hit_box_size_y = 20 if veh["type"] == "barrier" else 28
            if abs(veh["x"] - self.rx) < 14 and abs(veh["y"] - 185.0) < (hit_box_size_y / 2 + 10):
                self.game_over = True
                self.play_sound("crash")

            if veh["y"] > 260 or veh["y"] < -60:
                self.traffic.remove(veh)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 12, 25))
        road_rect = pygame.Rect(70, 0, 180, 240)
        pygame.draw.rect(surface, (25, 25, 35), road_rect)

        pygame.draw.line(surface, (255, 255, 255), (70, 0), (70, 240), 2)
        pygame.draw.line(surface, (255, 255, 255), (250, 0), (250, 240), 2)

        for y_pos in range(int(-40 + self.road_scroll), 240, 40):
            pygame.draw.line(surface, (255, 255, 255), (130, y_pos), (130, y_pos + 20), 2)
            pygame.draw.line(surface, (255, 255, 255), (190, y_pos), (190, y_pos + 20), 2)

        for p in self.pylons:
            px, py = int(p["x"]), int(p["y"])
            pygame.draw.polygon(surface, (255, 128, 0), [(px, py - 6), (px - 5, py + 6), (px + 5, py + 6)])
            pygame.draw.rect(surface, (255, 255, 255), (px - 3, py, 6, 2))

        # Spieler-Fahrzeug im detailreichen Original-Design
        px, py = int(self.rx), 185
        pygame.draw.rect(surface, (0, 255, 180), (px - 10, py - 14, 20, 28), border_radius=5)
        pygame.draw.rect(surface, (255, 255, 255), (px - 6, py - 6, 12, 10), border_radius=2)
        pygame.draw.circle(surface, (255, 0, 0), (px - 7, py + 12), 2)
        pygame.draw.circle(surface, (255, 0, 0), (px + 7, py + 12), 2)

        # Andere Fahrzeuge im detailreichen Original-Design mit Front-/Heck-Blinkern
        for veh in self.traffic:
            vx, vy = int(veh["x"]), int(veh["y"])
            if veh["type"] == "barrier":
                pygame.draw.rect(surface, (255, 30, 30), (vx - 22, vy - 6, 44, 12), border_radius=3)
                pygame.draw.rect(surface, (255, 255, 255), (vx - 18, vy - 4, 36, 8), border_radius=2)
            else:
                pygame.draw.rect(surface, veh["color"], (vx - 10, vy - 14, 20, 28), border_radius=5)
                pygame.draw.rect(surface, (50, 50, 50), (vx - 6, vy - 4, 12, 8))

                if veh["blinking"] and int(pygame.time.get_ticks() / 200) % 2 == 0:
                    side_x = vx - 12 if veh["target_x"] < veh["x"] else vx + 12
                    pygame.draw.circle(surface, (255, 165, 0), (side_x, vy - 12), 2)
                    pygame.draw.circle(surface, (255, 165, 0), (side_x, vy + 12), 2)

        self.render_ui(surface)

# ==========================================
# QUANTUM MAZE (Advanced Collectibles & Reset Progress)
# ==========================================
import random

import pygame

from pocket_games.games.base import BaseGame


class QuantumMazeGame(BaseGame):
    def __init__(self, engine) -> None:
        super().__init__(engine, "Quantum Maze")
        self.collected_count = 0
        self.level = 1
        self.grid_cols = 5
        self.grid_rows = 5
        self.time_counter = 0.0

        self.screen_bounds = pygame.Rect(10, 35, 300, 185)
        self.walls: list[pygame.Rect] = []
        self.items: list[dict] = []

        self.px, self.py = 20.0, 40.0
        self.pw, self.ph = 10, 10

        self._generate_maze()

    def _generate_maze(self) -> None:
        """Generates a procedural maze based on current grid density."""
        cols = self.grid_cols
        rows = self.grid_rows

        bounds = self.screen_bounds
        cell_w = bounds.width / cols
        cell_h = bounds.height / rows

        visited = [[False] * rows for _ in range(cols)]
        horiz_walls = [[True] * (rows + 1) for _ in range(cols)]
        vert_walls = [[True] * rows for _ in range(cols + 1)]

        stack = [(0, 0)]
        visited[0][0] = True

        while stack:
            cx, cy = stack[-1]
            neighbors = []
            for dx, dy, w_type, wx, wy in [
                (0, -1, "h", cx, cy),
                (0, 1, "h", cx, cy + 1),
                (-1, 0, "v", cx, cy),
                (1, 0, "v", cx + 1, cy),
            ]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < cols and 0 <= ny < rows and not visited[nx][ny]:
                    neighbors.append((nx, ny, w_type, wx, wy))

            if neighbors:
                nx, ny, w_type, wx, wy = random.choice(neighbors)
                visited[nx][ny] = True
                if w_type == "h":
                    horiz_walls[wx][wy] = False
                else:
                    vert_walls[wx][wy] = False
                stack.append((nx, ny))
            else:
                stack.pop()

        self.walls = []
        wall_thick = 4

        self.walls.append(
            pygame.Rect(
                bounds.x - wall_thick,
                bounds.y - wall_thick,
                bounds.width + 2 * wall_thick,
                wall_thick,
            )
        )
        self.walls.append(
            pygame.Rect(
                bounds.x - wall_thick,
                bounds.bottom,
                bounds.width + 2 * wall_thick,
                wall_thick,
            )
        )
        self.walls.append(
            pygame.Rect(bounds.x - wall_thick, bounds.y, wall_thick, bounds.height)
        )
        self.walls.append(
            pygame.Rect(bounds.right, bounds.y, wall_thick, bounds.height)
        )

        for x in range(cols):
            for y in range(rows + 1):
                if horiz_walls[x][y] and 0 < y < rows:
                    wx = bounds.x + x * cell_w
                    wy = bounds.y + y * cell_h - wall_thick / 2
                    self.walls.append(
                        pygame.Rect(wx, wy, cell_w + wall_thick / 2, wall_thick)
                    )

        for x in range(cols + 1):
            for y in range(rows):
                if vert_walls[x][y] and 0 < x < cols:
                    wx = bounds.x + x * cell_w - wall_thick / 2
                    wy = bounds.y + y * cell_h
                    self.walls.append(
                        pygame.Rect(wx, wy, wall_thick, cell_h + wall_thick / 2)
                    )

        self.px = bounds.x + cell_w / 2 - self.pw / 2
        self.py = bounds.y + cell_h / 2 - self.ph / 2

        self.items.clear()
        for _ in range(5):
            self._spawn_item()

    def _spawn_item(self) -> None:
        bounds = self.screen_bounds
        cols, rows = self.grid_cols, self.grid_rows
        cell_w, cell_h = bounds.width / cols, bounds.height / rows

        for _ in range(200):
            gx = random.randint(0, cols - 1)
            gy = random.randint(0, rows - 1)

            cx = bounds.x + gx * cell_w + cell_w / 2
            cy = bounds.y + gy * cell_h + cell_h / 2
            candidate = pygame.Rect(cx - 5, cy - 5, 10, 10)

            p_rect = pygame.Rect(int(self.px), int(self.py), self.pw, self.ph)
            if not p_rect.colliderect(candidate.inflate(20, 20)) and not any(
                candidate.colliderect(w) for w in self.walls
            ):
                itype = random.choices(
                    ["core", "fragment", "trap"], weights=[50, 30, 20]
                )[0]
                self.items.append(
                    {"rect": candidate, "cx": cx, "cy": cy, "type": itype}
                )
                break

    def handle_input(self) -> None:
        super().handle_input()
        if self.game_over:
            return

        inp = self.engine.input
        dx, dy = 0.0, 0.0
        speed = 95.0

        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            dx -= speed
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            dx += speed
        if inp.is_key_down(pygame.K_UP) or inp.is_key_down(pygame.K_w):
            dy -= speed
        if inp.is_key_down(pygame.K_DOWN) or inp.is_key_down(pygame.K_s):
            dy += speed

        dt = 0.016

        if dx != 0:
            next_x = self.px + dx * dt
            test_rect_x = pygame.Rect(int(next_x), int(self.py), self.pw, self.ph)
            if not any(test_rect_x.colliderect(w) for w in self.walls):
                self.px = next_x

        if dy != 0:
            next_y = self.py + dy * dt
            test_rect_y = pygame.Rect(int(self.px), int(next_y), self.pw, self.ph)
            if not any(test_rect_y.colliderect(w) for w in self.walls):
                self.py = next_y

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.game_over:
            return

        self.time_counter += dt
        player_rect = pygame.Rect(int(self.px), int(self.py), self.pw, self.ph)

        for item in self.items[:]:
            if player_rect.colliderect(item["rect"]):
                self.items.remove(item)

                if item["type"] == "core":
                    self.collected_count += 1
                    self.add_score(100)
                    self.play_sound("score")

                    if self.collected_count % 10 == 0:
                        self.level += 1
                        if self.grid_cols < 12:
                            self.grid_cols += 1
                            self.grid_rows += 1
                        self._generate_maze()
                        return
                elif item["type"] == "fragment":
                    self.add_score(50)
                    self.play_sound("score")
                elif item["type"] == "trap":
                    self.add_score(-50)
                    self.play_sound("hit")

                self._spawn_item()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 10, 20))

        for x in range(0, 320, 20):
            pygame.draw.line(surface, (15, 22, 38), (x, 0), (x, 240))
        for y in range(0, 240, 20):
            pygame.draw.line(surface, (15, 22, 38), (0, y), (320, y))

        for w in self.walls:
            pygame.draw.rect(surface, (40, 70, 150), w.inflate(2, 2), border_radius=1)
            pygame.draw.rect(surface, (100, 180, 255), w, border_radius=1)

        for item in self.items:
            cx, cy = int(item["cx"]), int(item["cy"])
            if item["type"] == "core":
                pygame.draw.circle(surface, (0, 255, 200), (cx, cy), 5)
                pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 2)
            elif item["type"] == "fragment":
                pygame.draw.circle(surface, (255, 220, 0), (cx, cy), 4)
            elif item["type"] == "trap":
                pygame.draw.circle(surface, (255, 40, 80), (cx, cy), 5)
                pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 2)

        px, py = int(self.px), int(self.py)
        pygame.draw.rect(
            surface, (255, 80, 180), (px, py, self.pw, self.ph), border_radius=2
        )

        progress_text = self.font.render(
            f"Maze Reset Progress: {self.collected_count % 10}/10 Cores",
            True,
            (0, 255, 200),
        )
        surface.blit(progress_text, (160 - progress_text.get_width() // 2, 12))

        self.render_ui(surface)

from __future__ import annotations

import pygame


class CircuitBreakerGame:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)
        self.nodes = [
            {"pos": (50, 60), "connected": True},
            {"pos": (120, 60), "connected": False},
            {"pos": (200, 140), "connected": False},
            {"pos": (270, 180), "connected": False},
        ]
        self.selected_node = 0

    def handle_input(self) -> None:
        inp = self.engine.input
        if (
            inp.is_key_pressed(pygame.K_ESCAPE)
            or inp.is_key_pressed(pygame.K_BACKSPACE)
            or self.engine.input.is_back_pressed()
        ):
            self.active = False
        if inp.is_key_pressed(pygame.K_LEFT) and self.selected_node > 0:
            self.selected_node -= 1
        if inp.is_key_pressed(pygame.K_RIGHT) and self.selected_node < len(self.nodes) - 1:
            self.selected_node += 1
        if inp.is_key_pressed(pygame.K_RETURN) or inp.is_key_pressed(pygame.K_SPACE):
            self.nodes[self.selected_node]["connected"] = True
            self.score = sum(100 for n in self.nodes if n["connected"])
            self.engine.highscores.submit_score("Circuit Breaker", self.score)

        if inp.mouse_clicked:
            for i, node in enumerate(self.nodes):
                nx, ny = node["pos"]
                if pygame.Rect(nx - 12, ny - 12, 24, 24).collidepoint(inp.mouse_pos):
                    self.selected_node = i
                    node["connected"] = True
                    self.score = sum(100 for n in self.nodes if n["connected"])
                    self.engine.highscores.submit_score("Circuit Breaker", self.score)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 25, 20))
        # Draw wires
        for i in range(len(self.nodes) - 1):
            n1, n2 = self.nodes[i], self.nodes[i+1]
            color = (0, 255, 100) if n1["connected"] and n2["connected"] else (80, 80, 80)
            pygame.draw.line(surface, color, n1["pos"], n2["pos"], 3)

        # Draw nodes
        for i, node in enumerate(self.nodes):
            color = (255, 255, 0) if i == self.selected_node else ((0, 255, 0) if node["connected"] else (150, 50, 50))
            pygame.draw.circle(surface, color, node["pos"], 10)

        sc = self.font.render(f"Circuit Score: {self.score}", True, (255, 255, 255))
        surface.blit(sc, (10, 10))

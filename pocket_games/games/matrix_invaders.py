from __future__ import annotations

import random

import pygame

from pocket_games.games.base import BaseGame


class MatrixInvadersGame(BaseGame):
    """Refactored Matrix Invaders fixed vertical arcade shooter."""

    def __init__(self, engine) -> None:
        super().__init__(engine, game_name="Matrix Invaders")
        self.px = 160.0
        self.bullets: list[dict] = []
        self.bugs: list[dict] = []
        self.spawn_timer = 0.0
        self.spawn_bugs()

    def spawn_bugs(self) -> None:
        for _ in range(6):
            self.bugs.append(
                {
                    "x": float(random.randint(20, 300)),
                    "y": float(random.randint(30, 80)),
                    "speed": float(random.randint(15, 35)),
                }
            )

    def handle_input(self) -> None:
        super().handle_input()
        if not self.active:
            return

        inp = self.engine.input
        speed = 180.0
        dt = 0.016

        if inp.is_key_down(pygame.K_LEFT) or inp.is_key_down(pygame.K_a):
            self.px = max(15.0, self.px - speed * dt)
        if inp.is_key_down(pygame.K_RIGHT) or inp.is_key_down(pygame.K_d):
            self.px = min(305.0, self.px + speed * dt)

        if inp.is_key_pressed(pygame.K_SPACE) or inp.is_key_pressed(pygame.K_RETURN) or inp.mouse_clicked:
            self.bullets.append({"x": self.px, "y": 210.0})
            self.engine.audio.play("select")

    def update(self, dt: float) -> None:
        super().update(dt)
        if not self.active or self.paused or self.game_over:
            return

        # Move bullets
        for b in self.bullets[:]:
            b["y"] -= 240.0 * dt
            if b["y"] < 20:
                self.bullets.remove(b)

        # Move bugs & handle collision
        for bug in self.bugs[:]:
            bug["y"] += bug["speed"] * dt
            if bug["y"] >= 210:
                self.game_over = True
                self.engine.audio.play("hit")
                return

            for b in self.bullets[:]:
                if abs(b["x"] - bug["x"]) < 12 and abs(b["y"] - bug["y"]) < 12:
                    if b in self.bullets:
                        self.bullets.remove(b)
                    self.bugs.remove(bug)
                    self.add_score(25)
                    self.engine.audio.play("confirm")
                    self.bugs.append(
                        {
                            "x": float(random.randint(20, 300)),
                            "y": float(random.randint(30, 60)),
                            "speed": float(random.randint(20, 45)),
                        }
                    )
                    break

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((5, 12, 10))

        # Ship
        pygame.draw.polygon(
            surface,
            (0, 255, 150),
            [(int(self.px), 205), (int(self.px) - 10, 220), (int(self.px) + 10, 220)],
        )

        # Bullets
        for b in self.bullets:
            pygame.draw.rect(surface, (255, 255, 0), (int(b["x"]) - 1, int(b["y"]), 3, 7))

        # Bugs
        for bug in self.bugs:
            bx, by = int(bug["x"]), int(bug["y"])
            pygame.draw.rect(surface, (255, 40, 100), (bx - 8, by - 8, 16, 16), border_radius=3)

        if self.game_over:
            go = self.title_font.render("MATRIX BREACH", True, (255, 50, 50))
            surface.blit(go, (160 - go.get_width() // 2, 110))

        self.render_ui(surface)

from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager


class TestInputManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def test_key_handling(self) -> None:
        inp = InputManager()
        # Simuliere Keydown Event
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        pygame.event.post(event)
        inp.update()

        self.assertTrue(inp.is_key_down(pygame.K_LEFT))
        self.assertTrue(inp.is_key_just_pressed(pygame.K_LEFT))
        self.assertTrue(inp.is_left_pressed())

        # Simuliere Keyup Event
        event_up = pygame.event.Event(pygame.KEYUP, key=pygame.K_LEFT)
        pygame.event.post(event_up)
        inp.update()

        self.assertFalse(inp.is_key_down(pygame.K_LEFT))

    def test_navigation_shortcuts(self) -> None:
        inp = InputManager()
        # Back and action test
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        pygame.event.post(event)
        event_space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        pygame.event.post(event_space)
        inp.update()

        self.assertTrue(inp.is_back_pressed())
        self.assertTrue(inp.is_action_pressed())
        self.assertTrue(inp.is_action_just_pressed())


if __name__ == "__main__":
    unittest.main()

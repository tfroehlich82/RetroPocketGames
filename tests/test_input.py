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

    def test_key_just_pressed_vs_held(self) -> None:
        inp = InputManager()

        # Simuliere ein KEYDOWN Event
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        pygame.event.post(event)

        inp.update()

        # Im Frame des Tastenanschlags muss is_key_just_pressed True sein
        self.assertTrue(inp.is_key_just_pressed(pygame.K_UP))

        # Im nächsten Frame ohne neues Event muss is_key_just_pressed wieder False sein
        inp.update()
        self.assertFalse(inp.is_key_just_pressed(pygame.K_UP))

    def test_back_pressed_trigger(self) -> None:
        inp = InputManager()

        # Simuliere ESCAPE Taste
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        inp.update()

        self.assertTrue(inp.is_back_pressed())


if __name__ == "__main__":
    unittest.main()

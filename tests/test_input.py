from __future__ import annotations

import os
import unittest
from unittest import mock

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import START_HOLD_SECONDS, InputManager


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

    def test_back_pressed_accepts_all_back_keys(self) -> None:
        inp = InputManager()
        for key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_x, pygame.K_b):
            inp.keys_just_pressed = {key}
            self.assertTrue(inp.is_back_pressed(), key)
        inp.keys_just_pressed = {pygame.K_q}
        self.assertFalse(inp.is_back_pressed())

    def test_directional_helpers_accept_arrow_and_wasd_keys(self) -> None:
        inp = InputManager()
        cases = (
            (inp.is_left_pressed, pygame.K_LEFT, pygame.K_a),
            (inp.is_right_pressed, pygame.K_RIGHT, pygame.K_d),
            (inp.is_up_pressed, pygame.K_UP, pygame.K_w),
            (inp.is_down_pressed, pygame.K_DOWN, pygame.K_s),
        )
        for helper, arrow, letter in cases:
            inp.keys_pressed = {arrow}
            self.assertTrue(helper(), arrow)
            inp.keys_pressed = {letter}
            self.assertTrue(helper(), letter)
            inp.keys_pressed = set()
            self.assertFalse(helper())

    def test_action_accepts_enter_variants_and_mouse(self) -> None:
        inp = InputManager()
        inp.keys_pressed = {pygame.K_KP_ENTER}
        inp.keys_just_pressed = {pygame.K_KP_ENTER}
        self.assertTrue(inp.is_action_pressed())
        self.assertTrue(inp.is_action_just_pressed())

        inp.keys_pressed = set()
        inp.keys_just_pressed = set()
        self.assertFalse(inp.is_action_pressed())
        self.assertFalse(inp.is_action_just_pressed())

        inp.mouse_clicked = True
        self.assertTrue(inp.is_action_pressed())
        self.assertTrue(inp.is_action_just_pressed())

    def test_action_held_key_without_just_press(self) -> None:
        inp = InputManager()
        inp.keys_pressed = {pygame.K_SPACE}
        self.assertTrue(inp.is_action_pressed())
        self.assertFalse(inp.is_action_just_pressed())

    def test_global_exit_on_escape(self) -> None:
        inp = InputManager()
        inp.keys_just_pressed = {pygame.K_ESCAPE}
        self.assertTrue(inp.is_global_exit_pressed())

    def test_global_exit_after_holding_start_for_threshold(self) -> None:
        inp = InputManager()
        inp.keys_pressed = {pygame.K_BREAK}
        with mock.patch("pocket_games.core.input.pygame.time.get_ticks", return_value=1000):
            self.assertFalse(inp.is_global_exit_pressed())
        with mock.patch("pocket_games.core.input.pygame.time.get_ticks", return_value=1000 + 2999):
            self.assertFalse(inp.is_global_exit_pressed())
        with mock.patch("pocket_games.core.input.pygame.time.get_ticks", return_value=1000 + 3000):
            self.assertTrue(inp.is_global_exit_pressed())
        self.assertIsNone(inp._start_press_start_time)

    def test_global_exit_hold_timer_resets_on_release(self) -> None:
        inp = InputManager()
        inp.keys_pressed = {pygame.K_BREAK}
        with mock.patch("pocket_games.core.input.pygame.time.get_ticks", return_value=500):
            inp.is_global_exit_pressed()
        self.assertIsNotNone(inp._start_press_start_time)
        inp.keys_pressed = set()
        self.assertFalse(inp.is_global_exit_pressed())
        self.assertIsNone(inp._start_press_start_time)

    def test_start_hold_threshold_constant(self) -> None:
        self.assertEqual(START_HOLD_SECONDS, 3.0)


if __name__ == "__main__":
    unittest.main()

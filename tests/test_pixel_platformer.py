from __future__ import annotations

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.pixel_platformer import (
    GROUND_Y,
    MAX_LEVELS,
    SPAWN_INVULNERABILITY,
    STAR_DURATION,
    PixelPlatformerGame,
)


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()
        self.highscores = None


class TestPixelPlatformer(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def make_game(self, level: int = 1) -> PixelPlatformerGame:
        game = PixelPlatformerGame(MockEngine())
        game.showing_intro = False
        game.level = level
        game._setup_level()
        game.invulnerable_timer = 0.0
        return game

    def test_initial_state(self) -> None:
        game = self.make_game()
        self.assertEqual(game.lives, 3)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.max_levels, MAX_LEVELS)
        self.assertFalse(game.has_gun)
        self.assertGreater(len(game.platforms), 0)

    def test_space_key_makes_player_jump_from_ground(self) -> None:
        game = self.make_game()
        game.powerups = []
        game.enemies = []
        game.hazards = []
        game.px, game.py = 40.0, GROUND_Y - 20.0
        game.pvy = 0.0
        game.engine.input.keys_just_pressed = {pygame.K_SPACE}
        game.handle_input()
        self.assertLess(game.pvy, 0.0)
        self.assertFalse(game.is_grounded)

    def test_space_key_jump_works_after_landing(self) -> None:
        game = self.make_game()
        game.powerups = []
        game.enemies = []
        game.hazards = []
        game.px, game.py = 40.0, 140.0
        for _ in range(120):
            game.engine.input.keys_just_pressed = set()
            game.handle_input()
            game.update(0.016)
        self.assertAlmostEqual(game.py, GROUND_Y - 20.0, delta=1.0)
        game.engine.input.keys_just_pressed = {pygame.K_SPACE}
        game.handle_input()
        self.assertLess(game.pvy, 0.0)

    def test_powerup_life_gain(self) -> None:
        game = self.make_game()
        game.powerups = [{"x": game.px, "y": game.py, "type": "life", "collected": False}]
        game.update(0.016)
        self.assertEqual(game.lives, 4)
        self.assertTrue(game.powerups[0]["collected"])

    def test_gun_powerup_enables_shooting(self) -> None:
        game = self.make_game()
        game.powerups = [{"x": game.px, "y": game.py, "type": "gun", "collected": False}]
        game.update(0.016)
        self.assertTrue(game.has_gun)
        game.engine.input.is_key_just_pressed = lambda key: key == pygame.K_z
        game.handle_input()
        self.assertEqual(len(game.projectiles), 1)

    def test_star_powerup_grants_temporary_invulnerability(self) -> None:
        game = self.make_game()
        game.powerups = [{"x": game.px, "y": game.py, "type": "star", "collected": False}]
        game.update(0.016)
        self.assertGreater(game.star_timer, STAR_DURATION - 0.1)
        game.lives = 3
        game.handle_damage()
        self.assertEqual(game.lives, 3)

    def test_star_timer_expires(self) -> None:
        game = self.make_game()
        game.star_timer = 0.5
        game.update(1.0)
        self.assertEqual(game.star_timer, 0.0)

    def test_stomping_enemy_kills_it_and_bounces(self) -> None:
        game = self.make_game()
        game.powerups = []
        game.enemies = [{"kind": "walker", "x": 100.0, "y": 100.0, "w": 16, "h": 16, "dir": 1,
                         "speed": 0.0, "min_x": 0.0, "max_x": 300.0, "base_y": 0.0, "phase": 0.0, "alive": True}]
        game.px, game.py = 100.0, 84.0
        game.pvy = 200.0
        game.update(0.016)
        self.assertFalse(game.enemies[0]["alive"])
        self.assertLess(game.pvy, 0.0)
        self.assertEqual(game.lives, 3)

    def test_side_contact_costs_life(self) -> None:
        game = self.make_game()
        game.powerups = []
        game.enemies = [{"kind": "walker", "x": 100.0, "y": 185.0, "w": 16, "h": 16, "dir": 1,
                         "speed": 0.0, "min_x": 0.0, "max_x": 300.0, "base_y": 0.0, "phase": 0.0, "alive": True}]
        game.px, game.py = 100.0, 185.0
        game.pvy = 0.0
        game.update(0.016)
        self.assertEqual(game.lives, 2)

    def test_flyer_moves_vertically_in_sine_wave(self) -> None:
        game = self.make_game(level=6)
        flyers = [e for e in game.enemies if e["kind"] == "flyer"]
        self.assertGreater(len(flyers), 0)
        flyer = flyers[0]
        flyer["x"] = 150.0
        flyer["y"] = 80.0
        start_y = flyer["y"]
        game.px, game.py = 0.0, 0.0
        game.anim_time = 0.0
        game.update(0.1)
        self.assertNotEqual(flyer["y"], start_y)

    def test_walker_turns_at_patrol_boundary(self) -> None:
        game = self.make_game()
        game.powerups = []
        game.px, game.py = 290.0, 0.0
        walker = {"kind": "walker", "x": 200.0, "y": 170.0, "w": 16, "h": 16, "dir": 1,
                  "speed": 100.0, "min_x": 100.0, "max_x": 210.0, "base_y": 0.0, "phase": 0.0, "alive": True}
        game.enemies = [walker]
        game.update(0.2)
        self.assertEqual(walker["dir"], -1)
        self.assertLessEqual(walker["x"], 210.0)

    def test_spike_damage(self) -> None:
        game = self.make_game()
        game.hazards = [pygame.Rect(100, 195, 16, 10)]
        game.px, game.py = 100.0, 185.0
        game.update(0.016)
        self.assertEqual(game.lives, 2)

    def test_falling_into_pit_costs_life(self) -> None:
        game = self.make_game()
        game.px, game.py = 100.0, 260.0
        game.update(0.016)
        self.assertEqual(game.lives, 2)
        self.assertEqual(game.py, 140.0)

    def test_invulnerability_after_respawn(self) -> None:
        game = self.make_game()
        game.px, game.py = 100.0, 260.0
        game.update(0.016)
        self.assertEqual(game.invulnerable_timer, SPAWN_INVULNERABILITY)

    def test_game_over_after_last_life(self) -> None:
        game = self.make_game()
        game.lives = 1
        game.px, game.py = 100.0, 260.0
        game.update(0.016)
        self.assertTrue(game.game_over)
        self.assertEqual(game.lives, 0)

    def test_gun_absorbs_one_hit(self) -> None:
        game = self.make_game()
        game.has_gun = True
        game.handle_damage()
        self.assertFalse(game.has_gun)
        self.assertEqual(game.lives, 3)

    def test_coins_are_collected(self) -> None:
        game = self.make_game()
        game.powerups = []
        game.coins = [{"x": 100.0, "y": 180.0, "collected": False}]
        coin = game.coins[0]
        game.px, game.py = coin["x"], coin["y"]
        game.update(0.016)
        self.assertTrue(coin["collected"])
        self.assertEqual(game.coins_collected, 1)
        self.assertGreater(game.score, 0)

    def test_reaching_flag_advances_level(self) -> None:
        game = self.make_game()
        game.px = 315.0
        game.py = 185.0
        game.update(0.016)
        self.assertEqual(game.level, 2)
        self.assertEqual(game.px, 40.0)

    def test_final_level_completion_wins_game(self) -> None:
        game = self.make_game(level=MAX_LEVELS)
        game.px = 315.0
        game.py = 185.0
        game.update(0.016)
        self.assertTrue(game.game_won)
        self.assertEqual(game.level, MAX_LEVELS + 1)

    def test_all_levels_are_generated_and_solvable_in_principle(self) -> None:
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game(level=level)
            self.assertGreater(len(game.ground), 0, level)
            self.assertGreater(len(game.floating), 0, level)
            for rect in game.platforms:
                self.assertGreaterEqual(rect.left, 0, level)
                self.assertLessEqual(rect.right, 320, level)

    def test_difficulty_grows_with_level(self) -> None:
        early = self.make_game(level=1)
        late = self.make_game(level=MAX_LEVELS)
        self.assertGreaterEqual(len(late.enemies), len(early.enemies))
        self.assertGreater(len(late.hazards) + sum(1 for e in late.enemies if e["kind"] == "flyer"), 0)
        self.assertLessEqual(len(late.ground), 4)
        early_speed = max(e["speed"] for e in early.enemies)
        late_speed = max(e["speed"] for e in late.enemies)
        self.assertGreater(late_speed, early_speed)

    def test_each_level_has_a_powerup(self) -> None:
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game(level=level)
            self.assertEqual(len(game.powerups), 1, level)

    def test_render_all_levels_without_error(self) -> None:
        surface = pygame.Surface((320, 240))
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game(level=level)
            game.has_gun = True
            game.star_timer = 1.0
            game.projectiles = [{"x": 50.0, "y": 50.0, "vx": 320.0}]
            game.render(surface)

    def test_render_game_over_and_won_screens(self) -> None:
        surface = pygame.Surface((320, 240))
        game = self.make_game()
        game.game_over = True
        game.render(surface)
        game.game_over = False
        game.game_won = True
        game.render(surface)

    def test_metadata_is_registered_for_game(self) -> None:
        from pocket_games.games.base import GAME_METADATA

        self.assertIn("Pixel Platformer", GAME_METADATA)
        for lang in ("de", "en"):
            self.assertTrue(GAME_METADATA["Pixel Platformer"][lang]["desc"])
            self.assertTrue(GAME_METADATA["Pixel Platformer"][lang]["goal"])
            self.assertTrue(GAME_METADATA["Pixel Platformer"][lang]["controls"])


if __name__ == "__main__":
    unittest.main()

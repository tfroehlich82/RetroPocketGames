from __future__ import annotations

import os
import random
import unittest
from unittest import mock

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games import cyber_flipper as cf
from pocket_games.games.cyber_flipper import (
    BALLS_PER_GAME,
    FLIPPER_ACTIVE_ANGLE,
    FLIPPER_REST_ANGLE,
    LEFT_PIVOT,
    LEVELS,
    MAX_CHARGE,
    PLUNGER_START,
    RIGHT_PIVOT,
    CyberFlipperGame,
    advance_flipper_angle,
    closest_point_on_segment,
    flipper_tip,
    reflect_velocity,
)

INPUT_METHODS = (
    "is_left_pressed",
    "is_right_pressed",
    "is_down_pressed",
    "is_up_pressed",
    "is_action_pressed",
    "is_action_just_pressed",
)


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.highscores = mock.Mock()
        self.audio = mock.Mock()
        self.settings = type("MockSettings", (), {"language": "English"})()


class TestCyberFlipperGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def make_game(self, seed: int = 1) -> CyberFlipperGame:
        game = CyberFlipperGame(MockEngine(), rng=random.Random(seed))
        game.showing_intro = False
        return game

    def press(self, game: CyberFlipperGame, keys: tuple[int, ...] = (), **buttons: bool):
        """
        Patches the input manager so that the given buttons and keys appear held or pressed.

        :param game: Game whose engine input is patched.
        :param keys: Pygame key codes reported as held through is_key_down.
        :param buttons: Input method names mapped to True to report as active.
        :return: A context manager that restores the input methods on exit.
        """
        values = {name: buttons.get(name, False) for name in INPUT_METHODS}
        patches = {name: mock.Mock(return_value=value) for name, value in values.items()}
        patches["is_key_down"] = mock.Mock(side_effect=lambda key: key in keys)
        return mock.patch.multiple(game.engine.input, **patches)

    # ----- level data -----

    def test_five_levels_with_distinct_themes(self) -> None:
        self.assertEqual(len(LEVELS), 5)
        self.assertEqual(len({level.name for level in LEVELS}), 5)
        self.assertEqual(len({level.background for level in LEVELS}), 5)
        self.assertEqual(len({level.wall for level in LEVELS}), 5)

    def test_levels_have_distinct_layouts(self) -> None:
        layouts = {tuple((b[0], b[1], b[2]) for b in level.bumpers) for level in LEVELS}
        self.assertEqual(len(layouts), 5)

    def test_score_targets_increase_per_level(self) -> None:
        targets = [level.score_target for level in LEVELS]
        self.assertEqual(targets, sorted(targets))
        self.assertEqual(len(set(targets)), len(targets))

    def test_level_elements_lie_inside_playfield(self) -> None:
        for level in LEVELS:
            for x, y, r, pts, _color in level.bumpers:
                self.assertTrue(cf.PLAYFIELD_LEFT < x - r and x + r < cf.LANE_X, level.name)
                self.assertTrue(cf.PLAYFIELD_TOP < y - r and y + r < 200.0, level.name)
                self.assertGreater(pts, 0)
            for (ax, ay), (bx, by) in level.walls:
                for px, py in ((ax, ay), (bx, by)):
                    self.assertTrue(cf.PLAYFIELD_LEFT <= px <= cf.LANE_X, level.name)
                    self.assertTrue(cf.PLAYFIELD_TOP <= py <= 200.0, level.name)

    def test_level_physics_values_are_positive(self) -> None:
        for level in LEVELS:
            self.assertGreater(level.gravity, 0)
            self.assertGreater(level.wall_restitution, 0)
            self.assertLessEqual(level.wall_restitution, 1.0)

    # ----- initialization and level loading -----

    def test_initialization_defaults(self) -> None:
        game = self.make_game()
        self.assertEqual(game.game_name, "Cyber Flipper")
        self.assertEqual(game.level_index, 0)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.balls_left, BALLS_PER_GAME)
        self.assertEqual((game.bx, game.by), PLUNGER_START)
        self.assertEqual((game.bvx, game.bvy), (0.0, 0.0))
        self.assertTrue(game.ball_on_plunger)
        self.assertEqual(len(game.bumpers), 3)
        self.assertEqual(game.particles, [])
        self.assertEqual(game.score, 0)
        self.assertFalse(game.game_won)

    def test_default_rng_is_seeded_for_reproducibility(self) -> None:
        first = CyberFlipperGame(MockEngine())
        second = CyberFlipperGame(MockEngine())
        first._spawn_particles(10.0, 10.0, (1, 2, 3), 4, 50.0, 0.3)
        second._spawn_particles(10.0, 10.0, (1, 2, 3), 4, 50.0, 0.3)
        self.assertEqual(first.particles, second.particles)

    def test_table_property_returns_active_level(self) -> None:
        game = self.make_game()
        self.assertIs(game.table, LEVELS[0])
        game.load_level(3)
        self.assertIs(game.table, LEVELS[3])

    def test_load_level_applies_theme_physics_and_layout(self) -> None:
        game = self.make_game()
        game.load_level(4)
        level = LEVELS[4]
        self.assertEqual(game.level, 5)
        self.assertEqual(game.gravity, level.gravity)
        self.assertEqual(game.wall_restitution, level.wall_restitution)
        self.assertEqual(len(game.bumpers), len(level.bumpers))
        self.assertEqual(len(game.walls), len(cf.FRAME_WALLS) + len(level.walls))
        self.assertEqual(game.bumpers[0]["flash"], 0.0)

    def test_load_level_resets_level_state(self) -> None:
        game = self.make_game()
        game.level_score = 999
        game.particles = [{"x": 0, "y": 0, "vx": 0, "vy": 0, "life": 1, "color": (0, 0, 0)}]
        game.ball_on_plunger = False
        game.load_level(1)
        self.assertEqual(game.level_score, 0)
        self.assertEqual(game.particles, [])
        self.assertTrue(game.ball_on_plunger)
        self.assertGreater(game.banner_timer, 0)

    def test_reset_ball_places_ball_on_plunger(self) -> None:
        game = self.make_game()
        game.bx, game.by = 50.0, 60.0
        game.bvx, game.bvy = 9.0, -9.0
        game.launcher_pulled = 12.0
        game.ball_on_plunger = False
        game.reset_ball()
        self.assertEqual((game.bx, game.by), PLUNGER_START)
        self.assertEqual((game.bvx, game.bvy), (0.0, 0.0))
        self.assertEqual(game.launcher_pulled, 0.0)
        self.assertTrue(game.ball_on_plunger)

    # ----- pure helpers -----

    def test_closest_point_on_segment_projects_inside(self) -> None:
        self.assertEqual(closest_point_on_segment(5.0, 3.0, 0.0, 0.0, 10.0, 0.0), (5.0, 0.0))

    def test_closest_point_on_segment_clamps_to_endpoints(self) -> None:
        self.assertEqual(closest_point_on_segment(-5.0, 3.0, 0.0, 0.0, 10.0, 0.0), (0.0, 0.0))
        self.assertEqual(closest_point_on_segment(20.0, 3.0, 0.0, 0.0, 10.0, 0.0), (10.0, 0.0))

    def test_closest_point_on_degenerate_segment(self) -> None:
        self.assertEqual(closest_point_on_segment(4.0, 4.0, 1.0, 2.0, 1.0, 2.0), (1.0, 2.0))

    def test_reflect_velocity_bounces_incoming_motion(self) -> None:
        vx, vy = reflect_velocity(0.0, -10.0, 0.0, 1.0, 1.0)
        self.assertAlmostEqual(vx, 0.0)
        self.assertAlmostEqual(vy, 10.0)

    def test_reflect_velocity_applies_restitution(self) -> None:
        _vx, vy = reflect_velocity(0.0, -10.0, 0.0, 1.0, 0.5)
        self.assertAlmostEqual(vy, 5.0)

    def test_reflect_velocity_ignores_separating_motion(self) -> None:
        self.assertEqual(reflect_velocity(3.0, 4.0, 0.0, 1.0, 1.0), (3.0, 4.0))

    def test_flipper_tips_point_towards_centre_when_active(self) -> None:
        left_rest = flipper_tip(-1, FLIPPER_REST_ANGLE)
        left_active = flipper_tip(-1, FLIPPER_ACTIVE_ANGLE)
        right_active = flipper_tip(1, FLIPPER_ACTIVE_ANGLE)
        self.assertGreater(left_rest[1], LEFT_PIVOT[1])
        self.assertLess(left_active[1], LEFT_PIVOT[1])
        self.assertGreater(left_active[0], LEFT_PIVOT[0])
        self.assertLess(right_active[1], RIGHT_PIVOT[1])
        self.assertLess(right_active[0], RIGHT_PIVOT[0])

    def test_advance_flipper_angle_moves_towards_active(self) -> None:
        angle = advance_flipper_angle(FLIPPER_REST_ANGLE, True, 0.01)
        self.assertLess(angle, FLIPPER_REST_ANGLE)
        self.assertGreaterEqual(angle, FLIPPER_ACTIVE_ANGLE)

    def test_advance_flipper_angle_clamps_to_target(self) -> None:
        self.assertEqual(advance_flipper_angle(FLIPPER_REST_ANGLE, True, 10.0), FLIPPER_ACTIVE_ANGLE)
        self.assertEqual(advance_flipper_angle(FLIPPER_ACTIVE_ANGLE, False, 10.0), FLIPPER_REST_ANGLE)

    def test_advance_flipper_angle_returns_to_rest(self) -> None:
        angle = advance_flipper_angle(FLIPPER_ACTIVE_ANGLE, False, 0.01)
        self.assertGreater(angle, FLIPPER_ACTIVE_ANGLE)
        self.assertLessEqual(angle, FLIPPER_REST_ANGLE)

    # ----- input -----

    def test_handle_input_returns_early_when_game_over(self) -> None:
        game = self.make_game()
        game.game_over = True
        with self.press(game, keys=(pygame.K_z, pygame.K_x), is_action_pressed=True):
            game.handle_input()
        self.assertFalse(game.flipper_left_active)
        self.assertFalse(game.flipper_right_active)
        self.assertEqual(game.launcher_pulled, 0.0)

    def test_left_flipper_activated_by_z_key(self) -> None:
        game = self.make_game()
        with self.press(game, keys=(pygame.K_z,)):
            game.handle_input()
        self.assertTrue(game.flipper_left_active)
        self.assertFalse(game.flipper_right_active)

    def test_right_flipper_activated_by_x_key(self) -> None:
        game = self.make_game()
        with self.press(game, keys=(pygame.K_x,)):
            game.handle_input()
        self.assertTrue(game.flipper_right_active)
        self.assertFalse(game.flipper_left_active)

    def test_flippers_activated_by_directional_input(self) -> None:
        game = self.make_game()
        with self.press(game, is_left_pressed=True, is_right_pressed=True):
            game.handle_input()
        self.assertTrue(game.flipper_left_active)
        self.assertTrue(game.flipper_right_active)

    def test_plunger_charges_while_holding_action(self) -> None:
        game = self.make_game()
        with self.press(game, is_action_pressed=True):
            game.handle_input()
        self.assertAlmostEqual(game.launcher_pulled, 40.0 * 0.016)

    def test_plunger_charges_while_holding_down(self) -> None:
        game = self.make_game()
        with self.press(game, is_down_pressed=True):
            game.handle_input()
        self.assertGreater(game.launcher_pulled, 0.0)

    def test_plunger_charge_is_capped(self) -> None:
        game = self.make_game()
        game.launcher_pulled = MAX_CHARGE - 0.01
        with self.press(game, is_action_pressed=True):
            for _ in range(5):
                game.handle_input()
        self.assertEqual(game.launcher_pulled, MAX_CHARGE)

    def test_release_launches_ball_upwards(self) -> None:
        game = self.make_game()
        game.launcher_pulled = 10.0
        with self.press(game, is_action_just_pressed=True):
            game.handle_input()
        self.assertFalse(game.ball_on_plunger)
        self.assertEqual(game.launcher_pulled, 0.0)
        self.assertAlmostEqual(
            game.bvy, -cf.LAUNCH_BASE_SPEED - 10.0 * cf.LAUNCH_SPEED_PER_CHARGE
        )
        game.engine.audio.play.assert_called_with("confirm")

    def test_up_key_also_launches_charged_ball(self) -> None:
        game = self.make_game()
        game.launcher_pulled = 5.0
        with self.press(game, is_up_pressed=True):
            game.handle_input()
        self.assertFalse(game.ball_on_plunger)

    def test_release_without_charge_does_nothing(self) -> None:
        game = self.make_game()
        with self.press(game, is_action_just_pressed=True):
            game.handle_input()
        self.assertTrue(game.ball_on_plunger)
        self.assertEqual(game.bvy, 0.0)

    def test_plunger_ignored_while_ball_in_play(self) -> None:
        game = self.make_game()
        game.ball_on_plunger = False
        with self.press(game, is_action_pressed=True):
            game.handle_input()
        self.assertEqual(game.launcher_pulled, 0.0)

    # ----- update loop -----

    def test_update_returns_early_when_paused(self) -> None:
        game = self.make_game()
        game.ball_on_plunger = False
        game.bvy = -100.0
        game.paused = True
        game.update(0.1)
        self.assertEqual(game.bvy, -100.0)

    def test_ball_stays_on_plunger_until_launched(self) -> None:
        game = self.make_game()
        game.update(0.5)
        self.assertEqual((game.bx, game.by), PLUNGER_START)

    def test_gravity_pulls_launched_ball_down(self) -> None:
        game = self.make_game()
        game.load_level(0)
        game.bx, game.by = 150.0, 150.0
        game.bvx, game.bvy = 0.0, 0.0
        game.ball_on_plunger = False
        game.update(0.1)
        self.assertGreater(game.bvy, 0.0)
        self.assertGreater(game.by, 150.0)

    def test_particles_expire_and_move(self) -> None:
        game = self.make_game()
        game.particles = [
            {"x": 0.0, "y": 0.0, "vx": 10.0, "vy": 0.0, "life": 0.1, "color": (1, 1, 1)},
            {"x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0, "life": 5.0, "color": (1, 1, 1)},
        ]
        game.update(0.2)
        self.assertEqual(len(game.particles), 1)
        self.assertEqual(game.particles[0]["life"], 4.8)

    def test_particle_moves_with_velocity(self) -> None:
        game = self.make_game()
        game.particles = [{"x": 0.0, "y": 0.0, "vx": 10.0, "vy": -5.0, "life": 5.0, "color": (1, 1, 1)}]
        game._update_particles(0.5)
        self.assertEqual((game.particles[0]["x"], game.particles[0]["y"]), (5.0, -2.5))

    def test_bumper_flash_decays(self) -> None:
        game = self.make_game()
        game.bumpers[0]["flash"] = 0.2
        game.update(0.05)
        self.assertAlmostEqual(game.bumpers[0]["flash"], 0.15)

    def test_ball_on_raised_deck_hits_upper_bumper_only(self) -> None:
        game = self.make_game()
        game.load_level(1)
        game.ball_layer = cf.LAYER_HIGH
        upper = game.upper_bumpers[0]
        game.bx, game.by = upper["x"] + upper["r"] + game.ball_radius - 1.0, upper["y"]
        game.bvx, game.bvy = -50.0, 0.0
        game._collide_bumpers()
        self.assertGreater(upper["flash"], 0.0)

    def test_ball_on_low_layer_ignores_upper_bumpers(self) -> None:
        game = self.make_game()
        game.load_level(1)
        game.ball_layer = cf.LAYER_LOW
        upper = game.upper_bumpers[0]
        game.bx, game.by = upper["x"] + upper["r"] + game.ball_radius - 1.0, upper["y"]
        game.bvx, game.bvy = -50.0, 0.0
        game._collide_bumpers()
        self.assertEqual(upper["flash"], 0.0)
        self.assertEqual(game.score, 0)

    def test_ball_on_low_layer_uses_low_walls_only(self) -> None:
        game = self.make_game()
        game.load_level(1)
        game.ball_layer = cf.LAYER_LOW
        self.assertNotIn(game.upper_walls[0], game.active_walls())
        game.ball_layer = cf.LAYER_HIGH
        self.assertIn(game.upper_walls[0], game.active_walls())
        self.assertNotIn(game.walls[len(cf.FRAME_WALLS)], game.active_walls())

    def test_entering_ramp_zone_moves_ball_to_raised_layer(self) -> None:
        game = self.make_game()
        game.load_level(1)
        ramp = game.ramps[0]
        game.bx = ramp.x + ramp.w / 2
        game.by = ramp.y + ramp.h / 2
        game.bvx, game.bvy = 0.0, 0.0
        game._step_ball(0.0)
        self.assertEqual(game.ball_layer, cf.LAYER_HIGH)

    def test_leaving_raised_deck_returns_ball_to_low_layer(self) -> None:
        game = self.make_game()
        game.load_level(1)
        game.ball_layer = cf.LAYER_HIGH
        game.bx, game.by = 150.0, 180.0
        game.bvx, game.bvy = 0.0, 0.0
        game._step_ball(0.0)
        self.assertEqual(game.ball_layer, cf.LAYER_LOW)

    def test_layer_at_defaults_to_low_outside_zones(self) -> None:
        self.assertEqual(cf.layer_at((), 0.0, 0.0), cf.LAYER_LOW)

    def test_ramp_zone_sets_layer_inside_it(self) -> None:
        ramp = cf.RampZone(0.0, 0.0, 10.0, 10.0, cf.LAYER_HIGH)
        self.assertEqual(cf.layer_at((ramp,), 5.0, 5.0), cf.LAYER_HIGH)
        self.assertEqual(cf.layer_at((ramp,), 50.0, 50.0), cf.LAYER_LOW)

    def test_point_in_rect_includes_edges(self) -> None:
        self.assertTrue(cf.point_in_rect(0.0, 0.0, 0.0, 0.0, 10.0, 10.0))
        self.assertTrue(cf.point_in_rect(10.0, 10.0, 0.0, 0.0, 10.0, 10.0))
        self.assertFalse(cf.point_in_rect(10.1, 5.0, 0.0, 0.0, 10.0, 10.0))

    def test_shade_and_brighten_clamp_channels(self) -> None:
        self.assertEqual(cf.shade((200, 100, 0), 0.5), (100, 50, 0))
        self.assertEqual(cf.shade((200, 100, 0), 2.0), (255, 200, 0))
        self.assertEqual(cf.brighten((10, 250, 0), 20), (30, 255, 20))
        self.assertEqual(cf.brighten((10, 20, 30), -50), (0, 0, 0))

    def test_every_level_deck_fits_playfield(self) -> None:
        for level in LEVELS:
            for ramp in level.ramps:
                self.assertTrue(cf.PLAYFIELD_LEFT <= ramp.x and ramp.x + ramp.w <= cf.PLAYFIELD_RIGHT, level.name)
                self.assertIn(ramp.to_layer, (cf.LAYER_LOW, cf.LAYER_HIGH))

    def test_render_draws_ball_on_high_layer(self) -> None:
        game = self.make_game()
        game.load_level(1)
        game.ball_on_plunger = False
        game.ball_layer = cf.LAYER_HIGH
        game.bx, game.by = 60.0, 100.0
        surface = pygame.Surface((320, 240))
        game.render(surface)
        self.assertEqual(surface.get_at((60, 100))[:3], (215, 222, 232))

    def test_render_draws_plunger_with_charge(self) -> None:
        game = self.make_game()
        game.launcher_pulled = MAX_CHARGE
        surface = pygame.Surface((320, 240))
        game.render(surface)
        self.assertEqual(surface.get_at((290, 200))[:3], LEVELS[0].accent)

    def test_flipper_angles_follow_input(self) -> None:
        game = self.make_game()
        game.ball_on_plunger = True
        game.flipper_left_active = True
        game.update(0.05)
        self.assertLess(game.left_angle, FLIPPER_REST_ANGLE)
        self.assertTrue(game.left_rising)
        game.flipper_left_active = False
        game.update(0.05)
        self.assertFalse(game.left_rising)

    def test_right_flipper_follows_input(self) -> None:
        game = self.make_game()
        game.flipper_right_active = True
        game.update(0.05)
        self.assertLess(game.right_angle, FLIPPER_REST_ANGLE)
        self.assertTrue(game.right_rising)

    def test_drain_costs_ball_and_resets_plunger(self) -> None:
        game = self.make_game()
        game.ball_on_plunger = False
        game.bx, game.by = 150.0, cf.DRAIN_Y + 10.0
        game.update(0.0)
        self.assertEqual(game.balls_left, BALLS_PER_GAME - 1)
        self.assertTrue(game.ball_on_plunger)
        self.assertFalse(game.game_over)
        game.engine.audio.play.assert_any_call("gameover")

    def test_last_ball_drained_ends_game(self) -> None:
        game = self.make_game()
        game.balls_left = 1
        game.ball_on_plunger = False
        game.by = cf.DRAIN_Y + 10.0
        game.update(0.0)
        self.assertEqual(game.balls_left, 0)
        self.assertTrue(game.game_over)

    def test_ball_is_not_moved_when_on_plunger_even_with_gravity(self) -> None:
        game = self.make_game()
        game._drain_ball = mock.Mock()
        game.update(1.0)
        game._drain_ball.assert_not_called()

    # ----- collisions -----

    def test_collide_segment_without_overlap_does_nothing(self) -> None:
        game = self.make_game()
        game.bx, game.by = 100.0, 100.0
        game.bvx, game.bvy = 3.0, 4.0
        self.assertFalse(game._collide_segment(0.0, 0.0, 10.0, 0.0, 5.0, 1.0))
        self.assertEqual((game.bx, game.by, game.bvx, game.bvy), (100.0, 100.0, 3.0, 4.0))

    def test_collide_segment_pushes_out_and_reflects(self) -> None:
        game = self.make_game()
        game.bx, game.by = 50.0, 2.0
        game.bvx, game.bvy = 0.0, 10.0
        self.assertTrue(game._collide_segment(0.0, 5.0, 100.0, 5.0, 5.0, 1.0))
        self.assertAlmostEqual(game.by, 0.0)
        self.assertAlmostEqual(game.bvy, -10.0)

    def test_collide_segment_handles_ball_centred_on_segment(self) -> None:
        game = self.make_game()
        game.bx, game.by = 5.0, 0.0
        game.bvx, game.bvy = 0.0, 0.0
        self.assertTrue(game._collide_segment(0.0, 0.0, 10.0, 0.0, 5.0, 1.0))
        self.assertAlmostEqual(game.by, -5.0)

    def test_collide_segment_adds_kick_along_normal(self) -> None:
        game = self.make_game()
        game.bx, game.by = 50.0, 2.0
        game.bvx, game.bvy = 0.0, 0.0
        game._collide_segment(0.0, 5.0, 100.0, 5.0, 5.0, 0.0, kick=100.0)
        self.assertAlmostEqual(game.bvy, -100.0)

    def test_wall_collision_plays_sound(self) -> None:
        game = self.make_game()
        game.bx, game.by = 21.0, 100.0
        game.bvx, game.bvy = -50.0, 0.0
        game._collide_walls()
        self.assertGreater(game.bvx, 0.0)
        game.engine.audio.play.assert_any_call("hit")

    def test_no_wall_collision_in_open_table(self) -> None:
        game = self.make_game()
        game.bx, game.by = 150.0, 120.0
        game.bvx, game.bvy = 5.0, 5.0
        game._collide_walls()
        self.assertEqual((game.bx, game.by, game.bvx, game.bvy), (150.0, 120.0, 5.0, 5.0))

    def test_left_flipper_kicks_ball_up_when_rising(self) -> None:
        game = self.make_game()
        px, py = LEFT_PIVOT
        tx, ty = flipper_tip(-1, FLIPPER_REST_ANGLE)
        mx, my = (px + tx) / 2, (py + ty) / 2
        nx, ny = (ty - py), -(tx - px)
        length = (nx * nx + ny * ny) ** 0.5
        nx, ny = nx / length, ny / length
        game.bx, game.by = mx + nx * 7.0, my + ny * 7.0
        game.bvx, game.bvy = 0.0, 0.0
        game.left_rising = True
        game._collide_flippers()
        self.assertLess(game.bvy, -150.0)
        self.assertGreater(game.bvx, 0.0)
        self.assertGreater(len(game.particles), 0)
        game.engine.audio.play.assert_any_call("select")

    def test_static_flipper_does_not_kick(self) -> None:
        game = self.make_game()
        game.bx, game.by = 116.0, 200.0
        game.bvx, game.bvy = 0.0, 0.0
        game.left_rising = False
        game.right_rising = False
        game._collide_flippers()
        self.assertEqual(game.bvy, 0.0)

    def test_right_flipper_kicks_ball_up_when_rising(self) -> None:
        game = self.make_game()
        px, py = RIGHT_PIVOT
        tx, ty = flipper_tip(1, FLIPPER_REST_ANGLE)
        mx, my = (px + tx) / 2, (py + ty) / 2
        nx, ny = -(ty - py), (tx - px)
        length = (nx * nx + ny * ny) ** 0.5
        nx, ny = nx / length, ny / length
        game.bx, game.by = mx + nx * 7.0, my + ny * 7.0
        game.bvx, game.bvy = 0.0, 0.0
        game.right_rising = True
        game._collide_flippers()
        self.assertLess(game.bvy, -150.0)
        self.assertLess(game.bvx, 0.0)

    def test_bumper_collision_awards_points_and_boosts_ball(self) -> None:
        game = self.make_game()
        bumper = game.bumpers[0]
        game.bx, game.by = bumper["x"] + bumper["r"] + game.ball_radius - 1.0, bumper["y"]
        game.bvx, game.bvy = -50.0, 0.0
        game._collide_bumpers()
        self.assertEqual(game.score, bumper["pts"])
        self.assertEqual(game.level_score, bumper["pts"])
        self.assertGreater(game.bvx, 0.0)
        self.assertAlmostEqual(game.bvx, 50.0 * cf.BUMPER_RESTITUTION * cf.BUMPER_BOOST)
        self.assertEqual(bumper["flash"], 0.2)
        self.assertEqual(len(game.particles), 8)
        game.engine.audio.play.assert_any_call("score")

    def test_bumper_collision_at_exact_centre_is_handled(self) -> None:
        game = self.make_game()
        bumper = game.bumpers[0]
        game.bx, game.by = bumper["x"], bumper["y"]
        game.bvx, game.bvy = 0.0, 0.0
        game._collide_bumpers()
        self.assertLess(game.by, bumper["y"])
        self.assertGreater(game.score, 0)

    def test_no_bumper_collision_when_far_away(self) -> None:
        game = self.make_game()
        game.bx, game.by = 150.0, 220.0
        game._collide_bumpers()
        self.assertEqual(game.score, 0)

    def test_award_updates_total_and_level_score(self) -> None:
        game = self.make_game()
        game._award(120)
        self.assertEqual(game.score, 120)
        self.assertEqual(game.level_score, 120)

    # ----- level progression and win -----

    def test_reaching_target_advances_to_next_level(self) -> None:
        game = self.make_game()
        game.level_score = LEVELS[0].score_target
        game.balls_left = 1
        game._check_level_complete()
        self.assertEqual(game.level_index, 1)
        self.assertEqual(game.level, 2)
        self.assertEqual(game.balls_left, BALLS_PER_GAME)
        self.assertEqual(game.level_score, 0)
        self.assertFalse(game.game_won)

    def test_below_target_keeps_level(self) -> None:
        game = self.make_game()
        game.level_score = LEVELS[0].score_target - 1
        game._check_level_complete()
        self.assertEqual(game.level_index, 0)

    def test_update_checks_level_completion(self) -> None:
        game = self.make_game()
        game.level_score = LEVELS[0].score_target
        game.update(0.0)
        self.assertEqual(game.level_index, 1)

    def test_clearing_last_table_wins_game(self) -> None:
        game = self.make_game()
        game.load_level(len(LEVELS) - 1)
        game.level_score = LEVELS[-1].score_target
        game._check_level_complete()
        self.assertTrue(game.game_won)
        self.assertEqual(game.level_index, len(LEVELS) - 1)

    def test_all_tables_can_be_completed_in_sequence(self) -> None:
        game = self.make_game()
        for index, level in enumerate(LEVELS):
            self.assertEqual(game.level_index, index)
            game.level_score = level.score_target
            game._check_level_complete()
        self.assertTrue(game.game_won)

    def test_game_over_submits_level_number_to_highscores(self) -> None:
        game = self.make_game()
        game.load_level(2)
        game.game_over = True
        game.update(0.1)
        game.engine.highscores.submit_score.assert_called_once()
        args = game.engine.highscores.submit_score.call_args[0]
        self.assertEqual(args[0], "Cyber Flipper")
        self.assertEqual(args[2], 3)

    # ----- rendering -----

    def test_render_every_level_without_errors(self) -> None:
        game = self.make_game()
        surface = pygame.Surface((320, 240))
        for index in range(len(LEVELS)):
            game.load_level(index)
            game.render(surface)

    def test_render_with_active_effects(self) -> None:
        game = self.make_game()
        surface = pygame.Surface((320, 240))
        game.flipper_left_active = True
        game.flipper_right_active = True
        game.launcher_pulled = 15.0
        game.bumpers[0]["flash"] = 0.1
        game.particles = [{"x": 100.0, "y": 100.0, "vx": 0, "vy": 0, "life": 1, "color": (9, 9, 9)}]
        game.render(surface)

    def test_render_hides_plunger_charge_when_ball_in_play(self) -> None:
        game = self.make_game()
        surface = pygame.Surface((320, 240))
        game.ball_on_plunger = False
        game.launcher_pulled = 15.0
        game.render(surface)

    def test_render_draws_banner_only_briefly(self) -> None:
        game = self.make_game()
        surface = pygame.Surface((320, 240))
        game.banner_timer = 0.0
        game.render(surface)

    def test_render_flipper_colors_for_both_states(self) -> None:
        game = self.make_game()
        surface = pygame.Surface((320, 240))
        game._draw_flipper(surface, -1, FLIPPER_REST_ANGLE, False)
        game._draw_flipper(surface, -1, FLIPPER_ACTIVE_ANGLE, True)
        game._draw_flipper(surface, 1, FLIPPER_REST_ANGLE, False)
        game._draw_flipper(surface, 1, FLIPPER_ACTIVE_ANGLE, True)

    def test_render_hud_shows_table_and_balls(self) -> None:
        game = self.make_game()
        surface = pygame.Surface((320, 240))
        game._draw_hud(surface)


if __name__ == "__main__":
    unittest.main()

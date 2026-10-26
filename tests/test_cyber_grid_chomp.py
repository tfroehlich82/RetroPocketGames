from __future__ import annotations

import os
import random
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

from pocket_games.core.input import InputManager
from pocket_games.games.base import GAME_METADATA
from pocket_games.games.cyber_grid_chomp import (
    BLOCKED_TILES,
    MAX_LEVELS,
    PHANTOM_COUNTS,
    PHANTOM_SPAWNS,
    WALL_RECTS,
    CyberGridChompGame,
    _distance_map,
    _open_neighbors,
    _tile_center,
    _tile_of,
)


class MockEngine:
    def __init__(self) -> None:
        self.screen = pygame.Surface((320, 240))
        self.input = InputManager()
        self.audio = type("MockAudio", (), {"play": lambda s, name: None})()
        self.settings = type("MockSettings", (), {"language": "English"})()
        self.highscores = None


class TestCyberGridChomp(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def setUp(self) -> None:
        random.seed(1234)

    def make_game(self) -> CyberGridChompGame:
        game = CyberGridChompGame(MockEngine())
        game.showing_intro = False
        return game

    def place_player_on_tile(self, game: CyberGridChompGame, tile: tuple[int, int]) -> None:
        game.px, game.py = _tile_center(tile)
        game.pdir_x, game.pdir_y = 0.0, 0.0
        game.next_dir_x, game.next_dir_y = 0.0, 0.0

    def test_game_flow_and_input(self) -> None:
        engine = MockEngine()
        game = CyberGridChompGame(engine)
        game.showing_intro = False

        self.assertEqual(game.lives, 3)
        self.assertEqual(game.level, 1)

        # Simulate a direction change through input
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        pygame.event.post(event)
        engine.input.update()
        game.handle_input()
        self.assertEqual(game.next_dir_x, 1.0)

        # Simulate a collision with a phantom once the spawn grace period is over
        game.invulnerable_timer = 0.0
        game.px, game.py = 100.0, 100.0
        game.phantoms[0]["x"], game.phantoms[0]["y"] = 100.0, 100.0
        game.update(0.016)
        self.assertEqual(game.lives, 2)

    def test_player_is_safe_for_two_seconds_after_start(self) -> None:
        game = self.make_game()
        self.assertEqual(game.invulnerable_timer, 2.0)
        game.px, game.py = 100.0, 100.0
        game.phantoms[0]["x"], game.phantoms[0]["y"] = 100.0, 100.0
        game.update(0.016)
        self.assertEqual(game.lives, 3)
        game.update(1.9)
        self.assertGreater(game.invulnerable_timer, 0.0)
        game.px, game.py = 100.0, 100.0
        game.phantoms[0]["x"], game.phantoms[0]["y"] = 100.0, 100.0
        game.update(0.0)
        self.assertEqual(game.lives, 3)
        game.px, game.py = 250.0, 150.0
        game.phantoms[0]["x"], game.phantoms[0]["y"] = 60.0, 60.0
        game.update(0.2)
        self.assertEqual(game.lives, 3)
        game.px, game.py = 100.0, 100.0
        game.phantoms[0]["x"], game.phantoms[0]["y"] = 100.0, 100.0
        game.update(0.0)
        self.assertEqual(game.lives, 2)

    def test_bits_and_power_pills_are_centered_in_lanes(self) -> None:
        game = self.make_game()

        def blocked(x: float, y: float) -> bool:
            rect = pygame.Rect(int(x - 6), int(y - 6), 12, 12)
            return rect.collidelist(game.walls) != -1

        for item in game.bits + game.power_pills:
            x, y = item["x"], item["y"]
            for offset in (3, 4):
                self.assertEqual(blocked(x - offset, y), blocked(x + offset, y), (x, y))
                self.assertEqual(blocked(x, y - offset), blocked(x, y + offset), (x, y))

    def test_metadata_is_registered_for_game(self) -> None:
        self.assertIn("Cyber Grid Chomp", GAME_METADATA)
        for lang in ("de", "en"):
            entry = GAME_METADATA["Cyber Grid Chomp"][lang]
            for key in ("desc", "goal", "gameplay", "controls"):
                self.assertTrue(entry[key], f"{lang}.{key} must not be empty")

    def test_game_has_five_sectors(self) -> None:
        self.assertEqual(MAX_LEVELS, 5)
        game = self.make_game()
        self.assertEqual(game.level, 1)
        self.assertEqual(game.game_name, "Cyber Grid Chomp")

    def test_phantom_count_increases_per_level(self) -> None:
        counts = []
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game()
            game.level = level
            game._setup_level()
            counts.append(len(game.phantoms))
        self.assertEqual(counts, list(PHANTOM_COUNTS))
        self.assertEqual(counts, sorted(counts))
        self.assertGreater(counts[-1], counts[0])

    def test_phantom_speed_and_chase_chance_increase_per_level(self) -> None:
        speeds, chases = [], []
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game()
            game.level = level
            game._setup_level()
            speeds.append(game.phantom_speed)
            chases.append(game.chase_chance)
        self.assertEqual(speeds, sorted(speeds))
        self.assertEqual(len(set(speeds)), MAX_LEVELS)
        self.assertEqual(chases, sorted(chases))
        self.assertLessEqual(max(chases), 1.0)

    def test_overclock_duration_shrinks_per_level(self) -> None:
        durations = []
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game()
            game.level = level
            game._setup_level()
            durations.append(game.pill_duration)
        self.assertEqual(durations, sorted(durations, reverse=True))
        self.assertGreaterEqual(min(durations), 4.0)

    def test_each_level_has_data_bits_to_clear(self) -> None:
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game()
            game.level = level
            game._setup_level()
            self.assertGreater(len(game.bits), 0)

    def test_bits_and_phantoms_never_sit_inside_walls(self) -> None:
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game()
            game.level = level
            game._setup_level()
            for bit in game.bits:
                bit_rect = pygame.Rect(bit["x"] - 2, bit["y"] - 2, 4, 4)
                self.assertFalse(any(bit_rect.colliderect(w) for w in WALL_RECTS))
            for ph in game.phantoms:
                self.assertNotIn(_tile_of(ph["x"], ph["y"]), BLOCKED_TILES)

    def test_phantom_spawn_tiles_are_open(self) -> None:
        for tile in PHANTOM_SPAWNS:
            self.assertNotIn(tile, BLOCKED_TILES)

    def test_tile_helpers_clamp_to_grid(self) -> None:
        self.assertEqual(_tile_of(-50.0, -50.0), (0, 0))
        self.assertEqual(_tile_of(9999.0, 9999.0), (31, 23))
        self.assertEqual(_tile_center((2, 3)), (25.0, 35.0))

    def test_open_neighbors_skip_blocked_tiles(self) -> None:
        for tile in ((20, 11), (16, 11)):
            for nxt in _open_neighbors(tile):
                self.assertNotIn(nxt, BLOCKED_TILES)

    def test_distance_map_covers_connected_open_tiles_only(self) -> None:
        distances = _distance_map((16, 11))
        self.assertEqual(distances[(16, 11)], 0)
        self.assertEqual(distances[(19, 11)], 3)
        for tile in distances:
            self.assertNotIn(tile, BLOCKED_TILES)

    def test_hunting_phantom_steps_toward_player(self) -> None:
        game = self.make_game()
        game.chase_chance = 1.0
        game.overclock_timer = 0.0
        self.place_player_on_tile(game, (16, 11))
        ph = game.phantoms[0]
        ph["x"], ph["y"] = _tile_center((20, 11))
        ph["target"], ph["dx"], ph["dy"] = None, 0, 0
        self.assertEqual(game._choose_next_tile(ph), (19, 11))

    def test_fleeing_phantom_steps_away_from_player(self) -> None:
        game = self.make_game()
        game.overclock_timer = 5.0
        self.place_player_on_tile(game, (16, 11))
        ph = game.phantoms[0]
        ph["x"], ph["y"] = _tile_center((20, 11))
        ph["target"], ph["dx"], ph["dy"] = None, 0, 0
        for _ in range(10):
            self.assertIn(game._choose_next_tile(ph), {(21, 11), (20, 12)})

    def test_phantom_movement_stays_on_open_tiles(self) -> None:
        game = self.make_game()
        for _ in range(600):
            game.update(0.05)
            if game.game_over:
                break
            for ph in game.phantoms:
                self.assertNotIn(_tile_of(ph["x"], ph["y"]), BLOCKED_TILES)

    def test_higher_levels_chase_more_often_than_level_one(self) -> None:
        game = self.make_game()
        self.place_player_on_tile(game, (16, 11))
        ph = game.phantoms[0]
        ph["x"], ph["y"] = _tile_center((20, 11))
        ph["target"] = None

        def hunting_hits(chase: float) -> int:
            game.chase_chance = chase
            random.seed(99)
            hits = 0
            for _ in range(200):
                if game._choose_next_tile(ph) == (19, 11):
                    hits += 1
            return hits

        self.assertGreater(hunting_hits(1.0), hunting_hits(0.6))

    def test_player_cannot_walk_into_wall(self) -> None:
        game = self.make_game()
        game.px, game.py = 160.0, 31.0
        game.next_dir_x, game.next_dir_y = 0.0, -1.0
        game.update(0.1)
        self.assertEqual(game.pdir_y, 0.0)
        self.assertEqual(game.py, 31.0)

    def test_valid_turn_is_applied(self) -> None:
        game = self.make_game()
        self.place_player_on_tile(game, (16, 11))
        game.next_dir_x, game.next_dir_y = 1.0, 0.0
        start_x = game.px
        game.update(0.1)
        self.assertEqual((game.pdir_x, game.pdir_y), (1.0, 0.0))
        self.assertGreater(game.px, start_x)

    def test_player_wraps_around_horizontal_edges(self) -> None:
        game = self.make_game()
        game.px, game.py = 14.0, 110.0
        game.update(0.0)
        self.assertEqual(game.px, 290.0)

    def test_power_pill_activates_overclock(self) -> None:
        game = self.make_game()
        game.bits = [{"x": 1000, "y": 1000}]
        game.px, game.py = 30.0, 30.0
        game.update(0.0)
        self.assertEqual(game.overclock_timer, game.pill_duration)
        self.assertEqual(len(game.power_pills), 3)

    def test_eating_bit_adds_score(self) -> None:
        game = self.make_game()
        game.bits = [{"x": 1000, "y": 1000}, {"x": 160, "y": 110}]
        self.place_player_on_tile(game, (16, 11))
        game.update(0.0)
        self.assertEqual(game.score, 10)
        self.assertEqual(len(game.bits), 1)

    def test_phantom_collision_costs_life(self) -> None:
        game = self.make_game()
        game.bits = [{"x": 1000, "y": 1000}]
        game.invulnerable_timer = 0.0
        game.px, game.py = 200.0, 150.0
        game.phantoms[0]["x"], game.phantoms[0]["y"] = 200.0, 150.0
        game.update(0.0)
        self.assertEqual(game.lives, 2)
        self.assertEqual(game.invulnerable_timer, 2.0)
        self.assertEqual((game.px, game.py), (160.0, 110.0))

    def test_invulnerability_prevents_life_loss(self) -> None:
        game = self.make_game()
        game.bits = [{"x": 1000, "y": 1000}]
        game.invulnerable_timer = 1.0
        game.px, game.py = 200.0, 150.0
        game.phantoms[0]["x"], game.phantoms[0]["y"] = 200.0, 150.0
        game.update(0.0)
        self.assertEqual(game.lives, 3)

    def test_losing_last_life_ends_game(self) -> None:
        game = self.make_game()
        game.bits = [{"x": 1000, "y": 1000}]
        game.lives = 1
        game.invulnerable_timer = 0.0
        game.px, game.py = 200.0, 150.0
        game.phantoms[0]["x"], game.phantoms[0]["y"] = 200.0, 150.0
        game.update(0.0)
        self.assertEqual(game.lives, 0)
        self.assertTrue(game.game_over)

    def test_life_loss_resets_phantoms_to_spawns(self) -> None:
        game = self.make_game()
        game.bits = [{"x": 1000, "y": 1000}]
        game.phantoms[1]["x"], game.phantoms[1]["y"] = 40.0, 40.0
        game.invulnerable_timer = 0.0
        game.px, game.py = 200.0, 150.0
        game.phantoms[0]["x"], game.phantoms[0]["y"] = 200.0, 150.0
        game.update(0.0)
        for index, ph in enumerate(game.phantoms):
            self.assertEqual((ph["x"], ph["y"]), _tile_center(PHANTOM_SPAWNS[index]))

    def test_overclock_collision_eats_phantom_for_points(self) -> None:
        game = self.make_game()
        game.bits = [{"x": 1000, "y": 1000}]
        game.overclock_timer = 5.0
        game.px, game.py = 200.0, 150.0
        game.phantoms[0]["x"], game.phantoms[0]["y"] = 200.0, 150.0
        game.update(0.0)
        self.assertEqual(game.score, 300)
        self.assertEqual(game.lives, 3)
        self.assertEqual(
            (game.phantoms[0]["x"], game.phantoms[0]["y"]), _tile_center(PHANTOM_SPAWNS[0])
        )

    def test_clearing_sector_advances_level_and_awards_bonus(self) -> None:
        game = self.make_game()
        game.bits = []
        game.update(0.0)
        self.assertEqual(game.level, 2)
        self.assertEqual(game.score, 1000)
        self.assertGreater(game.banner_timer, 0.0)
        self.assertGreater(len(game.bits), 0)

    def test_clearing_final_sector_wins_game(self) -> None:
        game = self.make_game()
        game.level = MAX_LEVELS
        game._setup_level()
        game.bits = []
        game.update(0.0)
        self.assertTrue(game.game_won)
        self.assertEqual(game.level, MAX_LEVELS)

    def test_overclock_timer_expires(self) -> None:
        game = self.make_game()
        game.bits = [{"x": 1000, "y": 1000}]
        game.overclock_timer = 0.5
        game.update(1.0)
        self.assertLessEqual(game.overclock_timer, 0.0)

    def test_update_is_paused_when_paused(self) -> None:
        game = self.make_game()
        game.paused = True
        game.bits = [{"x": 1000, "y": 1000}]
        before = [dict(ph) for ph in game.phantoms]
        game.update(0.5)
        self.assertEqual(
            [(ph["x"], ph["y"]) for ph in game.phantoms],
            [(ph["x"], ph["y"]) for ph in before],
        )

    def test_render_all_sectors_without_errors(self) -> None:
        surface = pygame.Surface((320, 240))
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game()
            game.level = level
            game._setup_level()
            game.banner_timer = 1.0
            game.render(surface)
            game.overclock_timer = 5.0
            game.render(surface)
            game.invulnerable_timer = 1.0
            game.render(surface)

    def test_render_game_over_and_win_without_errors(self) -> None:
        surface = pygame.Surface((320, 240))
        game = self.make_game()
        game.game_over = True
        game.render(surface)
        game.game_over = False
        game.game_won = True
        game.render(surface)


if __name__ == "__main__":
    unittest.main()

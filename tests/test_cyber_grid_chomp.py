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
    GRID_COLS,
    GRID_ROWS,
    MAX_LEVELS,
    PHANTOM_COUNTS,
    PHANTOM_SPAWNS,
    PLAYER_SPAWN,
    POWER_PILL_TILES,
    SPAWN_INVULNERABILITY,
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


def open_tiles() -> set[tuple[int, int]]:
    return {(c, r) for c in range(GRID_COLS) for r in range(GRID_ROWS)} - BLOCKED_TILES


class TestCyberGridChomp(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((320, 240))

    def setUp(self) -> None:
        random.seed(1234)

    def make_game(self, level: int = 1) -> CyberGridChompGame:
        game = CyberGridChompGame(MockEngine())
        game.showing_intro = False
        if level != 1:
            game.level = level
            game._setup_level()
        game.invulnerable_timer = 0.0
        return game

    def place_player_on_tile(self, game: CyberGridChompGame, tile: tuple[int, int]) -> None:
        game.ptile = tile
        game.px, game.py = _tile_center(tile)
        game.ptarget = None
        game.pdir_x, game.pdir_y = 0.0, 0.0
        game.next_dir_x, game.next_dir_y = 0.0, 0.0

    def place_phantom_on_tile(self, game: CyberGridChompGame, index: int, tile: tuple[int, int]) -> dict:
        ph = game.phantoms[index]
        ph["x"], ph["y"] = _tile_center(tile)
        ph["target"], ph["dx"], ph["dy"] = None, 0, 0
        return ph

    def isolate_player_from_bits(self, game: CyberGridChompGame) -> None:
        game.bits = [{"x": 1000, "y": 1000}]

    def test_game_flow_and_input(self) -> None:
        engine = MockEngine()
        game = CyberGridChompGame(engine)
        game.showing_intro = False

        self.assertEqual(game.lives, 3)
        self.assertEqual(game.level, 1)

        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        pygame.event.post(event)
        engine.input.update()
        game.handle_input()
        self.assertEqual(game.next_dir_x, 1.0)

    def test_player_is_safe_for_two_seconds_after_start(self) -> None:
        game = CyberGridChompGame(MockEngine())
        game.showing_intro = False
        self.assertEqual(game.invulnerable_timer, SPAWN_INVULNERABILITY)
        self.isolate_player_from_bits(game)
        self.place_player_on_tile(game, (7, 7))
        self.place_phantom_on_tile(game, 0, (7, 7))
        game.update(0.016)
        self.assertEqual(game.lives, 3)
        game.update(1.9)
        self.assertGreater(game.invulnerable_timer, 0.0)
        self.place_phantom_on_tile(game, 0, (7, 7))
        game.update(0.0)
        self.assertEqual(game.lives, 3)
        game.invulnerable_timer = 0.0
        self.place_phantom_on_tile(game, 0, (7, 7))
        game.update(0.0)
        self.assertEqual(game.lives, 2)

    def test_player_starts_centered_on_spawn_tile(self) -> None:
        game = self.make_game()
        self.assertEqual((game.px, game.py), PLAYER_SPAWN)
        self.assertEqual(game.ptile, _tile_of(*PLAYER_SPAWN))

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

    def test_corridors_are_one_tile_wide(self) -> None:
        tiles = open_tiles()
        for col in range(GRID_COLS - 1):
            for row in range(GRID_ROWS - 1):
                block = {(col, row), (col + 1, row), (col, row + 1), (col + 1, row + 1)}
                self.assertFalse(block <= tiles, f"2x2 open area at {(col, row)}")

    def test_all_open_tiles_are_reachable_from_spawn(self) -> None:
        distances = _distance_map(PHANTOM_SPAWNS[0])
        self.assertEqual(set(distances), open_tiles())

    def test_level_layout_is_reproducible(self) -> None:
        for level in range(1, MAX_LEVELS + 1):
            random.seed(1)
            first = self.make_game(level)
            random.seed(999)
            second = self.make_game(level)
            self.assertEqual(
                [(b["x"], b["y"]) for b in first.bits], [(b["x"], b["y"]) for b in second.bits]
            )
            self.assertEqual(
                [(p["x"], p["y"]) for p in first.phantoms], [(p["x"], p["y"]) for p in second.phantoms]
            )

    def test_phantom_behaviour_is_reproducible_regardless_of_global_random(self) -> None:
        def simulate(global_seed: int) -> list[tuple[float, float]]:
            random.seed(global_seed)
            game = self.make_game(level=3)
            track = []
            for _ in range(200):
                game.update(0.05)
                track.extend((ph["x"], ph["y"]) for ph in game.phantoms)
                if game.game_over:
                    break
            return track

        self.assertEqual(simulate(1), simulate(777))

    def test_phantom_count_increases_per_level(self) -> None:
        counts = []
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game(level)
            counts.append(len(game.phantoms))
        self.assertEqual(counts, list(PHANTOM_COUNTS))
        self.assertEqual(counts, sorted(counts))
        self.assertGreater(counts[-1], counts[0])

    def test_phantom_speed_and_chase_chance_increase_per_level(self) -> None:
        speeds, chases = [], []
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game(level)
            speeds.append(game.phantom_speed)
            chases.append(game.chase_chance)
        self.assertEqual(speeds, sorted(speeds))
        self.assertEqual(len(set(speeds)), MAX_LEVELS)
        self.assertEqual(chases, sorted(chases))
        self.assertLessEqual(max(chases), 1.0)

    def test_overclock_duration_shrinks_per_level(self) -> None:
        durations = []
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game(level)
            durations.append(game.pill_duration)
        self.assertEqual(durations, sorted(durations, reverse=True))
        self.assertGreaterEqual(min(durations), 4.0)

    def test_each_level_has_data_bits_to_clear(self) -> None:
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game(level)
            self.assertGreater(len(game.bits), 0)

    def test_bits_and_phantoms_never_sit_inside_walls(self) -> None:
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game(level)
            for bit in game.bits:
                self.assertNotIn(_tile_of(bit["x"], bit["y"]), BLOCKED_TILES)
            for ph in game.phantoms:
                self.assertNotIn(_tile_of(ph["x"], ph["y"]), BLOCKED_TILES)

    def test_phantom_spawn_tiles_are_open(self) -> None:
        for tile in PHANTOM_SPAWNS:
            self.assertNotIn(tile, BLOCKED_TILES)
        for tile in POWER_PILL_TILES:
            self.assertNotIn(tile, BLOCKED_TILES)

    def test_wall_rects_match_blocked_tiles(self) -> None:
        self.assertEqual(len(WALL_RECTS), len(BLOCKED_TILES))

    def test_tile_helpers_clamp_to_grid(self) -> None:
        self.assertEqual(_tile_of(-50.0, -50.0), (0, 0))
        self.assertEqual(_tile_of(9999.0, 9999.0), (GRID_COLS - 1, GRID_ROWS - 1))
        self.assertEqual(_tile_center((2, 3)), (60.0, 80.0))

    def test_open_neighbors_skip_blocked_tiles(self) -> None:
        self.assertEqual(set(_open_neighbors((1, 1))), {(2, 1), (1, 2)})
        for tile in open_tiles():
            for nxt in _open_neighbors(tile):
                self.assertNotIn(nxt, BLOCKED_TILES)

    def test_distance_map_covers_connected_open_tiles_only(self) -> None:
        distances = _distance_map((7, 7))
        self.assertEqual(distances[(7, 7)], 0)
        self.assertEqual(distances[(8, 7)], 1)
        for tile in distances:
            self.assertNotIn(tile, BLOCKED_TILES)

    def test_hunting_phantom_steps_toward_player(self) -> None:
        game = self.make_game()
        game.chase_chance = 1.0
        game.overclock_timer = 0.0
        self.place_player_on_tile(game, (7, 7))
        ph = self.place_phantom_on_tile(game, 0, (11, 7))
        self.assertEqual(game._choose_next_tile(ph), (10, 7))

    def test_fleeing_phantom_steps_away_from_player(self) -> None:
        game = self.make_game()
        game.overclock_timer = 5.0
        self.place_player_on_tile(game, (7, 7))
        ph = self.place_phantom_on_tile(game, 0, (11, 7))
        for _ in range(10):
            self.assertIn(game._choose_next_tile(ph), {(11, 6), (12, 7)})

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
        self.place_player_on_tile(game, (7, 7))
        ph = self.place_phantom_on_tile(game, 0, (11, 7))

        def hunting_hits(chase: float) -> int:
            game.chase_chance = chase
            random.seed(99)
            hits = 0
            for _ in range(200):
                if game._choose_next_tile(ph) == (10, 7):
                    hits += 1
            return hits

        self.assertGreater(hunting_hits(1.0), hunting_hits(0.6))

    def test_player_cannot_walk_into_wall(self) -> None:
        game = self.make_game()
        self.isolate_player_from_bits(game)
        self.place_player_on_tile(game, (1, 1))
        start = (game.px, game.py)
        game.next_dir_x, game.next_dir_y = 0.0, -1.0
        game.update(0.1)
        self.assertEqual((game.pdir_x, game.pdir_y), (0.0, 0.0))
        self.assertEqual((game.px, game.py), start)

    def test_valid_turn_is_applied(self) -> None:
        game = self.make_game()
        self.place_player_on_tile(game, (7, 7))
        game.next_dir_x, game.next_dir_y = 1.0, 0.0
        start_x = game.px
        game.update(0.1)
        self.assertEqual((game.pdir_x, game.pdir_y), (1.0, 0.0))
        self.assertGreater(game.px, start_x)

    def test_player_stays_in_lane_while_moving(self) -> None:
        game = self.make_game()
        self.isolate_player_from_bits(game)
        self.place_player_on_tile(game, (7, 7))
        game.next_dir_x, game.next_dir_y = 1.0, 0.0
        lane_y = _tile_center((7, 7))[1]
        for _ in range(40):
            game.update(0.02)
            self.assertEqual(game.py, lane_y)

    def test_player_reaches_next_tile_center_exactly(self) -> None:
        game = self.make_game()
        self.isolate_player_from_bits(game)
        self.place_player_on_tile(game, (7, 7))
        game.next_dir_x, game.next_dir_y = 1.0, 0.0
        for _ in range(30):
            game.update(0.02)
            if game.ptile == (8, 7):
                break
        self.assertEqual(game.ptile, (8, 7))
        self.assertEqual((game.px, game.py), _tile_center((8, 7)))

    def test_power_pill_activates_overclock(self) -> None:
        game = self.make_game()
        self.isolate_player_from_bits(game)
        self.place_player_on_tile(game, POWER_PILL_TILES[0])
        game.update(0.0)
        self.assertEqual(game.overclock_timer, game.pill_duration)
        self.assertEqual(len(game.power_pills), 3)

    def test_eating_bit_adds_score(self) -> None:
        game = self.make_game()
        game.bits = [{"x": 1000, "y": 1000}, {"x": _tile_center((7, 7))[0], "y": _tile_center((7, 7))[1]}]
        self.place_player_on_tile(game, (7, 7))
        game.update(0.0)
        self.assertEqual(game.score, 10)
        self.assertEqual(len(game.bits), 1)

    def test_phantom_collision_costs_life(self) -> None:
        game = self.make_game()
        game.invulnerable_timer = 0.0
        self.isolate_player_from_bits(game)
        self.place_player_on_tile(game, (7, 7))
        self.place_phantom_on_tile(game, 0, (7, 7))
        game.update(0.0)
        self.assertEqual(game.lives, 2)
        self.assertEqual(game.invulnerable_timer, SPAWN_INVULNERABILITY)
        self.assertEqual((game.px, game.py), PLAYER_SPAWN)

    def test_invulnerability_prevents_life_loss(self) -> None:
        game = self.make_game()
        self.isolate_player_from_bits(game)
        game.invulnerable_timer = 1.0
        self.place_player_on_tile(game, (7, 7))
        self.place_phantom_on_tile(game, 0, (7, 7))
        game.update(0.0)
        self.assertEqual(game.lives, 3)

    def test_losing_last_life_ends_game(self) -> None:
        game = self.make_game()
        self.isolate_player_from_bits(game)
        game.lives = 1
        self.place_player_on_tile(game, (7, 7))
        self.place_phantom_on_tile(game, 0, (7, 7))
        game.update(0.0)
        self.assertEqual(game.lives, 0)
        self.assertTrue(game.game_over)

    def test_life_loss_resets_phantoms_to_spawns(self) -> None:
        game = self.make_game()
        self.isolate_player_from_bits(game)
        self.place_phantom_on_tile(game, 1, (2, 2))
        self.place_player_on_tile(game, (7, 7))
        self.place_phantom_on_tile(game, 0, (7, 7))
        game.update(0.0)
        for index, ph in enumerate(game.phantoms):
            self.assertEqual((ph["x"], ph["y"]), _tile_center(PHANTOM_SPAWNS[index]))

    def test_overclock_collision_eats_phantom_for_points(self) -> None:
        game = self.make_game()
        self.isolate_player_from_bits(game)
        game.overclock_timer = 5.0
        self.place_player_on_tile(game, PHANTOM_SPAWNS[0])
        self.place_phantom_on_tile(game, 0, PHANTOM_SPAWNS[0])
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
        game = self.make_game(level=MAX_LEVELS)
        game.bits = []
        game.update(0.0)
        self.assertTrue(game.game_won)
        self.assertEqual(game.level, MAX_LEVELS)

    def test_overclock_timer_expires(self) -> None:
        game = self.make_game()
        self.isolate_player_from_bits(game)
        game.overclock_timer = 0.5
        game.update(1.0)
        self.assertLessEqual(game.overclock_timer, 0.0)

    def test_update_is_paused_when_paused(self) -> None:
        game = self.make_game()
        game.paused = True
        self.isolate_player_from_bits(game)
        before = [(ph["x"], ph["y"]) for ph in game.phantoms]
        game.update(0.5)
        self.assertEqual([(ph["x"], ph["y"]) for ph in game.phantoms], before)

    def test_render_all_sectors_without_errors(self) -> None:
        surface = pygame.Surface((320, 240))
        for level in range(1, MAX_LEVELS + 1):
            game = self.make_game(level)
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

    def test_metadata_is_registered_for_game(self) -> None:
        self.assertIn("Cyber Grid Chomp", GAME_METADATA)
        for lang in ("de", "en"):
            entry = GAME_METADATA["Cyber Grid Chomp"][lang]
            for key in ("desc", "goal", "gameplay", "controls"):
                self.assertTrue(entry[key], f"{lang}.{key} must not be empty")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"

from pocket_games.core.settings import CYBER_FLIPPER_TUNING_FILE, TUNING_DIR
from pocket_games.core.tuning import get_number, get_section, load_tuning_file
from pocket_games.games import cyber_flipper as cf


class TestLoadTuningFile(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_none_path_returns_empty_dict(self) -> None:
        self.assertEqual(load_tuning_file(None), {})

    def test_missing_file_returns_empty_dict(self) -> None:
        self.assertEqual(load_tuning_file(self.dir / "missing.json"), {})

    def test_valid_object_is_loaded(self) -> None:
        path = self.dir / "tuning.json"
        path.write_text(json.dumps({"physics": {"gravity": 1.0}}), encoding="utf-8")
        self.assertEqual(load_tuning_file(path), {"physics": {"gravity": 1.0}})

    def test_non_object_json_raises(self) -> None:
        path = self.dir / "list.json"
        path.write_text("[1, 2, 3]", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_tuning_file(path)

    def test_utf8_content_is_read(self) -> None:
        path = self.dir / "utf8.json"
        path.write_text(json.dumps({"name": "Größe"}, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(load_tuning_file(path)["name"], "Größe")


class TestSectionAndNumberHelpers(unittest.TestCase):
    def test_get_section_returns_dict(self) -> None:
        self.assertEqual(get_section({"a": {"b": 1}}, "a"), {"b": 1})

    def test_get_section_missing_returns_empty(self) -> None:
        self.assertEqual(get_section({}, "a"), {})

    def test_get_section_non_dict_returns_empty(self) -> None:
        self.assertEqual(get_section({"a": 5}, "a"), {})

    def test_get_number_uses_value_when_present(self) -> None:
        self.assertEqual(get_number({"speed": 3}, "speed", 1.0), 3.0)

    def test_get_number_uses_default_when_missing(self) -> None:
        self.assertEqual(get_number({}, "speed", 1.5), 1.5)


class TestCyberFlipperTuningData(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads(CYBER_FLIPPER_TUNING_FILE.read_text(encoding="utf-8"))

    def test_tuning_file_lives_in_data_tuning_folder(self) -> None:
        self.assertEqual(CYBER_FLIPPER_TUNING_FILE.parent, TUNING_DIR)
        self.assertTrue(CYBER_FLIPPER_TUNING_FILE.is_file())

    def test_physics_constants_match_json(self) -> None:
        physics = self.data["physics"]
        self.assertEqual(cf.BALL_RADIUS, physics["ball_radius"])
        self.assertEqual(cf.MAX_BALL_SPEED, physics["max_ball_speed"])
        self.assertEqual(cf.BALLS_PER_GAME, physics["balls_per_game"])
        self.assertEqual(cf.LAUNCH_BASE_SPEED, physics["launch_base_speed"])

    def test_level_count_matches_json(self) -> None:
        self.assertEqual(len(cf.LEVELS), len(self.data["levels"]))

    def test_level_names_match_json_order(self) -> None:
        self.assertEqual([lvl.name for lvl in cf.LEVELS], [e["name"] for e in self.data["levels"]])

    def test_frame_walls_loaded_from_json(self) -> None:
        self.assertEqual(len(cf.FRAME_WALLS), len(self.data["frame_walls"]))

    def test_vortex_ring_bumpers_are_expanded(self) -> None:
        vortex = cf.LEVELS[3]
        ring = self.data["levels"][3]["ring_bumpers"]
        self.assertEqual(vortex.bumpers[0][3], ring["pts"])
        self.assertEqual(len(vortex.bumpers), ring["count"] + len(self.data["levels"][3]["bumpers"]))

    def test_game_loads_tuning_file(self) -> None:
        from tests.test_cyber_flipper import MockEngine

        game = cf.CyberFlipperGame(MockEngine())
        self.assertEqual(game.tuning, self.data)


class TestCyberFlipperBuilders(unittest.TestCase):
    def test_pair_returns_floats_for_valid_input(self) -> None:
        self.assertEqual(cf._pair([1, 2], (0.0, 0.0)), (1.0, 2.0))

    def test_pair_falls_back_for_invalid_input(self) -> None:
        self.assertEqual(cf._pair("nope", (3.0, 4.0)), (3.0, 4.0))
        self.assertEqual(cf._pair([1], (3.0, 4.0)), (3.0, 4.0))

    def test_color_returns_default_for_invalid_input(self) -> None:
        self.assertEqual(cf._color([1, 2], (9, 9, 9)), (9, 9, 9))
        self.assertEqual(cf._color([1, 2, 3], (9, 9, 9)), (1, 2, 3))

    def test_segment_builds_two_points(self) -> None:
        self.assertEqual(cf._segment([[0, 1], [2, 3]]), ((0.0, 1.0), (2.0, 3.0)))

    def test_bumper_builds_specification(self) -> None:
        spec = cf._bumper([10, 20, 5, 100, [1, 2, 3]])
        self.assertEqual(spec, (10.0, 20.0, 5.0, 100, (1, 2, 3)))

    def test_ramp_builds_zone(self) -> None:
        ramp = cf._ramp({"x": 1, "y": 2, "w": 3, "h": 4, "to_layer": 1})
        self.assertEqual(ramp, cf.RampZone(1.0, 2.0, 3.0, 4.0, 1))

    def test_build_level_applies_defaults(self) -> None:
        level = cf._build_level({"name": "Plain"})
        self.assertEqual(level.name, "Plain")
        self.assertEqual(level.gravity, 450.0)
        self.assertEqual(level.score_target, 1500)
        self.assertEqual(level.bumpers, ())
        self.assertEqual(level.ramps, ())

    def test_build_level_expands_ring_bumpers(self) -> None:
        level = cf._build_level(
            {
                "name": "Ring",
                "ring_bumpers": {"cx": 0, "cy": 0, "radius": 10, "count": 4, "pts": 7, "color": [1, 1, 1]},
                "bumpers": [[5, 5, 2, 1, [0, 0, 0]]],
            }
        )
        self.assertEqual(len(level.bumpers), 5)

    def test_build_levels_empty_when_no_levels(self) -> None:
        self.assertEqual(cf._build_levels({}), ())


if __name__ == "__main__":
    unittest.main()

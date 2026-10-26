from __future__ import annotations

import contextlib
import os
import unittest
from unittest import mock

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame

from pocket_games.core import engine as engine_module
from pocket_games.core.engine import VIRTUAL_HEIGHT, VIRTUAL_WIDTH, Engine


def make_settings(fullscreen: bool = True, sound_enabled: bool = True, master_volume: float = 0.6):
    settings = mock.Mock()
    settings.fullscreen = fullscreen
    settings.sound_enabled = sound_enabled
    settings.master_volume = master_volume
    return settings


@contextlib.contextmanager
def patched_engine_environment(platform: str, fullscreen: bool = True):
    settings = make_settings(fullscreen=fullscreen)
    with mock.patch.object(engine_module, "sys") as fake_sys, \
            mock.patch.object(engine_module, "Settings", return_value=settings), \
            mock.patch.object(engine_module, "HighScoreManager") as highscores_cls, \
            mock.patch.object(engine_module, "InputManager") as input_cls, \
            mock.patch.object(engine_module, "AudioManager") as audio_cls, \
            mock.patch.object(pygame.display, "set_mode", return_value=pygame.Surface((1, 1))) as set_mode, \
            mock.patch.object(pygame.display, "set_caption") as set_caption:
        fake_sys.platform = platform
        yield {
            "settings": settings,
            "highscores_cls": highscores_cls,
            "input_cls": input_cls,
            "audio_cls": audio_cls,
            "set_mode": set_mode,
            "set_caption": set_caption,
        }


class TestEngineInit(unittest.TestCase):
    def test_windows_uses_windowed_640x480(self) -> None:
        with patched_engine_environment("win32", fullscreen=True) as mocks:
            Engine("Test Title")
            mocks["set_mode"].assert_called_once_with((640, 480), 0)

    def test_linux_fullscreen_uses_480x320_with_fullscreen_flag(self) -> None:
        with patched_engine_environment("linux", fullscreen=True) as mocks:
            Engine()
            mocks["set_mode"].assert_called_once_with((480, 320), pygame.FULLSCREEN)

    def test_linux_windowed_uses_480x320_without_fullscreen_flag(self) -> None:
        with patched_engine_environment("linux", fullscreen=False) as mocks:
            Engine()
            mocks["set_mode"].assert_called_once_with((480, 320), 0)

    def test_window_caption_uses_given_title(self) -> None:
        with patched_engine_environment("win32") as mocks:
            Engine("Custom Title")
            mocks["set_caption"].assert_called_once_with("Custom Title")

    def test_default_title_is_used_when_none_given(self) -> None:
        with patched_engine_environment("win32") as mocks:
            Engine()
            mocks["set_caption"].assert_called_once_with("RetroPocket Games")

    def test_audio_is_configured_from_settings(self) -> None:
        with patched_engine_environment("win32", fullscreen=False) as mocks:
            eng = Engine()
            mocks["audio_cls"].assert_called_once_with(enabled=True)
            eng.audio.set_volume.assert_called_once_with(0.6)

    def test_sound_disabled_setting_is_forwarded_to_audio(self) -> None:
        settings = make_settings(sound_enabled=False, master_volume=0.25)
        with mock.patch.object(engine_module, "Settings", return_value=settings), \
                mock.patch.object(engine_module, "HighScoreManager"), \
                mock.patch.object(engine_module, "InputManager"), \
                mock.patch.object(engine_module, "AudioManager") as audio_cls, \
                mock.patch.object(pygame.display, "set_mode", return_value=pygame.Surface((1, 1))), \
                mock.patch.object(pygame.display, "set_caption"):
            audio_cls.return_value.set_volume = mock.Mock()
            Engine()
            audio_cls.assert_called_once_with(enabled=False)
            audio_cls.return_value.set_volume.assert_called_once_with(0.25)

    def test_engine_creates_virtual_surface_and_running_state(self) -> None:
        with patched_engine_environment("win32"):
            eng = Engine()
            self.assertEqual(eng.virtual_surface.get_size(), (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
            self.assertTrue(eng.running)
            self.assertIsNotNone(eng.clock)

    def test_engine_wires_managers_from_constructors(self) -> None:
        with patched_engine_environment("win32") as mocks:
            eng = Engine()
            self.assertIs(eng.settings, mocks["settings"])
            self.assertIs(eng.highscores, mocks["highscores_cls"].return_value)
            self.assertIs(eng.input, mocks["input_cls"].return_value)
            self.assertIs(eng.audio, mocks["audio_cls"].return_value)


class TestRenderToScreen(unittest.TestCase):
    def setUp(self) -> None:
        pygame.init()
        self.eng = Engine.__new__(Engine)
        self.eng.virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        self.eng.screen = pygame.Surface((640, 480))

    def test_virtual_surface_is_scaled_onto_screen(self) -> None:
        self.eng.virtual_surface.fill((255, 0, 0))
        with mock.patch.object(pygame.display, "flip") as flip:
            self.eng.render_to_screen()
            flip.assert_called_once()
        self.assertEqual(self.eng.screen.get_size(), (640, 480))
        self.assertEqual(self.eng.screen.get_at((0, 0))[:3], (255, 0, 0))
        self.assertEqual(self.eng.screen.get_at((639, 479))[:3], (255, 0, 0))

    def test_scaling_follows_screen_size(self) -> None:
        self.eng.screen = pygame.Surface((480, 320))
        self.eng.virtual_surface.fill((0, 255, 0))
        with mock.patch.object(pygame.display, "flip"):
            self.eng.render_to_screen()
        self.assertEqual(self.eng.screen.get_at((479, 319))[:3], (0, 255, 0))


class FakeScene:
    def __init__(self, engine, frames: int = 3) -> None:
        self.engine = engine
        self.active = True
        self.frames_left = frames
        self.input_calls = 0
        self.update_dts: list[float] = []
        self.render_calls = 0

    def handle_input(self) -> None:
        self.input_calls += 1

    def update(self, dt: float) -> None:
        self.update_dts.append(dt)
        self.frames_left -= 1
        if self.frames_left <= 0:
            self.active = False

    def render(self, surface) -> None:
        self.render_calls += 1


class ScoredScene(FakeScene):
    game_name = "Test Game"
    score = 42


class ScoreOnlyScene(FakeScene):
    score = 7


def make_run_engine() -> Engine:
    pygame.init()
    eng = Engine.__new__(Engine)
    eng.running = True
    eng.clock = mock.Mock()
    eng.clock.tick.return_value = 16
    eng.input = mock.Mock()
    eng.highscores = mock.Mock()
    eng.virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    eng.screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    eng.render_to_screen = mock.Mock()
    return eng


class TestRunScene(unittest.TestCase):
    def test_loop_runs_until_scene_inactive(self) -> None:
        eng = make_run_engine()
        created = {}

        def factory(engine):
            scene = FakeScene(engine, frames=3)
            created["scene"] = scene
            return scene

        eng.run_scene(factory)
        scene = created["scene"]
        self.assertEqual(scene.input_calls, 3)
        self.assertEqual(scene.render_calls, 3)
        self.assertEqual(eng.render_to_screen.call_count, 3)
        self.assertEqual(len(scene.update_dts), 3)

    def test_delta_time_is_derived_from_clock_in_seconds(self) -> None:
        eng = make_run_engine()
        created = {}

        def factory(engine):
            created["scene"] = FakeScene(engine, frames=1)
            return created["scene"]

        eng.run_scene(factory)
        eng.clock.tick.assert_called_with(60)
        self.assertAlmostEqual(created["scene"].update_dts[0], 0.016)

    def test_loop_does_not_run_when_engine_stopped(self) -> None:
        eng = make_run_engine()
        eng.running = False
        created = {}

        def factory(engine):
            created["scene"] = FakeScene(engine, frames=5)
            return created["scene"]

        eng.run_scene(factory)
        self.assertEqual(created["scene"].render_calls, 0)
        eng.render_to_screen.assert_not_called()

    def test_loop_stops_when_engine_flag_cleared_mid_run(self) -> None:
        eng = make_run_engine()

        class StoppingScene(FakeScene):
            def update(self, dt: float) -> None:
                super().update(dt)
                self.engine.running = False

        eng.run_scene(lambda engine: StoppingScene(engine, frames=10))
        eng.render_to_screen.assert_called_once()

    def test_score_is_submitted_when_scene_has_game_name_and_score(self) -> None:
        eng = make_run_engine()
        eng.run_scene(lambda engine: ScoredScene(engine, frames=1))
        eng.highscores.submit_score.assert_called_once_with("Test Game", 42)

    def test_score_not_submitted_without_game_name(self) -> None:
        eng = make_run_engine()
        eng.run_scene(lambda engine: ScoreOnlyScene(engine, frames=1))
        eng.highscores.submit_score.assert_not_called()

    def test_score_not_submitted_when_highscores_missing(self) -> None:
        eng = make_run_engine()
        eng.highscores = None
        eng.run_scene(lambda engine: ScoredScene(engine, frames=1))
        self.assertIsNone(eng.highscores)

    def test_errors_in_scene_are_logged_and_reraised(self) -> None:
        eng = make_run_engine()

        class BrokenScene(FakeScene):
            def update(self, dt: float) -> None:
                raise ValueError("boom")

        with mock.patch.object(engine_module, "logger") as logger_mock:
            with self.assertRaises(Exception):
                eng.run_scene(BrokenScene)
            logger_mock.error.assert_called_once()
            self.assertIn("BrokenScene", logger_mock.error.call_args.args[0])

    def test_errors_do_not_submit_score(self) -> None:
        eng = make_run_engine()

        class BrokenScoredScene(ScoredScene):
            def render(self, surface) -> None:
                raise RuntimeError("render failed")

        with mock.patch.object(engine_module, "logger"):
            with self.assertRaises(Exception):
                eng.run_scene(lambda engine: BrokenScoredScene(engine, frames=1))
        eng.highscores.submit_score.assert_not_called()


if __name__ == "__main__":
    unittest.main()

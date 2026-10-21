from __future__ import annotations

import json
from pathlib import Path

import pygame

BASE_DIR = Path(__file__).resolve().parent.parent

TRANSLATIONS_FILE = BASE_DIR / "data/translations.json"
TRANSLATIONS = json.loads(TRANSLATIONS_FILE.read_text())

GAME_METADATA_FILE = BASE_DIR / "data/game_metadata.json"
GAME_METADATA = json.loads(GAME_METADATA_FILE.read_text())

def t(engine, key: str) -> str:
    lang = "English"
    if hasattr(engine, "settings") and engine.settings:
        lang = getattr(engine.settings, "language", "English")
    if lang not in TRANSLATIONS:
        lang = "English"
    return TRANSLATIONS[lang].get(key, key)


class BaseGame:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if "handle_input" in cls.__dict__:
            orig_handle = cls.__dict__["handle_input"]
            def wrapped_handle(self, *args, **kwargs):
                BaseGame.handle_input(self)
                if self.showing_intro or self.game_over:
                    return
                return orig_handle(self, *args, **kwargs)
            cls.handle_input = wrapped_handle

        if "update" in cls.__dict__:
            orig_update = cls.__dict__["update"]
            def wrapped_update(self, dt, *args, **kwargs):
                BaseGame.update(self, dt)
                if self.showing_intro or self.game_over:
                    return
                res = orig_update(self, dt, *args, **kwargs)
                if (
                    self.game_over
                    and hasattr(self, "engine")
                    and self.engine
                    and hasattr(self.engine, "highscores")
                ):
                    self.engine.highscores.submit_score(self.game_name, self.score)
                return res
            cls.update = wrapped_update

        if "render" in cls.__dict__:
            orig_render = cls.__dict__["render"]
            def wrapped_render(self, surface, *args, **kwargs):
                if self.showing_intro:
                    self.render_intro(surface)
                    return
                orig_render(self, surface, *args, **kwargs)
                if self.game_over:
                    self.render_game_over(surface)
                return
            cls.render = wrapped_render

    def __init__(self, engine, game_name: str) -> None:
        self.engine = engine
        self.game_name = game_name
        self.active = True
        self.paused = False
        self.game_over = False
        self.score = 0
        self.elapsed_time = 0.0
        self.showing_intro = True

        lang = "English"
        if hasattr(self.engine, "settings") and self.engine.settings:
            lang = getattr(self.engine.settings, "language", "English")
        lang_key = "de" if lang == "Deutsch" else "en"

        game_data = GAME_METADATA.get(game_name, {})
        meta = game_data.get(
            lang_key,
            game_data.get(
                "en",
                {
                    "desc": "An exciting retro game.",
                    "goal": "Achieve the highest score.",
                    "gameplay": "Play skillfully.",
                    "controls": "D-Pad & A",
                },
            ),
        )
        self.description = meta["desc"]
        self.goal = meta["goal"]
        self.gameplay = meta["gameplay"]
        self.controls = meta["controls"]

        try:
            self.font = pygame.font.Font(None, 18)
            self.title_font = pygame.font.Font(None, 24)
        except Exception:  # noqa: BLE001
            self.font = pygame.font.SysFont("sans-serif", 16)
            self.title_font = pygame.font.SysFont("sans-serif", 22)

    @property
    def difficulty_factor(self) -> float:
        return 1.0 + self.elapsed_time * 0.03

    def get_virtual_mouse_pos(self) -> tuple[int, int]:
        inp = getattr(self.engine, "input", None)
        raw_pos = (
            inp.mouse_pos
            if inp and hasattr(inp, "mouse_pos")
            else pygame.mouse.get_pos()
        )

        if hasattr(self.engine, "screen") and self.engine.screen:
            mw, mh = self.engine.screen.get_size()
        else:
            surf = pygame.display.get_surface()
            mw, mh = surf.get_size() if surf else (320, 240)

        vx = int(raw_pos[0] * (320 / max(1, mw)))
        vy = int(raw_pos[1] * (240 / max(1, mh)))
        return (vx, vy)

    def add_score(self, amount: int) -> None:
        self.score += amount

    def play_sound(self, sound_name: str) -> None:
        if hasattr(self.engine, "audio") and self.engine.audio:
            self.engine.audio.play(sound_name)

    def render_ui(self, surface: pygame.Surface) -> None:
        score_txt = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        surface.blit(score_txt, (10, 5))

    def handle_input(self) -> None:
        inp = getattr(self.engine, "input", None)
        if not inp:
            return

        back_pressed = False
        if hasattr(inp, "is_back_pressed") and callable(inp.is_back_pressed):
            back_pressed = inp.is_back_pressed()
        elif hasattr(inp, "is_key_just_pressed"):
            back_pressed = inp.is_key_just_pressed(
                pygame.K_ESCAPE
            ) or inp.is_key_just_pressed(pygame.K_BACKSPACE)

        if back_pressed or (
                hasattr(inp, "is_key_just_pressed")
                and inp.is_key_just_pressed(pygame.K_ESCAPE)
        ):
            self.active = False
            return

        if self.showing_intro:
            if (
                    hasattr(inp, "is_key_just_pressed")
                    and (
                            inp.is_key_just_pressed(pygame.K_SPACE)
                            or inp.is_key_just_pressed(pygame.K_RETURN)
                            or inp.is_key_just_pressed(pygame.K_z)
                            or inp.is_key_just_pressed(pygame.K_UP)
                    )
            ) or getattr(inp, "mouse_clicked", False):
                self.showing_intro = False
                self.play_sound("confirm")
                if hasattr(inp, "mouse_clicked"):
                    inp.mouse_clicked = False
        elif self.game_over and (
                (
                        hasattr(inp, "is_key_just_pressed")
                        and (
                                inp.is_key_just_pressed(pygame.K_ESCAPE)
                                or inp.is_key_just_pressed(pygame.K_RETURN)
                                or inp.is_key_just_pressed(pygame.K_SPACE)
                        )
                )
                or getattr(inp, "mouse_clicked", False)
        ):
            self.active = False

    def update(self, dt: float) -> None:
        if self.showing_intro or self.game_over:
            return
        if not self.paused:
            self.elapsed_time += dt

    def render(self, surface: pygame.Surface) -> None:
        if self.showing_intro:
            self.render_intro(surface)
        elif self.game_over:
            self.render_game_over(surface)

    def render_intro(self, surface: pygame.Surface) -> None:
        surface.fill((8, 12, 22))
        pygame.draw.rect(surface, (0, 200, 255), (10, 10, 300, 220), 2, border_radius=6)
        pygame.draw.rect(surface, (15, 25, 45), (12, 12, 296, 216), border_radius=5)

        title_surf = self.title_font.render(self.game_name.upper(), True, (0, 255, 200))
        surface.blit(title_surf, (160 - title_surf.get_width() // 2, 18))

        y = 48
        desc_lbl = self.font.render(t(self.engine, "desc_lbl"), True, (255, 215, 0))
        surface.blit(desc_lbl, (22, y))
        y += 15
        desc_txt = self.font.render(self.description, True, (220, 220, 220))
        surface.blit(desc_txt, (22, y))
        y += 22

        goal_lbl = self.font.render(t(self.engine, "goal_lbl"), True, (255, 215, 0))
        surface.blit(goal_lbl, (22, y))
        y += 15
        goal_txt = self.font.render(self.goal, True, (220, 220, 220))
        surface.blit(goal_txt, (22, y))
        y += 22

        gp_lbl = self.font.render(t(self.engine, "gp_lbl"), True, (255, 215, 0))
        surface.blit(gp_lbl, (22, y))
        y += 15
        gp_txt = self.font.render(self.gameplay, True, (220, 220, 220))
        surface.blit(gp_txt, (22, y))
        y += 22

        ctrl_lbl = self.font.render(t(self.engine, "ctrl_lbl"), True, (255, 215, 0))
        surface.blit(ctrl_lbl, (22, y))
        y += 15
        ctrl_txt = self.font.render(self.controls, True, (0, 255, 150))
        surface.blit(ctrl_txt, (22, y))

        if int(pygame.time.get_ticks() / 250) % 2 == 0:
            prompt_txt = self.font.render(t(self.engine, "press_start"), True, (255, 255, 255))
            surface.blit(prompt_txt, (160 - prompt_txt.get_width() // 2, 205))

    def render_game_over(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((320, 240), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, (255, 50, 80), (35, 45, 250, 150), 2, border_radius=8)
        pygame.draw.rect(surface, (20, 10, 15), (37, 47, 246, 146), border_radius=7)

        go_surf = self.title_font.render(t(self.engine, "game_over"), True, (255, 50, 80))
        surface.blit(go_surf, (160 - go_surf.get_width() // 2, 60))

        score_surf = self.font.render(f"{t(self.engine, 'final_score')}: {self.score}", True, (255, 255, 255))
        surface.blit(score_surf, (160 - score_surf.get_width() // 2, 105))

        best_score = self.score
        if hasattr(self.engine, "highscores") and self.engine.highscores:
            best_score = max(
                self.score,
                self.engine.highscores.scores.get(self.game_name, self.score),
            )
        high_txt = self.font.render(f"{t(self.engine, 'high_score')}: {best_score}", True, (0, 255, 200))
        surface.blit(high_txt, (160 - high_txt.get_width() // 2, 125))

        if int(pygame.time.get_ticks() / 300) % 2 == 0:
            exit_surf = self.font.render(t(self.engine, "back_hint"), True, (0, 255, 200))
            surface.blit(exit_surf, (160 - exit_surf.get_width() // 2, 155))

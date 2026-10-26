from __future__ import annotations

import json
from pathlib import Path

import pygame

from pocket_games.core.settings import GAME_METADATA_FILE, TRANSLATIONS_FILE
from pocket_games.core.tuning import load_tuning_file

TRANSLATIONS = json.loads(TRANSLATIONS_FILE.read_text(encoding="iso-8859-1"))
GAME_METADATA = json.loads(GAME_METADATA_FILE.read_text(encoding="iso-8859-1"))


def t(engine, key: str) -> str:
    """
    Translates a specific key based on the language preference found in engine settings or defaults to English. Returns the localized value if available, otherwise returns the original key.

    :param engine: The object that may contain settings determining the translation language.
    :param key: The string identifier to look up in the translations dictionary.
    :return: The translated string for the key or the original key string itself.
    """
    lang = "English"
    if hasattr(engine, "settings") and engine.settings:
        lang = getattr(engine.settings, "language", "English")
    if lang not in TRANSLATIONS:
        lang = "English"
    return TRANSLATIONS[lang].get(key, key)


class BaseGame:
    """
    BaseGame provides fundamental functionality and state management for game applications within a generic engine framework. It initializes the core attributes required for rendering, input handling, and lifecycle tracking including intro screens, pause states, win/loss conditions, and basic UI elements. Subclasses should override specific update, render, or handle_input methods to define unique gameplay logic while inheriting standardized checks for game state transitions to prevent processing during inactive phases like the intro or ending.

    .. py:attribute:: CONTROLS
       :type: dict[str, list[typing.Any]]
       A dictionary mapping action strings (e.g., 'left', 'action') to lists of pygame key constants.

    .. py:attribute:: engine
       :type: Any
       The parent game engine instance providing access to audio, screen, and input systems.

    .. py:attribute:: game_name
       :type: str
       Unique identifier string assigned during initialization for highscore and logging purposes.

    .. py:attribute:: active
       :type: bool
       Flag indicating whether the main game loop is currently running or stopped.

    .. py:attribute:: paused
       :type: bool
       Flag indicating whether the update logic is suspended.

    .. py:attribute:: game_over
       :type: bool
       Boolean state set when the player loses or the game session ends via failure condition.

    .. py:attribute:: game_won
       :type: bool
       Boolean state set when the primary objective of the game has been successfully completed.

    .. py:attribute:: score
       :type: int
       The current accumulated points tracked throughout the gameplay session.

    .. py:attribute:: elapsed_time
       :type: float
       Total duration in seconds that the game has been running actively since start.

    .. py:attribute:: showing_intro
       :type: bool
       Boolean flag used to determine if the rendering logic should display the introduction screen instead of gameplay content.

    .. py:attribute:: description
       :type: str
       Detailed textual explanation describing the specific game rules or narrative provided in metadata.

    .. py:attribute:: goal
       :type: str
       String defining the primary objective the player needs to achieve to win the game.

    .. py:attribute:: gameplay
       :type: str
       Instructions describing the mechanics and style of play expected from the user.

    .. py:attribute:: controls
       :type: str
       Brief hint text indicating the default input scheme used for interacting with the game.

    """
    CONTROLS = {  # noqa: RUF012
        "left": [pygame.K_LEFT, pygame.K_a],
        "right": [pygame.K_RIGHT, pygame.K_d],
        "up": [pygame.K_UP, pygame.K_w],
        "down": [pygame.K_DOWN, pygame.K_s],
        "action": [pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_z],
        "back": [pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_x, pygame.K_b]
    }

    def __init_subclass__(cls, **kwargs):
        """
        This method initializes subclasses by wrapping handle_input, update, and render methods to enforce game state conditions such as intro showing or game over status before executing original logic.

        :param cls: The class being initialized via subclassing.
        :type cls: Type[Any]
        :param kwargs: Arbitrary keyword arguments passed to the superclass's __init_subclass__ method.
        :type kwargs: Dict[str, Any]
        :returns: None (implicitly sets class attributes).
        :rtype: None
        """
        super().__init_subclass__(**kwargs)

        if "handle_input" in cls.__dict__:
            orig_handle = cls.__dict__["handle_input"]
            def wrapped_handle(self, *args, **kwargs):
                BaseGame.handle_input(self)
                if self.showing_intro or self.game_over or self.game_won:
                    return
                return orig_handle(self, *args, **kwargs)
            cls.handle_input = wrapped_handle

        if "update" in cls.__dict__:
            orig_update = cls.__dict__["update"]
            def wrapped_update(self, dt, *args, **kwargs):
                BaseGame.update(self, dt)
                if self.showing_intro or self.game_over or self.game_won:
                    return
                return orig_update(self, dt, *args, **kwargs)
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
                elif self.game_won:
                    self.render_game_finished(surface)
                return
            cls.render = wrapped_render

    def __init__(self, engine, game_name: str, tuning_file: Path | None = None) -> None:
        self.engine = engine
        self.game_name = game_name
        self.tuning = load_tuning_file(tuning_file)
        self.active = True
        self.paused = False
        self.game_over = False
        self.game_won = False
        self.score = 0
        self.elapsed_time = 0.0
        self.showing_intro = True
        self._score_submitted = False
        self.game_end_timer = 0.0

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

    def is_control_pressed(self, action: str) -> bool:
        """
        Verifies whether a specific control action is currently active within the engine input system.

        :param action: The name of the action string representing a user input control to be checked.
        :return: A boolean value indicating if the associated input state corresponds to the specified action being pressed or clicked.
        :rtype: bool"""
        keys = self.CONTROLS.get(action, [])
        inp = getattr(self.engine, "input", None)
        if not inp:
            return False
        for key in keys:
            if hasattr(inp, "is_key_down") and inp.is_key_down(key):
                return True
        return bool(action == "action" and getattr(inp, "mouse_clicked", False))

    def is_control_just_pressed(self, action: str) -> bool:
        """
        This method evaluates whether the provided control action has been triggered by the engine input state.

        :param action: The name of the control action to verify for key or mouse press events.
        :return: True if the action corresponds to a just-pressed input, False otherwise.
        """
        keys = self.CONTROLS.get(action, [])
        inp = getattr(self.engine, "input", None)
        if not inp:
            return False
        for key in keys:
            if hasattr(inp, "is_key_just_pressed") and inp.is_key_just_pressed(key):
                return True
        return bool(action == "action" and getattr(inp, "mouse_clicked", False))

    @property
    def difficulty_factor(self) -> float:
        """
        This property calculates and returns the current difficulty factor based on the elapsed time of the instance. The calculation starts at a base value of 1.0 and increases linearly with respect to time passed.

        :return: The computed difficulty multiplier derived from the elapsed time attribute without type restrictions.
        """
        return 1.0 + self.elapsed_time * 0.03

    def get_virtual_mouse_pos(self) -> tuple[int, int]:
        """
        Returns the scaled virtual mouse position mapped to a fixed resolution of 320 by 240 pixels. The calculation utilizes the input engine mouse position if available, otherwise falling back to pygame defaults, and scales coordinates relative to the current screen dimensions or default surface size.

        :param self: The instance of the class containing the active engine context and screen reference.
        :return: A tuple of two integers representing the normalized x and y coordinates within the scaled viewport.
        """
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
        """
        Updates the internal score attribute by adding the provided value to it.

        :param amount: The quantity to increase the score by.
        :return: None once the score has been updated.

        """
        self.score += amount

    def play_sound(self, sound_name: str) -> None:
        """
        Play a sound using the engine's audio system if available.

        :param sound_name: The name of the audio clip to play.
        :type sound_name: str
        :return: None
        :rtype: NoneType
        """
        if hasattr(self.engine, "audio") and self.engine.audio:
            self.engine.audio.play(sound_name)

    def render_ui(self, surface: pygame.Surface) -> None:
        """
        Renders the user interface score text onto the provided display surface using the configured font and color settings. The method creates a score string representation based on the current instance score attribute and blits it at the top-left position (10, 5) of the surface.

        :param surface: A pygame.Surface object where the score text is to be rendered.
        :return: None"""
        score_txt = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        surface.blit(score_txt, (10, 5))

    def handle_input(self) -> None:
        """
        Handles user input processing for the game engine logic and state management. This method
        evaluates active input sources to detect quit commands via escape or back keys, which
        immediately deactivates the engine. It also monitors the introductory sequence phase
        where pressing action or up keys transitions out of intro mode and triggers sound effects.
        For game over or win scenarios, it waits for a specific timer duration before responding
        to exit or action inputs to deactivate the application accordingly. Updates internal
        flags and mouse input states based on control events.

        :return: None
        """
        inp = getattr(self.engine, "input", None)
        if not inp:
            return

        if self.is_control_just_pressed("back") or (
            hasattr(inp, "is_key_just_pressed") and inp.is_key_just_pressed(pygame.K_ESCAPE)
        ):
            self.active = False
            return

        if self.showing_intro:
            if self.is_control_just_pressed("action") or self.is_control_just_pressed("up"):
                self.showing_intro = False
                self.play_sound("confirm")
                if hasattr(inp, "mouse_clicked"):
                    inp.mouse_clicked = False
        elif (
            (self.game_over or self.game_won)
            and self.game_end_timer >= 3.0
            and (self.is_control_just_pressed("action") or self.is_control_just_pressed("back"))
        ):
            self.active = False

    def update(self, dt: float) -> None:
        """
        Updates game state based on the time delta, handles game end conditions and score submission, checks for intro visibility, and advances elapsed time if not paused.

        :param dt: Delta time step in seconds for the current frame.
        :return: None (void).
        """
        if self.game_over or self.game_won:
            self.game_end_timer += dt
            if not self._score_submitted:
                self._score_submitted = True
                if (
                    hasattr(self, "engine")
                    and self.engine
                    and hasattr(self.engine, "highscores")
                ):
                    level = getattr(self, "level", 1)
                    time_played = getattr(self, "elapsed_time", 0.0)
                    self.engine.highscores.submit_score(
                        self.game_name, self.score, level, time_played
                    )
            return
        if self.showing_intro:
            return
        if not self.paused:
            self.elapsed_time += dt

    def render(self, surface: pygame.Surface) -> None:
        """
        Renders the appropriate visual representation of the current game state onto the specified drawing surface based on internal application flags. This method determines whether to render an introduction sequence or a game over screen depending on the active status variables, executing the corresponding rendering logic without modifying private attributes or exposing internal state details in its documentation.

        :param surface: The target PyGame Surface object intended to receive the rendered graphical content for the current frame.
        :return: None after completing the drawing operations and returning control to the caller.

        """
        if self.showing_intro:
            self.render_intro(surface)
        elif self.game_over:
            self.render_game_over(surface)

    def render_intro(self, surface: pygame.Surface) -> None:
        """
        Renders the introductory screen interface onto the provided surface, applying background colors and positioning game metadata including title, description, goals, gameplay mechanics, control instructions, and a toggle start prompt.

        :param surface: The pygame.Surface object used as the canvas for all UI rendering operations.
        :return: None after successfully drawing all elements to the specified surface.
        """
        surface.fill((8, 12, 22))
        pygame.draw.rect(surface, (0, 200, 255), (10, 10, 300, 220), 2, border_radius=6)
        pygame.draw.rect(surface, (15, 25, 45), (12, 12, 296, 216), border_radius=5)

        title_surf = self.title_font.render(self.game_name.upper(), True, (0, 255, 200))
        surface.blit(title_surf, (160 - title_surf.get_width() // 2, 18))

        y = 46
        y = self._draw_intro_block(surface, y, t(self.engine, "desc_lbl"), self.description, (220, 220, 220))
        y = self._draw_intro_block(surface, y, t(self.engine, "goal_lbl"), self.goal, (220, 220, 220))
        y = self._draw_intro_block(surface, y, t(self.engine, "gp_lbl"), self.gameplay, (220, 220, 220))
        self._draw_intro_block(surface, y, t(self.engine, "ctrl_lbl"), self.controls, (0, 255, 150))

        if int(pygame.time.get_ticks() / 250) % 2 == 0:
            prompt_txt = self.font.render(t(self.engine, "press_start"), True, (255, 255, 255))
            surface.blit(prompt_txt, (160 - prompt_txt.get_width() // 2, 216))

    def _draw_intro_block(self, surface: pygame.Surface, y: int, label: str, text: str, color: tuple[int, int, int]) -> int:
        label_surf = self.font.render(label, True, (255, 215, 0))
        surface.blit(label_surf, (22, y))
        y += 13
        for line in (text or "").split("\n"):
            if not line:
                continue
            line_surf = self.font.render(line, True, color)
            surface.blit(line_surf, (22, y))
            y += 12
        return y + 4

    def render_game_over(self, surface: pygame.Surface) -> None:
        """
        Render the game over interface overlay onto the specified surface, displaying current score, elapsed time, level, best run statistics, and top 3 historical runs.

        :param surface: The destination surface to blit the game over UI content onto.
        :return: None
        """
        overlay = pygame.Surface((320, 240), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, (255, 50, 80), (20, 20, 280, 200), 2, border_radius=8)
        pygame.draw.rect(surface, (20, 10, 15), (22, 22, 276, 196), border_radius=7)

        go_surf = self.title_font.render(t(self.engine, "game_over"), True, (255, 50, 80))
        surface.blit(go_surf, (160 - go_surf.get_width() // 2, 26))

        final_str = f"{t(self.engine, 'final_score')}: {self.score} (Lvl {getattr(self, 'level', 1)}, {round(self.elapsed_time, 1)}s)"
        score_surf = self.font.render(final_str, True, (255, 255, 255))
        surface.blit(score_surf, (30, 50))

        best_run = {"score": self.score, "level": getattr(self, "level", 1), "time": round(self.elapsed_time, 1)}
        runs = []
        if hasattr(self.engine, "highscores") and self.engine.highscores:
            best_run = self.engine.highscores.get_best_run(self.game_name)
            runs = self.engine.highscores.get_runs(self.game_name)

        high_str = f"{t(self.engine, 'high_score')}: {best_run['score']} (Lvl {best_run.get('level', 1)}, {best_run.get('time', 0.0)}s)"
        high_txt = self.font.render(high_str, True, (0, 255, 200))
        surface.blit(high_txt, (30, 68))

        history_title = self.font.render("TOP 3 BEST RUNS (Score / Lvl / Time):", True, (255, 215, 0))
        surface.blit(history_title, (30, 92))

        y_offset = 110
        if not runs:
            no_runs = self.font.render("No previous runs recorded.", True, (150, 150, 150))
            surface.blit(no_runs, (30, y_offset))
        else:
            for idx, run in enumerate(runs[:3]):
                run_str = f"#{idx+1}: {run.get('score', 0)} pts | Lvl {run.get('level', 1)} | {run.get('time', 0.0)}s"
                run_txt = self.font.render(run_str, True, (200, 220, 240))
                surface.blit(run_txt, (30, y_offset))
                y_offset += 18

        if self.game_end_timer < 3.0:
            lock_txt = self.font.render(f"Please wait... ({max(0, 3 - int(self.game_end_timer))}s)", True, (255, 100, 100))
            surface.blit(lock_txt, (160 - lock_txt.get_width() // 2, 196))
        elif int(pygame.time.get_ticks() / 300) % 2 == 0:
            exit_surf = self.font.render(t(self.engine, "back_hint"), True, (0, 255, 200))
            surface.blit(exit_surf, (160 - exit_surf.get_width() // 2, 196))

    def render_game_finished(self, surface: pygame.Surface) -> None:
        """
        Renders the game finished overlay on the provided surface, displaying final scores and countdown or exit hints based on internal timers.

        :param surface: The pygame.Surface instance to draw the finished state onto.
        :return: None
        """
        overlay = pygame.Surface((320, 240), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, (0, 255, 200), (35, 45, 250, 150), 2, border_radius=8)
        pygame.draw.rect(surface, (10, 25, 20), (37, 47, 246, 146), border_radius=7)

        win_surf = self.title_font.render("GAME FINISHED!", True, (0, 255, 200))
        surface.blit(win_surf, (160 - win_surf.get_width() // 2, 60))

        score_surf = self.font.render(
            f"{t(self.engine, 'final_score')}: {self.score}", True, (255, 255, 255)
        )
        surface.blit(score_surf, (160 - score_surf.get_width() // 2, 105))

        best_score = self.score
        if hasattr(self.engine, "highscores") and self.engine.highscores:
            best_score = max(
                self.score,
                self.engine.highscores.scores.get(self.game_name, {}).get("all_time", self.score),
            )
        high_txt = self.font.render(
            f"{t(self.engine, 'high_score')}: {best_score}", True, (255, 215, 0)
        )
        surface.blit(high_txt, (160 - high_txt.get_width() // 2, 125))

        if self.game_end_timer < 3.0:
            lock_txt = self.font.render(f"Please wait... ({max(0, 3 - int(self.game_end_timer))}s)", True, (255, 100, 100))
            surface.blit(lock_txt, (160 - lock_txt.get_width() // 2, 155))
        elif int(pygame.time.get_ticks() / 300) % 2 == 0:
            exit_surf = self.font.render(
                t(self.engine, "back_hint"), True, (255, 255, 255)
            )
            surface.blit(exit_surf, (160 - exit_surf.get_width() // 2, 155))

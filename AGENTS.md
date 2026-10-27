# AGENTS.md — Instructions for Coding Agents

This document is intended for automated coding agents (e.g. Junie, Copilot, Claude Code, Cursor) as well as human developers working on the **Retro Pocket Games** project. It describes the goal, architecture, conventions, testing requirements, and common pitfalls. If this document conflicts with a direct instruction, the direct instruction takes precedence. User documentation is located in `README.md`.

---

## 1. Project Overview

- **Purpose:** A collection of 23 retro arcade and puzzle games for handheld devices (Raspberry Pi with a 3.5" display) and desktop systems (Linux, Windows).
- **Language / Engine:** Python 3.12+, `pygame-ce` (dependency as defined in `pyproject.toml`).
- **Package name:** `retro-pocket-games`; for the current version see `pyproject.toml`.
- **Entry point:** `pocket_games/main.py` → `main()` creates an `Engine` (title "Retro Pocket Collection") and starts the `MainMenu` scene (`pocket_games/ui/menu.py`). The console script `pocket-games` is wired to this in `pyproject.toml`.
- **Virtual resolution:** 320 × 240 pixels, scaled to the output size (e.g. 480 × 320 or 640 × 480). Target: 60 FPS.
- **Sound:** Procedurally synthesized audio via `pocket_games/core/audio.py`.

---

## 2. Directory Structure

```text
RetroPocketGames/
├── AGENTS.md                    # this document
├── README.md                    # user documentation
├── pyproject.toml               # package metadata, dependencies, console script
├── uv.lock                      # locked dependencies (uv)
├── install.sh / run.sh / update.sh / setup_shortcut.sh
├── input_diagnostics.py         # helper script for input diagnostics
├── test_aether_defender_updated.py  # standalone script in the root directory
├── assets/                      # icon and icon generator (create_icon.py)
├── .github/workflows/release.yml    # release pipeline (tags v*)
├── pocket_games/
│   ├── main.py                  # entry point
│   ├── core/                    # engine and cross-cutting modules
│   │   ├── engine.py            # main loop, scene management, window
│   │   ├── input.py             # InputManager (keyboard, gamepad, touch)
│   │   ├── audio.py             # sound synthesis and playback
│   │   ├── physics.py           # gravity, collision, damping, clamping
│   │   ├── highscore.py         # HighScoreManager (persistence)
│   │   ├── settings.py          # path constants and Settings class
│   │   ├── tuning.py            # loading of JSON tuning files
│   │   └── logger.py            # central logger
│   ├── games/                   # one module per game + base.py (BaseGame)
│   ├── ui/                      # menu, highscore, game-over, and settings screens
│   ├── data/
│   │   ├── translations.json    # translations (key → language → text)
│   │   ├── game_metadata.json   # game descriptions per language
│   │   └── tuning/*.json        # balancing values per game
│   └── docs/
│       ├── finetuning.md        # balancing documentation (mandatory, see section 6)
│       ├── generate_docs.py     # generator for docs/api
│       └── api/                 # generated API documentation
├── data/                        # runtime data (created by the program)
│   ├── highscores.json
│   ├── settings.json
│   └── pocket_games.log
└── tests/                       # unittest suite (≈ 40 test modules)
```

Note: The list of test modules changes frequently. The actual contents of `tests/` are authoritative.

---

## 3. Architecture

### 3.1 Engine and Scenes
- `core/engine.py` owns the main loop (target 60 FPS) and scene management via `run_scene(...)`.
- Menus and screens are scenes in `ui/`. Games are launched from the menu.
- The engine provides access to audio, screen, input, and `settings`. Games access these through `engine`.

### 3.2 Base Game Class `BaseGame` (`games/base.py`)
Every game inherits from `BaseGame`. The base class provides state and lifecycle handling:
- State flags: `active`, `paused`, `game_over`, `game_won`, `showing_intro`.
- Metrics: `score`, `elapsed_time`.
- Texts: `description`, `goal`, `gameplay`, `controls` (taken from the metadata).
- `CONTROLS`: mapping of actions (`left`, `right`, `up`, `down`, `action`, `back`) to keys.
- `__init_subclass__` wraps `handle_input`, `update`, and `render` so that no game logic runs during intro, pause, or game over. Subclasses override the methods for game logic and must not bypass the state check.
- Translations are retrieved via the function `t(engine, key)`. If the language or key is missing, English is used; if the English text is also missing, the key itself is returned.

### 3.3 Configuration and Paths (`core/settings.py`)
- All file paths are defined as constants in `core/settings.py` (e.g. `HIGHSCORE_FILE`, `SETTINGS_FILE`, `TRANSLATIONS_FILE`, `GAME_METADATA_FILE`, `<GAME>_TUNING_FILE`). New paths belong there, not as literals in other modules.
- The `Settings` class stores `sound_enabled`, `master_volume`, `fullscreen`, and `language` in `data/settings.json`.
- **Default volume:** `master_volume` defaults to `0.6`, both in the constructor and as the fallback in `load()`. Both values must always stay identical.

### 3.4 Tuning Files (`core/tuning.py`, `data/tuning/`)
- Balancing values are stored per game in `pocket_games/data/tuning/<game>.json`.
- `load_tuning_file(path)` returns a dictionary (empty if the file is missing). A top-level value that is not a JSON object raises `ValueError`.
- `get_section(data, name)` and `get_number(section, key, default)` read values with defaults. Missing or invalid values fall back to the default.
- Important: When changing tuning values, the default in the code must match the JSON file; otherwise behavior and documentation diverge.

### 3.5 Physics (`core/physics.py`)
Central, deterministic helper functions used by several games:
- Gravity: `v_y = v_y0 + g · Δt`
- Clamping to `[min, max]`
- Collision: circle–circle (`d < r1 + r2`) and AABB rectangles
- Damping: `v = v · damping^Δt`
- Paddle reflection depending on the impact point

Physics functions remain pure functions without hidden state so they stay testable.

### 3.6 Audio (`core/audio.py`)
Sounds are synthesized at runtime. Volume follows `Settings`. For tests, audio output should be replaceable or disableable (see `tests/test_audio.py`).

---

## 4. Input and Navigation (`core/input.py`)

The `InputManager` combines hardware buttons (D-pad, A/B/Start), keyboard, and touch.

| Action | Hardware / Keyboard | Touch |
| :--- | :--- | :--- |
| Menu navigation | D-pad up/down (`W`/`S`) | Tap or swipe list items |
| Confirm / Action | A / `Enter` / `Space` | Single tap on target |
| Back / Pause | B / `Esc` / `Backspace` | Tap the back button |
| Global exit | Hold Start (> 3 s) / `Esc` | Tap the exit button |

New controls belong in the `InputManager` or in `BaseGame.CONTROLS`, not hard-wired into individual games.

---

## 5. Highscores and Persistence (`core/highscore.py`)

`HighScoreManager` manages `data/highscores.json`:
- **Schema per game:** `all_time` (best score), `best_run` (`score`, `level`, `time`), `runs` (at most the last/best three runs, sorted descending by score).
- **Legacy formats** are normalized on load: plain integers become full entries, and a missing `best_run` is derived from `runs` or `all_time`.
- **Writing:** `save()` creates directories and writes JSON. If the in-memory state is empty but the file is not, the file is **not** overwritten.
- **Errors** during reading or writing are logged, not propagated.
- Overwriting with an empty state must remain prevented. This also applies to refactorings.

---

## 6. Project Rules (mandatory)

These rules apply to every change:

1. **Docstrings and comments** must always be present and written in **English**. The existing code uses the Sphinx format (`:param:`, `:return:`). Follow this format.
2. **Unit tests** must always be written and should achieve the highest possible coverage. Classes and functions are designed to be testable: injectable dependencies, pure helper functions, no hidden global state.
3. **User documentation:** `README.md` must be updated whenever a change affects it.
4. **Fine-tuning notes:** Balance values, formulas, tuning knobs, and their effects are documented in `pocket_games/docs/finetuning.md`.
5. **Refactoring checklist:** With every refactoring, check and update as needed: documentation, tests, translations (`translations.json`, `game_metadata.json` for German and English), and the generated API documentation in `docs/api/`.

Communication with users follows the users' language. The code remains commented in English.

---

## 7. Game Overview

All 23 games are modules in `pocket_games/games/`. Overview (genre):

| Game | Module | Genre |
| :--- | :--- | :--- |
| Neon Dash | `neon_dash.py` | Endless runner |
| Matrix Invaders | `matrix_invaders.py` | Space shooter |
| Glitch Runner | `glitch_runner.py` | Grid puzzle |
| Bit Blaster | `bit_blaster.py` | Brick breaker |
| Pixel Drop | `pixel_drop.py` | Falling-block puzzle |
| Sub-Zero Miner | `sub_zero_miner.py` | Survival |
| Kernel Panic | `kernel_panic.py` | Memory defense |
| Pulse Racer | `pulse_racer.py` | Racing |
| Quantum Maze | `quantum_maze.py` | Maze |
| Cyber Snake | `cyber_snake.py` | Snake |
| Bug Hunter | `bug_hunter.py` | Whack-a-mole |
| Aether Defender | `aether_defender.py` | Color shooter |
| Circuit Breaker | `circuit_breaker.py` | Routing puzzle |
| Chrono Shift | `chrono_shift.py` | Action |
| Orbital Defense | `orbital_defense.py` | Planetary defense |
| Gravity Sling | `gravity_sling.py` | Space navigation |
| Retro Pong 2077 | `retro_pong.py` | Pong |
| Byte Hopper | `byte_hopper.py` | Vertical platformer |
| Crypto Decrypt | `crypto_decrypt.py` | Code breaking |
| Sonic Pulse | `sonic_pulse.py` | Timing |
| Cyber Grid Chomp | `cyber_grid_chomp.py` | Pac-Man style maze |
| Pixel Platformer | `pixel_platformer.py` | Platformer |
| Cyber Flipper | `cyber_flipper.py` | Pinball |

The menu (`ui/menu.py`) lists exactly these 23 games. Their display names are also the keys in `game_metadata.json`.

Every game follows these patterns:
- Balancing constants at module level or in the corresponding tuning file.
- Level generation is seed-based and reproducible (e.g. `LEVEL_SEED_BASE` in Pixel Platformer and Cyber Grid Chomp). The same inputs must produce the same levels.
- Scores are reported via `HighScoreManager.submit_score(...)`.

---

## 8. Build, Installation, Execution

- **Installation scripts:** `install.sh` (system dependencies, virtual environment, package build), `setup_shortcut.sh` (desktop entry, symlink), `update.sh` (update repository and packages), `run.sh` (starts the launcher).
- **Dependencies:** `pyproject.toml` and `uv.lock`. Introduce new dependencies only through the build system and keep `uv.lock` consistent.
- **Release pipeline** (`.github/workflows/release.yml`): runs on tags `v*`, produces `pocket-games-linux.tar.gz` and `pocket-games-windows.zip`, and then creates a GitHub release.
- **Versioning:** Raise the version in `pyproject.toml` when preparing a release.
- **On Windows**, use the project's Python environment for local development. The `.sh` scripts are intended for Linux/Raspberry Pi.

---

## 9. Tests

- Framework: `unittest`, with headless pygame: set `SDL_VIDEODRIVER=dummy` (and `SDL_AUDIODRIVER=dummy` if needed) so no windows or audio devices are required.
- Running:

```bash
# All tests
python -m unittest discover -s tests

# Single module
python -m unittest tests.test_neon_dash
```

- Test coverage by area:
  - **Physics:** clamping, gravity, collisions, damping.
  - **Highscores:** file creation, schema, persistence, backup restore, no overwriting with an empty state.
  - **Game logic:** initial states, level thresholds, time extensions, boundary collisions.
  - **Tuning and settings:** defaults, missing files, invalid values.
  - **Translations:** selected language, English fallback for missing keys, key fallback as last resort.
- Not allowed to make tests pass: deleting tests or disabling them with `@skip`, weakening assertions, mocks that hide the error, or bypassing test runs. A failing test is first treated as a sign of your own regression.
- For bug fixes, first write a test that reproduces the bug, then implement the fix.

---

## 10. Code Style and Conventions

- **Python:** PEP 8, `from __future__ import annotations` in new modules, type hints where useful.
- **Formatting and linting:** `ruff` (version as defined in `pyproject.toml`). Before submitting, make sure no new warnings are introduced. Add existing `# noqa` comments only with a justification.
- **Naming:** modules and files in `snake_case`. Game classes follow the style of the existing modules (`PascalCase`).
- **Comments:** follow the amount of comments present in the respective module. Do not add comments if the surrounding code has none, unless requested. Always in English.
- **Logging:** via `core/logger.py` (`logger`). No `print` output in game code.
- **No global side effects on import.** For example, translations and metadata are loaded in `base.py` at import time. New modules should load data lazily or via parameters.

---

## 11. Pitfalls

- **Character encoding:** `translations.json` and `game_metadata.json` are read in `base.py` as **ISO-8859-1**. When editing these files, use the same encoding, otherwise umlauts will be broken.
- **Language selection:** Translations must exist for all supported languages (German and English). The English text is the mandatory fallback: `t()` returns it whenever a key is missing in the selected language. The English entry must therefore exist for every key.
- **Runtime data:** `data/` (highscores, settings, log) is not versioned and is created at runtime. Test runs must not modify the real file. Tests should use temporary paths or inject paths.
- **Path constants:** do not hard-code paths in modules. Always import them from `core/settings.py`.
- **Frame-rate dependency:** physics and timers should work with `Δt` (seconds), not frame counters, so that 60 FPS and slower devices behave the same.
- **Resources on the Pi:** avoid heavy allocations per frame and do not recreate large surfaces in the render path.

---

## 12. Procedure for Coding Agents

1. Read the relevant files before changing anything, especially `core/` and `games/base.py`.
2. Check the project rules from section 6 before every change.
3. Make small, focused changes. No unrequested refactorings or formatting runs over entire files.
4. Write or adapt tests and run them. For failures, fix the cause instead of bypassing the test.
5. Keep documentation in sync: `README.md`, `finetuning.md`, translations, and `docs/api/` where affected.
6. No commits, pushes, or tags without explicit instruction. Do not create files outside the project. Use the `.junie` folder only for configuration.
7. In the final report, briefly state what was changed, which tests were run, and what remains open.

---

## 13. Open Points for Maintaining This Document

- The directory structure in section 2 is an overview. Update it after larger restructurings.
- The game list in section 7 reflects `games/` and `ui/menu.py`. Re-check it whenever games are added or removed from the menu.

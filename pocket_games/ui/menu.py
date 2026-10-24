from __future__ import annotations

import sys

import pygame

from pocket_games.core.engine import VIRTUAL_WIDTH
from pocket_games.ui.highscore_screen import HighScoreScreen
from pocket_games.ui.settings_screen import SettingsScreen


class MainMenu:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True

        from pocket_games.games.aether_defender import AetherDefenderGame
        from pocket_games.games.bit_blaster import BitBlasterGame
        from pocket_games.games.bug_hunter import BugHunterGame
        from pocket_games.games.byte_hopper import ByteHopperGame
        from pocket_games.games.chrono_shift import ChronoShiftGame
        from pocket_games.games.circuit_breaker import CircuitBreakerGame
        from pocket_games.games.crypto_decrypt import CryptoDecryptGame
        from pocket_games.games.cyber_grid_chomp import CyberGridChompGame
        from pocket_games.games.cyber_snake import CyberSnakeGame
        from pocket_games.games.glitch_runner import GlitchRunnerGame
        from pocket_games.games.gravity_sling import GravitySlingGame
        from pocket_games.games.kernel_panic import KernelPanicGame
        from pocket_games.games.matrix_invaders import MatrixInvadersGame
        from pocket_games.games.neon_dash import NeonDashGame
        from pocket_games.games.orbital_defense import OrbitalDefenseGame
        from pocket_games.games.pixel_drop import PixelDropGame
        from pocket_games.games.pixel_platformer import PixelPlatformerGame
        from pocket_games.games.pulse_racer import PulseRacerGame
        from pocket_games.games.quantum_maze import QuantumMazeGame
        from pocket_games.games.retro_pong import RetroPongGame
        from pocket_games.games.sonic_pulse import SonicPulseGame
        from pocket_games.games.sub_zero_miner import SubZeroMinerGame

        self.games = [
            ("Pixel Drop", PixelDropGame),
            ("Circuit Breaker", CircuitBreakerGame),
            ("Neon Dash", NeonDashGame),
            ("Byte Hopper", ByteHopperGame),
            ("Quantum Maze", QuantumMazeGame),
            ("Sub-Zero Miner", SubZeroMinerGame),
            ("Retro Pong 2077", RetroPongGame),
            ("Bug Hunter", BugHunterGame),
            ("Cyber Snake", CyberSnakeGame),
            ("Matrix Invaders", MatrixInvadersGame),
            ("Bit Blaster", BitBlasterGame),
            ("Pulse Racer", PulseRacerGame),
            ("Crypto Decrypt", CryptoDecryptGame),
            ("Kernel Panic", KernelPanicGame),
            ("Orbital Defense", OrbitalDefenseGame),
            ("Chrono Shift", ChronoShiftGame),
            ("Sonic Pulse", SonicPulseGame),
            ("Gravity Sling", GravitySlingGame),
            ("Glitch Runner", GlitchRunnerGame),
            ("Aether Defender", AetherDefenderGame),
            ("Cyber Grid Chomp", CyberGridChompGame),
            ("Pixel Platformer", PixelPlatformerGame),
        ]

        self.menu_items = self.games + [
            ("Settings", SettingsScreen),
            ("Highscores", HighScoreScreen),
            ("Exit", None),
        ]

        self.selected_index = 0
        self.scroll_offset = 0
        self.font = pygame.font.SysFont(None, 18)
        self.title_font = pygame.font.SysFont(None, 24)
        self.item_rects: list[pygame.Rect] = []

    def handle_input(self) -> None:
        visible_count = 8
        inp = self.engine.input

        if inp.is_key_just_pressed(pygame.K_UP) or inp.is_key_just_pressed(pygame.K_w):
            self.engine.audio.play("select")
            self.selected_index -= 1
            if self.selected_index < 0:
                self.selected_index = len(self.menu_items) - 1
                self.scroll_offset = max(0, len(self.menu_items) - visible_count)
            elif self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index

        elif inp.is_key_just_pressed(pygame.K_DOWN) or inp.is_key_just_pressed(
            pygame.K_s
        ):
            self.engine.audio.play("select")
            self.selected_index += 1
            if self.selected_index >= len(self.menu_items):
                self.selected_index = 0
                self.scroll_offset = 0
            elif self.selected_index >= self.scroll_offset + visible_count:
                self.scroll_offset = self.selected_index - visible_count + 1

        elif inp.is_key_just_pressed(pygame.K_RETURN) or inp.is_key_just_pressed(
            pygame.K_SPACE
        ):
            self.engine.audio.play("confirm")
            self.launch_selected()

    def launch_selected(self) -> None:
        name, cls = self.menu_items[self.selected_index]
        if name.lower() == "exit":
            self.engine.running = False
            sys.exit(0)
        if cls:
            self.engine.run_scene(cls)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 10, 20))
        title_surf = self.title_font.render("POCKET ARCADE", True, (0, 255, 200))
        surface.blit(title_surf, (VIRTUAL_WIDTH // 2 - title_surf.get_width() // 2, 6))

        self.item_rects = []
        start_y = 30
        item_h = 23
        visible_count = 8

        for i in range(visible_count):
            idx = self.scroll_offset + i
            if idx >= len(self.menu_items):
                break
            name, _ = self.menu_items[idx]
            rect = pygame.Rect(15, start_y + i * item_h, VIRTUAL_WIDTH - 30, 20)
            self.item_rects.append(rect)

            is_sel = (idx == self.selected_index)
            bg_color = (50, 40, 80) if idx >= len(self.games) else ((40, 40, 80) if is_sel else (20, 20, 35))
            text_color = (255, 255, 0) if is_sel else (200, 200, 200)

            pygame.draw.rect(surface, bg_color, rect, border_radius=4)
            pygame.draw.rect(surface, (0, 150, 200) if is_sel else (50, 50, 80), rect, 1, border_radius=4)

            display_text = f"{idx+1}. {name}" if idx < len(self.games) else f"⚙ {name}"
            t_surf = self.font.render(display_text, True, text_color)
            surface.blit(t_surf, (rect.x + 8, rect.y + 3))

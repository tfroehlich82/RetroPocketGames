from __future__ import annotations
import pygame
from pocket_games.core.engine import VIRTUAL_WIDTH, VIRTUAL_HEIGHT

class MainMenu:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.active = True

        # Import all 14 games
        from pocket_games.games.pixel_drop import PixelDropGame
        from pocket_games.games.circuit_breaker import CircuitBreakerGame
        from pocket_games.games.neon_dash import NeonDashGame
        from pocket_games.games.byte_hopper import ByteHopperGame
        from pocket_games.games.quantum_maze import QuantumMazeGame
        from pocket_games.games.sub_zero_miner import SubZeroMinerGame
        from pocket_games.games.retro_pong import RetroPongGame
        from pocket_games.games.bug_hunter import BugHunterGame
        from pocket_games.games.cyber_snake import CyberSnakeGame
        from pocket_games.games.matrix_invaders import MatrixInvadersGame
        from pocket_games.games.bit_blaster import BitBlasterGame
        from pocket_games.games.pulse_racer import PulseRacerGame
        from pocket_games.games.crypto_decrypt import CryptoDecryptGame
        from pocket_games.games.kernel_panic import KernelPanicGame

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
        ]
        self.selected_index = 0
        self.scroll_offset = 0
        self.font = pygame.font.SysFont(None, 18)
        self.title_font = pygame.font.SysFont(None, 24)

    def handle_input(self) -> None:
        inp = self.engine.input
        if inp.is_key_pressed(pygame.K_UP) or inp.is_key_pressed(pygame.K_w):
            self.selected_index = (self.selected_index - 1) % len(self.games)
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
        elif inp.is_key_pressed(pygame.K_DOWN) or inp.is_key_pressed(pygame.K_s):
            self.selected_index = (self.selected_index + 1) % len(self.games)
            if self.selected_index >= self.scroll_offset + 8:
                self.scroll_offset = self.selected_index - 7
        elif inp.is_key_pressed(pygame.K_RETURN) or inp.is_key_pressed(pygame.K_SPACE):
            self.launch_selected()

        if inp.mouse_clicked:
            mw, mh = self.engine.screen.get_size()
            vx = int(inp.mouse_pos[0] * (VIRTUAL_WIDTH / mw))
            vy = int(inp.mouse_pos[1] * (VIRTUAL_HEIGHT / mh))
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(vx, vy):
                    actual_idx = i + self.scroll_offset
                    if actual_idx < len(self.games):
                        self.selected_index = actual_idx
                        self.launch_selected()

    def launch_selected(self) -> None:
        name, cls = self.games[self.selected_index]
        self.engine.run_scene(cls)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 10, 20))
        title_surf = self.title_font.render("HANDHELD ARCADE (14 GAMES)", True, (0, 255, 200))
        surface.blit(title_surf, (VIRTUAL_WIDTH // 2 - title_surf.get_width() // 2, 6))

        self.item_rects = []
        start_y = 30
        item_h = 23
        visible_count = 8

        for i in range(visible_count):
            idx = self.scroll_offset + i
            if idx >= len(self.games):
                break
            name, _ = self.games[idx]
            rect = pygame.Rect(15, start_y + i * item_h, VIRTUAL_WIDTH - 30, 20)
            self.item_rects.append(rect)

            is_sel = (idx == self.selected_index)
            bg_color = (40, 40, 80) if is_sel else (20, 20, 35)
            text_color = (255, 255, 0) if is_sel else (200, 200, 200)

            pygame.draw.rect(surface, bg_color, rect, border_radius=4)
            pygame.draw.rect(surface, (0, 150, 200) if is_sel else (50, 50, 80), rect, 1, border_radius=4)

            t_surf = self.font.render(f"{idx+1}. {name}", True, text_color)
            surface.blit(t_surf, (rect.x + 8, rect.y + 3))

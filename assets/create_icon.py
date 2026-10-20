# ==========================================
# ICON GENERATOR FOR RETRO GAMES SUITE
# ==========================================
from __future__ import annotations

import os

import pygame


def generate_icon() -> None:
    pygame.init()

    # 128x128 Pixel für ein hochauflösendes App-Icon
    size = 128
    surface = pygame.Surface((size, size))

    # Dunkler Cyberpunk-Hintergrund
    surface.fill((8, 12, 24))

    # Handheld-Gehäuse (abgerundetes Retro-Design mit Rahmen)
    body_rect = pygame.Rect(14, 12, 100, 104)
    pygame.draw.rect(surface, (25, 35, 55), body_rect, border_radius=20)
    pygame.draw.rect(surface, (0, 255, 200), body_rect, 3, border_radius=20)

    # Bildschirm (mit leuchtendem Pink-/Cyan-Rand)
    screen_rect = pygame.Rect(26, 22, 76, 52)
    pygame.draw.rect(surface, (5, 8, 16), screen_rect, border_radius=8)
    pygame.draw.rect(surface, (255, 0, 150), screen_rect, 2, border_radius=8)

    # Arcade-Grafikelement auf dem Bildschirm (Games Suite Logo-Element)
    pygame.draw.rect(surface, (0, 255, 200), (52, 38, 24, 20), border_radius=4)
    pygame.draw.rect(surface, (5, 8, 16), (58, 44, 12, 8))
    pygame.draw.circle(surface, (255, 215, 0), (64, 48), 3)

    # D-Pad (Linke Seite)
    dpad_bg = pygame.Rect(32, 86, 22, 22)
    pygame.draw.rect(surface, (40, 50, 70), dpad_bg, border_radius=5)
    pygame.draw.rect(surface, (0, 255, 200), (41, 88, 4, 18))
    pygame.draw.rect(surface, (0, 255, 200), (34, 95, 18, 4))

    # Action-Buttons (Rechte Seite - Retro Pink, Gelb & Cyan)
    pygame.draw.circle(surface, (255, 40, 110), (83, 92), 7)
    pygame.draw.circle(surface, (255, 215, 0), (98, 102), 7)
    pygame.draw.circle(surface, (0, 240, 255), (83, 106), 5)

    # Pfad des Skriptverzeichnisses ermitteln
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "icon.png")

    # Als PNG speichern
    pygame.image.save(surface, output_path)
    print(f"Games-Suite-Icon erfolgreich unter '{output_path}' erstellt!")
    pygame.quit()


if __name__ == "__main__":
    generate_icon()

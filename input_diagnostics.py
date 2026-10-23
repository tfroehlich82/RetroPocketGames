from __future__ import annotations

import sys

import pygame


def main() -> None:
    pygame.init()
    pygame.display.init()
    pygame.joystick.init()

    screen = pygame.display.set_mode((320, 240))
    pygame.display.set_caption("PocketTerm35 Input Diagnostics")
    clock = pygame.time.Clock()

    try:
        font = pygame.font.Font(None, 18)
    except Exception:  # noqa: BLE001
        font = pygame.font.SysFont("sans-serif", 16)

    # Alle verbundenen Joysticks/Gamepads initialisieren
    joysticks = [
        pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())
    ]
    for js in joysticks:
        js.init()
        print(
            f"🎮 Joystick erkannt: {js.get_name()} ({js.get_numbuttons()} Buttons)"
        )

    print("\n" + "=" * 50)
    print("DIAGNOSE GESTARTET: Drücke Tasten oder den Touchscreen.")
    print("Drücke ESC (oder schließe das Fenster), um den Test zu beenden.")
    print("=" * 50 + "\n")

    last_event_str = "Warte auf Eingabe..."

    running = True
    while running:
        screen.fill((15, 15, 25))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                last_event_str = f"KEY DOWN: {event.key} ({key_name})"
                print(f"[TASTATUR] {last_event_str}")
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                last_event_str = f"JOYSTICK BUTTON: {event.button}"
                print(f"[GAMEPAD] {last_event_str}")
            elif event.type == pygame.JOYAXISMOTION:
                if abs(event.value) > 0.5:
                    last_event_str = f"JOYSTICK AXIS: {event.axis} = {event.value:.1f}"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                last_event_str = f"MOUSE/TOUCH: {event.pos}"
                print(f"[TOUCH] {last_event_str}")

        # Text auf dem Bildschirm anzeigen
        title_txt = font.render("INPUT DIAGNOSTICS", True, (255, 215, 0))
        screen.blit(title_txt, (160 - title_txt.get_width() // 2, 20))

        # Event-Anzeige (Zeilenumbruch-Sicherheit)
        lines = last_event_str.split("\n")
        for idx, line in enumerate(lines):
            txt = font.render(line, True, (0, 255, 200))
            screen.blit(txt, (20, 70 + (idx * 20)))

        hint_txt = font.render("ESC drücken zum Beenden", True, (140, 140, 180))
        screen.blit(hint_txt, (160 - hint_txt.get_width() // 2, 210))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

from __future__ import annotations

import pygame

GAME_METADATA = {
    "Pixel Drop": {
        "desc": "Klassisches Tetris-Puzzle mit fallenden Steinen.",
        "goal": "Staple Blöcke sauber und räume Reihen ab.",
        "gameplay": "Alle 20 geräumten Reihen steigt das Level und die Geschwindigkeit.",
        "controls": "D-Pad: Bewegen / Drehen / Soft Drop"
    },
    "Circuit Breaker": {
        "desc": "Digitales Logik- und Stromnetz-Puzzle.",
        "goal": "Verbinde alle Knotenpunkte mit Strom.",
        "gameplay": "Klicke auf Knoten, um den Stromkreis zu schließen.",
        "controls": "Maus / Touch oder D-Pad zum Umschalten"
    },
    "Neon Dash": {
        "desc": "Rasanter Cyberpunk-Endless-Runner.",
        "goal": "Weiche Hindernissen aus.",
        "gameplay": "Springe über Spikes und Blockaden. Steigende Geschwindigkeit.",
        "controls": "Leertaste / D-Pad Oben / Touch (Springen)"
    },
    "Byte Hopper": {
        "desc": "Vertikale Jump-and-Run-Plattform-Action.",
        "goal": "Springe über Speicherregister so hoch wie möglich.",
        "gameplay": "Nutze präzise Sprünge und sammle Datenmünzen ein.",
        "controls": "D-Pad: Bewegen / Oben: Springen"
    },
    "Quantum Maze": {
        "desc": "Prozedural generiertes Sci-Fi-Labyrinth.",
        "goal": "Sammle Quantenkerne und Datenfragmente.",
        "gameplay": "Nach 10 Kernen baut sich ein komplexeres Labyrinth auf.",
        "controls": "D-Pad / Pfeiltasten (Bewegen)"
    },
    "Sub-Zero Miner": {
        "desc": "Mining-Abenteuer in eisigen Tiefen.",
        "goal": "Sammle O2-Blasen und Edelsteine.",
        "gameplay": "Meide Eis und toxische Sporen. O2 sinkt mit jeder Tiefe schneller.",
        "controls": "D-Pad / WASD (Bohr-Rig steuern)"
    },
    "Retro Pong 2077": {
        "desc": "High-Tech-Evolution des Arcade-Klassikers.",
        "goal": "Schlage den Energieball zurück und besiege den Gegner.",
        "gameplay": "Schnelle Ballwechsel und präzise Paddel-Action.",
        "controls": "D-Pad Oben / Unten (Paddel bewegen)"
    },
    "Bug Hunter": {
        "desc": "Schnelles Arcade-Such- und Tipp-Spiel.",
        "goal": "Zertrümmere digitale Bugs vor Ablauf des Timers.",
        "gameplay": "Reagiere blitzschnell auf erscheinende System-Bugs.",
        "controls": "Touch / Mausklick (Bugs antippen)"
    },
    "Cyber Snake": {
        "desc": "Klassisches Schlangen-Spiel im Cyber-Design.",
        "goal": "Sammle Datenpakete, ohne Wände zu treffen.",
        "gameplay": "Steuri die Cyber-Schlange geschickt über das Raster.",
        "controls": "D-Pad / WASD (Richtung ändern)"
    },
    "Matrix Invaders": {
        "desc": "Vertikaler Cyberpunk-Space-Shooter.",
        "goal": "Vernichte anstürmende Drohnen, Speeders und Tanks.",
        "gameplay": "Nutze Laser-Upgrades und Energieschilde gegen den Breach.",
        "controls": "D-Pad: Bewegen | Space: Feuer"
    },
    "Bit Blaster": {
        "desc": "Klassisches Brick-Breaker-Spiel.",
        "goal": "Zerstöre alle Datensteine mit dem Energieball.",
        "gameplay": "Fange den Ball mit dem Paddle ab und räume das Feld.",
        "controls": "D-Pad Links / Rechts (Paddle bewegen)"
    },
    "Pulse Racer": {
        "desc": "High-Speed-Autobahnrennen im Cyber-Space.",
        "goal": "Weiche entgegenkommendem Verkehr und Hindernissen aus.",
        "gameplay": "Manövriere mit Höchstgeschwindigkeit durch den Verkehr.",
        "controls": "D-Pad Links / Rechts (Lenken)"
    },
    "Crypto Decrypt": {
        "desc": "Logik-Code-Knacker-Puzzle.",
        "goal": "Errate die 4-stellige Sicherheitskombination.",
        "gameplay": "Kombiniere Ziffern vor Ablauf des System-Lockouts.",
        "controls": "D-Pad: Ziffern wählen | Enter: Bestätigen"
    },
    "Kernel Panic": {
        "desc": "System-Verteidigungsspiel gegen Speicherlecks.",
        "goal": "Flicke fallende Memory-Leaks, bevor der RAM überläuft.",
        "gameplay": "Klicke auf abstürzende Code-Blöcke (ERR, NULL).",
        "controls": "Touch / Mausklick (Lecks patchen)"
    },
    "Orbital Defense": {
        "desc": "Planetares Verteidigungsspiel.",
        "goal": "Schütze den Reaktor-Kern vor eintreffenden Meteoren.",
        "gameplay": "Rotiere den Energieschild präzise, um Weltraummüll abzuwehren.",
        "controls": "D-Pad Links / Rechts (Schild rotieren)"
    },
    "Chrono Shift": {
        "desc": "High-Speed-Zeitparadoxon-Spiel.",
        "goal": "Sammle Fragmente und meide deinen eigenen Echo-Trail.",
        "gameplay": "Jede Bewegung hinterlässt ein gefährliches Zeit-Echo.",
        "controls": "D-Pad / WASD (Navigation)"
    },
    "Sonic Pulse": {
        "desc": "Rhythmus-Timing-Präzisionsspiel.",
        "goal": "Triff kollabierende Energie-Ringe im exakten Moment.",
        "gameplay": "Baue Combos auf und halte die Systemintegrität aufrecht.",
        "controls": "Leertaste / A-Button / Klick (Puls auslösen)"
    },
    "Gravity Sling": {
        "desc": "Astrodynamisches Physik-Puzzle.",
        "goal": "Manövriere die Raumsonde durch Gravitationsfelder.",
        "gameplay": "Nutze die Schwerkraft von Planeten, um Kristalle zu sammeln.",
        "controls": "D-Pad / Touch (Schub geben)"
    },
    "Glitch Runner": {
        "desc": "Reaktionsschneller Plattform-Runner.",
        "goal": "Überlebe den Plattform-Wechsel im Glitch-Modus.",
        "gameplay": "Kurze Sprünge und schnelles Timing im digitalen Raster.",
        "controls": "D-Pad Oben / Space (Schnellstart-Sprung)"
    },
    "Aether Defender": {
        "desc": "Farbbasiertes Taktik-Shooter-Spiel.",
        "goal": "Absorbiere feindliche Drohnen mit passender Schild-Polarität.",
        "gameplay": "Wechsle im richtigen Moment die Polarität (Cyan/Magenta).",
        "controls": "D-Pad: Bewegen | Space: Polarität wechseln"
    }
}


class BaseGame:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Automatische Umschreibung von handle_input für Subklassen
        if "handle_input" in cls.__dict__:
            orig_handle = cls.__dict__["handle_input"]
            def wrapped_handle(self, *args, **kwargs):
                BaseGame.handle_input(self)
                if self.showing_intro:
                    return
                return orig_handle(self, *args, **kwargs)
            cls.handle_input = wrapped_handle

        # Automatische Umschreibung von update für Subklassen
        if "update" in cls.__dict__:
            orig_update = cls.__dict__["update"]
            def wrapped_update(self, dt, *args, **kwargs):
                BaseGame.update(self, dt)
                if self.showing_intro:
                    return
                return orig_update(self, dt, *args, **kwargs)
            cls.update = wrapped_update

        # Automatische Umschreibung von render für Subklassen
        if "render" in cls.__dict__:
            orig_render = cls.__dict__["render"]
            def wrapped_render(self, surface, *args, **kwargs):
                if self.showing_intro:
                    self.render_intro(surface)
                    return
                return orig_render(self, surface, *args, **kwargs)
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

        meta = GAME_METADATA.get(game_name, {
            "desc": "Ein spannendes Retro-Spiel für Handhelds.",
            "goal": "Erreiche den höchsten Score.",
            "gameplay": "Spiele geschickt und meistere alle Herausforderungen.",
            "controls": "D-Pad & A-Button / Touch"
        })
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
        return 1.0 + self.elapsed_time * 0.05

    def get_virtual_mouse_pos(self) -> tuple[int, int]:
        if hasattr(self.engine, "get_virtual_mouse_pos"):
            return self.engine.get_virtual_mouse_pos()
        return pygame.mouse.get_pos()

    def add_score(self, amount: int) -> None:
        self.score += amount

    def play_sound(self, sound_name: str) -> None:
        if hasattr(self.engine, "audio") and self.engine.audio:
            self.engine.audio.play(sound_name)

    def render_ui(self, surface: pygame.Surface) -> None:
        score_txt = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        surface.blit(score_txt, (10, 5))

    def handle_input(self) -> None:
        if self.showing_intro:
            inp = getattr(self.engine, "input", None)
            if inp and (getattr(inp, "is_key_just_pressed", lambda k: False)(pygame.K_SPACE) or
                        getattr(inp, "is_key_just_pressed", lambda k: False)(pygame.K_RETURN) or
                        getattr(inp, "is_key_just_pressed", lambda k: False)(pygame.K_z) or
                        getattr(inp, "is_key_just_pressed", lambda k: False)(pygame.K_UP) or
                        getattr(inp, "mouse_clicked", False)):
                self.showing_intro = False
                self.play_sound("confirm")

    def update(self, dt: float) -> None:
        if self.showing_intro:
            return
        if not self.paused and not self.game_over:
            self.elapsed_time += dt

    def render(self, surface: pygame.Surface) -> None:
        if self.showing_intro:
            self.render_intro(surface)

    def render_intro(self, surface: pygame.Surface) -> None:
        surface.fill((8, 12, 22))
        pygame.draw.rect(surface, (0, 200, 255), (10, 10, 300, 220), 2, border_radius=6)
        pygame.draw.rect(surface, (15, 25, 45), (12, 12, 296, 216), border_radius=5)

        title_surf = self.title_font.render(self.game_name.upper(), True, (0, 255, 200))
        surface.blit(title_surf, (160 - title_surf.get_width() // 2, 18))

        y = 48
        desc_lbl = self.font.render("BESCHREIBUNG:", True, (255, 215, 0))
        surface.blit(desc_lbl, (22, y))
        y += 15
        desc_txt = self.font.render(self.description, True, (220, 220, 220))
        surface.blit(desc_txt, (22, y))
        y += 22

        goal_lbl = self.font.render("SPIELZIEL:", True, (255, 215, 0))
        surface.blit(goal_lbl, (22, y))
        y += 15
        goal_txt = self.font.render(self.goal, True, (220, 220, 220))
        surface.blit(goal_txt, (22, y))
        y += 22

        gp_lbl = self.font.render("GAMEPLAY:", True, (255, 215, 0))
        surface.blit(gp_lbl, (22, y))
        y += 15
        gp_txt = self.font.render(self.gameplay, True, (220, 220, 220))
        surface.blit(gp_txt, (22, y))
        y += 22

        ctrl_lbl = self.font.render("STEUERUNG:", True, (255, 215, 0))
        surface.blit(ctrl_lbl, (22, y))
        y += 15
        ctrl_txt = self.font.render(self.controls, True, (0, 255, 150))
        surface.blit(ctrl_txt, (22, y))

        if int(pygame.time.get_ticks() / 250) % 2 == 0:
            prompt_txt = self.font.render("-> DRÜCKE SPACE / A ZUM STARTEN <-", True, (255, 255, 255))
            surface.blit(prompt_txt, (160 - prompt_txt.get_width() // 2, 205))

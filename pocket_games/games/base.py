from __future__ import annotations

import pygame

TRANSLATIONS = {
    "Deutsch": {
        "settings_title": "SYSTEM EINSTELLUNGEN",
        "sound_effects": "Soundeffekte Audio",
        "master_volume": "Gesamtlautstärke",
        "fullscreen_mode": "Vollbildmodus",
        "language": "Sprache",
        "back_menu": "Zurück zum Menü",
        "enabled": "AN",
        "disabled": "AUS",
        "on": "AN",
        "off": "AUS",
        "hall_of_fame": "🏆 HALL OF FAME (Highscores)",
        "no_scores": "Noch keine Highscores vorhanden.",
        "back_hint": "[Esc / Enter] Zurück zum Menü",
        "press_start": "-> DRÜCKE SPACE / A ZUM STARTEN <-",
        "game_over": "GAME OVER",
        "final_score": "FINAL SCORE",
        "high_score": "HIGH SCORE",
        "desc_lbl": "BESCHREIBUNG:",
        "goal_lbl": "SPIELZIEL:",
        "gp_lbl": "GAMEPLAY:",
        "ctrl_lbl": "STEUERUNG:"
    },
    "English": {
        "settings_title": "SYSTEM SETTINGS",
        "sound_effects": "Sound Effect Audio",
        "master_volume": "Master Volume",
        "fullscreen_mode": "Fullscreen Mode",
        "language": "Language",
        "back_menu": "Back to Main Menu",
        "enabled": "ENABLED",
        "disabled": "DISABLED",
        "on": "ON",
        "off": "OFF",
        "hall_of_fame": "🏆 HALL OF FAME (Highscores)",
        "no_scores": "No high scores available yet.",
        "back_hint": "[Esc / Enter] Back to Menu",
        "press_start": "-> PRESS SPACE / A TO START <-",
        "game_over": "GAME OVER",
        "final_score": "FINAL SCORE",
        "high_score": "HIGH SCORE",
        "desc_lbl": "DESCRIPTION:",
        "goal_lbl": "OBJECTIVE:",
        "gp_lbl": "GAMEPLAY:",
        "ctrl_lbl": "CONTROLS:"
    }
}


def t(engine, key: str) -> str:
    lang = "English"
    if hasattr(engine, "settings") and engine.settings:
        lang = getattr(engine.settings, "language", "English")
    if lang not in TRANSLATIONS:
        lang = "English"
    return TRANSLATIONS[lang].get(key, key)


GAME_METADATA = {
    "Pixel Drop": {
        "de": {
            "desc": "Klassisches Tetris-Puzzle mit fallenden Steinen.",
            "goal": "Staple Blöcke sauber und räume Reihen ab.",
            "gameplay": "Alle 20 geräumten Reihen steigt das Level und die Geschwindigkeit.",
            "controls": "D-Pad: Bewegen / Drehen / Soft Drop"
        },
        "en": {
            "desc": "Classic Tetris puzzle with falling blocks.",
            "goal": "Stack blocks cleanly and clear lines.",
            "gameplay": "Every 20 cleared lines increases level and speed.",
            "controls": "D-Pad: Move / Rotate / Soft Drop"
        }
    },
    "Circuit Breaker": {
        "de": {
            "desc": "Digitales Logik- und Stromnetz-Puzzle.",
            "goal": "Verbinde alle Knotenpunkte mit Strom.",
            "gameplay": "Klicke auf Knoten, um den Stromkreis zu schließen.",
            "controls": "Maus / Touch oder D-Pad zum Umschalten"
        },
        "en": {
            "desc": "Digital logic and power grid puzzle.",
            "goal": "Connect all nodes with power.",
            "gameplay": "Click nodes to close the circuit.",
            "controls": "Mouse / Touch or D-Pad to toggle"
        }
    },
    "Neon Dash": {
        "de": {
            "desc": "Rasanter Cyberpunk-Endless-Runner.",
            "goal": "Weiche Hindernissen und 2er/3er/4er-Blöcken aus.",
            "gameplay": "Springe über Spikes und Blockaden. Steigende Geschwindigkeit.",
            "controls": "Leertaste / D-Pad Oben / Touch (Springen)"
        },
        "en": {
            "desc": "Fast-paced cyberpunk endless runner.",
            "goal": "Dodge obstacles and 2/3/4-blocks.",
            "gameplay": "Jump over spikes and barriers. Increasing speed.",
            "controls": "Space / D-Pad Up / Touch (Jump)"
        }
    },
    "Byte Hopper": {
        "de": {
            "desc": "Vertikale Jump-and-Run-Plattform-Action.",
            "goal": "Springe über Speicherregister so hoch wie möglich.",
            "gameplay": "Nutze statische, horizontal und vertikal schwingende Plattformen.",
            "controls": "D-Pad: Bewegen / Oben: Springen"
        },
        "en": {
            "desc": "Vertical jump-and-run platform action.",
            "goal": "Jump across memory registers as high as possible.",
            "gameplay": "Use static, horizontally and vertically oscillating platforms.",
            "controls": "D-Pad: Move / Up: Jump"
        }
    },
    "Quantum Maze": {
        "de": {
            "desc": "Prozedural generiertes Sci-Fi-Labyrinth.",
            "goal": "Sammle Quantenkerne und Datenfragmente.",
            "gameplay": "Nach 10 Kernen baut sich ein komplexeres Labyrinth auf.",
            "controls": "D-Pad / Pfeiltasten (Bewegen)"
        },
        "en": {
            "desc": "Procedurally generated sci-fi labyrinth.",
            "goal": "Collect quantum cores and data fragments.",
            "gameplay": "After 10 cores, a more complex maze builds up.",
            "controls": "D-Pad / Arrow keys (Move)"
        }
    },
    "Sub-Zero Miner": {
        "de": {
            "desc": "Mining-Abenteuer in eisigen Tiefen.",
            "goal": "Sammle O2-Blasen und Edelsteine.",
            "gameplay": "Meide Eis und toxische Sporen. O2 sinkt mit jeder Tiefe schneller.",
            "controls": "D-Pad / WASD (Bohr-Rig steuern)"
        },
        "en": {
            "desc": "Mining adventure in deep ice.",
            "goal": "Collect O2 bubbles and gems.",
            "gameplay": "Avoid ice and toxic spores. O2 depletes faster with depth.",
            "controls": "D-Pad / WASD (Control mining rig)"
        }
    },
    "Retro Pong 2077": {
        "de": {
            "desc": "High-Tech-Evolution des Arcade-Klassikers.",
            "goal": "Schlage den Energieball zurück und besiege den Gegner.",
            "gameplay": "Schnelle Ballwechsel und präzise Paddel-Action.",
            "controls": "D-Pad Oben / Unten (Paddel bewegen)"
        },
        "en": {
            "desc": "High-tech evolution of the arcade classic.",
            "goal": "Return the energy ball and defeat the opponent.",
            "gameplay": "Fast ball rallies and precise paddle action.",
            "controls": "D-Pad Up / Down (Move paddle)"
        }
    },
    "Bug Hunter": {
        "de": {
            "desc": "Schnelles Arcade-Such- und Tipp-Spiel.",
            "goal": "Zertrümmere digitale Bugs vor Ablauf des Timers.",
            "gameplay": "Reagiere blitzschnell auf erscheinende System-Bugs.",
            "controls": "Touch / Mausklick (Bugs antippen)"
        },
        "en": {
            "desc": "Fast arcade search and tap game.",
            "goal": "Smash digital bugs before the timer runs out.",
            "gameplay": "React lightning-fast to appearing system bugs.",
            "controls": "Touch / Mouse click (Tap bugs)"
        }
    },
    "Cyber Snake": {
        "de": {
            "desc": "Klassisches Schlangen-Spiel im Cyber-Design.",
            "goal": "Sammle Datenpakete, ohne Wände zu treffen.",
            "gameplay": "Steuere die Cyber-Schlange geschickt über das Raster.",
            "controls": "D-Pad / WASD (Richtung ändern)"
        },
        "en": {
            "desc": "Classic snake game in cyber design.",
            "goal": "Collect data packets without hitting walls.",
            "gameplay": "Steer the cyber snake skillfully across the grid.",
            "controls": "D-Pad / WASD (Change direction)"
        }
    },
    "Matrix Invaders": {
        "de": {
            "desc": "Vertikaler Cyberpunk-Space-Shooter.",
            "goal": "Vernichte anstürmende Drohnen, Speeders und Tanks.",
            "gameplay": "Nutze Laser-Upgrades und Energieschilde gegen den Breach.",
            "controls": "D-Pad: Bewegen | Space: Feuer"
        },
        "en": {
            "desc": "Vertical cyberpunk space shooter.",
            "goal": "Destroy oncoming drones, speeders, and tanks.",
            "gameplay": "Use laser upgrades and energy shields against the breach.",
            "controls": "D-Pad: Move | Space: Fire"
        }
    },
    "Bit Blaster": {
        "de": {
            "desc": "Klassisches Brick-Breaker-Spiel.",
            "goal": "Zerstöre alle Datensteine mit dem Energieball.",
            "gameplay": "Fange den Ball mit dem Paddle ab und räume das Feld.",
            "controls": "D-Pad Links / Rechts (Paddle bewegen)"
        },
        "en": {
            "desc": "Classic brick breaker game.",
            "goal": "Destroy all data bricks with the energy ball.",
            "gameplay": "Catch the ball with the paddle and clear the field.",
            "controls": "D-Pad Left / Right (Move paddle)"
        }
    },
    "Pulse Racer": {
        "de": {
            "desc": "High-Speed-Autobahnrennen im Cyber-Space.",
            "goal": "Weiche entgegenkommendem Verkehr und Hindernissen aus.",
            "gameplay": "Manövriere mit Höchstgeschwindigkeit durch den Verkehr.",
            "controls": "D-Pad Links / Rechts (Lenken)"
        },
        "en": {
            "desc": "High-speed cyber space highway racing.",
            "goal": "Dodge oncoming traffic and obstacles.",
            "gameplay": "Maneuver through traffic at top speed.",
            "controls": "D-Pad Left / Right (Steer)"
        }
    },
    "Crypto Decrypt": {
        "de": {
            "desc": "Logik-Code-Knacker-Puzzle.",
            "goal": "Errate die 4-stellige Sicherheitskombination.",
            "gameplay": "Kombiniere Ziffern vor Ablauf des System-Lockouts.",
            "controls": "D-Pad: Ziffern wählen | Enter: Bestätigen"
        },
        "en": {
            "desc": "Logic code-breaking puzzle.",
            "goal": "Guess the 4-digit security combination.",
            "gameplay": "Combine digits before system lockout.",
            "controls": "D-Pad: Select digits | Enter: Submit"
        }
    },
    "Kernel Panic": {
        "de": {
            "desc": "System-Verteidigungsspiel gegen Speicherlecks.",
            "goal": "Flicke fallende Memory-Leaks, bevor der RAM überläuft.",
            "gameplay": "Klicke auf abstürzende Code-Blöcke (ERR, NULL).",
            "controls": "Touch / Mausklick (Lecks patchen)"
        },
        "en": {
            "desc": "System defense game against memory leaks.",
            "goal": "Patch falling memory leaks before RAM overflows.",
            "gameplay": "Click crashing code blocks (ERR, NULL).",
            "controls": "Touch / Mouse click (Patch leaks)"
        }
    },
    "Orbital Defense": {
        "de": {
            "desc": "Planetares Verteidigungsspiel.",
            "goal": "Schütze den Reaktor-Kern vor eintreffenden Meteoren.",
            "gameplay": "Rotiere den Energieschild präzise, um Weltraummüll abzuwehren.",
            "controls": "D-Pad Links / Rechts (Schild rotieren)"
        },
        "en": {
            "desc": "Planetary defense game.",
            "goal": "Protect the reactor core from incoming meteors.",
            "gameplay": "Rotate the energy shield precisely to deflect space debris.",
            "controls": "D-Pad Left / Right (Rotate shield)"
        }
    },
    "Chrono Shift": {
        "de": {
            "desc": "High-Speed-Zeitparadoxon-Spiel.",
            "goal": "Sammle Fragmente und meide deinen eigenen Echo-Trail.",
            "gameplay": "Jede Bewegung hinterlässt ein gefährliches Zeit-Echo.",
            "controls": "D-Pad / WASD (Navigation)"
        },
        "en": {
            "desc": "High-speed time paradox game.",
            "goal": "Collect fragments and avoid your own echo trail.",
            "gameplay": "Every movement leaves a dangerous time echo.",
            "controls": "D-Pad / WASD (Navigation)"
        }
    },
    "Sonic Pulse": {
        "de": {
            "desc": "Rhythmus-Timing-Präzisionsspiel.",
            "goal": "Triff kollabierende Energie-Ringe im exakten Moment.",
            "gameplay": "Baue Combos auf und halte die Systemintegrität aufrecht.",
            "controls": "Leertaste / A-Button / Klick (Puls auslösen)"
        },
        "en": {
            "desc": "Rhythm timing precision game.",
            "goal": "Hit collapsing energy rings at the exact moment.",
            "gameplay": "Build combos and maintain system integrity.",
            "controls": "Space / A-Button / Click (Trigger pulse)"
        }
    },
    "Gravity Sling": {
        "de": {
            "desc": "Astrodynamisches Physik-Puzzle.",
            "goal": "Manövriere die Raumsonde durch Gravitationsfelder.",
            "gameplay": "Nutze die Schwerkraft von Planeten, um Kristalle zu sammeln.",
            "controls": "D-Pad / Touch (Schub geben)"
        },
        "en": {
            "desc": "Astrodynamic physics puzzle.",
            "goal": "Maneuver the space probe through gravitational fields.",
            "gameplay": "Use planet gravity to collect crystals.",
            "controls": "D-Pad / Touch (Apply thrust)"
        }
    },
    "Glitch Runner": {
        "de": {
            "desc": "Reaktionsschneller Plattform-Runner.",
            "goal": "Überlebe den Plattform-Wechsel im Glitch-Modus.",
            "gameplay": "Kurze Sprünge und schnelles Timing im digitalen Raster.",
            "controls": "D-Pad Oben / Space (Schnellstart-Sprung)"
        },
        "en": {
            "desc": "Responsive platform runner.",
            "goal": "Survive platform switching in glitch mode.",
            "gameplay": "Short jumps and quick timing in the digital grid.",
            "controls": "D-Pad Up / Space (Quick jump)"
        }
    },
    "Aether Defender": {
        "de": {
            "desc": "Farbbasiertes Taktik-Shooter-Spiel.",
            "goal": "Absorbiere feindliche Drohnen mit passender Schild-Polarität.",
            "gameplay": "Wechsle im richtigen Moment die Polarität (Cyan/Magenta).",
            "controls": "D-Pad: Bewegen | Space: Polarität wechseln"
        },
        "en": {
            "desc": "Color-based tactical shooter game.",
            "goal": "Absorb hostile drones with matching shield polarity.",
            "gameplay": "Switch polarity at the right moment (Cyan/Magenta).",
            "controls": "D-Pad: Move | Space: Switch polarity"
        }
    }
}


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
        meta = game_data.get(lang_key, game_data.get("en", {
            "desc": "An exciting retro game.",
            "goal": "Achieve the highest score.",
            "gameplay": "Play skillfully.",
            "controls": "D-Pad & A"
        }))
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
        inp = getattr(self.engine, "input", None)
        if not inp:
            return
        if self.showing_intro:
            if (inp.is_key_just_pressed(pygame.K_SPACE) or 
                inp.is_key_just_pressed(pygame.K_RETURN) or 
                inp.is_key_just_pressed(pygame.K_z) or
                inp.is_key_just_pressed(pygame.K_UP) or
                inp.mouse_clicked):
                self.showing_intro = False
                self.play_sound("confirm")
        elif self.game_over and (inp.is_key_just_pressed(pygame.K_ESCAPE) or
            inp.is_key_just_pressed(pygame.K_RETURN) or
            inp.is_key_just_pressed(pygame.K_SPACE) or
            inp.mouse_clicked):
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

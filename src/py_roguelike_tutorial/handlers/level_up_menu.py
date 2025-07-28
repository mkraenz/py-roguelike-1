from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import tcod
from tcod.console import Console
from tcod.event import KeySym as Key

from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)
from py_roguelike_tutorial.handlers.confirmation_popup import ConfirmationPopup
from py_roguelike_tutorial.handlers.ingame_event_handler import IngameEventHandler
from py_roguelike_tutorial.handlers.main_game_event_handler import MainGameEventHandler
from py_roguelike_tutorial.render_functions import (
    print_aligned_texts_center,
    IngameMenuConsole,
)

if TYPE_CHECKING:
    pass


class LevelUpMenu(IngameEventHandler):
    def on_render(self, console: Console, delta_time: float) -> None:
        title = "New Level"
        super().on_render(console, delta_time)
        child_console, blit = IngameMenuConsole(console, title)

        fighter_stats = self.player.fighter
        health_stats = self.player.health
        texts = [
            "Select an attribute to increase.",
            "",
            f"[S] Strength (+1 attack, from {fighter_stats.power}",
            f"[A] Agility (+1 defense, from {fighter_stats.defense})",
            f"[C] Constitution (+20 HP, from {health_stats.max_hp})",
        ]
        print_aligned_texts_center(child_console, texts, child_console.height // 2 - 6)
        blit()

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        """User cannot exit the menu without selecting an option."""
        key = event.sym

        def on_confirm(cb: Callable[[], None]):
            def inner():
                cb()
                if self.player.level.requires_level_up:
                    return self
                self.engine.stack.pop()
                return MainGameEventHandler(self.engine)

            return inner

        match key:
            case Key.S:
                return ConfirmationPopup(
                    self.engine.stack,
                    "Increase strength?",
                    callback=on_confirm(self.player.level.increase_power),
                )
            case Key.A:
                return ConfirmationPopup(
                    self.engine.stack,
                    "Increase agility?",
                    callback=on_confirm(self.player.level.increase_defense),
                )
            case Key.C:
                return ConfirmationPopup(
                    self.engine.stack,
                    "Increase constitution?",
                    callback=on_confirm(self.player.level.increase_max_hp),
                )
            case _:
                pass
        # there may be multiple level ups at once necessary, e.g. if the player killed a super high-EXP boss
        if not self.player.level.requires_level_up:
            self.engine.stack.pop()
            return None
        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown, /
    ) -> ActionOrHandler | None:
        """Forbid exiting the menu on mouse click."""
        return None

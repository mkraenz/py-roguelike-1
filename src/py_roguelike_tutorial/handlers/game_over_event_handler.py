from __future__ import annotations

import os.path
from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.event import KeySym as Key, Quit, KeyDown

from py_roguelike_tutorial import setup_game
from py_roguelike_tutorial.constants import AUTOSAVE_FILENAME
from py_roguelike_tutorial.exceptions import QuitWithoutSaving
from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)
from py_roguelike_tutorial.handlers.ingame_event_handler import IngameEventHandler
from py_roguelike_tutorial.handlers.log_history_menu import LogHistoryMenu
from py_roguelike_tutorial.render_functions import (
    print_aligned_texts_center,
    render_you_died,
    dim_console,
)

if TYPE_CHECKING:
    pass

_CONFIRM_KEYS = {
    Key.RETURN,
    Key.KP_ENTER,
}


class GameOverEventHandler(IngameEventHandler):
    def on_render(self, console: Console, delta_time: float) -> None:
        super().on_render(console, delta_time)
        dim_console(console)
        render_you_died(console, 2, console.height // 2 - 7 // 2 - 1)
        texts = ["[F] Back to title menu", "[V] View combat log"]
        print_aligned_texts_center(console, texts, console.height // 2 + 10)

    def ev_keydown(self, event: KeyDown, /) -> ActionOrHandler | None:
        key = event.sym
        match key:
            case Key.ESCAPE | Key.F:
                return self.on_confirm()
            case _ if key in _CONFIRM_KEYS:
                return self.on_confirm()
            case Key.V:
                return LogHistoryMenu(self.engine)
            case _:
                return None

    def on_confirm(self) -> None | ActionOrHandler:
        self.engine.stack.clear()
        return setup_game.MainMenu(self.engine.stack)

    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists(AUTOSAVE_FILENAME):
            os.remove(AUTOSAVE_FILENAME)  # permadeath, baby
        raise QuitWithoutSaving()

    # compiler is not clever enough to notice that on_quit raises an exception...
    def ev_quit(self, event: Quit):  # type: ignore [reportIncompatibleMethodOverride]
        self.on_quit()

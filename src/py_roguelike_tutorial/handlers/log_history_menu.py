from __future__ import annotations

from typing import TYPE_CHECKING

import tcod
from tcod.console import Console
from tcod.event import KeySym as Key

from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)
from py_roguelike_tutorial.handlers.ingame_event_handler import IngameEventHandler
from py_roguelike_tutorial.handlers.key_map import _CURSOR_Y_KEYS
from py_roguelike_tutorial.render_functions import (
    IngameMenuConsole,
)

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine


class LogHistoryMenu(IngameEventHandler):
    """Print the history on a larger window which can be scrolled."""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: Console, delta_time: float) -> None:
        super().on_render(console, delta_time)

        child_console, blit = IngameMenuConsole(console, "Message History")

        self.engine.message_log.render_messages(
            child_console,
            x=1,
            y=1,
            width=child_console.width - 2,
            height=child_console.height - 2,
            messages=self.engine.message_log.messages[: self.cursor + 1],
        )
        blit()

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        end = self.log_length - 1
        match event.sym:
            case _ if event.sym in _CURSOR_Y_KEYS:
                adjust = _CURSOR_Y_KEYS[event.sym]
                match adjust:
                    case _ if adjust < 0 and self.cursor == 0:
                        # we wrap around to the bottom if we are at the top and continue going upwards
                        self.cursor = end
                    case _ if adjust > 0 and self.cursor == end:
                        # conversely, we wrap around to the top if we are at the bottom and continue going downwards
                        self.cursor = 0
                    case _:
                        self.cursor = max(0, min(self.cursor + adjust, end))
            case Key.HOME:
                self.cursor = 0  # move to first message
            case Key.END:
                self.cursor = end  # move to last message
            case _:  # if no key matches, return to the main game
                self.engine.stack.pop()
                return None
        return None

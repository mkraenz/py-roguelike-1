from __future__ import annotations

from typing import TYPE_CHECKING

import tcod
from tcod.console import Console

from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
    BaseEventHandler,
)
from py_roguelike_tutorial.render_functions import (
    dim_console,
    print_text_center,
)
from py_roguelike_tutorial.screen_stack import ScreenStack

if TYPE_CHECKING:
    pass


class PopupMessage(BaseEventHandler):
    """Displays a popup window. Hands back control to the `parent_handler`
    (typically, the previous screen) on any key stroke."""

    def __init__(self, stack: ScreenStack, text: str):
        self.stack = stack
        self.text = text

    def on_render(self, console: Console, delta_time: float) -> None:
        dim_console(console)
        print_text_center(console, self.text, console.height // 2)

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        self.stack.pop()
        return None

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import tcod
from tcod.console import Console
from tcod.event import KeySym as Key

from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
    BaseEventHandler,
)
from py_roguelike_tutorial.render_functions import (
    print_aligned_texts_center,
    dim_console,
)
from py_roguelike_tutorial.screen_stack import ScreenStack

if TYPE_CHECKING:
    pass


class ConfirmationPopup(BaseEventHandler):
    """A popup window asking for confirmation.
    On [Y], calls the callback. Else hands back control to the parent."""

    def __init__(
        self,
        stack: ScreenStack,
        text: str,
        callback: Callable[[], BaseEventHandler],
    ):
        self.text = text
        self.callback = callback
        self.stack = stack

    def on_render(self, console: Console, delta_time: float) -> None:
        dim_console(console)

        texts = [self.text, "", "[Y] Confirm", "[*] Cancel"]
        print_aligned_texts_center(console, texts, console.height // 2 - 2)

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        key = event.sym
        self.stack.pop()
        match key:
            case Key.Y:
                return self.callback()
            case _:
                return None

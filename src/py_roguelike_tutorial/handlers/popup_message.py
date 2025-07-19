from __future__ import annotations

import os.path
from typing import TYPE_CHECKING, Callable, Type

import tcod
from tcod.console import Console
from tcod.event import KeySym as Key, Quit, KeyDown, Modifier

from py_roguelike_tutorial import setup_game
from py_roguelike_tutorial.actions import (
    Action,
    DropItemAction,
    EquipAction,
)
from py_roguelike_tutorial.colors import Theme, Color
from py_roguelike_tutorial.constants import AUTOSAVE_FILENAME
from py_roguelike_tutorial.exceptions import QuitWithoutSaving
from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
    BaseEventHandler,
)
from py_roguelike_tutorial.handlers.ingame_event_handler import IngameEventHandler
from py_roguelike_tutorial.handlers.main_game_event_handler import MainGameEventHandler
from py_roguelike_tutorial.render_functions import (
    print_aligned_texts_center,
    render_you_died,
    dim_console,
    print_text_center,
    IngameMenuConsole,
)
from py_roguelike_tutorial.screen_stack import ScreenStack
from py_roguelike_tutorial.types import Coord

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Item


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

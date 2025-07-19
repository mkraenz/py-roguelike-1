from __future__ import annotations


import tcod

from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)
from py_roguelike_tutorial.handlers.ingame_event_handler import IngameEventHandler
from py_roguelike_tutorial.handlers.key_map import _MODIFIER_KEYS


class AskUserEventHandler(IngameEventHandler):
    """Handles user input for actions that require some special input."""

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        """By default, any unhandled key cancels the menu."""
        key = event.sym
        match key:
            case _ if key in _MODIFIER_KEYS:
                return None  # ignore modifiers
            case _:
                return self.on_exit()

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown, /
    ) -> ActionOrHandler | None:
        """By default, any mouse click exists the menu."""
        self.engine.stack.pop()
        return None

    def on_exit(self) -> ActionOrHandler | None:
        """Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        self.engine.stack.pop()
        return None

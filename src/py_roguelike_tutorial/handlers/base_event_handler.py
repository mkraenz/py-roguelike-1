from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import tcod
from tcod.console import Console
from tcod.event import EventDispatch

from py_roguelike_tutorial.actions import (
    Action,
)

if TYPE_CHECKING:
    pass

"""An event handler return type which can trigger an action or switch active event handlers.

If a handler is returned, then it will become the active event handler for future events.
If an action is returned, then it will be attempted and if it is valid, 
then MainGameEventHandler will become the active handler
"""
type ActionOrHandler = "Action | BaseEventHandler"


class BaseEventHandler(EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} cannot handle actions."
        return self

    def on_render(self, console: Console, delta_time: float) -> None:
        raise NotImplementedError("Must be implemented in subclass.")

    def ev_quit(self, event: tcod.event.Quit, /):
        sys.exit()

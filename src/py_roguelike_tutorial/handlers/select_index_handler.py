from __future__ import annotations

from typing import TYPE_CHECKING

import tcod
from tcod.console import Console
from tcod.event import Modifier

from py_roguelike_tutorial.colors import Color
from py_roguelike_tutorial.handlers.ask_user_event_handler import AskUserEventHandler
from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)
from py_roguelike_tutorial.handlers.key_map import _CONFIRM_KEYS, _MOVE_KEYS

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine


class SelectIndexHandler(AskUserEventHandler):
    """Asks the user for an index on the map."""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player on construction."""
        super().__init__(engine)
        engine.mouse_location = self.player.x, self.player.y

    def on_render(self, console: Console, delta_time: float) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console, delta_time)
        x, y = self.engine.mouse_location
        console.rgb["bg"][x, y] = Color.WHITE
        console.rgb["fg"][x, y] = Color.BLACK

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        """Check for key movement or confirmation keys."""
        key = event.sym
        x, y = self.engine.mouse_location
        match key:
            case _ if key in _MOVE_KEYS:
                # holding modifier keys will speed up movement, e.g. 5 tiles at a time when holding shift.
                modifier = 1
                if event.mod & (Modifier.LSHIFT | Modifier.RSHIFT):
                    modifier *= 5
                if event.mod & (Modifier.LCTRL | Modifier.RCTRL):
                    modifier *= 10
                if event.mod & (Modifier.LALT | Modifier.RALT):
                    modifier *= 20

                dx, dy = _MOVE_KEYS[key]
                x += dx * modifier
                y += dy * modifier
                # cursor should not leave the map, thus clamp
                x = max(0, min(x, self.engine.game_map.width - 1))
                y = max(0, min(y, self.engine.game_map.height - 1))
                self.engine.mouse_location = x, y
                return None
            case _ if key in _CONFIRM_KEYS:
                return self.on_index_selected(x, y)
            case _:
                return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown, /
    ) -> ActionOrHandler | None:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(int(event.position.x), int(event.position.y)):
            if event.button == 1:
                return self.on_index_selected(
                    int(event.position.x), int(event.position.y)
                )
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> ActionOrHandler | None:
        """Called when a tile index is selected."""
        raise NotImplementedError("Must be implemented by subclass.")

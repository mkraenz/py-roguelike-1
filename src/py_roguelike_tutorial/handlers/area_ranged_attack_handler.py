from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from tcod.console import Console

from py_roguelike_tutorial.actions import (
    Action,
)
from py_roguelike_tutorial.colors import Theme
from py_roguelike_tutorial.handlers.select_index_handler import SelectIndexHandler
from py_roguelike_tutorial.types import Coord

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine


class AreaRangedAttackHandler(SelectIndexHandler):
    """Targets an area."""

    def __init__(
        self, engine: Engine, radius: int, callback: Callable[[Coord], Action | None]
    ):
        super().__init__(engine)
        self.callback = callback
        self.radius = radius

    def on_render(self, console: Console, delta_time: float) -> None:
        """Highlight the area around the cursor"""
        super().on_render(console, delta_time)

        cursor_x, cursor_y = self.engine.mouse_location
        # enemies on the border will not be included in the radius
        console.draw_frame(
            x=cursor_x - self.radius - 1,
            y=cursor_y - self.radius - 1,
            width=(self.radius + 1) * 2 + 1,
            height=(self.radius + 1) * 2 + 1,
            fg=Theme.cursor_aoe,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Action | None:
        self.engine.stack.pop()
        return self.callback((x, y))

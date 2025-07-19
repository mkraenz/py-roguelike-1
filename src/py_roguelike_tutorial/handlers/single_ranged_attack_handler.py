from __future__ import annotations

from typing import TYPE_CHECKING, Callable


from py_roguelike_tutorial.actions import (
    Action,
)
from py_roguelike_tutorial.handlers.select_index_handler import SelectIndexHandler
from py_roguelike_tutorial.types import Coord

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine


class SingleRangedAttackHandler(SelectIndexHandler):
    """Targets a single enemy."""

    def __init__(self, engine: Engine, callback: Callable[[Coord], Action | None]):
        super().__init__(engine)
        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Action | None:
        self.engine.stack.pop()
        return self.callback((x, y))

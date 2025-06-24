from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Entity


class Action:
    def perform(self, engine: Engine, actor: Entity) -> None:
        raise NotImplementedError("subclasses must implement perform")


class EscapeAction(Action):
    def perform(self, engine: Engine, actor: Entity) -> None:
        sys.exit()


class MoveAction(Action):
    def __init__(self, dx: int, dy: int) -> None:
        super()
        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine, actor: Entity) -> None:
        next_x = actor.x + self.dx
        next_y = actor.y + self.dy
        if not engine.game_map.in_bounds(next_x, next_y):
            return
        if not engine.game_map.tiles["walkable"][next_x, next_y]:
            return

        actor.move(self.dx, self.dy)

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from py_roguelike_tutorial.types import Coord

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Entity


class Action:
    """Command pattern. Named Action to stick with the tutorial notion."""

    def __init__(self, entity: Entity):
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine

    def perform(self) -> None:
        raise NotImplementedError("subclasses must implement perform")


class WaitAction(Action):
    def perform(self) -> None:
        print(f"{self.entity.name} waits")


class EscapeAction(Action):
    def perform(self) -> None:
        sys.exit()


class DirectedAction(Action):
    def __init__(self, entity: Entity, dx: int, dy: int):
        super().__init__(entity)
        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Coord:
        """The destination coordinates."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Entity | None:
        return self.engine.game_map.get_blocking_entity_at(*self.dest_xy)


class MeleeAction(DirectedAction):
    def perform(self) -> None:
        target = self.blocking_entity
        if not target:
            return
        print(f"{self.entity.name} hits {target.name}")


class MoveAction(DirectedAction):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return
        if self.engine.game_map.get_blocking_entity_at(dest_x, dest_y):
            return
        self.entity.move(self.dx, self.dy)


class BumpAction(DirectedAction):
    def perform(self) -> None:
        if self.blocking_entity:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        return MoveAction(self.entity, self.dx, self.dy).perform()

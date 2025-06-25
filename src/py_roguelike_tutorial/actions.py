from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from py_roguelike_tutorial.types import Coord

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Entity


class Action:
    """Command pattern. Named Action to stick with the tutorial notion."""

    def __init__(self, actor: Entity):
        self.actor = actor

    @property
    def engine(self) -> Engine:
        return self.actor.game_map.engine

    def perform(self) -> None:
        raise NotImplementedError("subclasses must implement perform")


class WaitAction(Action):
    def perform(self) -> None:
        print(f"{self.actor.name} waits")


class EscapeAction(Action):
    def perform(self) -> None:
        sys.exit()


class DirectedAction(Action):
    def __init__(self, actor: Entity, dx: int, dy: int):
        super().__init__(actor)
        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Coord:
        """The destination coordinates."""
        return self.actor.x + self.dx, self.actor.y + self.dy

    @property
    def blocking_entity(self) -> Entity | None:
        return self.engine.game_map.get_blocking_entity_at(*self.dest_xy)


class MeleeAction(DirectedAction):
    def perform(self) -> None:
        target = self.blocking_entity
        if not target:
            return
        print(f"{self.actor.name} hits {target.name}")


class MoveAction(DirectedAction):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            return
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return
        if self.engine.game_map.get_blocking_entity_at(dest_x, dest_y):
            return
        self.actor.move(self.dx, self.dy)


class BumpAction(DirectedAction):
    def perform(self) -> None:
        if self.blocking_entity:
            return MeleeAction(self.actor, self.dx, self.dy).perform()
        return MoveAction(self.actor, self.dx, self.dy).perform()

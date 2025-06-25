from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from unittest import case

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Entity


class Action:
    """Command pattern. Named Action to stick with the tutorial notion."""

    def perform(self, engine: Engine, actor: Entity) -> None:
        raise NotImplementedError("subclasses must implement perform")


class WaitAction(Action):
    def perform(self, engine: Engine, actor: Entity) -> None:
        print(f'{actor.name} waits')

class EscapeAction(Action):
    def perform(self, engine: Engine, actor: Entity) -> None:
        sys.exit()


class DirectedAction(Action):
    def __init__(self, dx: int, dy: int):
        super().__init__()
        self.dx = dx
        self.dy = dy


class MeleeAction(DirectedAction):
    def perform(self, engine: Engine, actor: Entity) -> None:
        dest_x = actor.x + self.dx
        dest_y = actor.y + self.dy
        target = engine.game_map.get_blocking_entity_at(dest_x, dest_y)
        if not target:
            return
        print(f"{actor.name} hits {target.name}")


class MoveAction(DirectedAction):
    def perform(self, engine: Engine, actor: Entity) -> None:
        next_x = actor.x + self.dx
        next_y = actor.y + self.dy
        if not engine.game_map.in_bounds(next_x, next_y):
            return
        if not engine.game_map.tiles["walkable"][next_x, next_y]:
            return
        if engine.game_map.get_blocking_entity_at(next_x, next_y):
            return

        actor.move(self.dx, self.dy)


class BumpAction(DirectedAction):
    def perform(self, engine: Engine, actor: Entity) -> None:
        dest_x = actor.x + self.dx
        dest_y = actor.y + self.dy
        target = engine.game_map.get_blocking_entity_at(dest_x, dest_y)
        if target:
            return MeleeAction(self.dx, self.dy).perform(engine, actor)
        return MoveAction(self.dx, self.dy).perform(engine, actor)

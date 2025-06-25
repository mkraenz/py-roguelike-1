from __future__ import annotations
from typing import List, TYPE_CHECKING
import numpy as np
import tcod

from py_roguelike_tutorial.actions import Action, MeleeAction, MoveAction, WaitAction
from py_roguelike_tutorial.components.base_components import BaseComponent

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor
    from py_roguelike_tutorial.types import Coord


class BaseAI(Action, BaseComponent):
    entity: Actor  # type: ignore [reportIncompatibleVariableOverride]

    def get_path_to(self, dest_x, dest_y) -> List[Coord]:
        """Returns the list of coordinates to the destination, or an empty list if there is no such path."""
        cost = np.array(self.entity.game_map.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.game_map.entities:
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # we add to the cost of a blocked position. A lower number means more enemies will crowd behind
                # each other in hallways. Higher number means they will take longer paths towards the destination.
                cost[entity.x, entity.y] += 10
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)
        pathfinder.add_root(self.entity.pos)
        # path_to includes the start and ending points. we strip away the start point
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()
        return [(index[0], index[1]) for index in path]


class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Coord] = []

    def perform(self) -> None:
        target = self.engine.player
        (dx, dy) = target.diff_position(self.entity)
        distance = target.dist_chebyshev(self.entity)

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            in_melee_range = distance <= 1
            if in_melee_range:
                return MeleeAction(self.entity, dx, dy).perform()
            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            step_dx, step_dy = dest_x - self.entity.x, dest_y - self.entity.y
            return MoveAction(self.entity, step_dx, step_dy).perform()

        return WaitAction(self.entity).perform()

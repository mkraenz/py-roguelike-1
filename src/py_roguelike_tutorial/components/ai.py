from __future__ import annotations

import random
from typing import TYPE_CHECKING

import numpy as np
import tcod

from py_roguelike_tutorial.actions import (
    Action,
    MeleeAction,
    MoveAction,
    WaitAction,
    BumpAction,
)
from py_roguelike_tutorial.constants import INTERCARDINAL_DIRECTIONS

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor
    from py_roguelike_tutorial.types import Coord


class BaseAI(Action):

    def get_path_to(self, dest_x: int, dest_y: int) -> list[Coord]:
        """Returns the list of coordinates to the destination, or an empty list if there is no such path."""
        cost = np.array(self.entity.parent.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.parent.entities:
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # we add to the cost of a blocked position. A lower number means more enemies will crowd behind
                # each other in hallways. Higher number means they will take longer paths towards the destination.
                cost[entity.x, entity.y] += 10
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)
        pathfinder.add_root(self.entity.pos)
        # path_to includes the start and ending points. we strip away the start point
        path: list[list[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()
        return [(index[0], index[1]) for index in path]


class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: list[Coord] = []

    def perform(self) -> None:
        target = self.engine.player

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            (dx, dy) = target.diff_from(self.entity)
            distance = target.dist_chebyshev(self.entity)
            in_melee_range = distance <= 1
            if in_melee_range:
                return MeleeAction(self.entity, dx, dy).perform()
            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            step_dx, step_dy = dest_x - self.entity.x, dest_y - self.entity.y
            return MoveAction(self.entity, step_dx, step_dy).perform()

        return WaitAction(self.entity).perform()


class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then recover to its previous AI.
    If an actor occupies the tile the confused enemy moves into it will attack.
    """

    def __init__(self, entity: Actor, previous_ai: BaseAI | None, turns_remaining: int):
        super().__init__(entity)
        self.turns_remaining = turns_remaining
        self.previous_ai = previous_ai

    def perform(self) -> None:
        if self.turns_remaining <= 0:
            self.restore_previous_ai()
        else:
            self.move_randomly()

    def restore_previous_ai(self):
        txt = f"{self.entity.name} comes to their senses."
        self.engine.message_log.add(txt)
        self.entity.ai = self.previous_ai

    def move_randomly(self):
        dir_x, dir_y = random.choice(INTERCARDINAL_DIRECTIONS)
        self.turns_remaining -= 1
        return BumpAction(self.entity, dir_x, dir_y).perform()

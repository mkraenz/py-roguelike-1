from __future__ import annotations

import random
from typing import TYPE_CHECKING

import numpy as np
import tcod

from py_roguelike_tutorial.actions import (
    BumpAction,
    MeleeAction,
    MoveAction,
    WaitAction,
)
from py_roguelike_tutorial.components.vision import VisualSense
from py_roguelike_tutorial.constants import INTERCARDINAL_DIRECTIONS
from py_roguelike_tutorial.pathfinding import find_path

if TYPE_CHECKING:
    from py_roguelike_tutorial.behavior_trees.behavior_trees import BtNode
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Actor
    from py_roguelike_tutorial.types import Coord


class BaseAI:
    def __init__(self):
        self._agent: Actor = None  # type: ignore

    @property
    def agent(self):
        return self._agent

    @property
    def engine(self) -> Engine:
        return self.agent.parent.engine

    @agent.setter
    def agent(self, value: Actor):
        self._agent = value

    def perform(self) -> None:
        raise NotImplementedError("subclasses must implement perform")


class HostileEnemy(BaseAI):
    def __init__(self):
        super().__init__()
        self.path: list[Coord] = []
        self.alarmed = False

    def perform(self) -> None:
        target = self.engine.player

        if self.engine.game_map.visible[self.agent.x, self.agent.y]:
            self.alarmed = True

        if self.alarmed:
            distance = target.dist_chebyshev(self.agent)
            in_melee_range = distance <= 1
            if in_melee_range:
                (dx, dy) = target.diff_from(self.agent)
                return MeleeAction(self.agent, dx, dy).perform()

            else:
                self.path = find_path(self.agent.pos, target.pos, self.engine)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            step_dx, step_dy = dest_x - self.agent.x, dest_y - self.agent.y
            return MoveAction(self.agent, step_dx, step_dy).perform()

        return WaitAction(self.agent).perform()


class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then recover to its previous AI.
    If an actor occupies the tile the confused enemy moves into it will attack.
    """

    def __init__(self, previous_ai: BaseAI | None, turns_remaining: int):
        self.turns_remaining = turns_remaining
        self.previous_ai = previous_ai

    def perform(self) -> None:
        if self.turns_remaining <= 0:
            self.restore_previous_ai()
        else:
            self.move_randomly()

    def restore_previous_ai(self):
        txt = f"{self.agent.name} comes to their senses."
        self.engine.message_log.add(txt)
        self.agent.ai = self.previous_ai

    def move_randomly(self):
        dir_x, dir_y = random.choice(INTERCARDINAL_DIRECTIONS)
        self.turns_remaining -= 1
        return BumpAction(self.agent, dir_x, dir_y).perform()


class BehaviorTreeAI(BaseAI):
    def __init__(self, tree: BtNode, visual_sense: VisualSense):
        super().__init__()
        self.tree = tree
        self.visual_sense: VisualSense = visual_sense

    def perform(self) -> None:
        self.visual_sense.sense()
        self.tree.tick()

    @property
    def agent(self) -> Actor:
        return self._agent

    @agent.setter
    def agent(self, value: Actor):
        self._agent = value
        self.visual_sense.agent = value

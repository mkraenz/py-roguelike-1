"""Unlike ./behavior_trees.py, the functionality in this file is customized towards our particular game."""

import copy

import numpy as np
import tcod

from py_roguelike_tutorial.actions import (
    MoveAction,
    MeleeAction,
    RangedAttackAction,
    ItemAction,
)
import py_roguelike_tutorial.behavior_trees.behavior_trees as bt
from py_roguelike_tutorial.entity_factory import EntityPrefabs
from py_roguelike_tutorial.types import Coord
from py_roguelike_tutorial.behavior_trees import validators as bt_val


class SeesPlayerCondition(bt.BtCondition):
    def tick(self) -> bt.BtResult:
        target = self.player
        agent = self.agent
        return self.success_else_fail(
            self.engine.game_map.has_line_of_sight(target, agent)
        )


class MoveTowardsPlayerBehavior(bt.BtAction):
    def __init__(self, args: bt.BtConstructorArgs):
        super().__init__(args)
        self.path: list[Coord] = []

    def get_path_to(self, dest_x: int, dest_y: int) -> list[Coord]:
        """Returns the list of coordinates to the destination, or an empty list if there is no such path."""
        cost = np.array(self.agent.parent.tiles["walkable"], dtype=np.int8)

        for entity in self.agent.parent.entities:
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # we add to the cost of a blocked position. A lower number means more enemies will crowd behind
                # each other in hallways. Higher number means they will take longer paths towards the destination.
                cost[entity.x, entity.y] += 10
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)
        pathfinder.add_root(self.agent.pos)
        # path_to includes the start and ending points. we strip away the start point
        path: list[list[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()
        return [(index[0], index[1]) for index in path]

    def tick(self) -> bt.BtResult:
        target = self.player
        self.path = self.get_path_to(target.x, target.y)
        dest_x, dest_y = self.path.pop(0)
        step_dx, step_dy = dest_x - self.agent.x, dest_y - self.agent.y
        MoveAction(self.agent, step_dx, step_dy).perform()
        return bt.BtResult.Success


class HealthCondition(bt.BtCondition):
    """Checks the agent's health."""

    def __init__(self, args: bt.BtConstructorArgs[bt_val.HealthConditionDataParams]):
        super().__init__(args)
        self.comparator = args.params.comparator
        self.value_percent = args.params.value_percent

    def tick(self) -> bt.BtResult:
        match self.comparator:
            case "leq":
                return self.success_else_fail(
                    self.agent.fighter.hp_percent <= self.value_percent / 100
                )
            case _:
                raise ValueError(f"Unsupported comparator: {self.comparator}")


class BlackboardCondition(bt.BtCondition):
    def __init__(
        self, args: bt.BtConstructorArgs[bt_val.BlackboardConditionDataParams]
    ):
        super().__init__(args)
        self.key = args.params.key
        self.comparator = args.params.comparator
        self.value = args.params.value

    def tick(self) -> bt.BtResult:
        match self.comparator:
            case "eq":
                return self.success_else_fail(
                    self.blackboard.get(self.key) == self.value
                )
            case "has":
                return self.success_else_fail(self.blackboard.has(self.key))
            case _:
                raise ValueError(f"Unsupported comparator: {self.comparator}")


class WriteToBlackboardBehavior(bt.BtAction):
    def __init__(self, args: bt.BtConstructorArgs[bt_val.WriteToBlackboardDataParams]):
        super().__init__(args)
        self.key = args.params.key
        self.value = args.params.value

    def tick(self) -> bt.BtResult:
        self.blackboard.set(self.key, self.value)
        return bt.BtResult.Success


class DistanceToPlayerCondition(bt.BtCondition):
    def __init__(self, args: bt.BtConstructorArgs[bt_val.DistanceToPlayerDataParams]):
        super().__init__(args)
        self.max_dist: int = args.params.max_dist
        self.min_dist: int = args.params.min_dist

    def tick(self) -> bt.BtResult:
        return self.success_else_fail(
            self.min_dist <= self.player.dist_chebyshev(self.agent) <= self.max_dist
        )


class WaitBehavior(bt.BtAction):
    def tick(self) -> bt.BtResult:
        # intentionally doing nothing
        return bt.BtResult.Success


class MeleeAttackBehavior(bt.BtAction):
    def tick(self) -> bt.BtResult:
        (dx, dy) = self.player.diff_from(self.agent)
        MeleeAction(self.agent, dx, dy).perform()
        return bt.BtResult.Success


class RangedAttackBehavior(bt.BtAction):
    def tick(self) -> bt.BtResult:
        RangedAttackAction(self.agent).perform()
        return bt.BtResult.Success


class HasItemCondition(bt.BtCondition):
    def __init__(self, args: bt.BtConstructorArgs[bt_val.HasItemDataParams]):
        super().__init__(args)
        self.item_kind = args.params.item_kind

    def tick(self) -> bt.BtResult:
        return self.success_else_fail(self.agent.inventory.has(self.item_kind))


class UseItemBehavior(bt.BtAction):
    """For the time being, this only handles items that are used on the agent themself."""

    def __init__(self, args: bt.BtConstructorArgs[bt_val.UseItemDataParams]):
        super().__init__(args)
        self.item_kind = args.params.item_kind

    def tick(self) -> bt.BtResult:
        item = self.agent.inventory.get_by_kind(self.item_kind)
        assert (
            item
        ), f"Agent {self.agent.name} does not have item of kind: {self.item_kind}."
        ItemAction(self.agent, item).perform()
        return bt.BtResult.Success


class Subtree(bt.BtNode):
    def __init__(self, args: bt.BtConstructorArgs[bt_val.SubtreeDataParams]):
        super().__init__(
            children=[copy.deepcopy(EntityPrefabs.behavior_trees[args.params.id])],
            max_children=1,
        )
        self.id = args.params.id

    def tick(self) -> bt.BtResult:
        for child in self.children:
            child_res = child.tick()
            if child_res == bt.BtResult.Failure or child_res == bt.BtResult.Running:
                return child_res
        return bt.BtResult.Success


BT_NODE_NAME_TO_CLASS = {
    "Root": bt.BtRoot,
    "Selector": bt.BtSelector,
    "Sequence": bt.BtSequence,
    "Inverter": bt.BtInverter,
    "DistanceToPlayer": DistanceToPlayerCondition,
    "MeleeAttack": MeleeAttackBehavior,
    "MoveTowardsPlayer": MoveTowardsPlayerBehavior,
    "Wait": WaitBehavior,
    "HealthCondition": HealthCondition,
    "BlackboardCondition": BlackboardCondition,
    "WriteToBlackboard": WriteToBlackboardBehavior,
    "SeesPlayer": SeesPlayerCondition,
    "RangedAttack": RangedAttackBehavior,
    "HasItem": HasItemCondition,
    "UseItem": UseItemBehavior,
    "Subtree": Subtree,
}

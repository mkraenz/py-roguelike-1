"""Unlike ./behavior_trees.py, the functionality in this file is customized towards our particular game."""

import copy
import random
from typing import TYPE_CHECKING, Any

import numpy as np
import tcod

from py_roguelike_tutorial.actions import (
    EquipAction,
    MoveAction,
    MeleeAction,
    PickupAction,
    RangedAttackAction,
    ItemAction,
)
import py_roguelike_tutorial.behavior_trees.behavior_trees as bt
from py_roguelike_tutorial.behavior_trees.behavior_trees import Blackboard, BtResult
from py_roguelike_tutorial.constants import INTERCARDINAL_DIRECTIONS
from py_roguelike_tutorial.entity_factory import EntityPrefabs
from py_roguelike_tutorial.exceptions import Impossible
from py_roguelike_tutorial.types import Coord
from py_roguelike_tutorial.behavior_trees import validators as bt_val
from py_roguelike_tutorial.entity import Entity

if TYPE_CHECKING:
    pass


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
        assert item, f"{self.agent.name} does not have item of kind: {self.item_kind}."
        ItemAction(self.agent, item).perform()
        return bt.BtResult.Success


class EquipItemBehavior(bt.BtAction):
    def __init__(self, args: bt.BtConstructorArgs[bt_val.EquipItemDataParams]):
        super().__init__(args)
        self.id_raw = args.params.id

    def tick(self) -> bt.BtResult:
        try:
            id, loaded = self.maybe_read_blackboard(self.id_raw)
            item = self.agent.inventory.get_by_id(id)
            if item is None:
                raise AssertionError(
                    f"{self.agent.name} tried to equip an item with id {id}, but it does not have such an item."
                )
            EquipAction(entity=self.agent, item=item).perform()
            if loaded:
                self.remove_from_blackboard(self.id_raw)
            return bt.BtResult.Success
        except Impossible:
            # TODO implement. maybe write that inventory is full or sth. also we should check the inventory before trying to pick up sth
            pass

        return bt.BtResult.Success


class PickUpItemBehavior(bt.BtAction):
    def __init__(self, args: bt.BtConstructorArgs[bt_val.PickUpItemDataParams]):
        super().__init__(args)
        self.key = args.params.key

    def tick(self) -> bt.BtResult:
        try:
            # item must be selected before picking because pickup action will remove the item
            item = self.engine.game_map.get_item_at_location(*self.agent.pos)
            PickupAction(self.agent).perform()
            if item is None:
                raise AssertionError(
                    f"Agent {self.agent.name} tried to pick up an item at its position, but there is no item there."
                )
            self.blackboard.set(self.key, item.id)
        except Impossible:
            # TODO implement. maybe write that inventory is full or sth. also we should check the inventory before trying to pick up sth
            # ignore for the time being
            pass
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


class RandomMoveBehavior(bt.BtAction):
    def tick(self) -> BtResult:
        dir_x, dir_y = random.choice(INTERCARDINAL_DIRECTIONS)
        try:
            MoveAction(self.agent, dir_x, dir_y).perform()
        except Impossible:
            pass  # ignore
        return bt.BtResult.Success


class HasItemAtPosition(bt.BtCondition):

    def tick(self) -> BtResult:
        item = self.engine.game_map.get_item_at_location(*self.agent.pos)
        if item is not None:
            if item.kind == "dagger":
                return bt.BtResult.Success
        return bt.BtResult.Failure


class WriteItemPosInVicinity(bt.BtAction):
    def __init__(
        self, args: bt.BtConstructorArgs[bt_val.WriteItemPosInVicinityDataParams]
    ):
        super().__init__(args)
        self.radius = args.params.radius
        self.look_for_kind = args.params.look_for_kind
        self.write_to_blackboard_key = args.params.write_to_blackboard_key

    def tick(self) -> BtResult:
        # TODO ideally we have a has item in vicinity with these params first.
        # TODO currently we only look at this specific position
        item = self.engine.game_map.get_item_at_location(*self.agent.pos)
        if item is not None:
            if item.kind == "dagger":
                self.blackboard.set(self.write_to_blackboard_key, item.pos)
                return bt.BtResult.Success
        return bt.BtResult.Failure


class MoveToEntityBehavior(bt.BtAction):
    def __init__(self, args: bt.BtConstructorArgs[bt_val.MoveToEntityDataParams]):
        super().__init__(args)
        self.to_raw = args.params.to

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

    def tick(self) -> BtResult:
        target, _ = self.maybe_read_blackboard(self.to_raw)
        if not isinstance(target, Entity):
            raise AssertionError("Expected target to be an Entity.")
        path = self.get_path_to(target.x, target.y)
        if len(path) == 0:
            return bt.BtResult.Failure
        dest_x, dest_y = path.pop(0)
        step_dx, step_dy = dest_x - self.agent.x, dest_y - self.agent.y
        MoveAction(self.agent, step_dx, step_dy).perform()
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
    "RandomMove": RandomMoveBehavior,
    "HasItemAtPosition": HasItemAtPosition,
    "WriteItemPosInVicinity": WriteItemPosInVicinity,
    "PickUpItem": PickUpItemBehavior,
    "MoveToEntity": MoveToEntityBehavior,
    "EquipItem": EquipItemBehavior,
}

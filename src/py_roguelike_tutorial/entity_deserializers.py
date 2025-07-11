from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any

import numpy as np
import tcod

import py_roguelike_tutorial.validators.behavior_tree_validator as bt_val
from py_roguelike_tutorial.actions import (
    MoveAction,
    MeleeAction,
    RangedAttackAction,
    ItemAction,
)
from py_roguelike_tutorial.behavior_trees.behavior_trees import (
    BtRoot,
    BtSequence,
    BtAction,
    BtResult,
    Blackboard,
    BtCondition,
    BtSelector,
    BtNode,
    BtInverter,
)
from py_roguelike_tutorial.colors import hex_to_rgb
from py_roguelike_tutorial.components.ai import HostileEnemy, BehaviorTreeAI
from py_roguelike_tutorial.components.consumable import (
    HealingConsumable,
    LightningDamageConsumable,
    ConfusionConsumable,
    FireballDamageConsumable,
    TeleportSelfConsumable,
)
from py_roguelike_tutorial.components.equipment import Equipment
from py_roguelike_tutorial.components.equippable import Equippable
from py_roguelike_tutorial.components.fighter import Fighter
from py_roguelike_tutorial.components.inventory import Inventory
from py_roguelike_tutorial.components.level import Level
from py_roguelike_tutorial.components.ranged import Ranged
from py_roguelike_tutorial.entity import Item, Actor
from py_roguelike_tutorial.entity_factory import EntityPrefabs
from py_roguelike_tutorial.validators.actor_validator import BehaviorTreeAIData

if TYPE_CHECKING:
    from py_roguelike_tutorial.types import Coord
    from py_roguelike_tutorial.validators.actor_validator import (
        ActorData,
    )
    from py_roguelike_tutorial.validators.item_validator import ItemData


CONSUMABLE_CLASSES = {
    "HealingConsumable": HealingConsumable,
    "LightningDamageConsumable": LightningDamageConsumable,
    "ConfusionConsumable": ConfusionConsumable,
    "FireballDamageConsumable": FireballDamageConsumable,
    "TeleportSelfConsumable": TeleportSelfConsumable,
}

AI_CLASSES = {
    "HostileEnemy": HostileEnemy,
    "BehaviorTreeAI": BehaviorTreeAI,
}


def item_from_dict(data: ItemData) -> Item:
    consumable_data = data.consumable
    consumable_class = (
        CONSUMABLE_CLASSES[consumable_data.class_type]
        if consumable_data is not None
        else None
    )
    consumable = (
        consumable_class(consumable_data.constructor_args)
        if consumable_data is not None and consumable_class is not None
        else None
    )
    equippable_data = data.equippable
    equippable = Equippable.from_dict(equippable_data) if equippable_data else None

    item = Item(
        char=data.char,
        color=hex_to_rgb(data.color),
        name=data.name,
        kind=data.kind,
        consumable=consumable,
        equippable=equippable,
    )
    if consumable:
        consumable.parent = item
    if equippable:
        equippable.parent = item
    return item


def actor_from_dict(data: ActorData, item_prefabs: dict[str, Item]) -> Actor:
    ai_cls = AI_CLASSES[data.ai.class_type]
    # TODO continue here by constructing an actual tree that if moves towards the player

    if ai_cls == HostileEnemy:
        ai = ai_cls()
    elif ai_cls == BehaviorTreeAI and isinstance(data.ai, BehaviorTreeAIData):
        behavior_tree = EntityPrefabs.behavior_trees[data.ai.behavior_tree_id]
        ai = BehaviorTreeAI(behavior_tree)
    else:
        raise Exception("Unhandled actor ai")

    fighter_data = data.fighter
    fighter = Fighter(
        max_hp=fighter_data.max_hp,
        defense=fighter_data.defense,
        power=fighter_data.power,
    )

    ranged = Ranged(data.ranged.power, data.ranged.range) if data.ranged else None

    inventory = Inventory(data.inventory)
    new_item = lambda key: copy.deepcopy(item_prefabs[key])
    inventory_items = [new_item(item_key) for item_key in data.inventory.items or []]
    inventory.add_many(inventory_items)

    equipment_data = data.equipment
    weapon = new_item(equipment_data.weapon) if equipment_data.weapon else None
    armor = new_item(equipment_data.armor) if equipment_data.armor else None
    equipment = Equipment(weapon=weapon, armor=armor)
    if weapon:
        inventory.add(weapon)
    if armor:
        inventory.add(armor)

    level_data = data.level
    level = Level(level_data)

    actor = Actor(
        char=data.char,
        color=hex_to_rgb(data.color),
        name=data.name,
        move_stepsize=data.move_stepsize,
        ai=ai,
        fighter=fighter,
        inventory=inventory,
        equipment=equipment,
        level=level,
        ranged=ranged,
    )
    return actor


class SeesPlayerCondition(BtCondition):
    def __init__(self, children: list[BtNode], params: None):
        super().__init__("sees_player", params=params)

    def tick(self) -> BtResult:
        target = self.player
        agent = self.agent
        return self.success_else_fail(
            self.engine.game_map.has_line_of_sight(target, agent)
        )


class MoveTowardsPlayerBehavior(BtAction):
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

    # TODO consider moving blackboard into a react-style "context", like the BtRoot
    def __init__(self, children: list[BtNode], params: None):
        # TODO move name and type into an abstract class var
        super().__init__("move_towards_player", params=params)
        self.path: list[Coord] = []

    def tick(self) -> BtResult:
        target = self.player
        self.path = self.get_path_to(target.x, target.y)
        dest_x, dest_y = self.path.pop(0)
        step_dx, step_dy = dest_x - self.agent.x, dest_y - self.agent.y
        MoveAction(self.agent, step_dx, step_dy).perform()
        return BtResult.Success


class HealthCondition(BtCondition):
    """Checks the agent's health."""

    def __init__(
        self,
        children: list[BtNode],
        params: bt_val.HealthConditionDataParams,
    ):
        super().__init__(
            name="health_condition",
            params=params,
        )
        self.comparator = params.comparator
        self.value_percent = params.value_percent

    def tick(self) -> BtResult:
        match self.comparator:
            case "leq":
                return self.success_else_fail(
                    self.agent.fighter.hp_percent <= self.value_percent / 100
                )
            case _:
                raise ValueError(f"Unsupported comparator: {self.comparator}")


class BlackboardCondition(BtCondition):
    def __init__(
        self,
        children: list[BtNode],
        params: bt_val.BlackboardConditionDataParams,
    ):
        super().__init__(
            name="blackboard_condition",
            params=params,
        )
        self.key = params.key
        self.comparator = params.comparator
        self.value = params.value

    def tick(self) -> BtResult:
        match self.comparator:
            case "eq":
                return self.success_else_fail(
                    self.blackboard.get(self.key) == self.value
                )
            case "has":
                return self.success_else_fail(self.blackboard.has(self.key))
            case _:
                raise ValueError(f"Unsupported comparator: {self.comparator}")


class WriteToBlackboardBehavior(BtAction):
    def __init__(
        self,
        children: list[BtNode],
        params: bt_val.WriteToBlackboardDataParams,
    ):
        super().__init__(
            name="write_to_blackboard",
            params=params,
        )
        self.key = params.key
        self.value = params.value

    def tick(self) -> BtResult:
        self.blackboard.set(self.key, self.value)
        return BtResult.Success


class DistanceToPlayerCondition(BtCondition):
    def __init__(
        self,
        children: list[BtNode],
        params: bt_val.DistanceToPlayerDataParamsA | bt_val.DistanceToPlayerDataParamsB,
    ):
        super().__init__(
            "max_distance_to_player",
            params=params,
        )
        self.max_dist: int = params.max_dist
        self.min_dist: int = params.min_dist

    def tick(self) -> BtResult:
        return self.success_else_fail(
            self.min_dist <= self.player.dist_chebyshev(self.agent) <= self.max_dist
        )


class WaitBehavior(BtAction):
    def __init__(self, children: list[BtNode], params: None):
        super().__init__("wait", params=params)

    def tick(self) -> BtResult:
        # intentionally doing nothing
        return BtResult.Success


class MeleeAttackBehavior(BtAction):
    def __init__(self, children: list[BtNode], params: None):
        super().__init__("melee_attack", params=params)

    def tick(self) -> BtResult:
        (dx, dy) = self.player.diff_from(self.agent)
        MeleeAction(self.agent, dx, dy).perform()
        return BtResult.Success


class RangedAttackBehavior(BtAction):
    def __init__(self, children: list[BtNode], params: None):
        super().__init__("ranged_attack", params=params)

    def tick(self) -> BtResult:
        RangedAttackAction(self.agent).perform()
        return BtResult.Success


class HasItemCondition(BtCondition):
    def __init__(self, children: list[BtNode], params: bt_val.HasItemDataParams):
        super().__init__("has_item", params=params)
        self.item_kind = params.item_kind

    def tick(self) -> BtResult:
        return self.success_else_fail(self.agent.inventory.has(self.item_kind))


class UseItemBehavior(BtAction):
    """For the time being, this only handles items that are used on the agent themself."""

    def __init__(self, children: list[BtNode], params: bt_val.UseItemDataParams):
        super().__init__("use_item", params=params)
        self.item_kind = params.item_kind

    def tick(self) -> BtResult:
        item = self.agent.inventory.get_by_kind(self.item_kind)
        assert (
            item
        ), f"Agent {self.agent.name} does not have item of kind: {self.item_kind}."
        ItemAction(self.agent, item).perform()
        return BtResult.Success


class Subtree(BtNode):
    def __init__(self, children: list[BtNode], params: bt_val.SubtreeDataParams):
        super().__init__(
            "subtree",
            children=[copy.deepcopy(EntityPrefabs.behavior_trees[params.id])],
            max_children=1,
        )
        self.id = params.id

    def tick(self) -> BtResult:
        for child in self.children:
            child_res = child.tick()
            if child_res == BtResult.Failure or child_res == BtResult.Running:
                return child_res
        return BtResult.Success


_bt_node_class = {
    "Root": BtRoot,
    "Selector": BtSelector,
    "Sequence": BtSequence,
    "Inverter": BtInverter,
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


def _children_to_bt_node(data: bt_val.BtNodeData) -> BtNode:
    cls = _bt_node_class[data.type]
    return cls(
        children=(
            [_children_to_bt_node(child) for child in data.children]
            if data.children is not None
            else []
        ),
        params=data.params,
    )


def behavior_tree_from_dict(data: bt_val.BehaviorTreeData) -> BtNode:
    # the blackboard will be filled after the gamemap finished initialization
    tree = _children_to_bt_node(data.root)
    tree.blackboard = Blackboard()
    return tree

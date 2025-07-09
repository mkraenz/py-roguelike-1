from __future__ import annotations
import copy
from typing import TYPE_CHECKING

import numpy as np
import tcod

from py_roguelike_tutorial.actions import MoveAction, MeleeAction
from py_roguelike_tutorial.behavior_trees.behavior_trees import (
    BtRoot,
    BtSequence,
    BtAction,
    BtResult,
    Blackboard,
    BtCondition,
    BtSelector,
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

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.types import Coord
    from py_roguelike_tutorial.validators.actor_validator import ActorData
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
        consumable=consumable,
        equippable=equippable,
    )
    if consumable:
        consumable.parent = item
    if equippable:
        equippable.parent = item
    return item


class MoveBehavior(BtAction):
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
    def __init__(self, blackboard: Blackboard):
        # TODO move name and type into an abstract class var
        super().__init__("move", blackboard)
        self.path: list[Coord] = []

    def tick(self) -> BtResult:
        target = self.player
        self.path = self.get_path_to(target.x, target.y)
        dest_x, dest_y = self.path.pop(0)
        step_dx, step_dy = dest_x - self.agent.x, dest_y - self.agent.y
        MoveAction(self.agent, step_dx, step_dy).perform()
        return BtResult.Success


class MaxDistanceToPlayer(BtCondition):
    def __init__(self, max_dist: int, blackboard: Blackboard):
        super().__init__("max_distance_to_player", blackboard)
        self.max_dist = max_dist

    def tick(self) -> BtResult:
        if self.player.dist_chebyshev(self.agent) <= self.max_dist:
            return BtResult.Success
        return BtResult.Failure


class WaitBehavior(BtAction):
    def __init__(self, blackboard: Blackboard):
        super().__init__("wait", blackboard)

    def tick(self) -> BtResult:
        # intentionally doing nothing
        return BtResult.Success


class MeleeAttackBehavior(BtAction):
    def __init__(self, blackboard: Blackboard):
        super().__init__("melee_attack", blackboard)

    def tick(self) -> BtResult:
        (dx, dy) = self.player.diff_from(self.agent)
        MeleeAction(self.agent, dx, dy).perform()
        return BtResult.Success


def actor_from_dict(data: ActorData, item_prefabs: dict[str, Item]) -> Actor:
    ai_cls = AI_CLASSES[data.ai.class_type]
    # TODO continue here by constructing an actual tree that if moves towards the player

    blackboard = Blackboard()
    behavior_tree = BtRoot(
        [
            BtSelector(
                children=[
                    BtSequence(
                        [
                            MaxDistanceToPlayer(1, blackboard=blackboard),
                            MeleeAttackBehavior(blackboard=blackboard),
                        ],
                        blackboard=blackboard,
                    ),
                    BtSequence(
                        [
                            MaxDistanceToPlayer(10, blackboard=blackboard),
                            MoveBehavior(blackboard=blackboard),
                        ],
                        blackboard=blackboard,
                    ),
                    WaitBehavior(blackboard=blackboard),
                ],
                blackboard=blackboard,
            )
        ],
        blackboard=blackboard,
    )
    ai = ai_cls() if ai_cls == HostileEnemy else ai_cls(behavior_tree)

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

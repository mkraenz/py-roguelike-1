from __future__ import annotations

from typing import TYPE_CHECKING

import py_roguelike_tutorial.behavior_trees.validators as bt_val
from py_roguelike_tutorial.behavior_trees.behavior_trees import (
    Blackboard,
    BtNode,
    BtConstructorArgs,
)
from py_roguelike_tutorial.behavior_trees.behaviors import BT_NODE_NAME_TO_CLASS
from py_roguelike_tutorial.colors import hex_to_rgb
from py_roguelike_tutorial.components.ai import (
    HostileEnemy,
    BehaviorTreeAI,
)
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
from py_roguelike_tutorial.components.vision import VisualSense
from py_roguelike_tutorial.entity import Item, Actor
from py_roguelike_tutorial.entity_factory import EntityPrefabs
from py_roguelike_tutorial.validators.actor_validator import BehaviorTreeAIData

if TYPE_CHECKING:
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
        stacking=data.stacking,
        quantity=data.quantity,
        consumable=consumable,
        equippable=equippable,
        tags=set(data.tags),
    )
    if consumable:
        consumable.parent = item
    if equippable:
        equippable.parent = item
    return item


def actor_from_dict(data: ActorData, item_prefabs: dict[str, Item]) -> Actor:
    ai_cls = AI_CLASSES[data.ai.class_type]

    if ai_cls == HostileEnemy:
        ai = ai_cls()
    elif ai_cls == BehaviorTreeAI and isinstance(data.ai, BehaviorTreeAIData):
        behavior_tree = EntityPrefabs.behavior_trees[data.ai.behavior_tree_id]
        interests = set(data.ai.interests)
        vision = VisualSense(
            behavior_tree.blackboard, interests=interests, range=data.ai.vision.range
        )
        ai = BehaviorTreeAI(behavior_tree, vision)
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
    new_item = lambda key: item_prefabs[key].duplicate()
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
        tags=set(data.tags),
    )
    return actor


def _to_bt_node(data: bt_val.BtNodeData) -> BtNode:
    cls = BT_NODE_NAME_TO_CLASS[data.type]
    return cls(
        BtConstructorArgs(
            children=(
                [_to_bt_node(child) for child in data.children]
                if data.children is not None
                else []
            ),
            params=data.params,
        )
    )


def behavior_tree_from_dict(data: bt_val.BehaviorTreeData) -> BtNode:
    # the blackboard will be filled after the gamemap finished initialization
    tree = _to_bt_node(data.root)
    tree.blackboard = Blackboard()
    return tree

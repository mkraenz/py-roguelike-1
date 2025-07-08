import copy

from py_roguelike_tutorial.colors import hex_to_rgb
from py_roguelike_tutorial.components.ai import HostileEnemy
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
from py_roguelike_tutorial.validators.actor_validator import ActorData
from py_roguelike_tutorial.validators.item_validator import ItemData

CONSUMABLE_CLASSES = {
    "HealingConsumable": HealingConsumable,
    "LightningDamageConsumable": LightningDamageConsumable,
    "ConfusionConsumable": ConfusionConsumable,
    "FireballDamageConsumable": FireballDamageConsumable,
    "TeleportSelfConsumable": TeleportSelfConsumable,
}

AI_CLASSES = {"HostileEnemy": HostileEnemy}


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


def actor_from_dict(data: ActorData, item_prefabs: dict[str, Item]) -> Actor:
    ai_cls = AI_CLASSES[data.ai.class_type]

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

    return Actor(
        char=data.char,
        color=hex_to_rgb(data.color),
        name=data.name,
        move_stepsize=data.move_stepsize,
        ai_cls=ai_cls,
        fighter=fighter,
        inventory=inventory,
        equipment=equipment,
        level=level,
        ranged=ranged,
    )

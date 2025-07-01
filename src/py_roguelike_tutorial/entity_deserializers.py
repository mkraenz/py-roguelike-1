import copy
from typing import Any, Type
from py_roguelike_tutorial.colors import hex_to_rgb
from py_roguelike_tutorial.components.ai import BaseAI, HostileEnemy
from py_roguelike_tutorial.components.consumable import (
    Consumable,
    HealingConsumable,
    LightningDamageConsumable,
    ConfusionConsumable,
    FireballDamageConsumable,
)
from py_roguelike_tutorial.components.equipment import Equipment
from py_roguelike_tutorial.components.equippable import Equippable
from py_roguelike_tutorial.components.fighter import Fighter
from py_roguelike_tutorial.components.inventory import Inventory
from py_roguelike_tutorial.components.level import Level
from py_roguelike_tutorial.entity import Item, Actor
from py_roguelike_tutorial.entity_factory import EntityPrefabs

CONSUMABLE_CLASSES: dict[str, Type[Consumable]] = {
    "HealingConsumable": HealingConsumable,
    "LightningDamageConsumable": LightningDamageConsumable,
    "ConfusionConsumable": ConfusionConsumable,
    "FireballDamageConsumable": FireballDamageConsumable,
}

AI_CLASSES: dict[str, Type[BaseAI]] = {"HostileEnemy": HostileEnemy}


def item_from_dict(data: dict[str, Any]) -> Item:
    consumable_data = data.get("consumable")
    consumable_class: Type[Consumable] | None = (
        CONSUMABLE_CLASSES[consumable_data["class"]]
        if consumable_data is not None
        else None
    )
    consumable: Consumable | None = (
        consumable_class.from_dict(consumable_data["constructor_args"])
        if consumable_data and consumable_class
        else None
    )
    equippable_data = data.get("equippable")
    equippable = Equippable.from_dict(equippable_data) if equippable_data else None

    item = Item(
        char=data["char"],
        color=hex_to_rgb(data["color"]),
        name=data["name"],
        consumable=consumable,
        equippable=equippable,
    )
    if consumable:
        consumable.parent = item
    if equippable:
        equippable.parent = item
    return item


def actor_from_dict(data: dict[str, Any], item_prefabs: dict[str, Item]) -> Actor:
    ai_data: dict = data["ai"]
    ai_cls = AI_CLASSES[ai_data["class"]]

    fighter_data: dict = data["fighter"]
    fighter = Fighter(
        max_hp=fighter_data["max_hp"],
        defense=fighter_data["defense"],
        power=fighter_data["power"],
    )

    inventory_data: dict = data["inventory"]
    inventory = (
        Inventory(capacity=inventory_data["capacity"])
        if inventory_data
        else Inventory.none()
    )

    equipment_data: dict = data["equipment"]
    weapon = (
        copy.deepcopy(item_prefabs[equipment_data["weapon"]])
        if equipment_data.get("weapon")
        else None
    )
    armor = (
        copy.deepcopy(item_prefabs[equipment_data["armor"]])
        if equipment_data.get("armor")
        else None
    )
    equipment = Equipment(weapon=weapon, armor=armor)
    if weapon:
        inventory.add(weapon)
    if armor:
        inventory.add(armor)

    level_data = data["level"]
    level = Level.from_dict(level_data)

    return Actor(
        char=data["char"],
        color=hex_to_rgb(data["color"]),
        name=data["name"],
        ai_cls=ai_cls,
        fighter=fighter,
        inventory=inventory,
        equipment=equipment,
        level=level,
    )

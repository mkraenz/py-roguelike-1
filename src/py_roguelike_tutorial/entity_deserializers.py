from typing import Any, Type
from py_roguelike_tutorial.colors import hex_to_rgb
from py_roguelike_tutorial.components.consumable import (
    Consumable,
    HealingConsumable,
    LightningDamageConsumable,
    ConfusionConsumable,
    FireballDamageConsumable,
)
from py_roguelike_tutorial.components.equippable import Equippable
from py_roguelike_tutorial.entity import Item


CONSUMABLE_CLASSES: dict[str, Type[Consumable]] = {
    "HealingConsumable": HealingConsumable,
    "LightningDamageConsumable": LightningDamageConsumable,
    "ConfusionConsumable": ConfusionConsumable,
    "FireballDamageConsumable": FireballDamageConsumable,
}


def item_from_dict(data: dict[str, Any]) -> Item:
    consumable_data = data.get("consumable")
    consumable_class: Type[Consumable] | None = (
        CONSUMABLE_CLASSES.get(consumable_data["class"])
        if consumable_data is not None
        else None
    )
    consumable: Consumable | None = (
        consumable_class.from_dict(consumable_data["constructor_args"])
        if consumable_data and consumable_class
        else None
    )
    equippable_data = data.get("equippable")
    equippable = (
        Equippable(
            defense=equippable_data.get("defense"),
            power=equippable_data.get("power"),
            type=equippable_data.get("type"),
        )
        if equippable_data
        else None
    )

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

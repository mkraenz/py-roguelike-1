from typing import Literal

from pydantic import BaseModel

from py_roguelike_tutorial.components.equipment_type import EquipmentType


class BaseConsumableConstructorData(BaseModel):
    charges: int = 1


class LightningDamageConsumableConstructorData(BaseConsumableConstructorData):
    damage: int
    max_range: int


class ConfusionConsumableConstructorData(BaseConsumableConstructorData):
    turns: int


class FireballDamageConsumableConstructorData(BaseConsumableConstructorData):
    damage: int
    radius: int


class HealingConsumableConstructorData(BaseConsumableConstructorData):
    amount: int


class TeleportSelfConsumableConstructorData(BaseConsumableConstructorData):
    radius: int


class LightningDamageConsumableData(BaseModel):
    class_type: Literal["LightningDamageConsumable"]
    constructor_args: LightningDamageConsumableConstructorData


class FireballDamageConsumableData(BaseModel):
    class_type: Literal["FireballDamageConsumable"]
    constructor_args: FireballDamageConsumableConstructorData


class ConfusionConsumableData(BaseModel):
    class_type: Literal["ConfusionConsumable"]
    constructor_args: ConfusionConsumableConstructorData


class HealingConsumableData(BaseModel):
    class_type: Literal["HealingConsumable"]
    constructor_args: HealingConsumableConstructorData


class TeleportSelfConsumableData(BaseModel):
    class_type: Literal["TeleportSelfConsumable"]
    constructor_args: TeleportSelfConsumableConstructorData


class EquippableData(BaseModel):
    slot: EquipmentType
    defense: int | None = None
    power: int | None = None
    range: int | None = None
    ranged_power: int | None = None


class ItemData(BaseModel):
    kind: str
    char: str
    color: str
    name: str
    description: str
    flavor_text: str
    tags: list[str]
    stacking: bool = False
    quantity: int = 1
    consumable: (
        LightningDamageConsumableData
        | HealingConsumableData
        | ConfusionConsumableData
        | FireballDamageConsumableData
        | TeleportSelfConsumableData
        | None
    ) = None
    equippable: EquippableData | None = None

from typing import Literal

from pydantic import BaseModel

from py_roguelike_tutorial.components.equipment_type import EquipmentType


class LightningDamageConsumableConstructorData(BaseModel):
    damage: int
    max_range: int


class ConfusionConsumableConstructorData(BaseModel):
    turns: int


class FireballDamageConsumableConstructorData(BaseModel):
    damage: int
    radius: int


class HealingConsumableConstructorData(BaseModel):
    amount: int


class TeleportSelfConsumableConstructorData(BaseModel):
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


class ItemData(BaseModel):
    char: str
    color: str
    name: str
    consumable: (
            LightningDamageConsumableData
            | HealingConsumableData
            | ConfusionConsumableData
            | FireballDamageConsumableData
            | TeleportSelfConsumableData
            | None
    ) = None
    equippable: EquippableData | None = None

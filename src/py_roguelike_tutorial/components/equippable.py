from py_roguelike_tutorial.components.base_components import BaseComponent
from py_roguelike_tutorial.components.equipment_type import EquipmentType
import py_roguelike_tutorial.validators.item_validator as validators
from py_roguelike_tutorial.entity import Item


class Equippable(BaseComponent):
    parent: Item  # type: ignore [reportIncompatibleVariableOverride]

    def __init__(self, slot: EquipmentType, power: int = 0, defense: int = 0):
        self.slot: EquipmentType = slot
        self.power: int = power
        self.defense: int = defense

    @classmethod
    def from_dict(cls, data: validators.EquippableData):
        return cls(
            defense=data.defense if data.defense else 0,
            power=data.power if data.power else 0,
            slot=data.slot,
        )

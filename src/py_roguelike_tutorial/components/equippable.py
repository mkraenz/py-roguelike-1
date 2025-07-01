from py_roguelike_tutorial.components.base_components import BaseComponent
from py_roguelike_tutorial.components.equipment_type import EquipmentType
from py_roguelike_tutorial.entity import Item


class Equippable(BaseComponent):
    parent: Item  # type: ignore [reportIncompatibleVariableOverride]

    def __init__(self, slot: EquipmentType, power: int = 0, defense: int = 0):
        self.slot: EquipmentType = slot
        self.power: int = power
        self.defense: int = defense

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            defense=data.get("defense", 0),
            power=data.get("power", 0),
            slot=data["slot"],
        )

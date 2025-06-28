from py_roguelike_tutorial.components.base_components import BaseComponent
from py_roguelike_tutorial.entity import Item
from py_roguelike_tutorial.equipment_types import EquipmentType


class Equippable(BaseComponent):
    parent: Item  # type: ignore [reportIncompatibleVariableOverride]

    def __init__(self, type: EquipmentType, power: int = 0, defense=0):
        self.type = type
        self.power = power
        self.defense = defense

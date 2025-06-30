from py_roguelike_tutorial.components.base_components import BaseComponent
from py_roguelike_tutorial.components.equipment_type import EquipmentType
from py_roguelike_tutorial.entity import Item


class Equippable(BaseComponent):
    parent: Item  # type: ignore [reportIncompatibleVariableOverride]

    def __init__(self, type: EquipmentType, power: int = 0, defense: int = 0):
        self.type: EquipmentType = type
        self.power: int = power
        self.defense: int = defense

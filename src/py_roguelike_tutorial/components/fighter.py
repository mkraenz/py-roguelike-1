from __future__ import annotations
from typing import TYPE_CHECKING

from py_roguelike_tutorial.constants import Theme
from py_roguelike_tutorial.components.base_components import BaseComponent

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor


class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, defense: int, power: int):
        self.base_defense = defense
        self.base_power = power

    @property
    def power(self) -> int:
        return self.base_power + self.power_bonus

    @property
    def defense(self) -> int:
        return self.base_defense + self.defense_bonus

    @property
    def defense_bonus(self) -> int:
        return self.parent.equipment.defense

    @property
    def power_bonus(self) -> int:
        return self.parent.equipment.power

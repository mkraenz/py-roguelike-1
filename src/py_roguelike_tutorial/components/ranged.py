from __future__ import annotations

from typing import TYPE_CHECKING

from py_roguelike_tutorial.components.base_component import BaseComponent

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor


class Ranged(BaseComponent):
    parent: Actor

    def __init__(self, power: int, range: int):
        self.base_power = power
        self.base_range = range

    @property
    def range(self) -> int:
        return self.base_range + self._range_bonus

    @property
    def _range_bonus(self) -> int:
        return self.parent.equipment.ranged_range

    @property
    def power(self) -> int:
        return self.base_power + self._power_bonus

    @property
    def _power_bonus(self) -> int:
        return self.parent.equipment.ranged_power

from __future__ import annotations
from typing import TYPE_CHECKING

from py_roguelike_tutorial.components.base_components import BaseComponent

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor


class Fighter(BaseComponent):
    entity: Actor  # type: ignore [reportIncompatibleVariableOverride]

    def __init__(self, hp: int, defense: int, power: int):
        self.max_hp = hp
        self._hp = hp
        self.defense = defense
        self.power = power

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, val: int) -> None:
        self._hp = max(0, min(self.max_hp, val))
        if self._hp <= 0:
            self.die()

    def die(self) -> None:
        death_msg = (
            "You died!"
            if self.engine.player is self.entity
            else f"{self.entity.name} has died!"
        )
        self.entity.die()
        print(death_msg)

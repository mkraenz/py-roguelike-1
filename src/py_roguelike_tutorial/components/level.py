from __future__ import annotations

from typing import TYPE_CHECKING

from py_roguelike_tutorial.components.base_components import BaseComponent
from py_roguelike_tutorial.validators.actor_validator import LevelData

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor


class Level(BaseComponent):
    parent: Actor  # type: ignore [reportIncompatibleVariableOverride]

    def __init__(
        self,
        current_level: int = 1,
        current_xp: int = 0,
        level_up_base: int = 0,
        level_up_factor: int = 150,
        xp_given: int = 0,
    ):
        """
        Parameters:
            level_up_base: If set to 0, the parent will NOT be able to level up! Enemies will have level_up_base=0.
            xp_given: The amount of EXP given to the player on death of the parent.
        """
        self.current_level = current_level
        self.current_xp = current_xp
        self.level_up_base = level_up_base
        self.level_up_factor = level_up_factor
        self.xp_given = xp_given

    @classmethod
    def from_dict(cls, data: LevelData):
        return cls(
            current_level=data.current_level if data.current_level else 1,
            current_xp=data.current_xp if data.current_xp else 0,
            level_up_base=data.level_up_base if data.level_up_base else 0,
            level_up_factor=data.level_up_factor if data.level_up_factor else 150,
            xp_given=data.xp_given if data.xp_given else 0
        )

    @property
    def xp_to_next_level(self) -> int:
        return self.level_up_base + self.current_level * self.level_up_factor

    @property
    def requires_level_up(self) -> bool:
        return self.current_xp >= self.xp_to_next_level

    def add_xp(self, xp: int) -> None:
        if xp == 0 or self.level_up_base == 0:
            return

        self.current_xp += xp
        self.log(f"You gain {xp} EXP.")
        if self.requires_level_up:
            self.log(f"You advance to level {self.current_level +1}!")

    def _increase_level(self) -> None:
        self.current_xp -= self.xp_to_next_level
        self.current_level += 1

    def increase_max_hp(self, amount: int = 20) -> None:
        self.parent.fighter.increase_max_hp(amount)
        self.log("Your health improves!")
        self._increase_level()

    def increase_power(self, amount: int = 1) -> None:
        self.parent.fighter.base_power += amount
        self.log("You feel stronger!")
        self._increase_level()

    def increase_defense(self, amount: int = 1) -> None:
        self.parent.fighter.base_defense += amount
        self.log("Your movements are getting swifter.")
        self._increase_level()

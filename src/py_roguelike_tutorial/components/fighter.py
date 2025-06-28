from __future__ import annotations
from typing import TYPE_CHECKING

from py_roguelike_tutorial.colors import Theme
from py_roguelike_tutorial.components.base_components import BaseComponent

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor


class Fighter(BaseComponent):
    parent: Actor  # type: ignore [reportIncompatibleVariableOverride]

    def __init__(self, max_hp: int, defense: int, power: int, hp: int | None = None):
        self.max_hp = max_hp
        self._hp = hp if hp else max_hp
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

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, val: int) -> None:
        self._hp = max(0, min(self.max_hp, val))
        if self._hp <= 0:
            self.die()

    def die(self) -> None:
        player_died = self.engine.player is self.parent
        death_msg = "You died!" if player_died else f"{self.parent.name} has died!"
        log_color = Theme.player_dies if player_died else Theme.enemy_dies
        self.parent.die()
        self.engine.message_log.add(death_msg, fg=log_color)
        self.engine.player.level.add_xp(self.parent.level.xp_given)

    def heal(self, amount: int) -> int:
        """Heals by the given amount and returns the amount recovered."""
        theoretical_new_hp = self.hp + amount
        new_hp_value = (
            theoretical_new_hp if theoretical_new_hp <= self.max_hp else self.max_hp
        )
        amount_recovered = new_hp_value - self.hp
        self.hp = new_hp_value
        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

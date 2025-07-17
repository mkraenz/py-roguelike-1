from __future__ import annotations
from typing import TYPE_CHECKING, Literal

from py_roguelike_tutorial.components.base_components import BaseComponent
from py_roguelike_tutorial.entity import Item

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine


type Slot = Literal["weapon", "armor"]


def get_attribute(attribute_name: str):
    def internal(item: Item | None, fallback: int = 0):
        if item is not None and item.equippable is not None:
            return getattr(item.equippable, attribute_name)
        return fallback

    return internal


class Equipment(BaseComponent):
    parent: Actor  # type: ignore [reportIncompatibleVariableOverride]

    def __init__(self, weapon: Item | None = None, armor: Item | None = None):
        self.armor = armor
        self.weapon = weapon

    @property
    def engine(self) -> Engine:
        return self.parent.game_map.engine

    @property
    def defense(self) -> int:
        return self.sum_attributes("defense")

    @property
    def ranged_power(self) -> int:
        return self.sum_attributes("ranged_power")

    @property
    def ranged_range(self) -> int:
        return self.sum_attributes("range")

    @property
    def power(self) -> int:
        return self.sum_attributes("power")

    def sum_attributes(self, attribute_name: str):
        return sum(map(get_attribute(attribute_name), [self.armor, self.weapon]))

    def is_equipped(self, item: Item) -> bool:
        return self.weapon == item or self.armor == item

    def _unequip_message(self, item_name: str) -> None:
        self.engine.message_log.add(f"{self.parent.name} unequips the {item_name}.")

    def _equip_message(self, item_name: str) -> None:
        self.engine.message_log.add(f"{self.parent.name} equips the {item_name}.")

    def _equip(self, slot: Slot, item: Item, show_message: bool) -> None:
        if self._slot_taken(slot):
            self._unequip(slot, show_message)
        setattr(self, slot, item)
        if show_message:
            self._equip_message(item.name)

    def _unequip(self, slot: Slot, show_message: bool) -> None:
        if not self._slot_taken(slot):
            return
        item: Item = getattr(self, slot)
        assert isinstance(item, Item)
        setattr(self, slot, None)
        if show_message:
            self._unequip_message(item.name)

    def _slot_taken(self, slot: Slot) -> bool:
        slotted_item: Item | None = getattr(self, slot)
        return slotted_item is not None

    def get(self, slot: Slot) -> Item | None:
        return getattr(self, slot)

    def toggle_equippable(self, equippable_item: Item, show_message: bool = True):
        is_weapon = (
            equippable_item.equippable and equippable_item.equippable.slot == "weapon"
        )
        slot: Slot = "weapon" if is_weapon else "armor"
        if self.is_equipped(equippable_item):
            self._unequip(slot, show_message)
        else:
            self._equip(slot, equippable_item, show_message)

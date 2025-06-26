from __future__ import annotations

from typing import TYPE_CHECKING

from py_roguelike_tutorial.components.base_components import BaseComponent

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor  # type: ignore [reportIncompatibleVariableOverride]

    @classmethod
    def none(cls):
        return Inventory(0)

    def __init__(self, capacity: int):
        self._capacity = capacity
        self.items: list[Item] = []

    def drop(self, item: Item) -> None:
        """Removes the item from the inventory and drops it at the parents location."""
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y)
        txt = f"You dropped the {item.name}."
        self.engine.message_log.add(text=txt)

    @property
    def len(self):
        return len(self.items)

    def has_capacity(self, items_to_add: int) -> bool:
        return self._capacity - self.len >= items_to_add

    def add(self, item: Item):
        self.items.append(item)
        item.parent = self

    def get(self, index: int) -> Item | None:
        return self.items[index] if index < len(self.items) else None

    def remove(self, item: Item) -> None:
        self.items.remove(item)
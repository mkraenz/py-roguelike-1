from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from py_roguelike_tutorial.components.base_components import BaseComponent
from py_roguelike_tutorial.validators.actor_validator import InventoryData

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor  # type: ignore [reportIncompatibleVariableOverride]

    def __init__(self, data: InventoryData):
        self._capacity = data.capacity
        self.items: list[Item] = []

    def drop(self, item: Item) -> None:
        """Removes the item from the inventory and drops it at the parents location."""
        self.items.remove(item)
        item.place(self.parent.x, self.parent.y, self.engine.game_map)
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

    def add_many(self, items: Iterable[Item]) -> None:
        for item in items:
            self.add(item)

    def get(self, index: int) -> Item | None:
        return self.items[index] if index < len(self.items) else None

    def remove(self, item: Item) -> None:
        self.items.remove(item)

    def has(self, kind: str) -> bool:
        kinds = (item.kind for item in self.items)
        return kind in kinds

    def get_by_kind(self, kind: str) -> Item | None:
        return next((item for item in self.items if item.kind == kind), None)

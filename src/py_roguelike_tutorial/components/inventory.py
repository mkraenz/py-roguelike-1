from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from py_roguelike_tutorial.components.base_components import BaseComponent
from py_roguelike_tutorial.validators.actor_validator import InventoryData

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, data: InventoryData):
        self._capacity = data.capacity
        self.items: list[Item] = []

    def get_by_id(self, item_id: str) -> Item | None:
        """Retrieve an item by its ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None

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

    def is_full(self) -> bool:
        return self._capacity == self.len

    def add(self, item: Item):
        if item.stacking:
            existing_item = self.get_by_kind(item.kind)
            if existing_item:
                existing_item.quantity += item.quantity
                return
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

    def has_by_tag(self, tag: str) -> bool:
        item = self.get_first_by_tag(tag)
        return item is not None

    def get_by_kind(self, kind: str) -> Item | None:
        return next((item for item in self.items if item.kind == kind), None)

    def get_first_by_tag(self, tag: str) -> Item | None:
        return next((item for item in self.items if tag in item.tags), None)

    def consume_by_tag(self, tag: str, quantity: int = 1) -> None:
        item = self.get_first_by_tag(tag)
        if not item:
            raise ValueError(f"No item with tag '{tag}' found in inventory.")

        item.quantity -= quantity
        if item.quantity <= 0:
            self.remove(item)
            txt = f"{self.parent.name} used up all {item.name}s."
            self.engine.message_log.add(text=txt)

    @property
    def gold(self) -> Item | None:
        return self.get_first_by_tag("gold")

    @property
    def gold_quantity(self) -> int:
        gold_item = self.gold
        return gold_item.quantity if gold_item else 0

    def replace_all(self, with_items: list[Item]):
        self.items.clear()
        self.items.extend(with_items)

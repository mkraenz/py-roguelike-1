from __future__ import annotations

from typing import TYPE_CHECKING


from py_roguelike_tutorial.actions import (
    DropItemAction,
)
from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)
from py_roguelike_tutorial.handlers.inventory_event_handler import InventoryEventHandler

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Item


class InventoryDropHandler(InventoryEventHandler):
    TITLE = "Select an item to drop"

    def on_item_selected(self, selected_item: Item) -> ActionOrHandler | None:
        return DropItemAction(self.player, selected_item)

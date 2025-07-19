from __future__ import annotations

from typing import TYPE_CHECKING


from py_roguelike_tutorial.actions import (
    EquipAction,
)
from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)
from py_roguelike_tutorial.handlers.inventory_event_handler import InventoryEventHandler

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Item


class InventoryActivateHandler(InventoryEventHandler):
    TITLE = "Select an item to use"

    def on_item_selected(self, selected_item: Item) -> ActionOrHandler | None:
        if selected_item.consumable:
            self.engine.stack.pop()
            return selected_item.consumable.get_action(self.player)
        if selected_item.equippable:
            self.engine.stack.pop()
            return EquipAction(self.player, selected_item)
        return None

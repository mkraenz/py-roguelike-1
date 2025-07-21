from __future__ import annotations

from typing import TYPE_CHECKING

import tcod
from tcod.console import Console
from tcod.event import KeySym as Key

from py_roguelike_tutorial.constants import Theme, Color
from py_roguelike_tutorial.handlers.ask_user_event_handler import AskUserEventHandler
from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Item


class InventoryEventHandler(AskUserEventHandler):
    """Let the user select items. Details are defined in the subclasses."""

    TITLE = "<missing title>"

    def on_render(self, console: Console, delta_time: float) -> None:
        super().on_render(console, delta_time)
        player = self.player
        carried_items = player.inventory.len
        height = max(carried_items + 2, 3)
        x = (
            0 if player.x > 30 else 40
        )  # render left or right of the player, wherever there's enough space
        y = 0
        width = len(self.TITLE) + 10

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            fg=Color.WHITE,
            bg=Color.BLACK,
            clear=True,
        )
        console.print(
            x=x + 1,
            y=y,
            width=width,
            height=height,
            fg=Color.WHITE,
            bg=Color.BLACK,
            text=f"┤{self.TITLE}├",
        )

        if carried_items > 0:
            for i, item in enumerate(player.inventory.items):
                item_key = chr(ord("a") + i)
                item_equipped = " (E)" if player.equipment.is_equipped(item) else ""
                item_charges = (
                    f" ({item.consumable.charges}Chg)"
                    if item.consumable is not None and item.consumable.charges > 1
                    else ""
                )
                console.print(
                    x=x + 1,
                    y=y + i + 1,
                    width=width,
                    height=height,
                    text=f"[{item_key}] {item.name}{item_equipped}{item_charges}",
                )
        else:
            console.print(x=x + 1, y=y + 1, width=width, height=height, text="(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        player = self.player
        key = event.sym
        index = key - Key.A
        carried_items = player.inventory.len

        if 0 <= index < carried_items:
            selected_item = player.inventory.get(index)
            if not selected_item:
                self.engine.message_log.add("Invalid entry.", Theme.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, selected_item: Item) -> ActionOrHandler | None:
        """Called when the user selects an item."""
        raise NotImplementedError("Must be implemented by subclass.")

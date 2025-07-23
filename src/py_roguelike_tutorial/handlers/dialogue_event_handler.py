from __future__ import annotations

from typing import TYPE_CHECKING

import tcod
from tcod.console import Console
from tcod.event import KeySym as Key

from py_roguelike_tutorial.entity import Item
from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)
from py_roguelike_tutorial.handlers.ingame_event_handler import IngameEventHandler
from py_roguelike_tutorial.render_functions import (
    IngameMenuConsole,
    print_texts,
)

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor
    from py_roguelike_tutorial.engine import Engine


class DialogueEventHandler(IngameEventHandler):
    def __init__(
        self,
        engine: Engine,
        speaker: Actor,
        other: Actor,
    ):
        super().__init__(engine)
        self.speaker = speaker
        self.other = other

    def on_render(self, console: Console, delta_time: float) -> None:
        super().on_render(console, delta_time)
        child_console, blit = IngameMenuConsole(console, f"{self.other.name}")
        texts = ["Hello, adventurer. How can i help you?"]
        width = child_console.width - 2
        x = 1
        y = 2
        print_texts(child_console, texts, x=x, start_y=y, width=width)

        y += len(texts) + 1
        shopkeeper = self.other
        carried_items = shopkeeper.inventory.len
        height = max(carried_items + 2, 3)
        if carried_items > 0:
            for i, item in enumerate(shopkeeper.inventory.items):
                item_key = chr(ord("a") + i)
                item_charges = (
                    f" ({item.consumable.charges}Chg)"
                    if item.consumable is not None and item.consumable.charges > 1
                    else ""
                )
                child_console.print(
                    x=x,
                    y=y + i,
                    width=width,
                    height=height,
                    text=f"[{item_key}] {item.name}{item_charges}",
                )
        else:
            child_console.print(
                x=x,
                y=y,
                width=width,
                height=height,
                text="Unfortunately, I've got nothing for sale today.",
            )

        blit()

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        shopkeeper = self.other
        key = event.sym
        index = key - Key.A
        carried_items = shopkeeper.inventory.len

        if 0 <= index < carried_items:
            selected_item = shopkeeper.inventory.get(index)
            if not selected_item:
                return None

            return self.on_item_selected(selected_item)
        self.engine.stack.pop()
        return super().ev_keydown(event)

    def on_item_selected(self, selected_item: Item) -> ActionOrHandler | None:
        """Called when the user selects an item."""
        self.other.inventory.remove(selected_item)
        self.speaker.inventory.add(selected_item)
        self.engine.message_log.add(
            text=f"{self.speaker.name} bought {selected_item.name} from {self.other
            .name}."
        )

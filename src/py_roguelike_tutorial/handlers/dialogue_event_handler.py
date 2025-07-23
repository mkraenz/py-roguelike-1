from __future__ import annotations

from typing import TYPE_CHECKING

import tcod
from tcod.console import Console
from tcod.event import KeySym as Key

from py_roguelike_tutorial.constants import Theme
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
        self.error = ""

    def on_render(self, console: Console, delta_time: float) -> None:
        super().on_render(console, delta_time)
        child_console, blit = IngameMenuConsole(console, f"{self.other.name}")
        texts = ["Hello, adventurer. How can i help you?"]
        width = child_console.width - 2
        x = 1
        y = 2
        print_texts(child_console, texts, x=x, start_y=y, width=width)

        buyers_gold_item = self.speaker.inventory.gold
        gold = buyers_gold_item.quantity if buyers_gold_item is not None else 0

        y += len(texts) + 1
        shopkeeper = self.other
        carried_items = shopkeeper.inventory.len
        height = max(carried_items + 2, 3)
        if carried_items > 0:
            for i, item in enumerate(shopkeeper.inventory.items):
                item_key = chr(ord("a") + i)
                quantity = f" x{item.quantity}" if item.quantity > 1 else ""
                price = 70  #  TODO for now fixed price 70
                price_tag = f"({price}G)"
                item_charges = (
                    f" ({item.consumable.charges}Chg)"
                    if item.consumable is not None and item.consumable.charges > 1
                    else ""
                )
                text = f"[{item_key}] {price_tag} {item.name}{quantity}{item_charges}"
                fg = Theme.menu_text if gold >= price else Theme.error
                child_console.print(
                    x=x, y=y, width=width, height=height, text=text, fg=fg
                )
                y += 1
        else:
            child_console.print(
                x=x,
                y=y,
                width=width,
                height=height,
                text="Unfortunately, I've got nothing for sale today.",
            )
        y += 1
        if self.error:
            child_console.print(
                x=x, y=y, width=width, height=height, text=self.error, fg=Theme.error
            )
        blit()

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        self.error = ""
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
        price = 70

        buyers_gold = self.speaker.inventory.gold
        if buyers_gold is None:
            self.error = "Come back when you have some gold."
            return None
        if buyers_gold.quantity < price:
            self.error = "You do not have enough gold to buy that."
            return None

        traded_gold = buyers_gold.duplicate()
        traded_gold.quantity = price

        self.other.inventory.remove(selected_item)
        self.speaker.inventory.consume_by_tag("gold", quantity=price)
        self.speaker.inventory.add(selected_item)
        self.other.inventory.add(traded_gold)

        self.engine.message_log.add(
            text=f"{self.speaker.name} bought {selected_item.name} from {self.other
            .name}."
        )

from __future__ import annotations

from typing import TYPE_CHECKING

from py_roguelike_tutorial.actions import Action, ItemAction
from py_roguelike_tutorial.colors import Theme
from py_roguelike_tutorial.components.base_components import BaseComponent
from py_roguelike_tutorial.components.inventory import Inventory
from py_roguelike_tutorial.exceptions import Impossible

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item  # type: ignore [reportIncompatibleVariableOverride]

    def get_action(self, consumer: Actor) -> Action | None:
        """Return the action for this item."""
        return ItemAction(consumer, self.parent)

    def activate(self, ctx: Action) -> None:
        """Invoke the item's ability."""
        raise NotImplementedError("Must be implemented by subclass")

    def consume(self) -> None:
        """Remove the used consumable from its containing inventory."""
        item = self.parent
        inventory = item.parent
        if isinstance(inventory, Inventory ):
            inventory.remove(item)

class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, ctx: Action) -> None:
        consumer = ctx.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            txt = f"You consume the {self.parent.name}, and recover {amount_recovered} HP (-> {consumer.fighter.hp} HP)."
            self.engine.message_log.add(text=txt, fg=Theme.health_recovered)
            self.consume()
        else:
            raise Impossible("You are at full health already.")

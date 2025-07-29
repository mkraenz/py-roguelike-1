from __future__ import annotations
from typing import TYPE_CHECKING, Protocol
from py_roguelike_tutorial.components.base_component import BaseComponent
from py_roguelike_tutorial.entity import Prop

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor


class Interactable(Protocol):
    parent: Prop

    def interact(self, actor: Actor) -> None: ...


class Chest(BaseComponent, Interactable):
    parent: Prop

    def interact(self, actor: Actor) -> None:
        if not actor.inventory.has_by_tag("kind:small_key"):
            self.log(f"The {self.parent.name} is locked.")
            return
        actor.inventory.consume_by_tag("kind:small_key")
        for item in self.parent.inventory.items:
            item.place(self.parent.x, self.parent.y, self.game_map)
            self.parent.inventory.remove(item)
        self.parent.health.die()

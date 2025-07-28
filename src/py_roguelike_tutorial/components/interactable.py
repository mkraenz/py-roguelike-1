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
        for item in self.parent.inventory.items:
            item.place(self.parent.x, self.parent.y, self.game_map)
            self.parent.inventory.remove(item)
        self.parent.blocks_movement = False
        self.parent.health.die()

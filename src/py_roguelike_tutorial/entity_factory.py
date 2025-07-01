from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor, Item


class EntityPrefabs:
    player: Actor
    npcs: dict[str, Actor] = {}
    items: dict[str, Item] = {}

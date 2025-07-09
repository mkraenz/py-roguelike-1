from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from py_roguelike_tutorial.behavior_trees.behavior_trees import BtNode
    from py_roguelike_tutorial.components.faction import Faction
    from py_roguelike_tutorial.entity import Actor, Item


class EntityPrefabs:
    player: Actor
    npcs: dict[str, Actor] = {}
    items: dict[str, Item] = {}
    behavior_trees: dict[str, BtNode] = {}
    factions: dict[str, Faction] = {}

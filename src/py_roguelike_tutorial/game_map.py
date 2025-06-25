from __future__ import annotations
from typing import TYPE_CHECKING, Iterable
import numpy as np
from tcod.console import Console

from py_roguelike_tutorial import tile_types

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Entity


class GameMap:
    def __init__(self, width: int, height: int, entities: Iterable[Entity]) -> None:
        self.width, self.height = width, height
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full((width, height), fill_value=False, order="F")
        self.explored = np.full((width, height), fill_value=False, order="F")

        self.entities = set(entities)

    def in_bounds(self, x: int, y: int) -> bool:
        """Is the coordinate within the map boundary?"""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        for entity in self.visible_entities:
            # only visible NPCs are drawn
            console.print(entity.x, entity.y, entity.char, fg=entity.color)

    @property
    def visible_entities(self) -> Iterable[Entity]:
        return filter(lambda e: self.visible[e.pos], self.entities)

    def get_blocking_entity_at(self, x: int, y: int) -> Entity | None:
        for entity in self.entities:
            if entity.blocks_movement and entity.pos == (x, y):
                return entity
        return None

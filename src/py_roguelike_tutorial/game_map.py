from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Iterator
import numpy as np
from tcod.console import Console

from py_roguelike_tutorial import tile_types
from py_roguelike_tutorial.entity import Actor, Item

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Entity


class GameMap:
    def __init__(
        self, *, engine: Engine, width: int, height: int, entities: Iterable[Entity]
    ) -> None:
        self.engine = engine
        self.width, self.height = width, height
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full((width, height), fill_value=False, order="F")
        self.explored = np.full((width, height), fill_value=False, order="F")

        self.entities = set(entities)

    @property
    def game_map(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterator of alive actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def visible_actors(self) -> Iterator[Actor]:
        yield from (
            entity for entity in self.actors if self.visible[entity.x, entity.y]
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_actor_at_location(self, x: int, y: int) -> Actor | None:
        for entity in self.actors:
            if entity.x == x and entity.y == y:
                return entity
        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Is the coordinate within the map boundary?"""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )
        sorted_entities = sorted(
            self.visible_entities, key=lambda x: x.render_order.value
        )

        for entity in sorted_entities:
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

    def get_item_at_location(self, x: int, y: int) -> Item | None:
        for entity in self.items:
            if entity.pos == (x, y):
                return entity

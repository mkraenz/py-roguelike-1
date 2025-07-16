from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Iterator

import numpy as np
import tcod
from tcod.console import Console

from py_roguelike_tutorial import tile_types
from py_roguelike_tutorial.colors import Color
from py_roguelike_tutorial.components.ai import BehaviorTreeAI
from py_roguelike_tutorial.entity import Actor, Item
from py_roguelike_tutorial.tile_types import SHROUD, floor, graphic_dt
from py_roguelike_tutorial.types import Coord, Rgb

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
        self.downstairs_location: Coord = (0, 0)
        self.dijkstra_map: np.ndarray = np.zeros(
            self.tiles.shape, dtype=np.int32, order="F"
        )

    def finalize_init(self):
        for actor in self.actors:
            ai = actor.ai
            if isinstance(ai, BehaviorTreeAI):
                ai.tree.blackboard["agent"] = actor
                ai.tree.blackboard["player"] = self.engine.player
                ai.tree.blackboard["engine"] = self.engine

        self.update_dijkstra_map()

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

    def update_dijkstra_map(self):
        # https://python-tcod.readthedocs.io/en/latest/tcod/path.html#tcod.path.dijkstra2d
        cost = self.tiles["walkable"].astype(np.uint32)
        distance = tcod.path.maxarray(self.tiles.shape, dtype=np.int32, order="F")
        distance[self.engine.player.pos] = 0
        tcod.path.dijkstra2d(distance, cost, 1, 1, out=distance)
        self.dijkstra_map = distance

    def get_actor_at_location(self, x: int, y: int) -> Actor | None:
        for entity in self.actors:
            if entity.x == x and entity.y == y:
                return entity
        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Is the coordinate within the map boundary?"""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        # excluded_value = np.iinfo(np.int32).max
        # masked_dijkstra_map = np.ma.masked_equal(self.dijkstra_map, excluded_value)
        # print(masked_dijkstra_map)
        # max_distance = (
        #     masked_dijkstra_map.max()
        # )  # Calculate the max excluding the masked value

        # def distance_to_color(distance: int) -> Rgb:
        #     if distance == excluded_value:
        #         return (0, 0, 0)
        #     return (
        #         # Transition logic
        #         # Normalize distance to [0, 1]
        #         (
        #             int(255 * (1 - distance / max_distance))
        #             if float(distance) / max_distance <= 0.5
        #             else 0
        #         ),  # Red
        #         (
        #             int(255 * (distance / (max_distance / 2)))
        #             if distance / max_distance <= 0.5
        #             else int(255 * (1 - distance / (max_distance / 2)))
        #         ),  # Green
        #         (
        #             int(255 * (distance / max_distance))
        #             if float(distance) / max_distance > 0.5
        #             else 0
        #         ),  # Blue
        #     )

        # vec = np.vectorize(distance_to_color)

        # color_map_wrong_axes = vec(self.dijkstra_map)
        # color_map = np.transpose(
        #     color_map_wrong_axes, axes=(1, 2, 0)
        # )  # Change shape from (3, 20, 15) to (20, 15, 3)
        # console.rgb["bg"][0 : self.width, 0 : self.height] = color_map

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
        return {e for e in self.entities if self.visible[e.pos]}

    def get_blocking_entity_at(self, x: int, y: int) -> Entity | None:
        for entity in self.entities:
            if entity.blocks_movement and entity.pos == (x, y):
                return entity
        return None

    def is_blocked(self, x: int, y: int):
        if self._is_blocking_tile(x, y):
            return True
        entity = self.get_blocking_entity_at(x, y)
        if entity:
            return True
        return False

    def _is_blocking_tile(self, x: int, y: int) -> bool:
        return not self.tiles[x, y]["walkable"]

    def get_item_at_location(self, x: int, y: int) -> Item | None:
        for entity in self.items:
            if entity.pos == (x, y):
                return entity
        return None

    def has_line_of_sight(self, first: Entity, second: Entity) -> bool:
        line_of_sight = tcod.los.bresenham(first.pos, second.pos)[1:-1]
        return all(not self.is_blocked(*pos) for pos in line_of_sight)

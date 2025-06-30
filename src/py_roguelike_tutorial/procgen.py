from __future__ import annotations

import random
from typing import Iterator, Protocol, TYPE_CHECKING

from tcod.los import bresenham

from py_roguelike_tutorial import tile_types
from py_roguelike_tutorial.components import procgen_config
from py_roguelike_tutorial.components.procgen_config import (
    ProcgenConfig as data,
)
from py_roguelike_tutorial.entity import Entity
from py_roguelike_tutorial.game_map import GameMap
from py_roguelike_tutorial.types import Coord

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine

DEBUG_STAIRS_AT_START = False


def get_prefabs_at_random(
    weighted_chances_by_floor: procgen_config.DungeonTable,
    num_of_entities: int,
    current_floor: int,
) -> list[Entity]:
    entity_weighted_chances = {}
    for floor, entity_table in weighted_chances_by_floor.items():
        if floor > current_floor:
            break
        for row in entity_table:
            entity_weighted_chances[row.entity] = row.weight
    entities = list(entity_weighted_chances.keys())
    weights = list(entity_weighted_chances.values())
    chosen_entities = random.choices(entities, weights=weights, k=num_of_entities)
    return chosen_entities


def get_max_row_for_floor(
    table: list[procgen_config.FloorTableRow], current_floor: int
) -> procgen_config.FloorTableRow:
    max_row: procgen_config.FloorTableRow = procgen_config.FloorTableRow(0, 0)
    for row in table:
        if current_floor >= row.floor > max_row.floor:
            max_row = row
    return max_row


class Room(Protocol):
    @property
    def center(self) -> Coord:
        raise NotImplementedError()


class RectangularRoom:
    def __init__(self, *, x: int, y: int, width: int, height: int) -> None:
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self) -> Coord:
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return center_x, center_y

    @property
    def inner(self) -> tuple[slice, slice]:
        """Return the inner area of this room as a 2D array index."""
        # +1's are for at least one row of walls between rooms with adjacent x's
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other: "RectangularRoom") -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def generate_dungeon(
    *,
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    current_floor: int,
    engine: Engine,
) -> GameMap:
    player = engine.player
    dungeon = GameMap(
        width=map_width, height=map_height, entities=[player], engine=engine
    )

    rooms: list[RectangularRoom] = []

    for _ in range(max_rooms):
        room_w = random.randint(room_min_size, room_max_size)
        room_h = random.randint(room_min_size, room_max_size)
        x = random.randint(0, dungeon.width - room_w - 1)
        y = random.randint(0, dungeon.height - room_h - 1)
        room = RectangularRoom(x=x, y=y, height=room_h, width=room_w)

        if any(room.intersects(other_room) for other_room in rooms):
            continue

        dungeon.tiles[room.inner] = tile_types.floor

        if len(rooms) != 0:
            for coord in tunnel_between_room_centers(room, rooms[-1]):
                dungeon.tiles[coord] = tile_types.floor

        place_entities(room, dungeon, current_floor)

        rooms.append(room)

    player.place(*rooms[0].center, dungeon)

    room_with_stairs = rooms[-1] if not DEBUG_STAIRS_AT_START else rooms[0]
    place_down_stairs(dungeon, room_with_stairs)

    return dungeon


def place_down_stairs(dungeon: GameMap, final_room: Room):
    dungeon.downstairs_location = final_room.center
    dungeon.tiles[final_room.center] = tile_types.down_stairs


def tunnel_between_room_centers(room1: Room, room2: Room) -> Iterator[Coord]:
    return tunnel_between(room1.center, room2.center)


def tunnel_between(start: Coord, end: Coord) -> Iterator[Coord]:
    """Return an L-shaped tunnel between these points."""
    x1, y1 = start
    x2, y2 = end
    # move horizontally then vertically or vice versa
    corner_x, corner_y = (x2, y1) if random.random() < 0.5 else (x1, y2)
    for x, y in bresenham(start=(x1, y1), end=(corner_x, corner_y)).tolist():
        yield x, y
    for x, y in bresenham(start=(corner_x, corner_y), end=(x2, y2)).tolist():
        yield x, y


def place_entities(
    room: RectangularRoom, game_map: GameMap, current_floor: int
) -> None:
    num_of_monsters = random.randint(
        0,
        get_max_row_for_floor(data.MAX_MONSTERS_BY_FLOOR, current_floor).max_value,
    )
    num_of_items = random.randint(
        0,
        get_max_row_for_floor(data.MAX_ITEMS_BY_FLOOR, current_floor).max_value,
    )

    items = get_prefabs_at_random(data.item_chances, num_of_items, current_floor)
    enemies = get_prefabs_at_random(data.enemy_chances, num_of_monsters, current_floor)

    for prefab in enemies + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)  # +-1 to avoid walls
        y = random.randint(room.y1 + 1, room.y2 - 1)
        place_taken = any(
            x == entity.x and y == entity.y for entity in game_map.entities
        )
        if not place_taken:
            prefab.spawn(game_map, x, y)

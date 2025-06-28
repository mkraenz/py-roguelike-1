from __future__ import annotations

import random
from typing import Iterator, Protocol, TYPE_CHECKING, NamedTuple

from tcod.los import bresenham

from py_roguelike_tutorial import tile_types
from py_roguelike_tutorial.entity import Entity
from py_roguelike_tutorial.entity_factory import EntityPrefabs as prefabs
from py_roguelike_tutorial.game_map import GameMap
from py_roguelike_tutorial.types import Coord

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine

DEBUG_STAIRS_AT_START = False

type Table = list[tuple[Entity, int]]


class FloorTableRow(NamedTuple):
    floor: int
    max_value: int


_MAX_ITEMS_BY_FLOOR = [
    FloorTableRow(1, 1),
    FloorTableRow(4, 2),
]
_MAX_MONSTERS_BY_FLOOR = [
    FloorTableRow(1, 2),
    FloorTableRow(4, 3),
    FloorTableRow(6, 5),
    FloorTableRow(9, 10),
]


class EntityTableRow(NamedTuple):
    entity: Entity
    weight: int
    """weights are the lottery tickets"""


type EntityTable = list[EntityTableRow]
type Floor = int
type DungeonTable = dict[Floor, EntityTable]

# The spawn chances are in some sense 'additive', so for floor 5, the actual roll table includes everything
# from floor 0 to 5. Each row for a higher floor may override the weights/lottery tickets of an entity from a
# previous floor.
_ITEM_CHANCES: DungeonTable = {
    0: [EntityTableRow(prefabs.health_potion, 35), EntityTableRow(prefabs.dagger, 5)],
    2: [
        EntityTableRow(prefabs.confusion_scroll, 10),
        EntityTableRow(prefabs.leather_armor, 15),
    ],
    4: [EntityTableRow(prefabs.lightning_scroll, 25), EntityTableRow(prefabs.sword, 5)],
    6: [
        EntityTableRow(prefabs.fireball_scroll, 25),
        EntityTableRow(prefabs.chain_mail, 15),
    ],
}

_ENEMY_CHANCES: DungeonTable = {
    0: [EntityTableRow(prefabs.orc, 80)],
    3: [EntityTableRow(prefabs.troll, 15)],
    5: [EntityTableRow(prefabs.troll, 30)],
    7: [EntityTableRow(prefabs.troll, 60)],
}


def get_prefabs_at_random(
    weighted_chances_by_floor: DungeonTable, num_of_entities: int, current_floor: int
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
    table: list[FloorTableRow], current_floor: int
) -> FloorTableRow:
    max_row: FloorTableRow = FloorTableRow(0, 0)
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
        0, get_max_row_for_floor(_MAX_MONSTERS_BY_FLOOR, current_floor).max_value
    )
    num_of_items = random.randint(
        0, get_max_row_for_floor(_MAX_ITEMS_BY_FLOOR, current_floor).max_value
    )
    items = get_prefabs_at_random(_ITEM_CHANCES, num_of_items, current_floor)
    enemies = get_prefabs_at_random(_ENEMY_CHANCES, num_of_monsters, current_floor)

    for prefab in enemies + items:
        x = random.randint(room.x1 + 1, room.x2 - 1)  # +-1 to avoid walls
        y = random.randint(room.y1 + 1, room.y2 - 1)
        place_taken = any(
            x == entity.x and y == entity.y for entity in game_map.entities
        )
        if not place_taken:
            prefab.spawn(game_map, x, y)

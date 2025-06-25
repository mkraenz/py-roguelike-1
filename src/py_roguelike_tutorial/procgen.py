import random
from typing import Iterator, List, Protocol, Tuple

from tcod.los import bresenham

from py_roguelike_tutorial import tile_types
from py_roguelike_tutorial.engine import Engine
from py_roguelike_tutorial.entity import Entity
from py_roguelike_tutorial.entity_factory import EntityFactory
from py_roguelike_tutorial.game_map import GameMap
from py_roguelike_tutorial.types import Coord


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
    def inner(self) -> Tuple[slice, slice]:
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
    max_monsters_per_room: int,
    engine: Engine,
) -> GameMap:
    player = engine.player
    dungeon = GameMap(
        width=map_width, height=map_height, entities=[player], engine=engine
    )

    rooms: List[RectangularRoom] = []

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

        place_entities(room, dungeon, max_monsters_per_room)

        rooms.append(room)

    player.place(*rooms[0].center, dungeon)

    return dungeon


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


def place_entities(room: RectangularRoom, game_map: GameMap, max_monsters: int) -> None:
    num_of_monsters = random.randint(0, max_monsters)
    for i in range(num_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1)  # +-1 to avoid walls
        y = random.randint(room.y1 + 1, room.y2 - 1)
        place_taken = any(
            x == entity.x and y == entity.y for entity in game_map.entities
        )
        if not place_taken:
            if random.random() < 0.8:
                EntityFactory.orc_prefab.spawn(game_map, x, y)
            else:
                EntityFactory.troll_prefab.spawn(game_map, x, y)

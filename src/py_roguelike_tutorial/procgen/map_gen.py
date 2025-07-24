from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterator, Literal, Protocol, TYPE_CHECKING

from tcod.los import bresenham
import networkx as nx

from py_roguelike_tutorial import constants, tile_types
from py_roguelike_tutorial.components.faction import Faction
from py_roguelike_tutorial.components.factions_manager import FactionsManager
from py_roguelike_tutorial.procgen.procgen_config import (
    ProcgenConfig as data,
)
from py_roguelike_tutorial.entity_factory import EntityPrefabs
from py_roguelike_tutorial.game_map import GameMap
from py_roguelike_tutorial.procgen.gen_helpers import (
    get_max_row_for_floor,
    get_prefabs_at_random,
)
from py_roguelike_tutorial.procgen.shop_gen import (
    ShopGenerationParams,
    generate_shop_inventory,
)
from py_roguelike_tutorial.types import Coord, CoordN

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine

DEBUG_STAIRS_AT_START = True


@dataclass
class LoadedDie:
    one_in: int
    at_most_once: bool = False
    _roll_count: int = 0
    _has_rolled_true: bool = False

    def roll(self) -> bool:
        if self.at_most_once and self._has_rolled_true:
            return False

        self._roll_count += 1
        if self._roll_count >= self.one_in:
            self._roll_count = 0
            self._has_rolled_true = True
            return True

        return False


class Room(Protocol):
    @property
    def center(self) -> Coord:
        raise NotImplementedError()


@dataclass(frozen=True)
class RectangularRoom:
    type: Literal["shop", "encounter", "treasury"]
    x1: int
    y1: int
    height: int
    width: int

    @property
    def x2(self):
        return self.x1 + self.width

    @property
    def y2(self):
        return self.y1 + self.height

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


@dataclass(frozen=True)
class MapGenerationParams:
    max_rooms: int
    room_min_size: int
    room_max_size: int
    map_width: int
    map_height: int


def generate_dungeon(
    *,
    params: MapGenerationParams,
    current_floor: int,
    engine: Engine,
    factions: FactionsManager,
) -> GameMap:
    player = engine.player
    dungeon = GameMap(
        width=params.map_width,
        height=params.map_height,
        entities=[player],
        engine=engine,
    )
    graph = nx.Graph()

    rooms: list[RectangularRoom] = []
    loaded_shop_die = LoadedDie(at_most_once=True, one_in=10)

    for _ in range(params.max_rooms):
        room_w = random.randint(params.room_min_size, params.room_max_size)
        room_h = random.randint(params.room_min_size, params.room_max_size)
        x = random.randint(0, dungeon.width - room_w - 1)
        y = random.randint(0, dungeon.height - room_h - 1)
        shop = loaded_shop_die.roll()
        type = "shop" if shop else "encounter"
        room = RectangularRoom(x1=x, y1=y, height=room_h, width=room_w, type=type)

        if any(room.intersects(other_room) for other_room in rooms):
            continue

        graph.add_node(room)
        dungeon.tiles[room.inner] = tile_types.floor

        if len(rooms) != 0:
            for coord in tunnel_between_room_centers(room, rooms[-1]):
                dungeon.tiles[coord] = tile_types.floor
                graph.add_edge(room, rooms[-1])

        rooms.append(room)

    player.place(*rooms[0].center, dungeon)
    # debug_place_entities(current_floor, player, dungeon)

    # for the time being we will place the player in rooms0. Overtime we should consider adding a start room type
    for room in rooms[1:]:
        match room.type:
            case "shop":
                make_shop_room(current_floor, dungeon, room)
            case "encounter":
                place_entities(room, dungeon, current_floor, factions)
            case "treasury":
                # Place entities in treasury room if needed
                pass

    room_with_stairs = rooms[-1] if not DEBUG_STAIRS_AT_START else rooms[0]
    place_down_stairs(dungeon, room_with_stairs)

    return dungeon


def make_shop_room(current_floor: int, dungeon: GameMap, room: Room) -> None:
    shopkeeper = EntityPrefabs.npcs["shopkeeper"].spawn(dungeon, *room.center)
    shopkeeper.inventory.replace_all(
        generate_shop_inventory(
            ShopGenerationParams(max_floors_ahead=constants.SHOP_MAX_FLOORS_AHEAD),
            current_floor,
        )
    )


def debug_place_entities(current_floor, player, dungeon):
    loc = (player.x + 5, player.y + 7)
    loc2 = (player.x + 1, player.y)
    loc3 = (player.x + 1, player.y + 1)
    loc4 = (player.x + 2, player.y + 1)
    EntityPrefabs.npcs["orc_archer"].spawn(dungeon, *loc)
    EntityPrefabs.items["dagger"].spawn(dungeon, *loc2)
    shopkeeper = EntityPrefabs.npcs["shopkeeper"].spawn(dungeon, *loc3)
    shopkeeper.inventory.replace_all(
        generate_shop_inventory(
            ShopGenerationParams(max_floors_ahead=constants.SHOP_MAX_FLOORS_AHEAD),
            current_floor,
        )
    )
    EntityPrefabs.items["gold"].spawn(dungeon, *loc3)
    EntityPrefabs.items["gold"].spawn(dungeon, *loc4)


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
    room: RectangularRoom,
    game_map: GameMap,
    current_floor: int,
    factions: FactionsManager,
) -> None:
    num_of_monsters = random.randint(
        0,
        get_max_row_for_floor(data.MAX_MONSTERS_BY_FLOOR, current_floor).max_value,
    )
    num_of_items = random.randint(
        0,
        get_max_row_for_floor(data.MAX_ITEMS_BY_FLOOR, current_floor).max_value,
    )

    room_faction: Faction = random.choice(list(factions.factions.values()))
    items = get_prefabs_at_random(data.item_chances, num_of_items, current_floor)
    enemies = get_prefabs_at_random(data.enemy_chances, num_of_monsters, current_floor)
    for item_prefab in items:
        loc = _random_spawn_location(room, game_map)
        if loc is None:
            continue
        item_prefab.spawn(game_map, loc.x, loc.y)

    for actor_prefab in enemies:
        loc = _random_spawn_location(room, game_map)
        if loc is None:
            continue
        actor = actor_prefab.spawn(game_map, loc.x, loc.y)
        actor.faction = room_faction


def _random_spawn_location(room: RectangularRoom, game_map: GameMap):
    x = random.randint(room.x1 + 1, room.x2 - 1)  # +-1 to avoid walls
    y = random.randint(room.y1 + 1, room.y2 - 1)
    place_taken = any(x == entity.x and y == entity.y for entity in game_map.entities)
    if place_taken:
        return None
    return CoordN(x, y)

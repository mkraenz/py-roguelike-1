import dataclasses
import random
from io import TextIOWrapper
from typing import Any

import numpy as np

wang_tile_dt = np.dtype(
    [("bitmask", np.int32), ("data", np.dtypes.StringDType), ("empty", np.bool)]
)


type Tile = np.ndarray


def new_wang_tile(bitmask: int, data: str, empty: bool = False) -> Tile:
    return np.array((bitmask, data, empty), dtype=wang_tile_dt)


def is_empty_wang_tile(tile: Tile):
    return tile["empty"]


def read_next_tile(file: TextIOWrapper):
    """We are very strict with our requirements on the file format.
    Each block must be separated by an empty line.
    At the end of the file, we need another empty line.
    Each block is 4 lines: the bitmask first, then the 3x3 room.

    TODO: find out why this is only including 30 out of 31 rooms from the file if we do not include anything
    on the last line in the file. The final room isn't being read properly.
    """
    current_tile_lines: list[str] = []
    for line in file:
        if line != "\n":
            current_tile_lines.append(line)
        else:
            bitmask_str, *room_data = current_tile_lines
            # TODO validation
            tile = new_wang_tile(int(bitmask_str.strip(), 2), "".join(room_data))
            yield tile
            current_tile_lines = []


def load_wang_tiles() -> list[Tile]:
    # filename = "assets/data/rooms/3x3rooms-test.txt"
    # with open(assets_filepath(filename)) as file:
    filename = "/home/mirco/programming/py-roguelike-tutorial/src/assets/data/rooms/3x3rooms-test.txt"
    tiles: list[Tile] = []
    with open(filename) as file:
        for tile in read_next_tile(file):
            tiles.append(tile)
    return tiles


class Bitmasks:
    NORTH = 0b1000
    EAST = 0b0100
    SOUTH = 0b0010
    WEST = 0b0001


@dataclasses.dataclass
class Neighbors:
    north: Any
    east: Any
    south: Any
    west: Any


def test_north_south_compatible(north_tile: Any, south_tile: Any) -> bool:
    # None-Tiles are always compatible
    if is_empty_wang_tile(north_tile) or is_empty_wang_tile(south_tile):
        return True
    a = (
        south_tile["bitmask"] & Bitmasks.NORTH
    )  # pick the north bit, bitmask abcd becomes a000
    b = north_tile["bitmask"] & Bitmasks.SOUTH  # abcd becomes 00c0
    c = a >> 2  # a000 becomes 00a0
    # if the two values are equal now, we know they are compatible (both have walls, or both entrances)
    return c == b


def test_east_west_compatible(east_tile: Any, west_tile: Any) -> bool:
    # None-Tiles are always compatible
    if is_empty_wang_tile(east_tile) or is_empty_wang_tile(west_tile):
        return True

    a = west_tile["bitmask"] & Bitmasks.EAST  # abcd becomes 0b00
    b = east_tile["bitmask"] & Bitmasks.WEST  # abcd becomes 000d
    c = a >> 2  # 0b00 becomes 000b
    return c == b


type Map = np.ndarray[tuple[int, int], Any]


def generate(tiles: list[Tile], width: int, height: int) -> Map:
    """Procedurally generate a filled map with all borders being all-walls wang tiles.
    The map will have dimensions width+2, height+2."""
    outer_width = width + 2
    outer_height = height + 2
    map: Map = np.full(
        (outer_height, outer_width), fill_value=new_wang_tile(0, "", True)
    )

    # prefill map borders
    # all_walls_tile = next((tile for tile in tiles if tile.bitmask == 0), None)
    # TODO
    all_walls_tile = new_wang_tile(0, "www\nwww\nwww\n")
    assert (
        all_walls_tile
    ), "No tile with bitmask 0000 found to fill in the borders with all-walls tiles."
    map[0, :] = all_walls_tile
    map[:, 0] = all_walls_tile
    map[-1, :] = all_walls_tile
    map[:, -1] = all_walls_tile
    # # here's the actual logic
    for x in range(1, width + 1):
        for y in range(1, height + 1):
            north_tile = map[y - 1][x]
            east_tile = map[y][x + 1]
            south_tile = map[y + 1][x]
            west_tile = map[y][x - 1]
            neighbors = Neighbors(north_tile, east_tile, south_tile, west_tile)

            candidates = get_tile_candidates(tiles, neighbors)
            map[y][x] = random.choice(candidates)
    return map


def get_tile_candidates(tiles: list[np.ndarray], neighbors: Neighbors):
    return [
        tile
        for tile in tiles
        if test_east_west_compatible(tile, neighbors.west)
        and test_east_west_compatible(neighbors.east, tile)
        and test_north_south_compatible(neighbors.north, tile)
        and test_north_south_compatible(tile, neighbors.south)
    ]


def draw(map: Map) -> str:
    # assuming square rooms
    room_size = len(map[0][0]["data"].splitlines()[0])
    display: list[str] = ["" for _ in range(len(map) * room_size)]
    for y in range(len(map)):
        for x in range(len(map[0])):
            tile = map[y][x]
            room_rows = tile["data"].splitlines()
            for i, room_row in enumerate(room_rows):
                display[room_size * y + i] += room_row
    return "\n".join(display)


if __name__ == "__main__":
    random.seed(14)
    tiles = load_wang_tiles()
    width, height = 50, 10
    # NOTE: map is actually width+2, height+2 due to all walls borders
    map = generate(tiles, width, height)
    rendered_map = draw(map)
    print(rendered_map)

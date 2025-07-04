import dataclasses
import random
from io import TextIOWrapper
from typing import Any

import numpy as np


type _Tile = np.ndarray

type _Map = np.ndarray[tuple[int, int], Any]


class _Bitmasks:
    NORTH = 0b1000
    EAST = 0b0100
    SOUTH = 0b0010
    WEST = 0b0001


@dataclasses.dataclass
class _Neighbors:
    north: _Tile
    east: _Tile
    south: _Tile
    west: _Tile


_wang_tile_dt = np.dtype(
    [("bitmask", np.int32), ("data", np.dtypes.StringDType), ("empty", np.bool)]
)


def _new_wang_tile(bitmask: int, data: str, empty: bool = False) -> _Tile:
    return np.array((bitmask, data, empty), dtype=_wang_tile_dt)


def _is_empty_wang_tile(tile: _Tile):
    return tile["empty"]


def _read_next_tile(file: TextIOWrapper):
    """We are very strict with our requirements on the file format.
    Each block must be separated by an empty line.
    At the end of the file, we need another empty line.
    Each block is 4 lines: the bitmask first, then the 3x3 room.

    TODO: find out why this is only including 30 out of 31 rooms from the file if we do not include anything
    on the last line in the file. The final room isn't being read properly.
    """
    current_tile_lines: list[str] = []
    for line in file:
        if line.startswith("//"):
            continue
        if line != "\n":
            current_tile_lines.append(line)
        else:
            if len(current_tile_lines) == 0:
                continue
            bitmask_str, *room_data = current_tile_lines
            # TODO validation?
            tile = _new_wang_tile(int(bitmask_str.strip(), 2), "".join(room_data))
            yield tile
            current_tile_lines = []


def load_wang_tiles(filepath: str) -> list[_Tile]:
    with open(filepath) as file:
        return [tile for tile in _read_next_tile(file)]


def _test_north_south_compatible(north_tile: _Tile, south_tile: _Tile) -> bool:
    # None-Tiles are always compatible
    if _is_empty_wang_tile(north_tile) or _is_empty_wang_tile(south_tile):
        return True
    a = (
        south_tile["bitmask"] & _Bitmasks.NORTH
    )  # pick the north bit, bitmask abcd becomes a000
    b = north_tile["bitmask"] & _Bitmasks.SOUTH  # abcd becomes 00c0
    c = a >> 2  # a000 becomes 00a0
    # if the two values are equal now, we know they are compatible (both have walls, or both entrances)
    return c == b


def _test_east_west_compatible(east_tile: _Tile, west_tile: _Tile) -> bool:
    # Empty Tiles are always compatible
    if _is_empty_wang_tile(east_tile) or _is_empty_wang_tile(west_tile):
        return True

    a = west_tile["bitmask"] & _Bitmasks.EAST  # abcd becomes 0b00
    b = east_tile["bitmask"] & _Bitmasks.WEST  # abcd becomes 000d
    c = a >> 2  # 0b00 becomes 000b
    return c == b


def _generate(tiles: list[_Tile], width: int, height: int) -> _Map:
    """Procedurally generate a filled map with all borders being all-walls wang tiles.
    The map will have dimensions width+2, height+2."""
    outer_width = width + 2
    outer_height = height + 2
    map: _Map = np.full(
        (outer_height, outer_width), fill_value=_new_wang_tile(0, "", True)
    )

    # prefill map borders
    all_walls_tile = next((tile for tile in tiles if tile["bitmask"] == 0), None)
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
            neighbors = _Neighbors(north_tile, east_tile, south_tile, west_tile)

            if x == 5 and y == 10:
                print("hello")
            candidates = _get_tile_candidates(tiles, neighbors, [all_walls_tile])
            # we try to keep the all_walls tile out of things as much as possible, only falling back to it in the worst case of no other matching tiles.
            candidates_or_fallback = (
                candidates if len(candidates) != 0 else [all_walls_tile]
            )
            map[y][x] = random.choice(candidates_or_fallback)

    return map


def _get_tile_candidates(
    tiles: list[_Tile], neighbors: _Neighbors, excluded_tiles: list[_Tile]
):
    return [
        tile
        for tile in tiles
        if _test_east_west_compatible(tile, neighbors.west)
        and _test_east_west_compatible(neighbors.east, tile)
        and _test_north_south_compatible(neighbors.north, tile)
        and _test_north_south_compatible(tile, neighbors.south)
        and not tile in excluded_tiles
    ]


def _draw(map: _Map) -> str:
    # assuming square rooms
    room_size_x = len(map[0, 0]["data"].splitlines()[0])
    room_size_y = len(map[0, 0]["data"].splitlines())
    display: list[str] = ["" for _ in range(len(map) * room_size_x)]
    for y in range(len(map)):
        for x in range(len(map[0])):
            tile = map[y][x]
            room_rows = tile["data"].splitlines()
            for i, room_row in enumerate(room_rows):
                display[room_size_y * y + i] += room_row
    return "\n".join(display)


def generate_map(tiles: list[_Tile], width: int, height: int) -> str:
    map = _generate(tiles, width, height)
    return _draw(map)


if __name__ == "__main__":
    # random.seed(14)
    # filename = "/home/mirco/programming/py-roguelike-tutorial/src/assets/data/rooms/3x3rooms-test.txt"
    filename = "/home/mirco/programming/py-roguelike-tutorial/src/assets/data/rooms/5x5rooms.txt"

    tiles = load_wang_tiles(filename)
    width, height = 30, 8
    # NOTE: map is actually width+2, height+2 due to all walls borders
    map = _generate(tiles, width, height)
    rendered_map = _draw(map)
    print(rendered_map)

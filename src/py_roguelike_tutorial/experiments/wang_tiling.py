import dataclasses
import random
from io import TextIOWrapper
from pprint import pprint
from typing import NamedTuple

from py_roguelike_tutorial.utils import assets_filepath


class WangTile(NamedTuple):
    bitmask: int
    data: str = "NONE"

    def __repr__(self):
        return str(self.bitmask)

    @staticmethod
    def is_none(tile: "WangTile") -> bool:
        return tile.data == "NONE"


WALLS = WangTile(0b0000, "WALLS")


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
            tile = WangTile(int(bitmask_str.strip(), 2), "".join(room_data))
            yield tile
            current_tile_lines = []


def load_wang_tiles() -> list[WangTile]:
    # filename = "assets/data/rooms/3x3rooms-test.txt"
    # with open(assets_filepath(filename)) as file:
    filename = "/home/mirco/programming/py-roguelike-tutorial/src/assets/data/rooms/3x3rooms-test.txt"
    tiles: list[WangTile] = []
    with open(filename) as file:
        for tile in read_next_tile(file):
            tiles.append(tile)
    return tiles


def load_wang_tiles_hard_coded() -> list[WangTile]:
    return [
        WALLS,
        WangTile(0b1000, "N1"),
        WangTile(0b1000, "N2"),
        WangTile(0b1001, "NW1"),
        WangTile(0b1001, "NW2"),
        WangTile(0b1010, "NS1"),
        WangTile(0b1010, "NS2"),
        WangTile(0b1011, "NSW1"),
        WangTile(0b1011, "NSW2"),
        WangTile(0b1100, "NE1"),
        WangTile(0b1100, "NE2"),
        WangTile(0b1101, "NEW1"),
        WangTile(0b1101, "NEW2"),
        WangTile(0b1110, "NES1"),
        WangTile(0b1110, "NES2"),
        WangTile(0b1111, "NESW1"),
        WangTile(0b1111, "NESW2"),
        WangTile(0b0100, "E1"),
        WangTile(0b0100, "E2"),
        WangTile(0b0101, "EW1"),
        WangTile(0b0101, "EW2"),
        WangTile(0b0110, "ES1"),
        WangTile(0b0110, "ES2"),
        WangTile(0b0111, "ESW1"),
        WangTile(0b0111, "ESW2"),
        WangTile(0b0010, "S1"),
        WangTile(0b0010, "S2"),
        WangTile(0b0011, "SW1"),
        WangTile(0b0011, "SW2"),
        WangTile(0b0001, "W1"),
        WangTile(0b0001, "W2"),
    ]


class Bitmasks:
    NORTH = 0b1000
    EAST = 0b0100
    SOUTH = 0b0010
    WEST = 0b0001


@dataclasses.dataclass
class Neighbors:
    north: WangTile
    east: WangTile
    south: WangTile
    west: WangTile


def test_north_south_compatible(north_tile: WangTile, south_tile: WangTile) -> bool:
    # None-Tiles are always compatible
    if WangTile.is_none(north_tile) or WangTile.is_none(south_tile):
        return True
    a = (
        south_tile.bitmask & Bitmasks.NORTH
    )  # pick the north bit, bitmask abcd becomes a000
    b = north_tile.bitmask & Bitmasks.SOUTH  # abcd becomes 00c0
    c = a >> 2  # a000 becomes 00a0
    # if the two values are equal now, we know they are compatible (both have walls, or both entrances)
    return c == b


def test_east_west_compatible(east_tile: WangTile, west_tile: WangTile) -> bool:
    # None-Tiles are always compatible
    if WangTile.is_none(east_tile) or WangTile.is_none(west_tile):
        return True

    a = west_tile.bitmask & Bitmasks.EAST  # abcd becomes 0b00
    b = east_tile.bitmask & Bitmasks.WEST  # abcd becomes 000d
    c = a >> 2  # 0b00 becomes 000b
    return c == b


def generate(tiles: list[WangTile], width: int, height: int):
    """Procedurally generate a filled map with all borders being all-walls wang tiles.
    The map will have dimensions width+2, height+2."""
    outer_width = width + 2
    outer_height = height + 2
    map = [
        [WangTile(-1) for _ in range(0, outer_width)] for _ in range(0, outer_height)
    ]

    # prefill map borders
    all_walls_tile = next((tile for tile in tiles if tile.bitmask == 0), None)
    assert (
        all_walls_tile
    ), "No tile with bitmask 0000 found to fill in the borders with all-walls tiles."
    for x in range(0, outer_width):
        for y in range(0, outer_height):
            if x == 0 or y == 0 or x == outer_width - 1 or y == outer_height - 1:
                map[y][x] = all_walls_tile

    # here's the actual logic
    for x in range(1, width + 1):
        for y in range(1, height + 1):
            north_tile = map[y - 1][x]
            east_tile = map[y][x + 1]
            south_tile = map[y + 1][x]
            west_tile = map[y][x - 1]
            neighbors = Neighbors(north_tile, east_tile, south_tile, west_tile)

            candidates = get_tile_candidates(tiles, neighbors)  # TODO continue here
            map[y][x] = random.choice(candidates)
    return map


def get_tile_candidates(tiles: list[WangTile], neighbors: Neighbors):
    return [
        tile
        for tile in tiles
        # TODO continue here. We somehow need to default to true if the neighboring tile is NONE
        if test_east_west_compatible(tile, neighbors.west)
        and test_east_west_compatible(neighbors.east, tile)
        and test_north_south_compatible(neighbors.north, tile)
        and test_north_south_compatible(tile, neighbors.south)
    ]


def draw(map: list[list[WangTile]]):
    # assuming square rooms
    room_size = len(map[0][0].data.splitlines()[0])
    display: list[str] = ["" for _ in range(len(map) * room_size)]
    for y in range(len(map)):
        for x in range(len(map[0])):
            tile = map[y][x]
            room_rows = tile.data.splitlines()
            for i, room_row in enumerate(room_rows):
                display[room_size * y + i] += room_row
    return "\n".join(display)


if __name__ == "__main__":
    random.seed(14)
    tiles = load_wang_tiles()
    width, height = 50, 10
    # NOTE: map is actually 5x6 due to all walls borders
    map = generate(tiles, width, height)
    pprint(map)
    rendered_map = draw(map)
    print(rendered_map)

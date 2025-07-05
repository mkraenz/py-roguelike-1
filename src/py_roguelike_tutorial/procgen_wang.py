from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from py_roguelike_tutorial import tile_types
from py_roguelike_tutorial.experiments import wang_tiling as wang
from py_roguelike_tutorial.utils import assets_filepath
from py_roguelike_tutorial.game_map import GameMap

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine

_replacements = {"w": tile_types.wall, ".": tile_types.floor}


def generate_dungeon(
    *,
    engine: Engine,
) -> GameMap:
    player = engine.player
    fake_width = 10
    fake_height = 5
    tiles = wang.load_wang_tiles(assets_filepath("assets/data/rooms/5x5rooms.txt"))
    proto_map = wang.generate_map(tiles, fake_width, fake_height)
    array = np.array([list(line) for line in proto_map.splitlines()])
    map_fn = np.vectorize(_replacements.get, otypes=[tile_types.tile_dt])
    map = map_fn(array)

    print(map)
    # width = len(proto_map.splitlines()[0])
    # height = len(proto_map.splitlines())
    # map = np.full((width, height), fill_value=tile_types.wall, order="F")

    # print(proto_map)

    width = len(map[0])
    height = len(map)

    dungeon = GameMap(
        width=width,
        height=height,
        entities=[player],
        engine=engine,
    )
    dim_x, dim_y = slice(width), slice(height)
    dungeon.tiles[dim_x, dim_y] = map.transpose()
    coord: tuple[int, int] = tuple(np.argwhere(map == tile_types.floor)[0])
    player.place(coord[0], coord[1], dungeon)
    return dungeon

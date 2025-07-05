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
    wang_width = 10
    wang_height = 5
    tiles = wang.load_wang_tiles(assets_filepath("assets/data/rooms/5x5rooms.txt"))
    wang_tile_map = wang.generate_map(tiles, wang_width, wang_height)
    proto_map = np.array([list(line) for line in wang_tile_map.splitlines()])
    map_fn = np.vectorize(_replacements.get, otypes=[tile_types.tile_dt])
    map = map_fn(proto_map)
    height, width = map.shape
    dungeon = GameMap(
        width=width,
        height=height,
        entities=[player],
        engine=engine,
    )
    dungeon.tiles[:] = map.transpose()
    coord: tuple[int, int] = tuple(np.argwhere(map == tile_types.floor)[0])
    player.place(coord[0], coord[1], dungeon)
    return dungeon

from typing import Tuple

import numpy as np

from py_roguelike_tutorial.types import Rgb

graphic_dt = np.dtype(
    [
        ("ch", np.int32),
        ("fg", "3B"),  # 3 bytes for RGB
        ("bg", "3B"),
    ]
)

tile_dt = np.dtype(
    [("walkable", np.bool), ("transparent", np.bool), ("dark", graphic_dt)]
)


def new_tile(
    *, walkable: int, transparent: int, dark: Tuple[int, Rgb, Rgb]
) -> np.ndarray:
    """Helper function for defining individual tile types.
    `dark` is for tiles outside the player's field of view.
    `transparent` - whether the tile is blocking field of view or not.
    """
    return np.array((walkable, transparent, dark), dtype=tile_dt)


floor = new_tile(
    walkable=True, transparent=True, dark=(ord(" "), (255, 255, 255), (50, 50, 150))
)
wall = new_tile(
    walkable=False, transparent=False, dark=(ord(" "), (255, 255, 255), (0, 0, 100))
)

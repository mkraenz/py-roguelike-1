import numpy as np

from py_roguelike_tutorial.colors import Color
from py_roguelike_tutorial.types import Rgb

_Graphic = tuple[int, Rgb, Rgb]

graphic_dt = np.dtype(
    [
        ("ch", np.int32),
        ("fg", "3B"),  # 3 bytes for RGB
        ("bg", "3B"),
    ]
)

tile_dt = np.dtype(
    [
        ("walkable", np.bool),
        ("transparent", np.bool),  # whether or not the field is blocking FOV
        ("dark", graphic_dt),  # graphics for when the field is not in FOV
        ("light", graphic_dt),  # graphics for when the field is in FOV
    ]
)


def new_tile(
    *, walkable: int, transparent: int, dark: _Graphic, light: _Graphic
) -> np.ndarray:
    """Helper function for defining individual tile types.
    `dark` is for tiles outside the player's field of view.
    `transparent` - whether the tile is blocking field of view or not.
    """
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), Color.WHITE, Color.BLACK), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), Color.WHITE, (50, 50, 150)),
    light=(ord(" "), Color.WHITE, (200, 180, 50)),
)
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord(" "), Color.WHITE, (0, 0, 100)),
    light=(ord(" "), Color.WHITE, (130, 110, 50)),
)

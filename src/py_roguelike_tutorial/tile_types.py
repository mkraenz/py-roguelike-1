import numpy as np

from py_roguelike_tutorial.constants import Color
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
        (
            "walkable",
            np.bool,
        ),  # whether the tile can be walk over, and whether it blocks ranged shots
        ("transparent", np.bool),  # whether or not the field is blocking FOV
        ("dark", graphic_dt),  # graphics for when the field is not in FOV
        ("light", graphic_dt),  # graphics for when the field is in FOV
        ("name", np.dtypes.StringDType),
    ]
)


def new_tile(
    *, walkable: int, transparent: int, dark: _Graphic, light: _Graphic, name: str
) -> np.ndarray:
    """Helper function for defining individual tile types.
    `dark` is for tiles outside the player's field of view.
    `transparent` - whether the tile is blocking field of view or not.
    """
    return np.array((walkable, transparent, dark, light, name), dtype=tile_dt)


# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), Color.WHITE, Color.BLACK), dtype=graphic_dt)

floor = new_tile(
    name="Floor",
    walkable=True,
    transparent=True,
    dark=(ord(" "), Color.WHITE, Color.BLUE_DARK),
    light=(ord(" "), Color.WHITE, Color.YELLOW_DARK),
)
wall = new_tile(
    name="Wall",
    walkable=False,
    transparent=False,
    dark=(ord(" "), Color.WHITE, Color.BLUE_NAVY_DARK),
    light=(ord(" "), Color.WHITE, Color.YELLOW_PALE_BROWN),
)
down_stairs = new_tile(
    name="Downwards Stairs",
    walkable=True,
    transparent=True,
    dark=(ord(">"), Color.BLUE_NAVY, Color.BLUE_LOCHMARA),
    light=(ord(">"), Color.WHITE, Color.YELLOW_AUTUMN_GOLD),
)

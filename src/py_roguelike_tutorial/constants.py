from typing import Final

from py_roguelike_tutorial.types import Coord


class Direction:
    N: Final[Coord] = (0, -1)
    S: Final[Coord] = (0, 1)
    W: Final[Coord] = (-1, 0)
    E: Final[Coord] = (1, 0)
    NW: Final[Coord] = (-1, -1)
    NE: Final[Coord] = (1, -1)
    SE: Final[Coord] = (1, 1)
    SW: Final[Coord] = (-1, 1)


INTERCARDINAL_DIRECTIONS = (
    Direction.N,
    Direction.S,
    Direction.W,
    Direction.E,
    Direction.NW,
    Direction.NE,
    Direction.SW,
    Direction.SE,
)

AUTOSAVE_FILENAME = "autosave.sav"
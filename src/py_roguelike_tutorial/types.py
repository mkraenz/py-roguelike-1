from typing import NamedTuple

Rgb = tuple[int, int, int]
Rgba = tuple[int, int, int, int]

Coord = tuple[int, int]


class CoordN(NamedTuple):
    x: int
    y: int

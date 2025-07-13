from py_roguelike_tutorial.types import Coord


class Math:
    @staticmethod
    def pos_diff(a: Coord, b: Coord) -> Coord:
        return a[0] - b[0], a[1] - b[1]

    @staticmethod
    def dist_chebyshev(a: Coord, b: Coord) -> int:
        dx, dy = Math.pos_diff(a, b)
        return max(abs(dx), abs(dy))

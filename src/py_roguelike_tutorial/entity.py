from py_roguelike_tutorial.types import Rgb


class Entity:
    """
    Generic object to represent players, enemies, items, etc
    """

    def __init__(self, x: int, y: int, char: str, color: Rgb) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

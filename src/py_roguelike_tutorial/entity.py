import copy

from py_roguelike_tutorial.game_map import GameMap
from py_roguelike_tutorial.types import Coord, Rgb
from py_roguelike_tutorial.colors import Color


class Entity:
    """
    Generic object to represent players, enemies, items, etc
    """

    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str,
        color: Rgb = Color.BLACK,
        name: str,
        blocks_movement: bool = False,
    ) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement

    def spawn(self, game_map: GameMap, x: int, y: int):
        """Returns a clone of this entity that has been added to the map.
        (Think like the spawning entity as the blueprint)
        """
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        game_map.entities.add(clone)
        return clone

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    @property
    def pos(self) -> Coord:
        return self.x, self.y

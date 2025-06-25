import copy

from py_roguelike_tutorial.game_map import GameMap
from py_roguelike_tutorial.types import Coord, Rgb
from py_roguelike_tutorial.colors import Color


class Entity:
    """
    Generic object to represent players, enemies, items, etc
    """

    game_map: GameMap

    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str,
        color: Rgb = Color.BLACK,
        name: str,
        blocks_movement: bool = False,
        game_map: GameMap | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        if game_map:
            self.game_map = game_map
            game_map.entities.add(self)

    def spawn(self, game_map: GameMap, x: int, y: int):
        """Returns a clone of this entity that has been added to the map.
        (Think like the spawning entity as the blueprint)
        """
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.game_map = game_map
        game_map.entities.add(clone)
        return clone

    def place(self, x: int, y: int, game_map: GameMap | None = None) -> None:
        """Places the entity at a new location. Handles movement across maps."""
        self.x, self.y = x, y
        if game_map:
            if hasattr(self, "game_map"):
                self.game_map.entities.remove(self)
            self.game_map = game_map
            game_map.entities.add(self)

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    @property
    def pos(self) -> Coord:
        return self.x, self.y

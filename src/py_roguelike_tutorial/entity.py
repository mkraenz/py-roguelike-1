from __future__ import annotations
import copy
from typing import Type, TYPE_CHECKING

from py_roguelike_tutorial.components.fighter import Fighter
from py_roguelike_tutorial.render_order import RenderOrder
from py_roguelike_tutorial.types import Coord, Rgb
from py_roguelike_tutorial.colors import Color

if TYPE_CHECKING:
    from py_roguelike_tutorial.components.ai import BaseAI
    from py_roguelike_tutorial.game_map import GameMap


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
        render_order: RenderOrder = RenderOrder.CORPSE,
    ) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
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

    def diff_position(self, from_: "Entity") -> Coord:
        """The position difference from `from_` to this entity"""
        return self.x - from_.x, self.y - from_.y

    def dist_chebyshev(self, from_: "Entity") -> int:
        dx, dy = self.diff_position(from_)
        return max(abs(dx), abs(dy))


class Actor(Entity):
    """An actor needs two things to function:
    ai: to move around and make decisions
    fighter: the ability to take (and deal) damage
    """

    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str,
        color: Rgb = Color.WHITE,
        name: str,
        ai_cls: Type[BaseAI],
        fighter: Fighter,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )
        self.ai: BaseAI | None = ai_cls(self)
        self.fighter = fighter
        self.fighter.entity = self

    @property
    def is_alive(self) -> bool:
        """Returns true as long as the actor can perform actions"""
        return bool(self.ai)

    def die(self):
        self.char = "%"
        self.color = Color.RED_GUARDMANS
        self.blocks_movement = False
        self.ai = None
        self.name = f"remains of {self.name}"
        self.render_order = RenderOrder.CORPSE

from __future__ import annotations

import copy
import math
from typing import Type, TYPE_CHECKING

from py_roguelike_tutorial.colors import Color
from py_roguelike_tutorial.components.faction import Faction
from py_roguelike_tutorial.render_order import RenderOrder
from py_roguelike_tutorial.types import Coord, Rgb

if TYPE_CHECKING:
    from py_roguelike_tutorial.components.equippable import Equippable
    from py_roguelike_tutorial.components.equipment import Equipment
    from py_roguelike_tutorial.components.level import Level
    from py_roguelike_tutorial.components.ai import BaseAI
    from py_roguelike_tutorial.game_map import GameMap
    from py_roguelike_tutorial.components.fighter import Fighter
    from py_roguelike_tutorial.components.inventory import Inventory
    from py_roguelike_tutorial.components.consumable import Consumable


class Entity:
    """
    Generic object to represent players, enemies, items, etc
    """

    parent: GameMap

    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str,
        color: Rgb = Color.BLACK,
        name: str,
        blocks_movement: bool = False,
        parent: GameMap | None = None,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            self.parent = parent
            parent.entities.add(self)

    @property
    def game_map(self) -> GameMap:
        # this is not type safe...
        return self.parent.game_map

    def spawn(self, game_map: GameMap, x: int, y: int):
        """Returns a clone of this entity that has been added to the map.
        (Think like the spawning entity as the blueprint)
        """
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = game_map
        game_map.entities.add(clone)
        return clone

    def place(self, x: int, y: int, game_map: GameMap | None = None) -> None:
        """Places the entity at a new location. Handles movement across maps."""
        self.x, self.y = x, y
        if game_map:
            if hasattr(self, "parent"):
                if self.parent is self.game_map:
                    self.game_map.entities.remove(self)
            self.parent = game_map
            game_map.entities.add(self)

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy

    @property
    def pos(self) -> Coord:
        return self.x, self.y

    def diff_from(self, from_: "Entity") -> Coord:
        """The position difference from `from_` to this entity"""
        return self.diff_position(*from_.pos)

    def diff_position(self, x: int, y: int) -> Coord:
        """The position difference from the given coordinates."""
        return self.x - x, self.y - y

    def dist_chebyshev(self, to: "Entity") -> int:
        return self.dist_chebyshev_pos(*to.pos)

    def dist_chebyshev_pos(self, x: int, y: int) -> int:
        dx, dy = self.diff_position(x, y)
        return max(abs(dx), abs(dy))

    def dist_euclidean(self, to: "Entity") -> float:
        return self.dist_euclidean_pos(*to.pos)

    def dist_euclidean_pos(self, x: int, y: int) -> float:
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)


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
        inventory: Inventory,
        level: Level,
        equipment: Equipment,
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
        self.level = level
        self.level.parent = self
        self.ai: BaseAI | None = ai_cls(self)
        self.fighter = fighter
        self.fighter.parent = self
        self.inventory = inventory
        self.inventory.parent = self
        self.equipment = equipment
        self.equipment.parent = self
        self.faction: Faction

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


class Item(Entity):
    parent: GameMap | Inventory  # type: ignore [reportIncompatibleVariableOverride]

    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Rgb = Color.WHITE,
        name: str = "<Unnamed Item>",
        consumable: Consumable | None = None,
        equippable: Equippable | None = None,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
        )
        self.equippable = equippable
        self.consumable = consumable
        if self.consumable:
            self.consumable.parent = self
        if self.equippable:
            self.equippable.parent = self

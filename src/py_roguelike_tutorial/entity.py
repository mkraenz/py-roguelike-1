from __future__ import annotations

import copy
import math
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

from py_roguelike_tutorial.components.faction import Faction
from py_roguelike_tutorial.components.ranged import Ranged
from py_roguelike_tutorial.constants import Color
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


class RenderOrder(Enum):
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()


@dataclass
class Entity:
    """
    Generic object to represent players, enemies, items, etc
    """

    parent: GameMap = field(init=False)

    name: str
    char: str
    tags: set[str]
    id: uuid.UUID = uuid.UUID("{00000000-0000-0000-0000-000000000000}")
    x: int = 0
    y: int = 0
    color: Rgb = Color.BLACK
    blocks_movement: bool = False
    render_order: RenderOrder = RenderOrder.CORPSE
    move_stepsize: int = 1

    def __post_init__(self):
        if self.parent:
            self.parent = self.parent
            self.parent.entities.add(self)

    @property
    def game_map(self) -> GameMap:
        # this is not type safe...
        return self.parent.game_map

    def spawn(self, game_map: GameMap, x: int, y: int):
        """Returns a clone of this entity that has been added to the map.
        (Think like the spawning entity as the blueprint)
        """
        clone = self.duplicate()
        clone.x = x
        clone.y = y
        clone.parent = game_map
        game_map.entities.add(clone)
        return clone

    def duplicate(self):
        clone = copy.deepcopy(self)
        clone.randomize_id()
        return clone

    def randomize_id(self) -> None:
        """Assigns a new random UUID to the entity."""
        self.id = uuid.uuid4()

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
        self.pos = self.test_move(dx, dy)

    def test_move(self, dx: int, dy: int) -> Coord:
        return self.x + dx * self.move_stepsize, self.y + dy * self.move_stepsize

    @property
    def pos(self) -> Coord:
        return self.x, self.y

    @pos.setter
    def pos(self, pos: Coord) -> None:
        self.x = pos[0]
        self.y = pos[1]

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

    def __hash__(self):
        """Make the entity hashable based on its unique ID."""
        return hash(self.id)

    def __eq__(self, other):
        """Equality check based on unique ID."""
        if isinstance(other, Entity):
            return self.id == other.id
        return False


@dataclass
class Actor(Entity):
    """An actor needs two things to function:
    ai: to move around and make decisions
    fighter: the ability to take (and deal) damage
    """

    # ai: BaseAI
    fighter: Fighter = None  # type: ignore
    inventory: Inventory = None  # type: ignore
    level: Level = None  # type: ignore
    equipment: Equipment = None  # type: ignore
    color: Rgb = Color.WHITE
    move_stepsize: int = 1
    blocks_movement: bool = True
    render_order: RenderOrder = RenderOrder.ACTOR
    ranged: Ranged | None = None

    def __post_init__(self):
        if self.ranged:
            self.ranged.parent = self
        self.level.parent = self
        self.fighter.parent = self
        self.inventory.parent = self
        self.equipment.parent = self
        self.faction: Faction

    @property
    def ai(self) -> BaseAI | None:
        return self._ai

    @ai.setter
    def ai(self, val: BaseAI | None):
        self._ai = val
        if val:
            val.agent = self

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

    def __hash__(self):
        """Make the entity hashable based on its unique ID."""
        return hash(self.id)

    def __eq__(self, other):
        """Equality check based on unique ID."""
        if isinstance(other, Entity):
            return self.id == other.id
        return False


@dataclass
class Item(Entity):
    description: str = ""
    flavor_text: str = ""
    kind: str = ""
    quantity: int = 1
    base_value: int = 1
    parent: GameMap | Inventory = field(init=False)
    stacking: bool = False
    consumable: Consumable | None = None
    equippable: Equippable | None = None

    @property
    def value(self):
        return self.base_value * self.quantity

    def __post_init__(self):
        if self.consumable:
            self.consumable.parent = self
        if self.equippable:
            self.equippable.parent = self

    def __hash__(self):
        """Make the entity hashable based on its unique ID."""
        return hash(self.id)

    def __eq__(self, other):
        """Equality check based on unique ID."""
        if isinstance(other, Entity):
            return self.id == other.id and self.name == other.name
        return False

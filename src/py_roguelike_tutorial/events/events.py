from typing import Callable, Literal, TypedDict

from py_roguelike_tutorial.entity import Actor
from py_roguelike_tutorial.types import Coord

type EventType = Literal["ranged_attack"]


class RangedAttackEvent(TypedDict):
    type: Literal["ranged_attack"]
    attacker: Actor
    target: Actor
    damage: int
    target_pos: Coord
    attacker_pos: Coord


type GameEvent = RangedAttackEvent
type EventCallback = Callable[[RangedAttackEvent], None]

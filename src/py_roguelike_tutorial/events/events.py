from dataclasses import dataclass
from typing import Callable, Literal, Protocol, TypedDict

from py_roguelike_tutorial.entity import Actor
from py_roguelike_tutorial.types import Coord

type EventType = Literal["ranged_attack", "talk"]


# Base protocol for all events
class GameEvent(Protocol):
    type: str


@dataclass
class RangedAttackEvent(GameEvent):
    type: Literal["ranged_attack"]
    attacker: Actor
    target: Actor
    damage: int
    target_pos: Coord
    attacker_pos: Coord


@dataclass
class TalkEvent(GameEvent):
    type: Literal["talk"]
    actor: Actor
    target: Actor

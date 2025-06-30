from __future__ import annotations

from typing import NamedTuple

from py_roguelike_tutorial.entity import Entity

type Table = list[tuple[Entity, int]]


class FloorTableRow(NamedTuple):
    floor: int
    max_value: int


class EntityTableRow(NamedTuple):
    entity: Entity
    weight: int
    """weights are the lottery tickets"""


type EntityTable = list[EntityTableRow]
type Floor = int
type DungeonTable = dict[Floor, EntityTable]


class ProcgenConfig:
    MAX_ITEMS_BY_FLOOR = [
        FloorTableRow(1, 1),
        FloorTableRow(4, 2),
    ]
    MAX_MONSTERS_BY_FLOOR = [
        FloorTableRow(1, 2),
        FloorTableRow(4, 3),
        FloorTableRow(6, 5),
        FloorTableRow(9, 10),
    ]

    # The spawn chances are in some sense 'additive', so for floor 5, the actual roll table includes everything
    # from floor 0 to 5. Each row for a higher floor may override the weights/lottery tickets of an entity from a
    # previous floor.
    item_chances: DungeonTable = {}

    enemy_chances: DungeonTable = {}

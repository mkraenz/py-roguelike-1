import random

from py_roguelike_tutorial.procgen import procgen_config


def get_max_row_for_floor(
    table: list[procgen_config.FloorTableRow], current_floor: int
) -> procgen_config.FloorTableRow:
    max_row: procgen_config.FloorTableRow = procgen_config.FloorTableRow(0, 0)
    for row in table:
        if current_floor >= row.floor > max_row.floor:
            max_row = row
    return max_row


def get_prefabs_at_random[T](
    weighted_chances_by_floor: procgen_config.DungeonTable[T],
    num_of_entities: int,
    current_floor: int,
) -> list[T]:
    entity_weighted_chances = {}
    for floor, entity_table in weighted_chances_by_floor.items():
        if floor > current_floor:
            break
        for row in entity_table:
            entity_weighted_chances[row.entity] = row.weight
    entities = list(entity_weighted_chances.keys())
    weights = list(entity_weighted_chances.values())
    chosen_entities = random.choices(entities, weights=weights, k=num_of_entities)
    return chosen_entities

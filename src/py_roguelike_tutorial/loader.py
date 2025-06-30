from __future__ import annotations
from typing import TYPE_CHECKING

import yaml

from py_roguelike_tutorial.components.procgen_config import DungeonTable, EntityTableRow
from py_roguelike_tutorial.entity_deserializers import item_from_dict
from py_roguelike_tutorial.utils import assets_filepath

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Item, Actor


class DataLoader:
    def load_item_entities(self):
        items: dict[str, Item] = {}

        # load items
        with open(assets_filepath("assets/data/entities/items.yml")) as items_file:
            contents = items_file.read()
        item_data: dict[str, dict] = yaml.safe_load(contents)
        # todo consider using pydantic for validation
        for key, val in item_data.items():
            items[key] = item_from_dict(val)
        return items

    def load_item_drops_rates(self, item_prefabs: dict[str, Item]):
        with open(
            assets_filepath("assets/data/tables/dungeon_item_drops.yml")
        ) as dungeon_drops_file:
            item_drops_data: dict[int, list[list[str | int]]] = yaml.safe_load(
                dungeon_drops_file.read()
            )
        item_chances: DungeonTable = {}
        for floor, entity_name_table in item_drops_data.items():
            entity_table = map(
                lambda row: EntityTableRow(item_prefabs[str(row[0])], int(row[1])),
                entity_name_table,
            )
            item_chances[floor] = list(entity_table)
        return item_chances

    def load_enemy_spawn_rates(self, npc_prefabs: dict[str, Actor]):
        # load enemy spawn rates
        with open(
            assets_filepath("assets/data/tables/dungeon_enemy_spawns.yml")
        ) as enemy_spawn_rates_file:
            raw_spawn_rates_by_floor: dict[int, list[list[str | int]]] = yaml.safe_load(
                enemy_spawn_rates_file.read()
            )
        spawn_rates: DungeonTable = {}
        for floor, raw_entity_table in raw_spawn_rates_by_floor.items():
            entity_table = map(
                lambda x: EntityTableRow(npc_prefabs[str(x[0])], int(x[1])),
                raw_entity_table,
            )
            spawn_rates[floor] = list(entity_table)
        return spawn_rates

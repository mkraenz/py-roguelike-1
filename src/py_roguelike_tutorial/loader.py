from __future__ import annotations
from typing import TYPE_CHECKING

import yaml

from py_roguelike_tutorial.components.procgen_config import DungeonTable, EntityTableRow
from py_roguelike_tutorial.entity_deserializers import item_from_dict
from py_roguelike_tutorial.utils import assets_filepath


if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Item, Actor

type SpawnRateTable = dict[int, list[tuple[str, int]]]


class DataLoader:
    @staticmethod
    def load_asset(filename: str):
        with open(assets_filepath(filename)) as file:
            return yaml.safe_load(file.read())

    def load_item_entities(self) -> dict[str, Item]:
        items: dict[str, Item] = {}

        filename = "assets/data/entities/items.yml"
        item_data: dict[str, dict] = self.load_asset(filename)
        # todo consider using pydantic for validation
        erroneous_keys: list[str] = []
        for key, val in item_data.items():
            try:
                items[key] = item_from_dict(val)
            except Exception as e:
                erroneous_keys.append(key)
        if erroneous_keys:
            error_keys = ", ".join(erroneous_keys)
            raise SystemError(
                f"Error loading {filename}. Entity definitions malformed: {error_keys}"
            )
        return items

    def load_item_drops_rates(self, item_prefabs: dict[str, Item]) -> DungeonTable:
        filename = "assets/data/tables/dungeon_item_drops.yml"
        item_drops_data: SpawnRateTable = self.load_asset(filename)
        item_chances: DungeonTable = {}
        for floor, entity_name_table in item_drops_data.items():
            entity_table = map(
                lambda row: EntityTableRow(item_prefabs[str(row[0])], int(row[1])),
                entity_name_table,
            )
            item_chances[floor] = list(entity_table)
        return item_chances

    def load_enemy_spawn_rates(self, npc_prefabs: dict[str, Actor]) -> DungeonTable:
        filename = "assets/data/tables/dungeon_enemy_spawns.yml"
        raw_spawn_rates_by_floor: SpawnRateTable = self.load_asset(filename)
        spawn_rates: DungeonTable = {}
        for floor, raw_entity_table in raw_spawn_rates_by_floor.items():
            entity_table = map(
                lambda x: EntityTableRow(npc_prefabs[str(x[0])], int(x[1])),
                raw_entity_table,
            )
            spawn_rates[floor] = list(entity_table)
        return spawn_rates

    def load_npcs(self) -> dict[str, Actor]:
        filename = "assets/data/entities/npcs.yml"
        npcs: dict[str, Actor] = {}
        return npcs

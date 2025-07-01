from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Callable

import yaml

from py_roguelike_tutorial.components.procgen_config import DungeonTable, EntityTableRow
from py_roguelike_tutorial.entity_deserializers import item_from_dict, actor_from_dict
from py_roguelike_tutorial.utils import assets_filepath

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Item, Actor

type SpawnRateTable = dict[int, list[tuple[str, int]]]


class DataLoader:
    @staticmethod
    def load_asset(filename: str):
        with open(assets_filepath(filename)) as file:
            return yaml.safe_load(file.read())

    @staticmethod
    def to_entities_or_fail[T](
        filename: str, data: dict, create_entity: Callable[[dict], T]
    ) -> dict[str, T]:
        # todo consider using pydantic for validation

        entities: dict[str, T] = {}
        erroneous_keys: list[str] = []
        for key, val in data.items():
            try:
                entities[key] = create_entity(val)
            except Exception:
                traceback.print_exc()
                erroneous_keys.append(key)
        if erroneous_keys:
            error_keys = ", ".join(erroneous_keys)
            raise SystemError(
                f"Error loading {filename}. Entity definitions malformed: {error_keys}"
            )
        return entities

    def load_item_drops_rates(self, item_prefabs: dict[str, Item]) -> DungeonTable:
        filename = "assets/data/tables/dungeon_item_drops.yml"
        item_drops_data: SpawnRateTable = self.load_asset(filename)
        item_chances: DungeonTable = {}
        for floor, entity_name_table in item_drops_data.items():
            entity_table = [
                EntityTableRow(item_prefabs[row[0]], row[1])
                for row in entity_name_table
            ]
            item_chances[floor] = list(entity_table)
        return item_chances

    def load_enemy_spawn_rates(self, npc_prefabs: dict[str, Actor]) -> DungeonTable:
        filename = "assets/data/tables/dungeon_enemy_spawns.yml"
        raw_spawn_rates_by_floor: SpawnRateTable = self.load_asset(filename)
        spawn_rates: DungeonTable = {}
        for floor, raw_entity_table in raw_spawn_rates_by_floor.items():
            entity_table = [
                EntityTableRow(npc_prefabs[row[0]], row[1]) for row in raw_entity_table
            ]
            spawn_rates[floor] = list(entity_table)
        return spawn_rates

    def load_item_entities(self) -> dict[str, Item]:
        filename = "assets/data/entities/items.yml"
        data: dict[str, dict] = self.load_asset(filename)
        entities = self.to_entities_or_fail(filename, data, item_from_dict)
        return entities

    def load_npcs_entities(self, item_entities: dict[str, Item]) -> dict[str, Actor]:
        filename = "assets/data/entities/npcs.yml"
        data: dict[str, dict] = self.load_asset(filename)
        partial_actor_from_dict = lambda val: actor_from_dict(val, item_entities)
        entities = self.to_entities_or_fail(filename, data, partial_actor_from_dict)
        return entities

    def load_player_entity(self, item_entities: dict[str, Item]) -> Actor:
        filename = "assets/data/entities/player.yml"
        data: dict[str, dict] = self.load_asset(filename)
        partial_actor_from_dict = lambda val: actor_from_dict(val, item_entities)
        entities = self.to_entities_or_fail(filename, data, partial_actor_from_dict)
        return entities["player"]

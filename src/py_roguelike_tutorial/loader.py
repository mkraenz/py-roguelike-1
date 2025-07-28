from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Callable, Any

import yaml
from pydantic import ValidationError

from py_roguelike_tutorial.behavior_trees.behavior_trees import BtNode
from py_roguelike_tutorial.components.faction import Faction
from py_roguelike_tutorial.procgen.procgen_config import DungeonTable, EntityTableRow
from py_roguelike_tutorial.entity_deserializers import (
    item_from_dict,
    actor_from_dict,
    behavior_tree_from_dict,
    prop_from_dict,
)
from py_roguelike_tutorial.utils import assets_filepath
from py_roguelike_tutorial.validators.actor_validator import ActorData
from py_roguelike_tutorial.behavior_trees.validators import BehaviorTreeData
from py_roguelike_tutorial.validators.faction_validator import FactionsData
from py_roguelike_tutorial.validators.item_validator import ItemData
from py_roguelike_tutorial.validators.prop_validator import PropData

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Item, Actor, Prop

type _SpawnRateTable = dict[int, list[tuple[str, int]]]


def _load_asset(filename: str):
    with open(assets_filepath(filename)) as file:
        return yaml.safe_load(file.read())


def _to_entities_or_fail[T, ValidatedData](
    filename: str,
    data: dict,
    validate: Callable[[Any], ValidatedData],
    create_entity: Callable[[ValidatedData, str], T],
) -> dict[str, T]:
    entities: dict[str, T] = {}
    erroneous_keys: list[str] = []
    for key, val in data.items():
        try:
            validated = validate(val)
            entities[key] = create_entity(validated, key)
        except ValidationError as e:
            traceback.print_exc()
            print(e.errors())
            erroneous_keys.append(key)
        except Exception:
            traceback.print_exc()
            erroneous_keys.append(key)
    if erroneous_keys:
        error_keys = ", ".join(erroneous_keys)
        raise SystemError(
            f"Error loading {filename}. Entity definitions malformed: {error_keys}"
        )
    return entities


def load_item_drops_rates(item_prefabs: dict[str, Item]) -> DungeonTable:
    filename = "assets/data/tables/dungeon_item_drops.yml"
    item_drops_data: _SpawnRateTable = _load_asset(filename)
    item_chances: DungeonTable = {}
    for floor, entity_name_table in item_drops_data.items():
        entity_table = [
            EntityTableRow(item_prefabs[row[0]], row[1]) for row in entity_name_table
        ]
        item_chances[floor] = list(entity_table)
    return item_chances


def load_enemy_spawn_rates(npc_prefabs: dict[str, Actor]) -> DungeonTable:
    filename = "assets/data/tables/dungeon_enemy_spawns.yml"
    raw_spawn_rates_by_floor: _SpawnRateTable = _load_asset(filename)
    spawn_rates: DungeonTable = {}
    for floor, raw_entity_table in raw_spawn_rates_by_floor.items():
        entity_table = [
            EntityTableRow(npc_prefabs[row[0]], row[1]) for row in raw_entity_table
        ]
        spawn_rates[floor] = list(entity_table)
    return spawn_rates


def load_item_entities() -> dict[str, Item]:
    filename = "assets/data/entities/items.yml"
    data: dict[str, dict] = _load_asset(filename)
    entities = _to_entities_or_fail(
        filename,
        data,
        create_entity=lambda val, key: item_from_dict(val),
        validate=lambda x: ItemData(**x),
    )
    return entities


def load_behavior_trees(behavior_tree_prefabs: dict) -> dict[str, BtNode]:
    filename = "assets/data/experiments/behavior_trees.yml"
    data: dict[str, dict] = _load_asset(filename)

    def create_behavior_tree_with_side_effects(val, key):
        tree = behavior_tree_from_dict(val)
        # FIXME: it would be nice if we can run this function side-effect free, postponing assignment to the prefabs.
        # The problem is that due to the Subtree node, we need the previously parsed behavior subtree prefab.
        # we could collect all of those in a temporary dict but haven't implemented yet.
        behavior_tree_prefabs[key] = tree
        return tree

    behavior_trees = _to_entities_or_fail(
        filename,
        data,
        create_entity=create_behavior_tree_with_side_effects,
        validate=lambda x: BehaviorTreeData(**x),
    )
    return behavior_trees


def load_npcs_entities(item_entities: dict[str, Item]) -> dict[str, Actor]:
    filename = "assets/data/entities/npcs.yml"
    data: dict[str, dict] = _load_asset(filename)
    partial_actor_from_dict = lambda val, key: actor_from_dict(val, item_entities)
    entities = _to_entities_or_fail(
        filename,
        data,
        create_entity=partial_actor_from_dict,
        validate=lambda x: ActorData(**x),
    )
    return entities


def load_props_entities(item_entities: dict[str, Item]) -> dict[str, Prop]:
    filename = "assets/data/entities/props.yml"
    data: dict[str, dict] = _load_asset(filename)
    partial_entity_from_dict = lambda val, key: prop_from_dict(val, item_entities)
    entities = _to_entities_or_fail(
        filename,
        data,
        create_entity=partial_entity_from_dict,
        validate=lambda x: PropData(**x),
    )
    return entities


def load_player_entity(item_entities: dict[str, Item]) -> Actor:
    filename = "assets/data/entities/player.yml"
    data: dict[str, dict] = _load_asset(filename)
    partial_actor_from_dict = lambda val, key: actor_from_dict(val, item_entities)
    entities = _to_entities_or_fail(
        filename,
        data,
        create_entity=partial_actor_from_dict,
        validate=lambda x: ActorData(**x),
    )
    return entities["player"]


def load_factions() -> dict[str, Faction]:
    filename = "assets/data/tables/factions.yml"
    data: dict[str, dict] = _load_asset(filename)
    factions_data = FactionsData(**data)
    factions = {
        id: Faction(id=id, name=faction.name)
        for (id, faction) in factions_data.factions.items()
    }
    return factions

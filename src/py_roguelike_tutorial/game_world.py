from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from py_roguelike_tutorial.components.factions_manager import FactionsManager
from py_roguelike_tutorial.procgen import generate_dungeon as generate_dungeon_default
from py_roguelike_tutorial.procgen_wang import generate_dungeon as generate_dungeon_wang

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine


class GameWorld:
    """Settings for the GameMap, and generates new maps when moving down the stairs."""

    _algorithm: Literal["wang", "default"] = "default"

    def __init__(
        self,
        *,
        engine: Engine,
        factions: FactionsManager,
        map_width: int,
        map_height: int,
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        current_floor: int = 0,
    ):
        self.engine = engine
        self.factions: FactionsManager = factions
        self.map_width = map_width
        self.map_height = map_height
        self.max_rooms = max_rooms
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size
        self.current_floor = current_floor

    def generate_floor(self) -> None:
        self.current_floor += 1
        if self._algorithm == "default":
            self.engine.game_map = generate_dungeon_default(
                factions=self.factions,
                max_rooms=self.max_rooms,
                room_min_size=self.room_min_size,
                room_max_size=self.room_max_size,
                map_width=self.map_width,
                map_height=self.map_height,
                engine=self.engine,
                current_floor=self.current_floor,
            )
        elif self._algorithm == "wang":
            self.engine.game_map = generate_dungeon_wang(
                engine=self.engine,
            )
        else:
            raise NotImplementedError(
                f"procgen algorithm not implemented. Found: {self._algorithm}"
            )

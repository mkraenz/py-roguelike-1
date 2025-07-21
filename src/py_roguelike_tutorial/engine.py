from __future__ import annotations
import lzma
import pickle
from typing import TYPE_CHECKING

import numpy as np
from tcod.console import Console
from tcod.map import compute_fov

from py_roguelike_tutorial import exceptions
from py_roguelike_tutorial.entity import Actor
from py_roguelike_tutorial.game_map import GameMap
from py_roguelike_tutorial.game_world import GameWorld
from py_roguelike_tutorial.message_log import MessageLog
from py_roguelike_tutorial.render_functions import (
    render_hp_bar,
    render_names_at,
    render_dungeon_level,
    render_xp,
)
from py_roguelike_tutorial.screen_stack import ScreenStack
from py_roguelike_tutorial.types import Coord

if TYPE_CHECKING:
    from py_roguelike_tutorial.event_bus import EventBus

_FOV_RADIUS = 8


class Engine:
    game_map: GameMap
    game_world: GameWorld
    np_rng: np.random.Generator

    def __init__(
        self,
        *,
        player: Actor,
        np_rng: np.random.Generator,
        stack: ScreenStack,
        event_bus: EventBus,
    ) -> None:
        self.message_log = MessageLog()
        self.mouse_location: Coord = (0, 0)
        self.player = player
        self.np_rng = np_rng
        self.stack = stack
        self.event_bus = event_bus

    def render(self, console: Console) -> None:
        self.game_map.render(console)
        self.message_log.render(console=console, x=21, y=45, width=40, height=5)
        stats = self.player.fighter
        render_hp_bar(console, stats.hp, stats.max_hp, 20)
        render_names_at(console=console, x=21, y=44, engine=self)
        render_xp(
            console=console,
            x=0,
            y=46,
            current_xp=self.player.level.current_xp,
            xp_needed=self.player.level.xp_to_next_level,
        )
        render_dungeon_level(
            console=console, x=0, y=47, dungeon_level=self.game_world.current_floor
        )

    def update_fov(self) -> None:
        """Recompute the visible area based on player's field of view."""
        self.game_map.visible[:] = compute_fov(
            transparency=self.game_map.tiles["transparent"],
            pov=self.player.pos,
            radius=_FOV_RADIUS,
        )
        # if a tile is visible, it should also be explored
        self.game_map.explored[:] |= self.game_map.visible

    def handle_npc_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # ignore impossible actions performed by the AI

    def save_to_file(self, filename: str) -> None:
        """Save this instance as compressed file.
        WARNING: Pickle may be used as an attack vector for arbitrary code execution,
        so never load other peoples' save files"""
        subscribers = self.event_bus._subscribers
        # pickle does not like stringifying callables inside of fields
        self.event_bus._subscribers = {}
        save_data = lzma.compress(pickle.dumps(self))
        # restoring subscribers in case the game continues
        self.event_bus._subscribers = subscribers
        with open(filename, "wb") as f:
            f.write(save_data)

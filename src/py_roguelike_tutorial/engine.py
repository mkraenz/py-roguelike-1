import random
from typing import Any, Iterable, Set

from tcod.console import Console
from tcod.context import Context
from tcod.map import compute_fov

from py_roguelike_tutorial.entity import Entity
from py_roguelike_tutorial.game_map import GameMap
from py_roguelike_tutorial.input_handlers import EventHandler


_FOV_RADIUS = 8


class Engine:
    game_map: GameMap

    def __init__(
        self,
        *,
        player: Entity,
    ) -> None:
        self.event_handler: EventHandler = EventHandler(self)
        self.player = player

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        context.present(console)
        console.clear()

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
        for entity in self.game_map.entities - {self.player}:
            print(f"{entity.name} wonders when it will get a real turn.")
            dx = random.randint(-1, 1)
            dy = random.randint(-1, 1)
            next_x, next_y = entity.x + dx, entity.y + dy
            if (
                self.game_map.in_bounds(next_x, next_y)
                and self.game_map.tiles["walkable"][next_x, next_y]
                and not self.game_map.get_blocking_entity_at(next_x, next_y)
            ):
                entity.move(dx, dy)

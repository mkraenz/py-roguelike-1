from typing import Any, Iterable, Set

from tcod.console import Console
from tcod.context import Context
from tcod.map import compute_fov

from py_roguelike_tutorial.entity import Entity
from py_roguelike_tutorial.game_map import GameMap
from py_roguelike_tutorial.input_handlers import EventHandler


_FOV_RADIUS = 8


class Engine:
    def __init__(
        self,
        *,
        entities: Set[Entity],
        event_handler: EventHandler,
        player: Entity,
        game_map: GameMap,
    ) -> None:
        self.entities = entities
        self.event_handler = event_handler
        self.player = player
        self.game_map = game_map
        self.update_fov()

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)
            if action is None:
                continue
            action.perform(self, self.player)
            self.update_fov()

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)
        for entity in self.entities:
            # only visible NPCs are drawn
            if self.game_map.visible[entity.pos]:
                console.print(entity.x, entity.y, entity.char, fg=entity.color)

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

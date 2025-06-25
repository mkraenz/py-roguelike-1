from tcod.console import Console
from tcod.context import Context
from tcod.map import compute_fov

from py_roguelike_tutorial.entity import Actor
from py_roguelike_tutorial.game_map import GameMap
from py_roguelike_tutorial.input_handlers import EventHandler

_FOV_RADIUS = 8


class Engine:
    game_map: GameMap

    def __init__(
        self,
        *,
        player: Actor,
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
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                entity.ai.perform()

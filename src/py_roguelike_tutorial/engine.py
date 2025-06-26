from pycparser.plyparser import Coord
from tcod.console import Console
from tcod.context import Context
from tcod.map import compute_fov

from py_roguelike_tutorial.colors import Theme
from py_roguelike_tutorial.entity import Actor
from py_roguelike_tutorial.game_map import GameMap
from py_roguelike_tutorial.input_handlers import EventHandler, MainGameEventHandler
from py_roguelike_tutorial.message_log import MessageLog
from py_roguelike_tutorial.render_functions import render_hp_bar, render_names_at

_FOV_RADIUS = 8

YOU_DIED = '''M""MMMM""M MMP"""""YMM M""MMMMM""M M""""""'YMM M""M MM""""""""`M M""""""'YMM 
M. `MM' .M M' .mmm. `M M  MMMMM  M M  mmmm. `M M  M MM  mmmmmmmM M  mmmm. `M 
MM.    .MM M  MMMMM  M M  MMMMM  M M  MMMMM  M M  M M`      MMMM M  MMMMM  M 
MMMb  dMMM M  MMMMM  M M  MMMMM  M M  MMMMM  M M  M MM  MMMMMMMM M  MMMMM  M 
MMMM  MMMM M. `MMM' .M M  `MMM'  M M  MMMM' .M M  M MM  MMMMMMMM M  MMMM' .M 
MMMM  MMMM MMb     dMM Mb       dM M       .MM M  M MM        .M M       .MM 
MMMMMMMMMM MMMMMMMMMMM MMMMMMMMMMM MMMMMMMMMMM MMMM MMMMMMMMMMMM MMMMMMMMMMM 
'''


class Engine:
    game_map: GameMap

    def __init__(
        self,
        *,
        player: Actor,
    ) -> None:
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log = MessageLog()
        self.mouse_location: Coord = (0, 0)
        self.player = player

    def render(self, console: Console) -> None:
        self.game_map.render(console)
        self.message_log.render(console=console, x=21, y=45, width=40, height=5)
        stats = self.player.fighter
        render_hp_bar(console, stats.hp, stats.max_hp, 20)
        if not self.player.is_alive:
            console.print(
                x=console.width // 2 - 76 // 2,
                y=console.height // 2 - 7 // 2 - 1,
                text=YOU_DIED,
                fg=Theme.you_died_text,
            )
        render_names_at(console=console, console_x=21, console_y=44, engine=self)


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

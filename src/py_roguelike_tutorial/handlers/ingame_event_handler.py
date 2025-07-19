from __future__ import annotations

from typing import TYPE_CHECKING

import tcod
from tcod.console import Console
from tcod.event import Quit

from py_roguelike_tutorial import exceptions
from py_roguelike_tutorial.actions import (
    Action,
)
from py_roguelike_tutorial.colors import Theme
from py_roguelike_tutorial.handlers.base_event_handler import (
    BaseEventHandler,
)

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine


class IngameEventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    @property
    def player(self):
        return self.engine.player

    def ev_quit(self, event: Quit):
        raise SystemExit()

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if not action_or_state:
            return self
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            if not self.player.is_alive:
                from py_roguelike_tutorial.handlers.game_over_event_handler import (
                    GameOverEventHandler,
                )

                return GameOverEventHandler(self.engine)
            if self.player.level.requires_level_up:
                from py_roguelike_tutorial.handlers.level_up_menu import LevelUpMenu

                return LevelUpMenu(self.engine)
            from py_roguelike_tutorial.handlers.main_game_event_handler import (
                MainGameEventHandler,
            )

            return (
                self
                if isinstance(self, MainGameEventHandler)
                else MainGameEventHandler(self.engine)
            )
        return self

    def handle_action(self, action: Action | None) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn."""
        if action is None:
            return False
        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add(text=exc.args[0], fg=Theme.impossible)
            return False
        self.engine.game_map.update_dijkstra_map()
        self.engine.handle_npc_turns()
        self.engine.update_fov()
        return True

    def on_render(self, console: Console, delta_time: float) -> None:
        self.engine.render(console)

    def ev_mousemotion(self, event: tcod.event.MouseMotion, /) -> None:
        if self.engine.game_map.in_bounds(int(event.position.x), int(event.position.y)):
            self.engine.mouse_location = int(event.position.x), int(event.position.y)

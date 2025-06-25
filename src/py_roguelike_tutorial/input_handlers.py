from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Any

from tcod.event import EventDispatch, KeyDown, wait
from tcod.event import KeySym as Key
from tcod.event import Quit

from py_roguelike_tutorial.actions import (
    Action,
    EscapeAction,
    BumpAction,
    WaitAction,
)

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine


class EventHandler(EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine

    def ev_quit(self, event: Quit) -> Action | None:
        raise SystemExit()

    """
    Like Godot's Input Map
    """

    def ev_keydown(self, event: KeyDown) -> Action | None:
        key = event.sym
        player = self.engine.player
        match key:
            case Key.W | Key.KP_8:
                return BumpAction(player, 0, -1)
            case Key.S | Key.KP_2:
                return BumpAction(player, 0, 1)
            case Key.A | Key.KP_4:
                return BumpAction(player, -1, 0)
            case Key.D | Key.KP_6:
                return BumpAction(player, 1, 0)
            case Key.Q | Key.KP_7:
                return BumpAction(player, -1, -1)
            case Key.E | Key.KP_9:
                return BumpAction(player, 1, -1)
            case Key.Z | Key.KP_1:
                return BumpAction(player, -1, 1)
            case Key.C | Key.KP_3:
                return BumpAction(player, 1, 1)
            case Key.PERIOD | Key.KP_5:
                return WaitAction(player)
            case Key.ESCAPE:
                return EscapeAction(player)
            case _:
                return None

    def handle_events(
        self,
    ) -> None:
        for event in wait():
            action = self.dispatch(event)
            if action is None:
                continue
            action.perform()
            self.engine.handle_npc_turns()
            self.engine.update_fov()

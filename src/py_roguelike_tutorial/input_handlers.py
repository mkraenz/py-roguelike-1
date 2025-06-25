from __future__ import annotations

from typing import TYPE_CHECKING

from tcod.event import EventDispatch, KeyDown, wait, T
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

_MOVE_KEYS = {
    # numpad
    Key.KP_1: (-1, 1),
    Key.KP_2: (0, 1),
    Key.KP_3: (1, 1),
    Key.KP_4: (-1, 0),
    Key.KP_6: (1, 0),
    Key.KP_7: (-1, -1),
    Key.KP_8: (0, -1),
    Key.KP_9: (1, -1),
    # wasd
    Key.Z: (-1, 1),
    Key.S: (0, 1),
    Key.C: (1, 1),
    Key.A: (-1, 0),
    Key.D: (1, 0),
    Key.Q: (-1, -1),
    Key.W: (0, -1),
    Key.E: (1, -1),
}

_WAIT_KEYS = {Key.KP_5, Key.PERIOD, Key.SPACE}


class EventHandler(EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine

    def ev_quit(self, event: Quit) -> Action | None:
        raise SystemExit()

    def handle_events(self) -> None:
        raise NotImplementedError()


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: KeyDown) -> Action | None:
        key = event.sym
        player = self.engine.player

        if key in _MOVE_KEYS:
            dx, dy = _MOVE_KEYS[key]
            return BumpAction(player, dx, dy)
        if key in _WAIT_KEYS:
            return WaitAction(player)
        match key:
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


class GameOverEventHandler(EventHandler):
    def handle_events(self) -> None:
        for event in wait():
            action = self.dispatch(event)
            if action is None:
                continue
            action.perform()

    def ev_keydown(self, event: KeyDown, /) -> Action | None:
        key = event.sym
        player = self.engine.player
        match key:
            case Key.ESCAPE:
                return EscapeAction(player)
            case _:
                return None

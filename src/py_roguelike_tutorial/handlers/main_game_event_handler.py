from __future__ import annotations

from typing import TYPE_CHECKING

from tcod.event import KeySym as Key, KeyDown

from py_roguelike_tutorial.actions import (
    EscapeAction,
    BumpAction,
    WaitAction,
    PickupAction,
    TakeStairsAction,
)
from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)
from py_roguelike_tutorial.handlers.ingame_event_handler import IngameEventHandler

if TYPE_CHECKING:
    pass

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
    Key.X: (1, 1),
    Key.A: (-1, 0),
    Key.D: (1, 0),
    Key.Q: (-1, -1),
    Key.W: (0, -1),
    Key.E: (1, -1),
}

_WAIT_KEYS = {Key.KP_5, Key.PERIOD, Key.SPACE}


_CONFIRM_KEYS = {
    Key.RETURN,
    Key.KP_ENTER,
}


class MainGameEventHandler(IngameEventHandler):
    def ev_keydown(self, event: KeyDown) -> ActionOrHandler | None:
        key = event.sym
        player = self.player

        match key:
            case _ if key in _MOVE_KEYS:
                dx, dy = _MOVE_KEYS[key]
                return BumpAction(player, dx, dy)
            case _ if key in _CONFIRM_KEYS:
                return TakeStairsAction(player)
            case _ if key in _WAIT_KEYS:
                return WaitAction(player)
            case Key.ESCAPE:
                return EscapeAction(player)
            case Key.V:
                from py_roguelike_tutorial.input_handlers import LogHistoryMenu

                return LogHistoryMenu(self.engine, MainGameEventHandler)
            case Key.I:
                from py_roguelike_tutorial.input_handlers import (
                    InventoryActivateHandler,
                )

                return InventoryActivateHandler(self.engine)
            case Key.P:
                from py_roguelike_tutorial.input_handlers import InventoryDropHandler

                return InventoryDropHandler(self.engine)
            case Key.C:
                from py_roguelike_tutorial.input_handlers import CharacterSheetMenu

                return CharacterSheetMenu(self.engine)
            case Key.G:
                return PickupAction(player)
            case Key.K:
                from py_roguelike_tutorial.input_handlers import LookAroundHandler

                return LookAroundHandler(self.engine)
            case _:
                return None

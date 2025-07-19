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
from py_roguelike_tutorial.handlers.character_sheet_menu import CharacterSheetMenu
from py_roguelike_tutorial.handlers.ingame_event_handler import IngameEventHandler
from py_roguelike_tutorial.handlers.inventory_activate_handler import (
    InventoryActivateHandler,
)
from py_roguelike_tutorial.handlers.inventory_drop_handler import InventoryDropHandler
from py_roguelike_tutorial.handlers.key_map import CONFIRM_KEYS, MOVE_KEYS, WAIT_KEYS
from py_roguelike_tutorial.handlers.log_history_menu import LogHistoryMenu

if TYPE_CHECKING:
    pass


class MainGameEventHandler(IngameEventHandler):
    def ev_keydown(self, event: KeyDown) -> ActionOrHandler | None:
        key = event.sym
        player = self.player

        match key:
            case _ if key in MOVE_KEYS:
                dx, dy = MOVE_KEYS[key]
                return BumpAction(player, dx, dy)
            case _ if key in CONFIRM_KEYS:
                return TakeStairsAction(player)
            case _ if key in WAIT_KEYS:
                return WaitAction(player)
            case Key.ESCAPE:
                return EscapeAction(player)
            case Key.V:
                return LogHistoryMenu(self.engine)
            case Key.I:
                return InventoryActivateHandler(self.engine)
            case Key.P:
                return InventoryDropHandler(self.engine)
            case Key.C:
                return CharacterSheetMenu(self.engine)
            case Key.G:
                return PickupAction(player)
            case Key.K:
                from py_roguelike_tutorial.handlers.look_around_handler import (
                    LookAroundHandler,
                )

                return LookAroundHandler(self.engine)
            case _:
                return None

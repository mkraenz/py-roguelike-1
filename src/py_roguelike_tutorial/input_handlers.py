from __future__ import annotations

from typing import TYPE_CHECKING

import tcod.context
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

_CURSOR_Y_KEYS = {
    Key.UP: -1,
    Key.DOWN: 1,
    Key.PAGEUP: -10,
    Key.PAGEDOWN: 10,
}


class EventHandler(EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine

    def ev_quit(self, event: Quit) -> Action | None:
        raise SystemExit()

    def handle_events(self, context: tcod.context.Context) -> None:
        for event in wait():
            context.convert_event(event)
            self.dispatch(event)

    def on_render(self, console: tcod.console.Console) -> None:
        self.engine.render(console)

    def ev_mousemotion(self, event: tcod.event.MouseMotion, /) -> None:
        if self.engine.game_map.in_bounds(int(event.tile.x), int(event.tile.y)):
            self.engine.mouse_location = int(event.tile.x), int(event.tile.y)


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: KeyDown) -> Action | None:
        key = event.sym
        player = self.engine.player

        match key:
            case _ if key in _MOVE_KEYS:
                dx, dy = _MOVE_KEYS[key]
                return BumpAction(player, dx, dy)
            case _ if key in _WAIT_KEYS:
                return WaitAction(player)
            case Key.ESCAPE:
                return EscapeAction(player)
            case Key.V:
                self.engine.event_handler = LogHistoryViewer(
                    self.engine, MainGameEventHandler
                )
                return
            case _:
                return None

    def handle_events(self, context: tcod.context.Context) -> None:
        for event in wait():
            context.convert_event(event)
            action = self.dispatch(event)
            if action is None:
                continue
            action.perform()
            self.engine.handle_npc_turns()
            self.engine.update_fov()


class GameOverEventHandler(EventHandler):
    def handle_events(self, context: tcod.context.Context) -> None:
        for event in wait():
            context.convert_event(event)
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
            case Key.V:
                self.engine.event_handler = LogHistoryViewer(
                    self.engine, GameOverEventHandler
                )
                return
            case _:
                return None


class LogHistoryViewer(EventHandler):
    """Print the history on a larger window which can be scrolled."""

    def __init__(self, engine: Engine, on_back_cls):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1
        self.on_back_cls = on_back_cls

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)  # draw main state as background

        log_console = tcod.console.Console(console.width - 6, console.height - 6)
        log_console.draw_frame(
            0, 0, log_console.width, log_console.height
        )  # screen border
        heading = "┤Message history├"
        log_console.print_box(
            x=0,
            y=0,
            width=log_console.width,
            height=1,
            alignment=tcod.tcod.constants.CENTER,
            string=heading,
        )

        self.engine.message_log.render_messages(
            log_console,
            x=1,
            y=1,
            width=log_console.width - 2,
            height=log_console.height - 2,
            messages=self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> None:
        end = self.log_length - 1
        match event.sym:
            case _ if event.sym in _CURSOR_Y_KEYS:
                adjust = _CURSOR_Y_KEYS[event.sym]
                match adjust:
                    case _ if adjust < 0 and self.cursor == 0:
                        # we wrap around to the bottom if we are at the top and continue going upwards
                        self.cursor = end
                    case _ if adjust > 0 and self.cursor == end:
                        # conversely, we wrap around to the top if we are at the bottom and continue going downwards
                        self.cursor = 0
                    case _:
                        self.cursor = max(0, min(self.cursor + adjust, end))
            case Key.HOME:
                self.cursor = 0  # move to first message
            case Key.END:
                self.cursor = end  # move to last message
            case _:  # if no key matches, return to the main game
                self.engine.event_handler = self.on_back_cls(self.engine)

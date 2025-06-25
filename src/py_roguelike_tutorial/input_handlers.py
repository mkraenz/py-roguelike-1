from tcod.event import EventDispatch, KeyDown
from tcod.event import KeySym as Key
from tcod.event import Quit

from py_roguelike_tutorial.actions import (
    Action,
    EscapeAction,
    BumpAction,
    WaitAction,
)


class EventHandler(EventDispatch[Action]):
    def ev_quit(self, event: Quit) -> Action | None:
        raise SystemExit()

    """
    Like Godot's Input Map
    """

    def ev_keydown(self, event: KeyDown) -> Action | None:
        key = event.sym
        match key:
            case Key.UP | Key.W | Key.KP_8:
                return BumpAction(0, -1)
            case Key.DOWN | Key.S | Key.KP_2:
                return BumpAction(0, 1)
            case Key.LEFT | Key.A | Key.KP_4:
                return BumpAction(-1, 0)
            case Key.RIGHT | Key.D | Key.KP_6:
                return BumpAction(1, 0)
            case Key.PERIOD | Key.KP_5:
                return WaitAction()
            case Key.ESCAPE:
                return EscapeAction()
            case _:
                return None

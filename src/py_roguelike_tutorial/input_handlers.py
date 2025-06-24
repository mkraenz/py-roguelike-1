from tcod.event import EventDispatch, KeyDown
from tcod.event import KeySym as Key
from tcod.event import Quit

from py_roguelike_tutorial.actions import Action, EscapeAction, MoveAction


class EventHandler(EventDispatch[Action]):
    def ev_quit(self, event: Quit) -> Action | None:
        raise SystemExit()

    """
    Like Godot's Input Map
    """

    def ev_keydown(self, event: KeyDown) -> Action | None:
        key = event.sym
        match key:
            case Key.UP | Key.W:
                return MoveAction(0, -1)
            case Key.DOWN | Key.S:
                return MoveAction(0, 1)
            case Key.LEFT | Key.A:
                return MoveAction(-1, 0)
            case Key.RIGHT | Key.D:
                return MoveAction(1, 0)
            case Key.ESCAPE:
                return EscapeAction()
            case _:
                return None

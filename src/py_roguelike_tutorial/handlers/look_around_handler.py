from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
)
from py_roguelike_tutorial.handlers.select_index_handler import SelectIndexHandler


class LookAroundHandler(SelectIndexHandler):
    """Lets the player look around with the keyboard."""

    def on_index_selected(self, x: int, y: int) -> ActionOrHandler | None:
        self.engine.stack.pop()
        return None

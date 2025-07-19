from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from py_roguelike_tutorial.input_handlers import BaseEventHandler


class ScreenStack:
    def __init__(self):
        self.items: list[BaseEventHandler] = (
            []
        )  # Initialize an empty list to store stack elements

    def push(self, item: BaseEventHandler):
        """Add an item to the top of the stack."""
        self.items.append(item)

    def pop(self):
        """Remove and return the item from the top of the stack."""
        if not self.is_empty():
            return self.items.pop()
        raise IndexError("Pop from an empty stack")

    def peek(self):
        """Return the item at the top of the stack without removing it."""
        if not self.is_empty():
            return self.items[-1]
        raise IndexError("Peek from an empty stack")

    def is_empty(self):
        """Check if the stack is empty."""
        return len(self.items) == 0

    def size(self):
        """Return the number of items in the stack."""
        return len(self.items)

from __future__ import annotations
from typing import TYPE_CHECKING
import uuid


if TYPE_CHECKING:
    from py_roguelike_tutorial.handlers.base_event_handler import BaseEventHandler


class ScreenStack:
    def __init__(self):
        self.items: list[BaseEventHandler] = (
            []
        )  # Initialize an empty list to store stack elements
        self.debug = True
        self.id = uuid.uuid4()

    def push(self, item: BaseEventHandler):
        """Add an item to the top of the stack."""
        self.items.append(item)
        if self.debug:
            print(f"Pushed {item}. stack_size:{self.size()}, {self.id}")

    def clear(self):
        """Clear the stack."""
        self.items.clear()
        if self.debug:
            print(f"Cleared stack. stack_size:{self.size()}")

    def pop(self):
        """Remove and return the item from the top of the stack."""
        if not self.is_empty():
            item = self.items.pop()
            if self.debug:
                print(f"Popped {item}. stack_size:{self.size()}, {self.id}")
            return item
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

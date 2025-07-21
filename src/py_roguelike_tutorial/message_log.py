import textwrap
from typing import Reversible, Iterable

import tcod

from py_roguelike_tutorial.constants import Theme
from py_roguelike_tutorial.types import Rgb


class Message:
    def __init__(self, text: str, fg: Rgb):
        self.plain_text = text
        self.fg = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        """Full text of this message, including the count if necessary."""
        if self.count > 1:
            return f"{self.plain_text} (x{self.count})"
        return self.plain_text


class MessageLog:
    def __init__(self):
        self.messages: list[Message] = []

    def add(
        self, text: str, fg: Rgb = Theme.log_message, *, stacking: bool = True
    ) -> None:
        """Add a message to the log.
        If `stack` is True, then the message can stack with a previous message of the same text.
        """
        if stacking and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            message = Message(text, fg)
            self.messages.append(message)

    def render(
        self, console: tcod.console.Console, x: int, y: int, width: int, height: int
    ) -> None:
        """Render the log over the given area."""
        self.render_messages(console, x, y, width, height, self.messages)

    @staticmethod
    def wrap(string: str, width: int) -> Iterable[str]:
        """Return a wrapped text message."""
        for line in string.splitlines():
            yield from textwrap.wrap(text=line, width=width, expand_tabs=True)

    @classmethod
    def render_messages(
        cls,
        console: tcod.console.Console,
        x: int,
        y: int,
        width: int,
        height: int,
        messages: Reversible[Message],
    ):
        """Render the messages in last-message-comes-first order."""
        y_offset = height - 1
        for message in reversed(messages):
            for line in reversed(list(cls.wrap(message.full_text, width))):
                console.print(x=x, y=y + y_offset, text=line, fg=message.fg)
                y_offset -= 1
                if y_offset < 0:
                    return

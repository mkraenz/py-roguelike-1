from __future__ import annotations

import os.path
from typing import TYPE_CHECKING, Callable, Type

import tcod
from tcod.console import Console
from tcod.event import KeySym as Key, Quit, KeyDown, Modifier

from py_roguelike_tutorial import setup_game
from py_roguelike_tutorial.actions import (
    Action,
    DropItemAction,
    EquipAction,
)
from py_roguelike_tutorial.colors import Theme, Color
from py_roguelike_tutorial.constants import AUTOSAVE_FILENAME
from py_roguelike_tutorial.exceptions import QuitWithoutSaving
from py_roguelike_tutorial.handlers.base_event_handler import (
    ActionOrHandler,
    BaseEventHandler,
)
from py_roguelike_tutorial.handlers.ingame_event_handler import IngameEventHandler
from py_roguelike_tutorial.handlers.main_game_event_handler import MainGameEventHandler
from py_roguelike_tutorial.render_functions import (
    print_aligned_texts_center,
    render_you_died,
    dim_console,
    print_text_center,
    IngameMenuConsole,
)
from py_roguelike_tutorial.screen_stack import ScreenStack
from py_roguelike_tutorial.types import Coord

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Item


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

_CURSOR_Y_KEYS = {
    Key.UP: -1,
    Key.DOWN: 1,
    Key.PAGEUP: -10,
    Key.PAGEDOWN: 10,
}

_MODIFIER_KEYS = {
    Key.LSHIFT,
    Key.RSHIFT,
    Key.LCTRL,
    Key.RCTRL,
    Key.LALT,
    Key.RALT,
}

_CONFIRM_KEYS = {
    Key.RETURN,
    Key.KP_ENTER,
}


class GameOverEventHandler(IngameEventHandler):

    def on_render(self, console: Console, delta_time: float) -> None:
        super().on_render(console, delta_time)
        dim_console(console)
        render_you_died(console, 2, console.height // 2 - 7 // 2 - 1)
        texts = ["[F] Back to title menu", "[V] View combat log"]
        print_aligned_texts_center(console, texts, console.height // 2 + 10)

    def ev_keydown(self, event: KeyDown, /) -> ActionOrHandler | None:
        key = event.sym
        match key:
            case Key.ESCAPE | Key.F:
                return self.on_confirm()
            case _ if key in _CONFIRM_KEYS:
                return self.on_confirm()
            case Key.V:
                return LogHistoryMenu(self.engine, GameOverEventHandler)
            case _:
                return None

    def on_confirm(self) -> None | ActionOrHandler:
        self.engine.stack.pop()
        return setup_game.MainMenu(self.engine.stack)

    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists(AUTOSAVE_FILENAME):
            os.remove(AUTOSAVE_FILENAME)  # permadeath, baby
        raise QuitWithoutSaving()

    # compiler is not clever enough to notice that on_quit raises an exception...
    def ev_quit(self, event: Quit):  # type: ignore [reportIncompatibleMethodOverride]
        self.on_quit()


class LevelUpMenu(IngameEventHandler):
    def on_render(self, console: Console, delta_time: float) -> None:
        title = "New Level"
        super().on_render(console, delta_time)
        child_console, blit = IngameMenuConsole(console, title)

        stats = self.player.fighter
        texts = [
            "Select an attribute to increase.",
            "",
            f"[S] Strength (+1 attack, from {stats.power}",
            f"[A] Agility (+1 defense, from {stats.defense})",
            f"[C] Constitution (+20 HP, from {stats.max_hp})",
        ]
        print_aligned_texts_center(child_console, texts, child_console.height // 2 - 6)
        blit()

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        """User cannot exit the menu without selecting an option."""
        key = event.sym

        def on_confirm(cb: Callable[[], None]):
            def inner():
                cb()
                if self.player.level.requires_level_up:
                    return self
                self.engine.stack.pop()
                # Todo This needs some more
                return MainGameEventHandler(self.engine)

            return inner

        match key:
            case Key.S:
                return ConfirmationPopup(
                    self.engine.stack,
                    "Increase strength?",
                    callback=on_confirm(self.player.level.increase_power),
                )
            case Key.A:
                return ConfirmationPopup(
                    self.engine.stack,
                    "Increase agility?",
                    callback=on_confirm(self.player.level.increase_defense),
                )
            case Key.C:
                return ConfirmationPopup(
                    self.engine.stack,
                    "Increase constitution?",
                    callback=on_confirm(self.player.level.increase_max_hp),
                )
            case _:
                pass
        # there may be multiple level ups at once necessary, e.g. if the player killed a super high-EXP boss
        if not self.player.level.requires_level_up:
            self.engine.stack.pop()
            return None
        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown, /
    ) -> ActionOrHandler | None:
        """Forbid exiting the menu on mouse click."""
        return None


class CharacterSheetMenu(IngameEventHandler):
    def on_render(self, console: Console, delta_time: float) -> None:
        super().on_render(console, delta_time)  # draw main state as background
        child_console, blit = IngameMenuConsole(console, "Character Details")

        p = self.player
        texts = [
            f"Health:     {p.fighter.hp}/{p.fighter.max_hp} HP",
            "",
            "" f"Level:      {p.level.current_level}",
            f"Experience: {p.level.current_xp}/{p.level.xp_to_next_level} EXP",
            "",
            "" f"Strength:   {p.fighter.power}",
            f"Agility:    {p.fighter.defense}",
        ]

        print_aligned_texts_center(child_console, texts, console.height // 2 + -4)
        blit()

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        self.engine.stack.pop()
        return None


class RangedAttackHandler(IngameEventHandler):
    def __init__(
        self,
        engine: Engine,
        from_pos: Coord,
        to: Coord,
        animation_tick_time_sec: float = 0.1,
    ):
        super().__init__(engine)
        self.animation_tick_time_sec = animation_tick_time_sec
        self.elapsed: float = 0

        self.path = tcod.los.bresenham(from_pos, to)

    def on_render(self, console: Console, delta_time: float) -> None:

        super().on_render(console, delta_time)
        self.elapsed += delta_time
        ticks = int(self.elapsed / self.animation_tick_time_sec)
        if ticks >= len(self.path):
            self.engine.stack.pop()
            return
        pos = self.path[ticks] if ticks < len(self.path) else self.path[-1]
        child_console = Console(console.width, console.height)
        child_console.print(x=pos[0], y=pos[1], fg=Color.WHITE, text="x")
        child_console.blit(console, bg_alpha=0)

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        return None  # no key input while the animation is running for the time being. Maybe allow skipping


class LogHistoryMenu(IngameEventHandler):
    """Print the history on a larger window which can be scrolled."""

    def __init__(self, engine: Engine, on_back_cls: Type[IngameEventHandler]):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1
        self.on_back_cls = on_back_cls

    def on_render(self, console: Console, delta_time: float) -> None:
        super().on_render(console, delta_time)

        child_console, blit = IngameMenuConsole(console, "Message History")

        self.engine.message_log.render_messages(
            child_console,
            x=1,
            y=1,
            width=child_console.width - 2,
            height=child_console.height - 2,
            messages=self.engine.message_log.messages[: self.cursor + 1],
        )
        blit()

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
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
                self.engine.stack.pop()
                return None
        return None


class AskUserEventHandler(IngameEventHandler):
    """Handles user input for actions that require some special input."""

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        """By default, any unhandled key cancels the menu."""
        key = event.sym
        match key:
            case _ if key in _MODIFIER_KEYS:
                return None  # ignore modifiers
            case _:
                return self.on_exit()

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown, /
    ) -> ActionOrHandler | None:
        """By default, any mouse click exists the menu."""
        self.engine.stack.pop()
        return None

    def on_exit(self) -> ActionOrHandler | None:
        """Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        self.engine.stack.pop()
        return None


class InventoryEventHandler(AskUserEventHandler):
    """Let the user select items. Details are defined in the subclasses."""

    TITLE = "<missing title>"

    def on_render(self, console: Console, delta_time: float) -> None:
        super().on_render(console, delta_time)
        player = self.player
        carried_items = player.inventory.len
        height = max(carried_items + 2, 3)
        x = (
            0 if player.x > 30 else 40
        )  # render left or right of the player, wherever there's enough space
        y = 0
        width = len(self.TITLE) + 10

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            fg=Color.WHITE,
            bg=Color.BLACK,
            clear=True,
        )
        console.print(
            x=x + 1,
            y=y,
            width=width,
            height=height,
            fg=Color.WHITE,
            bg=Color.BLACK,
            text=f"┤{self.TITLE}├",
        )

        if carried_items > 0:
            for i, item in enumerate(player.inventory.items):
                item_key = chr(ord("a") + i)
                item_equipped = " (E)" if player.equipment.is_equipped(item) else ""
                item_charges = (
                    f" ({item.consumable.charges}Chg)"
                    if item.consumable is not None and item.consumable.charges > 1
                    else ""
                )
                console.print(
                    x=x + 1,
                    y=y + i + 1,
                    width=width,
                    height=height,
                    text=f"[{item_key}] {item.name}{item_equipped}{item_charges}",
                )
        else:
            console.print(x=x + 1, y=y + 1, width=width, height=height, text="(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        player = self.player
        key = event.sym
        index = key - Key.A
        carried_items = player.inventory.len

        if 0 <= index < carried_items:
            selected_item = player.inventory.get(index)
            if not selected_item:
                self.engine.message_log.add("Invalid entry.", Theme.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, selected_item: Item) -> ActionOrHandler | None:
        """Called when the user selects an item."""
        raise NotImplementedError("Must be implemented by subclass.")


class InventoryActivateHandler(InventoryEventHandler):
    TITLE = "Select an item to use"

    def on_item_selected(self, selected_item: Item) -> ActionOrHandler | None:
        if selected_item.consumable:
            self.engine.stack.pop()
            return selected_item.consumable.get_action(self.player)
        if selected_item.equippable:
            self.engine.stack.pop()
            return EquipAction(self.player, selected_item)
        return None


class InventoryDropHandler(InventoryEventHandler):
    TITLE = "Select an item to drop"

    def on_item_selected(self, selected_item: Item) -> ActionOrHandler | None:
        return DropItemAction(self.player, selected_item)


class SelectIndexHandler(AskUserEventHandler):
    """Asks the user for an index on the map."""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player on construction."""
        super().__init__(engine)
        engine.mouse_location = self.player.x, self.player.y

    def on_render(self, console: Console, delta_time: float) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console, delta_time)
        x, y = self.engine.mouse_location
        console.rgb["bg"][x, y] = Color.WHITE
        console.rgb["fg"][x, y] = Color.BLACK

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        """Check for key movement or confirmation keys."""
        key = event.sym
        x, y = self.engine.mouse_location
        match key:
            case _ if key in _MOVE_KEYS:
                # holding modifier keys will speed up movement, e.g. 5 tiles at a time when holding shift.
                modifier = 1
                if event.mod & (Modifier.LSHIFT | Modifier.RSHIFT):
                    modifier *= 5
                if event.mod & (Modifier.LCTRL | Modifier.RCTRL):
                    modifier *= 10
                if event.mod & (Modifier.LALT | Modifier.RALT):
                    modifier *= 20

                dx, dy = _MOVE_KEYS[key]
                x += dx * modifier
                y += dy * modifier
                # cursor should not leave the map, thus clamp
                x = max(0, min(x, self.engine.game_map.width - 1))
                y = max(0, min(y, self.engine.game_map.height - 1))
                self.engine.mouse_location = x, y
                return None
            case _ if key in _CONFIRM_KEYS:
                return self.on_index_selected(x, y)
            case _:
                return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown, /
    ) -> ActionOrHandler | None:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(int(event.position.x), int(event.position.y)):
            if event.button == 1:
                return self.on_index_selected(
                    int(event.position.x), int(event.position.y)
                )
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> ActionOrHandler | None:
        """Called when a tile index is selected."""
        raise NotImplementedError("Must be implemented by subclass.")


class LookAroundHandler(SelectIndexHandler):
    """Lets the player look around with the keyboard."""

    def on_index_selected(self, x: int, y: int) -> ActionOrHandler | None:
        self.engine.stack.pop()
        return None


class SingleRangedAttackHandler(SelectIndexHandler):
    """Targets a single enemy."""

    def __init__(self, engine: Engine, callback: Callable[[Coord], Action | None]):
        super().__init__(engine)
        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Action | None:
        self.engine.stack.pop()
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """Targets an area."""

    def __init__(
        self, engine: Engine, radius: int, callback: Callable[[Coord], Action | None]
    ):
        super().__init__(engine)
        self.callback = callback
        self.radius = radius

    def on_render(self, console: Console, delta_time: float) -> None:
        """Highlight the area around the cursor"""
        super().on_render(console, delta_time)

        cursor_x, cursor_y = self.engine.mouse_location
        # enemies on the border will not be included in the radius
        console.draw_frame(
            x=cursor_x - self.radius - 1,
            y=cursor_y - self.radius - 1,
            width=(self.radius + 1) * 2 + 1,
            height=(self.radius + 1) * 2 + 1,
            fg=Theme.cursor_aoe,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Action | None:
        self.engine.stack.pop()
        return self.callback((x, y))


class PopupMessage(BaseEventHandler):
    """Displays a popup window. Hands back control to the `parent_handler`
    (typically, the previous screen) on any key stroke."""

    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: Console, delta_time: float) -> None:
        self.parent.on_render(console, delta_time)  # in background, display the parent
        dim_console(console)
        print_text_center(console, self.text, console.height // 2)

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        return self.parent


class ConfirmationPopup(BaseEventHandler):
    """A popup window asking for confirmation.
    On [Y], calls the callback. Else hands back control to the parent."""

    def __init__(
        self,
        stack: ScreenStack,
        text: str,
        callback: Callable[[], BaseEventHandler],
    ):
        self.text = text
        self.callback = callback
        self.stack = stack

    def on_render(self, console: Console, delta_time: float) -> None:
        dim_console(console)

        texts = [self.text, "", "[Y] Confirm", "[*] Cancel"]
        print_aligned_texts_center(console, texts, console.height // 2 - 2)

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        key = event.sym
        self.stack.pop()
        match key:
            case Key.Y:
                return self.callback()
            case _:
                return None

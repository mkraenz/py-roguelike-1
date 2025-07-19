from __future__ import annotations

import os.path
import sys
import time
from typing import TYPE_CHECKING, Callable, Type

import tcod
from tcod.console import Console
from tcod.event import KeySym as Key, Quit, EventDispatch, KeyDown, Modifier

from py_roguelike_tutorial import exceptions, setup_game
from py_roguelike_tutorial.actions import (
    Action,
    EscapeAction,
    BumpAction,
    WaitAction,
    PickupAction,
    DropItemAction,
    TakeStairsAction,
    EquipAction,
)
from py_roguelike_tutorial.colors import Theme, Color
from py_roguelike_tutorial.constants import AUTOSAVE_FILENAME
from py_roguelike_tutorial.exceptions import QuitWithoutSaving
from py_roguelike_tutorial.render_functions import (
    print_aligned_texts_center,
    render_you_died,
    dim_console,
    print_text_center,
    IngameMenuConsole,
)
from py_roguelike_tutorial.types import Coord

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Item

# nuitka really didn't like the version without quotes around the type bc BaseEventHandler is not yet defined (which in turn depends on ActionOrHandler). But this finally works!
type ActionOrHandler = "Action | BaseEventHandler"

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

"""An event handler return type which can trigger an action or switch active event handlers.

If a handler is returned, then it will become the active event handler for future events.
If an action is returned, then it will be attempted and if it is valid, 
then MainGameEventHandler will become the active handler
"""


class BaseEventHandler(EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} cannot handle actions."
        return self

    def on_render(self, console: Console, delta_time: float) -> None:
        raise NotImplementedError("Must be implemented in subclass.")

    def ev_quit(self, event: tcod.event.Quit, /):
        sys.exit()


class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    @property
    def player(self):
        return self.engine.player

    def ev_quit(self, event: Quit):
        raise SystemExit()

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if not action_or_state:
            return self
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        #
        if self.handle_action(action_or_state):
            if not self.player.is_alive:
                return GameOverEventHandler(self.engine)
            if self.player.level.requires_level_up:
                return LevelUpMenu(self.engine)
            return MainGameEventHandler(self.engine)
        return self

    def handle_action(self, action: Action | None) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn."""
        if action is None:
            return False
        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add(text=exc.args[0], fg=Theme.impossible)
            return False
        self.engine.game_map.update_dijkstra_map()
        self.engine.handle_npc_turns()
        self.engine.update_fov()
        return True

    def on_render(self, console: Console, delta_time: float) -> None:
        self.engine.render(console)

    def ev_mousemotion(self, event: tcod.event.MouseMotion, /) -> None:
        if self.engine.game_map.in_bounds(int(event.position.x), int(event.position.y)):
            self.engine.mouse_location = int(event.position.x), int(event.position.y)


class MainGameEventHandler(EventHandler):
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
                return RangedAttackHandler(self.engine, (0, 0), (100, 100))
                # return LogHistoryMenu(self.engine, MainGameEventHandler)
            case Key.I:
                return InventoryActivateHandler(self.engine)
            case Key.P:
                return InventoryDropHandler(self.engine)
            case Key.C:
                return CharacterSheetMenu(self.engine)
            case Key.G:
                return PickupAction(player)
            case Key.K:
                return LookAroundHandler(self.engine)
            case _:
                return None


class GameOverEventHandler(EventHandler):

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
        return setup_game.MainMenu()

    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists(AUTOSAVE_FILENAME):
            os.remove(AUTOSAVE_FILENAME)  # permadeath, baby
        raise QuitWithoutSaving()

    # compiler is not clever enough to notice that on_quit raises an exception...
    def ev_quit(self, event: Quit):  # type: ignore [reportIncompatibleMethodOverride]
        self.on_quit()


class LevelUpMenu(EventHandler):
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
                return (
                    MainGameEventHandler(self.engine)
                    if not self.player.level.requires_level_up
                    else self
                )

            return inner

        match key:
            case Key.S:
                return ConfirmationPopup(
                    self,
                    "Increase strength?",
                    callback=on_confirm(self.player.level.increase_power),
                )
            case Key.A:
                return ConfirmationPopup(
                    self,
                    "Increase agility?",
                    callback=on_confirm(self.player.level.increase_defense),
                )
            case Key.C:
                return ConfirmationPopup(
                    self,
                    "Increase constitution?",
                    callback=on_confirm(self.player.level.increase_max_hp),
                )
            case _:
                pass
        # there may be multiple level ups at once necessary, e.g. if the player killed a super high-EXP boss
        if not self.player.level.requires_level_up:
            return MainGameEventHandler(self.engine)
        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown, /
    ) -> ActionOrHandler | None:
        """Forbid exiting the menu on mouse click."""
        return None


class CharacterSheetMenu(EventHandler):
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
        return MainGameEventHandler(self.engine)


class RangedAttackHandler(EventHandler):
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
        self.elapsed += delta_time
        ticks = int(self.elapsed / self.animation_tick_time_sec)
        pos = self.path[ticks] if ticks < len(self.path) else self.path[-1]
        print(pos)
        child_console = Console(console.width, console.height)
        child_console.print(
            x=pos[0], y=pos[1], fg=Color.WHITE, bg=Color.WHITE, text="x"
        )
        child_console.blit(console)

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        return MainGameEventHandler(self.engine)


class LogHistoryMenu(EventHandler):
    """Print the history on a larger window which can be scrolled."""

    def __init__(self, engine: Engine, on_back_cls: Type[EventHandler]):
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
                return self.on_back_cls(self.engine)
        return None


class AskUserEventHandler(EventHandler):
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
        return MainGameEventHandler(self.engine)

    def on_exit(self) -> ActionOrHandler | None:
        """Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        return MainGameEventHandler(self.engine)


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
            return selected_item.consumable.get_action(self.player)
        if selected_item.equippable:
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
        return MainGameEventHandler(self.engine)


class SingleRangedAttackHandler(SelectIndexHandler):
    """Targets a single enemy."""

    def __init__(self, engine: Engine, callback: Callable[[Coord], Action | None]):
        super().__init__(engine)
        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Action | None:
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
        parent_handler: BaseEventHandler,
        text: str,
        callback: Callable[[], BaseEventHandler],
    ):
        self.parent = parent_handler
        self.text = text
        self.callback = callback

    def on_render(self, console: Console, delta_time: float) -> None:
        self.parent.on_render(console, delta_time)
        dim_console(console)

        texts = [self.text, "", "[Y] Confirm", "[*] Cancel"]
        print_aligned_texts_center(console, texts, console.height // 2 - 2)

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> ActionOrHandler | None:
        key = event.sym
        match key:
            case Key.Y:
                return self.callback()
            case _:
                return self.parent

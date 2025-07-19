import lzma
import os
import pickle
import sys
import traceback

import numpy as np
import tcod
from tcod.console import Console
from tcod.constants import CENTER
from tcod.event import KeySym as Key
from tcod.libtcodpy import BKGND_ALPHA

from py_roguelike_tutorial.colors import Theme
from py_roguelike_tutorial.components.factions_manager import FactionsManager
from py_roguelike_tutorial.constants import AUTOSAVE_FILENAME, RNG_SEED
from py_roguelike_tutorial.engine import Engine
from py_roguelike_tutorial.entity_factory import EntityPrefabs
from py_roguelike_tutorial.game_world import GameWorld
from py_roguelike_tutorial.handlers.base_event_handler import BaseEventHandler
from py_roguelike_tutorial.handlers.confirmation_popup import ConfirmationPopup
from py_roguelike_tutorial.handlers.main_game_event_handler import MainGameEventHandler
from py_roguelike_tutorial.handlers.popup_message import PopupMessage
from py_roguelike_tutorial.screen_stack import ScreenStack
from py_roguelike_tutorial.utils import assets_filepath

filepath = assets_filepath("assets/menu_background.png")
background_image = tcod.image.load(filepath)[:, :, :3]  # type: ignore [reportDeprecated]


def new_game(stack: ScreenStack) -> Engine:
    map_width = 80
    map_height = 43
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    player = EntityPrefabs.player.duplicate()

    np_rng = np.random.default_rng(RNG_SEED)
    engine = Engine(player=player, np_rng=np_rng, stack=stack)

    factions = FactionsManager(EntityPrefabs.factions)
    engine.game_world = GameWorld(
        factions=factions,
        engine=engine,
        map_width=map_width,
        map_height=map_height,
        max_rooms=max_rooms,
        room_max_size=room_max_size,
        room_min_size=room_min_size,
    )
    engine.game_world.generate_floor()
    engine.game_map.finalize_init()
    engine.update_fov()
    engine.message_log.add(text="Welcome, adventurer.", fg=Theme.welcome_text)
    return engine


def load_game(filepath: str):
    """Load an engine from a file."""
    with open(filepath, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(BaseEventHandler):
    """Handle the main menu rendering and input."""

    def __init__(self, stack: ScreenStack):
        self.stack = stack

    def on_render(self, console: Console, delta_time: float) -> None:
        TITLE = "TSTT's PYTYFYL Roguelike"
        SUBTITLE = "By TypeScriptTeatime"
        MENU_ITEMS = ("[N] New Game", "[C] Continue", "[Q] Quit")
        console.draw_semigraphics(background_image, 0, 0)
        half_height = console.height // 2
        self.render_title(TITLE, console, half_height - 4)
        self.render_title(SUBTITLE, console, console.height - 2)

        for i, text in enumerate(MENU_ITEMS):
            self.render_menu_item(text, console, half_height - 2 + i)

    def render_menu_item(
        self,
        text: str,
        console: Console,
        y: int,
    ):
        half_width = console.width // 2
        menu_width = 24
        console.print(
            x=half_width,
            y=y,
            text=text.ljust(menu_width),
            fg=Theme.menu_text,
            bg=Theme.menu_background,
            bg_blend=BKGND_ALPHA(64),
            alignment=CENTER,
        )

    def render_title(self, text: str, console: Console, y: int):
        half_width = console.width // 2
        console.print(
            x=half_width,
            y=y,
            alignment=CENTER,
            text=text,
            fg=Theme.menu_title,
        )

    def ev_keydown(self, event: tcod.event.KeyDown, /) -> BaseEventHandler | None:
        key = event.sym
        match key:
            case _ if key in {Key.ESCAPE, Key.Q}:
                sys.exit()
            case Key.C:
                return self.try_load_game()
            case Key.N:
                if not os.path.exists(AUTOSAVE_FILENAME):
                    self.stack.pop()
                    return MainGameEventHandler(
                        new_game(self.stack),
                    )

                def _new_game_callback():
                    self.stack.pop()
                    return MainGameEventHandler(
                        new_game(self.stack),
                    )

                return ConfirmationPopup(
                    stack=self.stack,
                    text="Your existing progress will be lost. Continue?",
                    callback=_new_game_callback,
                )
            case _:
                return None

    def try_load_game(self):
        try:
            engine = load_game(AUTOSAVE_FILENAME)
            engine.stack = self.stack
            self.stack.pop()
            return MainGameEventHandler(engine)
        except FileNotFoundError:
            # todo make this work
            return PopupMessage(
                self.stack, f"No save file named {AUTOSAVE_FILENAME} found."
            )
        except Exception as exc:
            traceback.print_exc()
            return PopupMessage(self.stack, f"Failed to load save file:\n{exc}")

import copy
import lzma
import pickle
import sys
import traceback

import tcod
from tcod.console import Console
from tcod.constants import CENTER
from tcod.event import KeySym as Key
from tcod.libtcodpy import BKGND_ALPHA

from py_roguelike_tutorial import input_handlers
from py_roguelike_tutorial.colors import Theme
from py_roguelike_tutorial.constants import SAVE_FILENAME
from py_roguelike_tutorial.engine import Engine
from py_roguelike_tutorial.entity_factory import EntityFactory
from py_roguelike_tutorial.game_world import GameWorld

background_image = tcod.image.load("assets/menu_background.png")[:, :, :3]


def new_game() -> Engine:
    map_width = 80
    map_height = 43
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 2
    max_items_per_room = 2

    player = copy.deepcopy(EntityFactory.player_prefab)
    fb1 = copy.deepcopy(EntityFactory.fireball_scroll_prefab)
    fb2 = copy.deepcopy(EntityFactory.fireball_scroll_prefab)
    fb3 = copy.deepcopy(EntityFactory.fireball_scroll_prefab)
    fb4 = copy.deepcopy(EntityFactory.fireball_scroll_prefab)
    player.inventory.add_many((fb1, fb2, fb3, fb4))

    engine = Engine(player=player)

    engine.game_world = GameWorld(
        engine=engine,
        map_width=map_width,
        map_height=map_height,
        max_rooms=max_rooms,
        room_max_size=room_max_size,
        room_min_size=room_min_size,
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room,
    )
    engine.game_world.generate_floor()
    engine.update_fov()
    engine.message_log.add(text="Welcome, adventurer.", fg=Theme.welcome_text)
    return engine


def load_game(filepath: str):
    """Load an engine from a file."""
    with open(filepath, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    def on_render(self, console: Console) -> None:
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

    def ev_keydown(
        self, event: tcod.event.KeyDown, /
    ) -> input_handlers.BaseEventHandler | None:
        key = event.sym
        match key:
            case _ if key in {Key.ESCAPE, Key.Q}:
                sys.exit()
            case Key.C:
                return self.try_load_game()
            case Key.N:
                return input_handlers.ConfirmationPopup(
                    self,
                    text="Your current progress will be reset. Continue?",
                    callback=lambda: input_handlers.MainGameEventHandler(
                        new_game(),
                    ),
                )
            case _:
                return None

    def try_load_game(self):
        try:
            return input_handlers.MainGameEventHandler(load_game(SAVE_FILENAME))
        except FileNotFoundError:
            return input_handlers.PopupMessage(
                self, f"No save file named {SAVE_FILENAME} found."
            )
        except Exception as exc:
            traceback.print_exc()
            return input_handlers.PopupMessage(
                self, f"Failed to load save file:\n{exc}"
            )
